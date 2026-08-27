// 插件自测脚本：模拟 opencode 事件，验证 skill-banner.js 全部逻辑分支
import { appendFileSync, existsSync, readFileSync, unlinkSync, writeFileSync } from "fs"
import { join } from "path"
import { homedir } from "os"

const HOME = homedir()
const TRACE = join(HOME, ".config", "opencode", "skills", "default", "evolution_skill", "evolution_trace.jsonl")
const LOG = join(HOME, ".config", "opencode", "plugins", "plugin-evolution.log")

// 清理旧测试数据
for (const f of [TRACE, LOG]) { try { unlinkSync(f) } catch {} }

// 加载插件模块
const mod = await import("file://" + join(HOME, ".config", "opencode", "plugins", "skill-banner.js").replace(/\\/g, "/"))

// mock client
const calls = { toast: [], prompt: [], messages: [] }
let mockMessages = []
const client = {
  tui: { showToast: async (x) => { calls.toast.push(x) } },
  session: {
    prompt: async (x) => { calls.prompt.push(x) },
    messages: async (x) => { calls.messages.push(x); return { data: mockMessages } },
  },
}

const plugin = await mod.SkillBanner({ client })
const handler = plugin.event

let pass = 0, fail = 0
function check(name, cond) {
  if (cond) { pass++; console.log("  ✓ " + name) } else { fail++; console.log("  ✗ " + name) }
}

// === 测试 1：session.created（主会话）→ toast 展示技能列表 + 注入注册表提醒 ===
console.log("[测试1] session.created 主会话")
await handler({ event: { type: "session.created", properties: { sessionID: "sess-main-001" } } })
check("toast 被调用", calls.toast.length === 1)
check("toast 含技能清单标题", calls.toast[0] && calls.toast[0].body.message.includes("本机全局技能"))
check("toast 列出 update_skill", calls.toast[0] && calls.toast[0].body.message.includes("update_skill"))
check("prompt 被调用 1 次（注册表提醒）", calls.prompt.length === 1)
const rem = calls.prompt[0] && calls.prompt[0].body || {}
check("注册表提醒为 noReply 静默", rem.noReply === true)
const remText = calls.prompt[0] && calls.prompt[0].body.parts[0].text || ""
check("提醒含 regedit.md", remText.includes("regedit.md"))
check("提醒含铁律第 0 条标记", remText.includes("铁律第0条"))

// === 测试 2：session.created（子会话）→ 不弹 toast ===
console.log("[测试2] session.created 子会话")
const toastCountBefore = calls.toast.length
const promptCountBefore2 = calls.prompt.length
await handler({ event: { type: "session.created", properties: { sessionID: "sess-child-002", parentID: "sess-main-001" } } })
check("子会话不弹 toast", calls.toast.length === toastCountBefore)
check("子会话不注入提醒", calls.prompt.length === promptCountBefore2)

// === 测试 3：session.idle → 注入进化检查任务 ===
console.log("[测试3] session.idle 注入进化检查")
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-main-001" } } })
check("prompt 累计 2 次", calls.prompt.length === 2)
const task = calls.prompt[1] && calls.prompt[1].body && calls.prompt[1].body.parts[0].text || ""
check("任务含【进化检查】标记", task.includes("进化检查"))
check("任务含工具登记要求", task.includes("tools-manifest"))
check("任务含校验自测要求", task.includes("skill_validate"))
check("任务含同步边界铁律", task.includes("git"))
check("prompt 会话 ID 正确", calls.prompt[1].path.id === "sess-main-001")

// === 测试 3b：session.idle 幂等去重（同会话二次 idle 不重复注入） ===
console.log("[测试3b] session.idle 幂等去重")
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-main-001" } } })
check("同会话二次 idle 不重复注入", calls.prompt.length === 2)

// === 测试 3c：五步检查点程序化强制（会话含固化但缺五步标记 → 任务附缺步警告） ===
console.log("[测试3c] 五步检查点缺步警告")
mockMessages = [{ info: { role: "assistant" }, parts: [{ type: "text", text: "进化：已固化 xxx\n但没有输出五步标记" }] }]
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-five-001" } } })
check("prompt 累计 3 次", calls.prompt.length === 3)
const fiveTask = calls.prompt[2] && calls.prompt[2].body && calls.prompt[2].body.parts[0].text || ""
check("缺步时任务附【五步检查点·程序化强制】警告", fiveTask.includes("五步检查点·程序化强制"))
check("警告点名缺失步骤（第二步·归属）", fiveTask.includes("第二步·归属"))
check("补做任务要求五步标记格式", fiveTask.includes("【第一步·归纳】"))

// === 测试 3d：五步检查点齐全 → 任务不含缺步警告 ===
console.log("[测试3d] 五步检查点齐全")
mockMessages = [{ info: { role: "assistant" }, parts: [{ type: "text", text: "进化：已固化 xxx\n【第一步·归纳】a\n【第二步·归属】b\n【第三步·edit】c\n【第四步·流水】d\n【第五步·校验】e" }] }]
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-five-002" } } })
check("prompt 累计 4 次", calls.prompt.length === 4)
const okTask = calls.prompt[3] && calls.prompt[3].body && calls.prompt[3].body.parts[0].text || ""
check("五步齐全时任务不含缺步警告", !okTask.includes("五步检查点·程序化强制"))

// === 测试 3e：messages 拉取异常 → 五步检查静默跳过，任务照常注入 ===
console.log("[测试3e] messages 异常容错")
const origMessages = client.session.messages
client.session.messages = async () => { throw new Error("messages api down") }
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-five-003" } } })
check("异常时任务照常注入（prompt 累计 5 次）", calls.prompt.length === 5)
check("异常时任务仍含进化检查主标记", (calls.prompt[4].body.parts[0].text || "").includes("进化检查"))
client.session.messages = origMessages

// === 测试 4：session.idle 无 sessionID → 不崩且记日志 ===
console.log("[测试4] session.idle 缺 sessionID")
const promptCountAfter5 = calls.prompt.length
await handler({ event: { type: "session.idle", properties: {} } })
check("无 sessionID 时 prompt 不增加", calls.prompt.length === promptCountAfter5)

// === 测试 5：未知事件 → 无副作用 ===
console.log("[测试5] 未知事件")
await handler({ event: { type: "session.unknown", properties: {} } })
check("未知事件无副作用（toast/prompt 均不增加）", calls.prompt.length === promptCountAfter5 && calls.toast.length === toastCountBefore)

// === 测试 6：轨迹与日志文件落盘 ===
console.log("[测试6] 轨迹与日志落盘")
check("evolution_trace.jsonl 已生成", existsSync(TRACE))
check("plugin-evolution.log 已生成且含注入记录", existsSync(LOG) && readFileSync(LOG, "utf8").includes("进化检查任务注入成功"))

// === 测试 7：注册事件注入 hook 存在 ===
console.log("[测试7] experimental.chat.system.transform hook")
const hook = plugin["experimental.chat.system.transform"]
check("hook 存在且为函数", typeof hook === "function")

// === 测试 8：注入 4 个 md 文件内容到 output.system ===
console.log("[测试8] 系统提示注入 4 文件")
const out1 = { system: ["orig-prompt"] }
await hook({ sessionID: "sess-inj-1" }, out1)
check("system 增加 1 个元素", out1.system.length === 2)
check("原内容未变", out1.system[0] === "orig-prompt")
const inj = out1.system[1] || ""
check("注入带【注册规则注入】标记", inj.includes("注册规则注入"))
check("含 instructions.md 注入标记", inj.includes("注入文件 instructions.md"))
check("含 regedit.md 注入标记", inj.includes("注入文件 regedit.md"))
check("含 docs-sync.md 注入标记", inj.includes("注入文件 docs-sync.md"))
check("含 tools-manifest.md 注入标记", inj.includes("注入文件 tools-manifest.md"))
check("regedit.md 正文被注入（A 系统注入字样）", inj.includes("A 系统注入"))

// === 测试 9：mtime 缓存——文件变化后注入更新 ===
console.log("[测试9] 缓存刷新")
const MAN = join(HOME, ".config", "opencode", "tools-manifest.md")
const origMan = readFileSync(MAN, "utf8")
try {
  appendFileSync(MAN, "\n<!-- CACHE_TEST_MARKER -->\n")
  const out2 = { system: [] }
  await hook({ sessionID: "sess-inj-2" }, out2)
  check("文件变化后缓存刷新（新 marker 进入注入）", (out2.system[0] || "").includes("CACHE_TEST_MARKER"))
} finally {
  writeFileSync(MAN, origMan)
}
const out3 = { system: [] }
await hook({ sessionID: "sess-inj-3" }, out3)
check("恢复文件后注入不再含 marker", !(out3.system[0] || "").includes("CACHE_TEST_MARKER"))

// === 测试 10：环境变量开关禁用 ===
console.log("[测试10] 环境变量开关")
process.env.OPENCODE_DISABLE_MD_INJECT = "1"
const out4 = { system: ["only"] }
await hook({ sessionID: "sess-inj-4" }, out4)
check("禁用时不注入（system 不变）", out4.system.length === 1 && out4.system[0] === "only")
delete process.env.OPENCODE_DISABLE_MD_INJECT

// === 测试 11：异常输出结构不崩 ===
console.log("[测试11] 异常输出结构")
await hook({ sessionID: "sess-inj-5" }, {})
await hook({ sessionID: "sess-inj-6" }, { system: "not-array" })
await hook({ sessionID: "sess-inj-7" }, null)
check("3 种非法 output 均无异常", true)

// === 测试 12：平台 API 保障异步检查落日志（实验性 hook 风险闭环） ===
console.log("[测试12] 平台 API 保障检查")
let apiLogged = false
for (let i = 0; i < 20; i++) {
  if (existsSync(LOG) && readFileSync(LOG, "utf8").includes("test_platform_api")) { apiLogged = true; break }
  await new Promise((r) => setTimeout(r, 500))
}
check("日志含 test_platform_api 检查记录（异步闭环已触发）", apiLogged)

console.log("\n结果：通过 " + pass + " 项，失败 " + fail + " 项")
process.exit(fail > 0 ? 1 : 0)
