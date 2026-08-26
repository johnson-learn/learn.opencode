# -*- coding: utf-8 -*-
# 修复 setup-windows.ps1 第 7 步：改用 path_convert.py to_local（占位符体系）
import re

p = "/home/github/learn.opencode/copy/setup/setup-windows.ps1"
with open(p, encoding="utf-8") as f:
    c = f.read()

old_block_start = "  # ---------- 7. 路径改写（旧机路径 → 新机路径） ----------"
new_block = '''  # ---------- 7. 路径改写（占位符 → 新机真实路径，path_convert 体系） ----------
  if (-not $NoPathRewrite) {
    Step "7. 路径改写（占位符转换为新机真实路径）"
    $conv = Join-Path $RepoRoot "scripts\\path_convert.py"
    $homeSlash = $env:USERPROFILE.Replace("\\", "/")
    if (Test-Path $conv) {
      python $conv to_local --home="$homeSlash" $ConfigDir
      python $conv to_local --home="$homeSlash" $ToolDir
      # 填写类占位符检查：提醒用户补 path_map.txt
      $leftover = Get-ChildItem $ConfigDir -Recurse -File -Include "*.md","*.jsonc" -ErrorAction SilentlyContinue | Select-String -Pattern "<(项目|源码|WSL安装|离线安装包|工具|LibreOffice|Chrome|Node|3GPP文档库)目录>" -List -ErrorAction SilentlyContinue
      if ($leftover) {
        Warn "存在未配置的填写类占位符，请编辑 $ConfigDir\\skills\\update_skill\\path_map.txt（每行：占位符=本机真实路径）后重跑："
        Warn "  python $conv to_local --home=`"$homeSlash`" $ConfigDir"
      }
      # 自动类占位符残留检查
      $autoLeft = Get-ChildItem $ConfigDir -Recurse -File -Include "*.md","*.jsonc" -ErrorAction SilentlyContinue | Select-String -Pattern "<用户目录>|<opencode配置目录>|<用户临时目录>" -List -ErrorAction SilentlyContinue
      if ($autoLeft) { Warn "仍有自动类占位符未转换，请检查 python 是否可用" } else { Ok "路径改写完成（占位符已转换为新机路径）" }
    } else { Warn "path_convert.py 不存在（scripts 目录缺失），跳过路径改写" }
  } else { Warn "已跳过路径改写（-NoPathRewrite）" }

# ---------- 5.5 规则注入验证 ----------'''
old_end_marker = "# ---------- 8. 汇总验证 ----------"

# 定位第 7 步块（从 7 注释到 8 注释）
i7 = c.find(old_block_start)
i8 = c.find(old_end_marker)
if i7 < 0 or i8 < 0:
    print("未找到标记，中止", i7, i8)
else:
    # 在 8 之前插入 5.5 验证（其实放在 5 部署之后更合理，这里放在 7 之后、8 之前）
    verify_block = '''
# ---------- 7.5 规则注入验证（语言跟随/输出规则依赖 instructions.md 生效） ----------
  Step "7.5 验证全局规则注入"
  $okJson = (Test-Path (Join-Path $ConfigDir "opencode.jsonc")) -and (Select-String -Path (Join-Path $ConfigDir "opencode.jsonc") -Pattern "instructions" -Quiet)
  $okMd = Test-Path (Join-Path $ConfigDir "instructions.md")
  if ($okJson -and $okMd) {
    Ok "opencode.jsonc 已注册 instructions.md，规则文件已部署"
  } else {
    Warn "规则注入缺失！请确认 $ConfigDir 下有 opencode.jsonc（含 instructions 注册）与 instructions.md"
  }
  Write-Host "  语言规则验证：重启 opencode 后，用中文提问，回答应为中文；若仍为英文，说明 instructions 未加载" -ForegroundColor Yellow
'''
    new7 = old_block_start + new_block
    c = c[:i7] + new7 + verify_block + c[i8:]
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(c)
    print("第 7 步已替换为 path_convert 体系，7.5 验证块已插入")
