import { readdirSync, readFileSync, existsSync, appendFileSync, statSync } from "fs"
import { join } from "path"
import { homedir } from "os"
import { execSync, spawn } from "child_process"

const HOME = homedir()
const SKILLS_DIR = join(HOME, ".config", "opencode", "skills")
const TRACE_FILE = join(HOME, ".config", "opencode", "skills", "default", "evolution_skill", "evolution_trace.jsonl")
const LOG_FILE = join(HOME, ".config", "opencode", "plugins", "plugin-evolution.log")
const ELOG = join(HOME, ".config", "opencode", "skills", "default", "evolution_skill", "evolution_log.txt")
const GATE = join(HOME, ".config", "opencode", "tools", "evolution_gate.py")
const API_TEST = join(HOME, ".config", "opencode", "tests", "test_platform_api.py")

// === 注册事件注入（E 类 100% 平台执行）：experimental.chat.system.transform ===
// 平台在每次 LLM 请求构建系统提示时触发本 hook（LLMRequestPrep.prepare），
// 插件直读 4 个铁律/协议文件并 push 进 output.system，内容与 AGENTS.md 同级进入系统提示。
// 环境变量 OPENCODE_DISABLE_MD_INJECT=1 可禁用。
const CONFIG_DIR = join(HOME, ".config", "opencode")
const INJECT_FILES = ["instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md"]

let injectCache = null

// === 语言检测（2026-08-27 用户方案：平台确定性识别提问语言，直接下达语言指令） ===
// 规则文本"用提问语言思考回答"是间接指令，部分模型无法识别自己的输入语言。
// 平台在 message.part.updated 事件里检测用户消息语言（含 CJK 字符=中文，否则=英文），
// system.transform 时把明确指令"请用中文/英文思考（含思考过程）并回答"注入系统提示。
let currentLang = "中文"

function detectLang(text) {
  if (!text) return null
  return /[\u4e00-\u9fff]/.test(text) ? "中文" : "英文"
}

function langLine() {
  return "【语言指令·平台检测】平台已检测用户最新消息为" + currentLang +
    "——本次会话期间，后续任何时候你的全部思考（含思考过程）、回答、输出都必须使用" + currentLang +
    "，直到平台下一次更新语言指令；任何情况下不得自行改用其它语言。"
}

function loadInjectContent() {
  // mtimeNs+size 缓存：文件未变时不重复读盘（hook 每次请求触发，须轻量）
  // 用纳秒精度 mtimeNs（Node 12+），防毫秒精度下连续写文件 mtime 相同致缓存不刷新
  let key = ""
  for (const f of INJECT_FILES) {
    try {
      const st = statSync(join(CONFIG_DIR, f), { bigint: true })
      key += f + ":" + st.mtimeNs.toString() + ":" + st.size.toString() + "|"
    } catch { key += f + ":missing|" }
  }
  if (injectCache && injectCache.key === key) return injectCache.text
  const parts = []
  for (const f of INJECT_FILES) {
    try { parts.push("<!-- 注入文件 " + f + " -->\n" + readFileSync(join(CONFIG_DIR, f), "utf8")) } catch {}
  }
  const text = parts.length
    ? "【注册规则注入】以下内容由 skill-banner 插件注册的 experimental.chat.system.transform 事件在每次请求构建系统提示时平台直读注入（E 类 100% 执行），与 AGENTS.md 同级生效：\n\n" + parts.join("\n\n")
    : ""
  injectCache = { key, text }
  return text
}

function runGate(action, sid) {
  // 进化门禁脚本：机制步骤（流水兜底/自动测试）确定性执行，不依赖模型自觉
  try {
    const out = execSync(`python "${GATE}" ${action} "${sid}"`, {
      timeout: 240000, encoding: "utf8", windowsHide: true,
    })
    return out.trim()
  } catch (e) {
    log("evolution_gate " + action + " 执行失败：" + (e && e.message ? String(e.message).slice(0, 200) : ""))
    return ""
  }
}

function runGateAsync(action) {
  // 异步后台执行（不阻塞会话创建）：drain 补跑残留快照可能耗时，输出写入插件日志
  try {
    const child = spawn("python", [GATE, action], {
      windowsHide: true, detached: false, stdio: "ignore",
    })
    child.on("error", (e) => log("evolution_gate " + action + " 异步启动失败：" + String(e && e.message).slice(0, 150)))
    log("evolution_gate " + action + " 已异步启动（后台补跑，不阻塞会话）")
  } catch (e) {
    log("evolution_gate " + action + " 异步启动异常：" + (e && e.message ? String(e.message).slice(0, 150) : ""))
  }
}

function runApiCheckAsync(client) {
  // 平台 API 保障闭环：实验性 hook 依赖风险——opencode 升级移除 API 后首次会话即 toast 告警
  try {
    const child = spawn("python", [API_TEST], { windowsHide: true, stdio: "ignore" })
    child.on("exit", (code) => {
      if (code !== 0) {
        try {
          client.tui.showToast({
            body: {
              message:
                "【框架风险告警】test_platform_api 未通过（rc=" + code + "）：experimental.chat.system.transform 可能已被当前 opencode 版本移除，注册事件注入机制失效。请跑 python " + API_TEST + " 查看详情，并按 regedit.md 注入策略回退预案处理。",
              variant: "warning",
            },
          })
        } catch (e) {
          log("API 风险告警 toast 失败：" + String(e && e.message).slice(0, 120))
        }
        log("test_platform_api 未通过（rc=" + code + "），实验性 hook 依赖风险告警已触发")
      } else {
        log("test_platform_api 通过，平台 API 依赖正常")
      }
    })
    child.on("error", (e) => log("test_platform_api 异步启动失败：" + String(e && e.message).slice(0, 150)))
  } catch (e) {
    log("runApiCheckAsync 异常：" + (e && e.message ? String(e.message).slice(0, 150) : ""))
  }
}

async function fetchAssistantText(client, sid) {
  // 拉取会话 assistant 文本（五步检查与使用率追踪共用；最近 40 条消息）
  let text = ""
  try {
    const resp = await client.session.messages({ path: { id: sid } })
    const msgs = (resp && resp.data) || []
    for (const m of msgs.slice(-40)) {
      if (!m || !m.info || m.info.role !== "assistant") continue
      for (const p of m.parts || []) {
        if (p && p.type === "text" && p.text) text += p.text + "\n"
      }
    }
  } catch (e) {
    log("session.idle 拉取会话消息失败（跳过）：" + (e && e.message ? String(e.message).slice(0, 150) : ""))
    return ""
  }
  return text
}

async function runGate5step(client, sid) {
  // 五步检查点程序化强制：拉取会话消息 → gate --check-5step 检测五步标记 → 返回缺步警告文本
  const text = await fetchAssistantText(client, sid)
  if (!text) return ""
  try {
    execSync(`python "${GATE}" --check-5step`, {
      timeout: 60000, encoding: "utf8", windowsHide: true, input: text,
    })
    return "" // rc=0：五步齐全或不适用，无需附加警告
  } catch (e) {
    // rc=1（缺步）时 execSync 抛异常但 stdout 含缺步清单，取出用于附加警告
    const out = e && e.stdout ? String(e.stdout).trim() : ""
    if (out && out.includes("五步检查点")) return out
    log("gate --check-5step 执行失败：" + (e && e.message ? String(e.message).slice(0, 150) : ""))
    return ""
  }
}

function collectExperienceKeywords() {
  // 使用率追踪（V5 方案甲' 2026-08-28）：从 evolution_log 结构化条目解析活跃经验的"核心关键词"表
  // 泛词过滤防误报（>=4 字符且排除常见通用词）；V6 剩余问题采纳：按标题分组为 {t, ks}
  try {
    const txt = readFileSync(ELOG, "utf8")
    const lines = txt.split(/\r?\n/)
    const byTitle = new Map()
    const generic = new Set(["信号", "文件", "规则", "脚本", "测试", "工具", "流程", "机制", "路径"])
    let lastTitle = ""
    let lastStatus = "active"
    for (const ln of lines) {
      const t = ln.match(/^\[(\d{4}-\d{2}-\d{2})\]\s*(.*)/)
      if (t) { lastTitle = t[2].trim().slice(0, 80); lastStatus = "active" }
      if (ln.startsWith("- 状态：")) lastStatus = ln.slice(5).trim()
      const kw = ln.match(/^- 核心关键词：(.+)/)
      if (kw && lastStatus === "active") {
        const ks = kw[1].split(/[、,，;；]/).map(s => s.trim()).filter(s => s.length >= 4 && !generic.has(s))
        if (ks.length && !byTitle.has(lastTitle)) byTitle.set(lastTitle, [])
        ks.forEach(k => byTitle.get(lastTitle).push(k))
      }
    }
    return Array.from(byTitle.entries()).map(([t, ks]) => ({ t, ks }))
  } catch (e) {
    return []
  }
}

function trackExperienceUsage(client, sid) {
  // 会话级关键词匹配（弱信号但可靠：整会话 assistant 文本一次匹配，命中写 evolution_trace.jsonl；
  // V6 剩余问题采纳：经验有 >=2 个关键词时需 >=2 个同时命中才记引用，防短词误报）
  const groups = collectExperienceKeywords()
  if (!groups.length) return
  fetchAssistantText(client, sid).then(text => {
    if (!text) return
    const hits = []
    for (const g of groups) {
      const n = g.ks.filter(k => text.includes(k)).length
      if (n >= Math.min(2, g.ks.length)) hits.push(g)
    }
    if (!hits.length) return
    try {
      appendFileSync(TRACE_FILE, hits.map(x => JSON.stringify({ t: new Date().toISOString(), sid: String(sid).slice(0, 40), entry: x.t, kw: x.ks.join("|") })).join("\n") + "\n")
      log("使用率追踪：会话命中 " + hits.length + " 条经验关键词（" + hits.map(x => x.t.slice(0, 30)).join("、") + "）")
    } catch (e) {
      log("使用率追踪写 trace 失败：" + (e && e.message ? String(e.message).slice(0, 120) : ""))
    }
  })
}

function log(msg) {
  try { appendFileSync(LOG_FILE, new Date().toISOString() + " " + msg + "\n") } catch {}
}

// 进化待办（方案A 2026-08-27）：session.idle 时机器步骤结果存入本模块级变量，
// 下一会话 session.created 时读入并静默注入——旧会话不再被 prompt 唤醒。
// 2026-08-27 由文件改为内存传递：文件读写存在间歇性竞态（test_plugin 实测偶发读不到刚写入的
// pending 致注入失败），且 idle→created 传递发生在同一 opencode 进程内，内存变量 100% 可靠；
// opencode 重启丢失一次进化检查可接受（机器步骤已由 gate 在 idle 时确定性执行）。
let pendingTask = null

function writePending(data) {
  pendingTask = data
}

function readPending() {
  return pendingTask
}

function clearPending() {
  pendingTask = null
}

function buildTaskText(gateOut, fiveOut) {
  // 进化检查任务文本（6 项强制清单 + 门禁结果 + 五步补做 + 执行时机）
  return (
    "【进化检查·程序化强制·不可跳过】本任务由插件在上一会话结束时生成、本会话创建时注入，必须完整执行，不得以任何理由跳过或精简。**执行时机：本会话你第一次回复时，先输出进化检查结论一行（「进化检查完成：本次无固化项」或固化项清单），再回答用户问题。**逐项执行：\n" +
    (gateOut ? "【进化门禁·机器已完成】机制步骤已由 evolution_gate 脚本确定性执行，结果：\n" + gateOut.slice(0, 2000) + "\n你只需补充智能部分（经验归纳/归属/edit 固化）：\n" : "") +
    (fiveOut ? "【五步检查点·程序化强制】" + fiveOut.slice(0, 600) + "\n补做任务：按五步流程逐步输出【第一步·归纳】【第二步·归属】【第三步·edit】【第四步·流水】【第五步·校验】结构化中间结果（格式见 evolution_skill SKILL.md）后再执行固化。\n" : "") +
    "1. 经验固化：回顾上一会话，按 instructions.md 智能进化协议五步流程，把可复用经验（新方法/工具/踩坑/风险规避）固化到对应 skill（自动执行）\n" +
    "2. 工具登记：上一会话中用到/发现/提及的任何新工具、脚本、库——无论是否已写进具体 skill——必须登记到 tools-manifest.md（已在分类中的更新条目；新的先入「待补充」清单）\n" +
    "3. 总表同步：若上一会话新增了 skill 依赖工具或本机配置变更，同步更新 tools-manifest.md\n" +
    "4. 校验自测：对本次所有 skill 文件改动，跑 python <项目目录>\\temp\\skill_validate.py <opencode配置目录>\\skills；涉及可执行内容的行为自测\n" +
    "5. 合并/拆分/迁移类发现：只输出「进化建议」清单供用户确认，不自动执行\n" +
    "6. 全部完成且无新经验时，回复一行：「进化检查完成：本次无固化项」；否则回复固化项清单\n" +
    "7. 新增文件适配（A+C 方案 2026-08-28）：若门禁结果含【新增文件】清单，按 evolution_skill「新增文件适配决策」流程执行——四问分析 → question 弹窗让用户逐项决定 适配/忽略/存档 → 适配的走纳入动作（regedit/tools-manifest/instructions 登记）→ 验收测试全绿（test_regedit+skill_validate+test_instructions+health_check）\n" +
    "铁律：不得执行任何 git 同步（同步边界铁律，同步只能由用户显式 update_skill 触发）。"
  )
}

function loadSkills() {
  if (!existsSync(SKILLS_DIR)) return []
  const out = []
  for (const name of readdirSync(SKILLS_DIR)) {
    const f = join(SKILLS_DIR, name, "SKILL.md")
    if (!existsSync(f)) continue
    let text
    try { text = readFileSync(f, "utf8") } catch { continue }
    const m = text.match(/^\ufeff?---\r?\n([\s\S]*?)\r?\n---/)
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
  const injectedSessions = new Set()
  return {
    "experimental.chat.system.transform": async (input, output) => {
      if (process.env.OPENCODE_DISABLE_MD_INJECT === "1") return
      if (!output || !Array.isArray(output.system)) return
      const text = loadInjectContent()
      if (text) output.system.push(text)
      output.system.push(langLine())
    },
    event: async ({ event }) => {
      try {
        const props = event.properties || {}
        // 语言检测：用户消息文本部分更新时识别语言（平台确定性检测，模型无需自行判断）
        if (event.type === "message.part.updated") {
          try {
            const part = props.part || {}
            const text = part.text || (part.state && part.state.text) || ""
            const role = part.role || (part.info && part.info.role) || ""
            if (text && role === "user") {
              const lang = detectLang(text)
              if (lang && lang !== currentLang) {
                currentLang = lang
                log("语言检测：用户消息 → " + lang)
              }
            }
          } catch (e) {
            log("语言检测异常：" + (e && e.message ? String(e.message).slice(0, 120) : ""))
          }
          return
        }
        if (event.type === "session.created") {
          if (props.parentID) return
          const skills = loadSkills()
          if (skills.length === 0) return
          const lines = skills.map(([n, d]) => `${n} — ${d}`).join("\n")
          await client.tui.showToast({
            body: { message: `本机全局技能（${skills.length} 个）\n` + lines, variant: "info" },
          })
          recordTrace(props.sessionID || "unknown", {})
          // 平台 API 保障闭环：异步检测实验性 hook 可用性（升级移除 API 时首会话即告警）
          runApiCheckAsync(client)
          // 自愈：异步后台补跑上次会话残留快照的门禁（防 idle 未触发单点故障；不阻塞会话创建）
          runGateAsync("--drain")
          runGate("--snapshot", props.sessionID || "unknown")
          // 双通道：程序化注入「读注册表」提醒，保证模型会话开始必读 regedit.md
          const sid = props.sessionID
          if (sid) {
            try {
              await client.session.prompt({
                path: { id: sid },
                body: {
                  noReply: true,
                  parts: [{
                    type: "text",
                    text:
                      "【注册表必读·铁律第0条·程序化提醒】会话开始第一动作：读取 " + join(HOME, ".config", "opencode", "regedit.md") +
                      "（全体系注册表），按其中生效方式分类（A~H）确定各组件何时加载、何时执行。组件新增/变更必须同步更新注册表并跑 python " +
                      join(HOME, ".config", "opencode", "tests", "test_regedit.py") + "。",
                  }],
                },
              })
              log("session.created 注册表提醒注入成功，会话 " + sid)
            } catch (e) {
              log("session.created 注册表提醒注入失败：" + (e && e.message ? e.message : String(e)))
            }
            // 方案A（2026-08-27）：上一会话 idle 时写入的进化待办 → 静默注入本会话上下文
            // （noReply=true 不唤醒模型；模型在本会话首次回复时看到任务并执行）
            const pending = readPending()
            if (pending) {
              try {
                await client.session.prompt({
                  path: { id: sid },
                  body: {
                    noReply: true,
                    parts: [{ type: "text", text: buildTaskText(pending.gateOut || "", pending.fiveOut || "") }],
                  },
                })
                clearPending()
                log("进化待办已注入新会话 " + sid + "（上一会话 " + (pending.prevSid || "未知") + " 遗留）")
              } catch (e) {
                log("进化待办注入失败：" + (e && e.message ? String(e.message).slice(0, 150) : ""))
              }
            }
          }
          return
        }
        // 方案A（2026-08-27）：会话空闲时只跑机器步骤并写进化待办，不再向旧会话注入 prompt
        // （防"会话已结束、窗口又被任务唤醒生成新对话"的时序问题）
        if (event.type === "session.idle") {
          const sid = props.sessionID || event.properties?.info?.id
          if (!sid) { log("session.idle 未取得 sessionID，props=" + JSON.stringify(props)); return }
          if (injectedSessions.has(sid)) { log("session.idle 幂等跳过：会话 " + sid + " 已写过进化待办"); return }
          injectedSessions.add(sid)
          recordTrace(sid, { phase: "idle" })
          log("session.idle 触发，执行机器步骤并写进化待办（会话 " + sid + "）")
          // 进化门禁：机制步骤由脚本确定性执行（流水兜底+自动测试，纯文件操作无 UI 副作用）
          const gateOut = runGate("--check", sid)
          if (gateOut) {
            log("evolution_gate 门禁输出：\n" + gateOut.slice(0, 600))
          }
          // 五步检查点：检测本会话固化响应是否含五步标记
          const fiveOut = await runGate5step(client, sid)
          if (fiveOut) {
            log("五步检查点输出：\n" + fiveOut.slice(0, 500))
          }
          // 使用率追踪（V5 方案甲'）：会话级关键词匹配 → evolution_trace.jsonl
          trackExperienceUsage(client, sid)
          writePending({ prevSid: sid, gateOut: gateOut, fiveOut: fiveOut, time: new Date().toISOString() })
          log("进化待办已写入（等待下一会话创建时静默注入）")
        }
      } catch (e) {
        log("event 处理异常：" + (e && e.message ? e.message : String(e)))
      }
    },
  }
}
