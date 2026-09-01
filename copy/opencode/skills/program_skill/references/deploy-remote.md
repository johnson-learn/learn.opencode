# program_skill 参考：远程部署运行（自主"上服务器跑程序"闭环关键）

> 目标：本地 WSL 写好 → 传服务器 → 远程编译/运行 → 日志回传。ssh 免密与目录约定一次性配好。

## 1. ssh 免密（一次性）

```bash
ssh-keygen -t ed25519 -C "备注"          # 本机生成密钥（无密钥时）
ssh-copy-id user@server                  # 公钥注入服务器
ssh user@server "hostname"               # 免密验证
```

## 2. 同步源码（scp/rsync）

```bash
# 全量同步（排除构建产物）
rsync -avz --exclude 'build/' --exclude '*.o' --exclude 'app' \
  /mnt/e/opencode_code/<项目>/ user@server:~/<项目>/
```

## 3. 远程编译运行

```bash
ssh user@server "cd ~/<项目> && make && ./app"          # 一次性
ssh -t user@server "cd ~/<项目> && gdb ./app"           # 远程调试（-t 分配 TTY）
```

## 4. 长驻运行（nohup / systemd）

```bash
# 后台运行 + 日志回传
ssh user@server "cd ~/<项目> && nohup ./app > app.log 2>&1 & echo \$!"
ssh user@server "tail -50 ~/<项目>/app.log"             # 查日志
# 正式服务用 systemd（见下模板）
```

```ini
# /etc/systemd/system/app.service
[Unit]
Description=App Service
After=network.target
[Service]
ExecStart=/home/user/<项目>/app
Restart=always
WorkingDirectory=/home/user/<项目>
[Install]
WantedBy=multi-user.target
```

## 5. 日志回传与比对

```bash
scp user@server:~/<项目>/app.log .                    # 回传
diff <(ssh user@server "cat ~/<项目>/app.log") app.log  # 比对
```

## 铁律

1. 源码同步用 rsync（增量）不用 scp 全量
2. 远程运行前先在本地 WSL 实编译实运行通过（本地不绿不上服务器）
3. 生产进程必须 systemd/nohup 托管，禁止裸 ssh 前台跑
4. 密钥文件权限 600，不入仓库
