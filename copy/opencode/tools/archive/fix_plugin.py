# -*- coding: utf-8 -*-
# 修复 skill-banner.js 缺失的 export 闭合
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r"<opencode配置目录>\plugins\skill-banner.js"
c = open(p, encoding="utf-8").read()
old = '''      } catch (e) {
        log("event \u5904\u7406\u5f02\u5e38\uff1a" + (e && e.message ? e.message : String(e)))
      }
  }
}'''
new = '''      } catch (e) {
        log("event \u5904\u7406\u5f02\u5e38\uff1a" + (e && e.message ? e.message : String(e)))
      }
    },
  }
}'''
if old in c:
    c = c.replace(old, new)
    open(p, "w", encoding="utf-8", newline="").write(c)
    print("已补回 export 闭合")
else:
    print("未匹配，文件末尾 200 字:")
    print(repr(c[-200:]))
