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

// === 测试 3：session.idle → 只跑机器步骤记录待办，不向旧会话注入 prompt（方案A 时序修复） ===
console.log("[测试3] session.idle 记录进化待办（不再唤醒旧会话）")
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-main-001" } } })
check("idle 后 prompt 不增加（旧会话不被唤醒）", calls.prompt.length === 1)

// === 测试 3b：session.idle 幂等去重（同会话二次 idle 不重复记录） ===
console.log("[测试3b] session.idle 幂等去重")
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-main-001" } } })
check("同会话二次 idle 无副作用（prompt 不增加）", calls.prompt.length === 1)
check("幂等日志已记录", existsSync(LOG) && readFileSync(LOG, "utf8").includes("已写过进化待办"))

// === 测试 3c：六步缺步 → 待办含警告 → 新会话创建时静默注入 ===
console.log("[测试3c] 六步缺步 → 新会话静默注入")
mockMessages = [{ info: { role: "assistant" }, parts: [{ type: "text", text: "进化：已固化 xxx\n但没有输出六步标记" }] }]
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-five-001" } } })
await handler({ event: { type: "session.created", properties: { sessionID: "sess-five-created" } } })
const lastPrompt = calls.prompt[calls.prompt.length - 1]
const fiveTask = lastPrompt && lastPrompt.body && lastPrompt.body.parts[0].text || ""
check("新会话收到进化检查任务（静默 noReply）", lastPrompt && lastPrompt.body.noReply === true && fiveTask.includes("进化检查"))
check("任务含执行时机指令（首次回复先输出进化检查结论）", fiveTask.includes("执行时机") && fiveTask.includes("进化检查完成：本次无固化项"))
check("任务附【固化检查点·程序化强制】警告", fiveTask.includes("固化检查点·程序化强制"))
check("警告点名缺失步骤（第二步·归属）", fiveTask.includes("第二步·归属"))
check("补做任务要求六步标记格式", fiveTask.includes("【第一步·归纳】") && fiveTask.includes("【第三步·确认】"))
const promptCountAfter3c = calls.prompt.length
await handler({ event: { type: "session.created", properties: { sessionID: "sess-five-created-again" } } })
check("注入后待办已消费（再次创建不再注入进化任务）", calls.prompt.length === promptCountAfter3c + 1)

// === 测试 3d：六步齐全 → 新会话任务不含缺步警告 ===
console.log("[测试3d] 六步齐全")
mockMessages = [{ info: { role: "assistant" }, parts: [{ type: "text", text: "进化：已固化 xxx\n【第一步·归纳】a\n【判定四条件】场景数：2 / 可移植：是（不含本机路径）/ 无重复：是（已比对）/ 边界：明确\n【第二步·归属】b\n【第三步·确认】c\n【第四步·edit】d\n【第五步·流水】e\n【第六步·校验】f" }] }]
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-five-002" } } })
await handler({ event: { type: "session.created", properties: { sessionID: "sess-five-created2" } } })
const okTask = calls.prompt[calls.prompt.length - 1].body.parts[0].text || ""
check("六步齐全时任务不含缺步警告", !okTask.includes("固化检查点·程序化强制"))

// === 测试 3f：使用率追踪（V5 方案甲'：会话级关键词匹配写 evolution_trace.jsonl） ===
console.log("[测试3f] 使用率追踪")
const src = readFileSync(join(HOME, ".config", "opencode", "plugins", "skill-banner.js"), "utf8")
check("源码含使用率追踪函数与调用点", src.includes("trackExperienceUsage") && src.includes("collectExperienceKeywords"))
check("关键词解析含泛词过滤（防误报）", src.includes("generic") && src.includes("length >= 4"))
check("会话级匹配写 evolution_trace.jsonl", src.includes("TRACE_FILE") && src.includes("JSON.stringify({ t:"))

// === 测试 3g：messages 拉取异常 → 固化检查静默跳过，待办与注入不受影响 ===
console.log("[测试3g] messages 异常容错")
const origMessages = client.session.messages
client.session.messages = async () => { throw new Error("messages api down") }
await handler({ event: { type: "session.idle", properties: { sessionID: "sess-five-003" } } })
await handler({ event: { type: "session.created", properties: { sessionID: "sess-five-created3" } } })
const exTask = calls.prompt[calls.prompt.length - 1].body.parts[0].text || ""
check("异常时任务仍含进化检查主标记", exTask.includes("进化检查"))
client.session.messages = origMessages

// === 测试 3h：无待办时新会话创建 → 只注入注册表提醒，不注入进化任务 ===
console.log("[测试3h] 无待办时创建不注入")
const promptCountBefore3f = calls.prompt.length
await handler({ event: { type: "session.created", properties: { sessionID: "sess-clean-004" } } })
check("无待办时 prompt 只增 1 次（注册表提醒）", calls.prompt.length === promptCountBefore3f + 1)
check("新增 prompt 为注册表提醒而非进化任务", calls.prompt[calls.prompt.length - 1].body.parts[0].text.includes("注册表必读"))

// === 测试 3i：使用率追踪端到端行为测试（V6 修复 ELOG bug 后补的测试缺口——报告点名测试体系应捕获此 bug） ===
console.log("[测试3i] 使用率追踪端到端")
const ELOG_TEST = join(HOME, ".config", "opencode", "skills", "default", "evolution_skill", "evolution_log.txt")
const realElog = existsSync(ELOG_TEST) ? readFileSync(ELOG_TEST, "utf8") : ""
try {
  writeFileSync(ELOG_TEST, "[2026-08-28] 测试经验A\n- 状态：active\n- 核心关键词：网关鉴权、链路预算\n\n[2026-08-28] 测试经验B\n- 状态：deprecated\n- 核心关键词：废弃机制\n")
  const mod2 = await import("file://" + join(HOME, ".config", "opencode", "plugins", "skill-banner.js").replace(/\\/g, "/") + "?v=usage")
  const plugin2 = await mod2.SkillBanner({ client })
  const h2 = plugin2.event
  mockMessages = [{ info: { role: "assistant" }, parts: [{ type: "text", text: "今天讨论网关鉴权方案与链路预算" }] }]
  await h2({ event: { type: "session.idle", properties: { sessionID: "sess-usage-001" } } })
  await new Promise(r => setTimeout(r, 400))
  const traceTxt = existsSync(TRACE) ? readFileSync(TRACE, "utf8") : ""
  check("使用率追踪端到端写入 trace（active 经验命中）", traceTxt.includes("测试经验A"))
  check("deprecated 条目不参与使用率匹配", !traceTxt.includes("测试经验B"))
  check("ELOG 常量已定义（V6 P0 bug 修复防回归）", readFileSync(join(HOME, ".config", "opencode", "plugins", "skill-banner.js"), "utf8").includes("const ELOG = join"))
} finally {
  writeFileSync(ELOG_TEST, realElog)
}

// === 测试 4：session.idle 无 sessionID → 不崩且记日志 ===
console.log("[测试4] session.idle 缺 sessionID")
const promptCountAfter5 = calls.prompt.length
await handler({ event: { type: "session.idle", properties: {} } })
check("无 sessionID 时 prompt 不增加", calls.prompt.length === promptCountAfter5)

// === 测试 5：未知事件 → 无副作用 ===
console.log("[测试5] 未知事件")
const promptCountB5 = calls.prompt.length
const toastCountB5 = calls.toast.length
await handler({ event: { type: "session.unknown", properties: {} } })
check("未知事件无副作用（toast/prompt 均不增加）", calls.prompt.length === promptCountB5 && calls.toast.length === toastCountB5)

// === 测试 6：轨迹与日志文件落盘 ===
console.log("[测试6] 轨迹与日志落盘")
check("evolution_trace.jsonl 已生成", existsSync(TRACE))
check("plugin-evolution.log 已生成且含待办写入记录", existsSync(LOG) && readFileSync(LOG, "utf8").includes("进化待办已写入"))

// === 测试 7：注册事件注入 hook 存在 ===
console.log("[测试7] experimental.chat.system.transform hook")
const hook = plugin["experimental.chat.system.transform"]
check("hook 存在且为函数", typeof hook === "function")

// === 测试 8：注入 4 个 md 文件内容 + 语言指令到 output.system ===
console.log("[测试8] 系统提示注入 4 文件 + 语言指令")
const out1 = { system: ["orig-prompt"] }
await hook({ sessionID: "sess-inj-1" }, out1)
check("system 增加 2 个元素（注入文件 + 语言指令）", out1.system.length === 3)
check("原内容未变", out1.system[0] === "orig-prompt")
const inj = out1.system[1] || ""
check("注入带【注册规则注入】标记", inj.includes("注册规则注入"))
check("含 instructions.md 注入标记", inj.includes("注入文件 instructions.md"))
check("含 regedit.md 注入标记", inj.includes("注入文件 regedit.md"))
check("含 docs-sync.md 注入标记", inj.includes("注入文件 docs-sync.md"))
check("含 tools-manifest.md 注入标记", inj.includes("注入文件 tools-manifest.md"))
check("regedit.md 正文被注入（A 系统注入字样）", inj.includes("A 系统注入"))
const langInj = out1.system[2] || ""
check("注入平台检测语言指令（默认中文）", langInj.includes("语言指令·平台检测") && langInj.includes("中文"))
check("语言指令为持续性约束（后续任何时候，非仅当前提问）", langInj.includes("后续任何时候") && langInj.includes("直到平台下一次更新语言指令"))

// === 测试 9：mtime 缓存——文件变化后注入更新（消毒式：按行过滤 marker，不依赖快照，防中断残留） ===
console.log("[测试9] 缓存刷新")
const MAN = join(HOME, ".config", "opencode", "tools-manifest.md")
const cleanMarkers = () => {
  const cc = readFileSync(MAN, "utf8")
  const cleaned = cc.replace(/\n<!-- CACHE_TEST_MARKER -->\n?/g, "")
  if (cleaned !== cc) writeFileSync(MAN, cleaned)
}
cleanMarkers() // 防上次异常中断的残留污染真实文件
appendFileSync(MAN, "\n<!-- CACHE_TEST_MARKER -->\n")
const out2 = { system: [] }
await hook({ sessionID: "sess-inj-2" }, out2)
check("文件变化后缓存刷新（新 marker 进入注入）", (out2.system[0] || "").includes("CACHE_TEST_MARKER"))
cleanMarkers() // 立即消毒，恢复真实文件
const out3 = { system: [] }
await hook({ sessionID: "sess-inj-3" }, out3)
check("恢复文件后注入不再含 marker", !(out3.system[0] || "").includes("CACHE_TEST_MARKER"))
cleanMarkers() // 收尾消毒（兜底）

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

// === 测试 13：平台语言检测（用户消息文本 → 明确语言指令注入） ===
console.log("[测试13] 平台语言检测")
await handler({ event: { type: "message.part.updated", properties: { part: { text: "你好，帮我查天气", role: "user" } } } })
const outL1 = { system: [] }
await hook({ sessionID: "sess-lang-1" }, outL1)
check("中文用户消息 → 注入中文语言指令", (outL1.system[outL1.system.length - 1] || "").includes("最新消息为中文"))
await handler({ event: { type: "message.part.updated", properties: { part: { text: "Hello, what's the weather", role: "user" } } } })
const outL2 = { system: [] }
await hook({ sessionID: "sess-lang-2" }, outL2)
check("英文用户消息 → 注入英文语言指令", (outL2.system[outL2.system.length - 1] || "").includes("最新消息为英文"))
await handler({ event: { type: "message.part.updated", properties: { part: { text: "assistant thinking in English", role: "assistant" } } } })
const outL3 = { system: [] }
await hook({ sessionID: "sess-lang-3" }, outL3)
check("非用户消息不更新语言（保持英文）", (outL3.system[outL3.system.length - 1] || "").includes("最新消息为英文"))
await handler({ event: { type: "message.part.updated", properties: { part: { role: "user" } } } })
await handler({ event: { type: "message.part.updated", properties: {} } })
check("无文本/空事件不崩", true)

console.log("\n结果：通过 " + pass + " 项，失败 " + fail + " 项")
process.exit(fail > 0 ? 1 : 0)
