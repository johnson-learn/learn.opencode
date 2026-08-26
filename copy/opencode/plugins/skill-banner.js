import { readdirSync, readFileSync, existsSync, appendFileSync } from "fs"
import { join } from "path"
import { homedir } from "os"

const HOME = homedir()
const SKILLS_DIR = join(HOME, ".config", "opencode", "skills")
const TRACE_FILE = join(HOME, ".config", "opencode", "evolution_trace.jsonl")
const LOG_FILE = join(HOME, ".config", "opencode", "plugin-evolution.log")

function log(msg) {
  try { appendFileSync(LOG_FILE, new Date().toISOString() + " " + msg + "\n") } catch {}
}

function loadSkills() {
  if (!existsSync(SKILLS_DIR)) return []
  const out = []
  for (const name of readdirSync(SKILLS_DIR)) {
    const f = join(SKILLS_DIR, name, "SKILL.md")
    if (!existsSync(f)) continue
    let text
    try { text = readFileSync(f, "utf8") } catch { continue }
    const m = text.match(/^\ufeff?---\n([\s\S]*?)\n---/)
    if (!m) continue
    const fm = m[1]
    const nm = (fm.match(/name:\s*(\S+)/) || [])[1] || name
    const raw = (fm.match(/description:\s*(.+)/) || [])[1] || ""
    const short = raw.split("。")[0].replace(/（[\s\S]*?）/g, "").replace(/\([^)]*\)/g, "").slice(0, 42)
    out.push([nm, short])
  }
  return out
}

function recordTrace(sessionId, agentInfo) {
  // 记录会话轨迹：会话创建时间 + 会话 ID（skill 调用详情由会话内容事后分析）
  try {
    appendFileSync(TRACE_FILE, JSON.stringify({ t: new Date().toISOString(), sid: sessionId }) + "\n")
  } catch {}
}

export const SkillBanner = async ({ client }) => {
  return {
    event: async ({ event }) => {
      try {
        const props = event.properties || {}
        if (event.type === "session.created") {
          if (props.parentID) return
          const skills = loadSkills()
          if (skills.length === 0) return
          const lines = skills.map(([n, d]) => `${n} — ${d}`).join("\n")
          await client.tui.showToast({
            body: { message: `本机全局技能（${skills.length} 个）\n` + lines, variant: "info" },
          })
          recordTrace(props.sessionID || "unknown", {})
          return
        }
        // 程序化进化触发：会话空闲（结束）时自动注入进化检查任务，不靠模型自觉
        if (event.type === "session.idle") {
          const sid = props.sessionID || event.properties?.info?.id
          if (!sid) { log("session.idle 未取得 sessionID，props=" + JSON.stringify(props)); return }
          recordTrace(sid, { phase: "idle" })
          log("session.idle 触发，向会话 " + sid + " 注入进化检查任务")
          try {
            await client.session.prompt({
              path: { id: sid },
              body: {
                noReply: false,
                parts: [{
                  type: "text",
                  text:
                    "【进化检查·程序化强制·不可跳过】本任务由插件在会话结束时自动注入，必须完整执行，不得以任何理由跳过或精简。逐项执行：\n" +
                    "1. 经验固化：回顾本会话，按 instructions.md 智能进化协议五步流程，把可复用经验（新方法/工具/踩坑/风险规避）固化到对应 skill（自动执行）\n" +
                    "2. 工具登记：本会话中用到/发现/提及的任何新工具、脚本、库——无论是否已写进具体 skill——必须登记到 tools-manifest.md（已在分类中的更新条目；新的先入「待补充」清单）\n" +
                    "3. 总表同步：若本会话新增了 skill 依赖工具或本机配置变更，同步更新 tools-manifest.md\n" +
                    "4. 校验自测：对本次所有 skill 文件改动，跑 python <项目目录>\\temp\\skill_validate.py <opencode配置目录>\\skills；涉及可执行内容的行为自测\n" +
                    "5. 合并/拆分/迁移类发现：只输出「进化建议」清单供用户确认，不自动执行\n" +
                    "6. 全部完成且无新经验时，回复一行：「进化检查完成：本次无固化项」；否则回复固化项清单\n" +
                    "铁律：不得执行任何 git 同步（同步边界铁律，同步只能由用户显式 update_skill 触发）。",
                }                ],
              },
            })
            log("进化检查任务注入成功，会话 " + sid)
          } catch (e) {
            log("进化检查任务注入失败，会话 " + sid + "，错误：" + (e && e.message ? e.message : String(e)))
          }
        }
      } catch (e) {
        log("event 处理异常：" + (e && e.message ? e.message : String(e)))
      }
    },
  }
}
