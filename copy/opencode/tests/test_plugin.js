// 插件自测脚本：模拟 opencode 事件，验证 skill-banner.js 全部逻辑分支
import { appendFileSync, existsSync, readFileSync, unlinkSync } from "fs"
import { join } from "path"
import { homedir } from "os"

const HOME = homedir()
const TRACE = join(HOME, ".config", "opencode", "evolution_trace.jsonl")
const LOG = join(HOME, ".config", "opencode", "plugin-evolution.log")

// 清理旧测试数据
for (const f of [TRACE, LOG]) { try { unlinkSync(f) } catch {} }

// 加载插件模块
const mod = await import("file://" + join(HOME, ".config", "opencode", "plugins", "skill-banner.js").replace(/\\/g, "/"))

// mock client
const calls = { toast: [], prompt: [] }
const client = {
  tui: { showToast: async (x) => { calls.toast.push(x) } },
  session: { prompt: async (x) => { calls.prompt.push(x) } },
}

const plugin = await mod.SkillBanner({ client })
const handler = plugin.event

let pass = 0, fail = 0
function check(name, cond) {
  if (cond) { pass++; console.log("  ✓ " + name) } else { fail++; console.log("  ✗ " + name) }
}

// === 测试 1：session.created（主会话）→ toast 展示技能列表 ===
console.log("[测试1] session.created 主会话")
await handler({ event: { type: "session.created", properties: { sessionID: "sess-main-001" } } })
check("toast 被调用", calls.toast.length === 1)
check("toast 含技能清单标题", calls.toast[0] && calls.toast[0].body.message.includes("本机全局技能"))
check("toast 列出 update_skill", calls.toast[0] && calls.toast[0].body.message.includes("update_skill"))
check("prompt 未被调用（created 不应注入任务）", calls.prompt.length === 0)

// === 测试 2：session.created（子会话）→ 不弹 toast ===
console.log("[测试2] session.created 子会话")
const toastCountBefore = calls.toast.length
await handler({ event: { type: "session.created", properties: { sessionID: "sess-child-002", parentID: "sess-main-001" } } })
check("子会话不弹 toast", calls.toast.length === toastCountBefore)

// === 测试 3：session.idle → 注入进化检查任务 ===
console.log("[测试3] session.idle 注入进化检查")
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-main-001" } } })
check("prompt 被调用一次", calls.prompt.length === 1)
const task = calls.prompt[0] && calls.prompt[0].body && calls.prompt[0].body.parts[0].text || ""
check("任务含【进化检查】标记", task.includes("进化检查"))
check("任务含工具登记要求", task.includes("tools-manifest"))
check("任务含校验自测要求", task.includes("skill_validate"))
check("任务含同步边界铁律", task.includes("git"))
check("prompt 会话 ID 正确", calls.prompt[0].path.id === "sess-main-001")

// === 测试 4：session.idle 无 sessionID → 不崩且记日志 ===
console.log("[测试4] session.idle 缺 sessionID")
await handler({ event: { type: "session.idle", properties: {} } })
check("无 sessionID 时 prompt 不增加", calls.prompt.length === 1)

// === 测试 5：未知事件 → 无副作用 ===
console.log("[测试5] 未知事件")
await handler({ event: { type: "session.unknown", properties: {} } })
check("未知事件无副作用（toast/prompt 均不增加）", calls.prompt.length === 1 && calls.toast.length === toastCountBefore)

// === 测试 6：轨迹与日志文件落盘 ===
console.log("[测试6] 轨迹与日志落盘")
check("evolution_trace.jsonl 已生成", existsSync(TRACE))
check("plugin-evolution.log 已生成且含注入记录", existsSync(LOG) && readFileSync(LOG, "utf8").includes("进化检查任务注入成功"))

console.log("\n结果：通过 " + pass + " 项，失败 " + fail + " 项")
process.exit(fail > 0 ? 1 : 0)
