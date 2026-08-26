import { readdirSync, readFileSync, existsSync, appendFileSync } from "fs"
import { join } from "path"
import { homedir } from "os"

const HOME = homedir()
const SKILLS_DIR = join(HOME, ".config", "opencode", "skills")
const TRACE_FILE = join(HOME, ".config", "opencode", "evolution_trace.jsonl")

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
          if (!sid) return
          recordTrace(sid, { phase: "idle" })
          try {
            await client.session.prompt({
              path: { id: sid },
              body: {
                noReply: false,
                parts: [{
                  type: "text",
                  text:
                    "【进化检查·程序化强制】按 instructions.md 智能进化协议执行：1) 回顾本会话，归纳可固化经验（新方法/工具/踩坑/风险规避，按可移植性要求通用化）；2) 判定归属 skill 章节并 edit 更新；3) 若发现两个 skill 功能重叠、某 skill 职责过多、或值得新建全局 skill 的主题，**不要直接执行合并/拆分/新建**，只在回答末尾输出「进化建议」清单供用户确认；4) 无新经验则回复"本次无进化项"。注意：不得执行任何 git 同步（同步边界铁律）。",
                }],
              },
            })
          } catch {}
        }
      } catch {}
    },
  }
}
