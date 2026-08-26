# -*- coding: utf-8 -*-
content = """

## 路径可移植配置（clone 后必做，把占位符转成本机真实路径）

仓库内所有文件使用占位符表示路径（如 <用户目录>、<项目目录>），clone 后必须转换：

1. 填写本机路径映射（skills 复制到本机后）：
   - 编辑 <用户目录>\\.config\\opencode\\skills\\update_skill\\path_map.txt，每行 `占位符=本机真实路径`：
     ```
     <项目目录>=D:\\work\\project
     <源码目录>=D:\\code
     <WSL安装目录>=D:\\WSL
     <离线安装包目录>=D:\\software\\wls
     <工具目录>=D:\\
     <LibreOffice目录>=<工具目录>\Program Files\\LibreOffice
     <Chrome目录>=<工具目录>\Program Files\\Google\\Chrome\\Application
     <Node目录>=<工具目录>\Program Files\\nodejs
     <3GPP文档库目录>=D:\\docs\\NR
     ```
2. 执行转换（占位符转为本机真实路径）：
   ```
   python scripts\\path_convert.py to_local --home="<本机用户目录正斜杠>" <本机opencode配置目录>
   python scripts\\path_convert.py to_local --home="<本机用户目录正斜杠>" <用户临时目录>\\opencode
   ```
3. 校验残留：grep 搜索 "<用户目录>" 等占位符应为空
4. 自动类占位符（用户目录等）无需填写，脚本按新机器自动推导
"""
with open("/home/github/learn.opencode/copy/INSTALL.md", "a", encoding="utf-8") as f:
    f.write(content)
print("INSTALL.md 已追加路径配置说明")
