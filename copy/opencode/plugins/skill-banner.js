import { readdirSync, readFileSync, existsSync } from "fs"
import { join } from "path"

function loadSkills() {
  const home = process.env.USERPROFILE || process.env.HOME
  const dir = join(home, ".config", "opencode", "skills")
  if (!existsSync(dir)) return []
  const out = []
  for (const name of readdirSync(dir)) {
    const f = join(dir, name, "SKILL.md")
    if (!existsSync(f)) continue
    let text
    try { text = readFileSync(f, "utf8") } catch { continue }
    const m = text.match(/^---\n([\s\S]*?)\n---/)
    if (!m) continue
    const fm = m[1]
    const nm = (fm.match(/name:\s*(\S+)/) || [])[1] || name
    const raw = (fm.match(/description:\s*(.+)/) || [])[1] || ""
    const short = raw
      .split("。")[0]
      .replace(/（[\s\S]*?）/g, "")
      .replace(/\([^)]*\)/g, "")
      .slice(0, 42)
    out.push([nm, short])
  }
  return out
}

export const SkillBanner = async ({ client }) => {
  return {
    event: async ({ event }) => {
      try {
        if (event.type !== "session.created") return
        const props = event.properties || {}
        if (props.parentID) return
        const skills = loadSkills()
        if (skills.length === 0) return
        const lines = skills.map(([n, d]) => `${n} — ${d}`).join("\n")
        await client.tui.showToast({
          body: {
            message: `本机全局技能（${skills.length} 个）\n` + lines,
            variant: "info",
          },
        })
      } catch (e) {}
    },
  }
}
