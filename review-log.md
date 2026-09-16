# Review Log

This file records periodic reviews of new Claude Code capabilities, agent workflows, prompt patterns, and MetaBot-related ideas that may improve the system.

## Purpose

The goal is not to chase novelty.
The goal is to notice when a newer method is genuinely better than the current one.

## What a review should answer

- What changed in Claude Code or the broader agent ecosystem?
- Does it improve continuity, recovery, speed, or reliability?
- Does it reduce manual effort without increasing fragility?
- Does it make MetaBot more capable, easier to maintain, or easier to resume?
- Should the current system prompt, hooks, recovery strategy, or review process change?

## Review output format

Use one of these outcomes:
- `adopt` — the new idea should become part of the operating model
- `adapt` — the idea is useful but needs adjustment for this project
- `ignore` — the idea is interesting but not worth adding here

## Suggested review cadence

Run on a regular schedule, and also whenever one of these happens:
- Claude Code adds or changes compaction/session behavior
- a new hook or memory pattern looks promising
- a MetaBot workflow becomes brittle or repetitive
- a repeated frustration suggests the current prompt or recovery method is stale

## Review entry template

```md
## YYYY-MM-DD

### What was checked
- 

### What looked promising
- 

### What was not worth changing
- 

### Decision
- adopt / adapt / ignore

### Follow-up
- 
```

## 2026-07-18 — Phase 5 pulse check (3 days post-scan)

### What was checked
- Claude Code changelog 2.1.210-212 (July 14-17, 2026) — 3 releases since the Phase 5 scan

### What looked promising
- **Agent SDK hosting guide** (2.1.210): covers Docker, K8s, multi-tenant deployment, and observability for Agent SDK. Directly fills the "how to deploy Track B agents" gap.
- **Plugin system in SDK** (2.1.210): skills, agents, hooks, MCP servers loadable as plugins through the Agent SDK. Reduces Track B integration complexity.
- **Session persistence** (2.1.210): mirror session transcripts to S3, Redis, or custom backends for cross-host resume. Key for Track B agent state management.
- **Subagent spawn cap** (2.1.212): CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION (default 200) — safety measure for Track B.
- **MCP auto-background** (2.1.212): 2-min threshold, MCP calls move to background automatically.
- **File checkpoint pruning** (2.1.210): up to 79x smaller transcripts. Relevant to Track A continuity.
- **Agent Teams fixes** (2.1.212): duplicate notifications, session initialization stability.
- **Memory/CPU improvements** (2.1.210): up to 7x faster tool rounds, bounded edit cache, LRU doc cache. Reduces Track B deployment overhead.

### What was not worth changing
- Screen reader mode, `/fork` behavior changes, terminal layout fixes — not relevant to Track B/A.
- `/loop` fixes, `/resume` picker — nice-to-have but not architecture-relevant.

### Decision
- adapt — all findings reinforce the Phase 5 recommendation to use Agent SDK for Track B, and add concrete hosting/state-management guidance for the deployment plan.

### Follow-up
- Add Agent SDK hosting (Docker/K8s) and session persistence (S3/Redis) to Track B Phase 1 spike scope in plan.md.
- Next full Phase 5 scan: 1-2 months (2026-08/09).

## Rule

If a review suggests that an older decision is now wrong, update the project files instead of only leaving a note here.

## 2026-05-12 — bootstrap workflow

### What was checked
- project docs

### What looked promising
- utility entry point

### What was not worth changing
- None

### Decision
- adopt

### Follow-up
- add first real review later

## 2026-05-12 — status bootstrap check

### What was checked
- selfdev status output

### What looked promising
- bootstrap entry suggestions

### What was not worth changing
- None

### Decision
- adopt

### Follow-up
- record a real use-case review next

## 2026-06-08 — Portraiture replay pipeline review

### What was checked
- Segmentation tuning impact on replay quality, state-aware hint system effectiveness, refinement loop marginal gains, divergence taxonomy coverage

### What looked promising
- Episode merging via time gap + similarity threshold works predictably. State-aware hints (+1.7%) add measurable value. Refinement loop (+3.4% over baseline) provides genuine differentiation. 59 examples is viable for coarse-label evaluation.

### What was not worth changing
- Fine-grained label accuracy is near zero across all divergence subtypes — the label space may be too granular for rule-based inference. Topic_shift dominates confusions.

### Decision
- adapt

### Follow-up
- Gate refined hints by divergence subtype and episode context. Run per-subtype before/after accuracy analysis. Consider whether fine-grained labels (10 classes) are realistic or if coarse (6 classes) is the practical ceiling.

## 2026-06-09 — Multi-project advancement session (7 projects)

### What was checked
- a2a-hub: 164 tests pass, cleaned obsolete files, simplified config; portraiture: re-ran pipeline with 149 conversations (257 replay examples), refined model +10.5pp over baseline; viora: Phase 4 complete (174 tests); IHD: 88 tests pass; shadow-system: Phase 7 documented as already complete in plan.md

### What looked promising
- portraiture: explicit modeling gains scale with data volume (+10.5pp at 257 examples vs +3.4pp at 59 examples); selfdev.py capsule is a useful resume tool

### What was not worth changing
- None

### Decision
- adopt

### Follow-up
- None

## 2026-06-11 — Multi-project advancement: IHD Phase 5 RAT + portraiture labels

### What was checked
- IHD_Trajectory_System (Phase 5): 164 tests pass (127 existing + 37 new Phase 5 RAT tests)
- Portraiture: label taxonomy added with coarse/fine hierarchy (27 tests)
- Shadow-system: 403 tests pass (import path issue in root-level pytest resolved by running from shadow-cli/)
- Viora: 174 tests pass
- Personal_website: Next.js SSG build succeeds

### What looked promising
- **IHD Phase 5 RAT**: Retrieval-Augmented Transformer with two fusion modes (cross-attention and gate) is implemented and tested. Pre-computes retrieval indices per fold to prevent leakage. Handles edge cases (empty retrieval, partial masking) correctly. Ready for full 5-fold CV experiment.
- **IHD `_init_weights` fix**: Changing `xavier_uniform_(weight, gain=0.02)` → default gain=1.0 fixes vanishing gradients that prevented single-epoch learning.
- **Portraiture label taxonomy**: Annotation dataclass with validation (coarse/fine consistency, JSON roundtrip) provides a solid foundation for the planned 40-sample relabel campaign.

### What was not worth changing
- IHD Phase 4 risk baselines (LR/XGB at ~0.50 AUC) confirm the core finding: flat feature representations cannot generalize across time in time-aware CV — this is a data noise ceiling, not a modelling issue.
- Shadow-system pre-existing import path issues are a project convention (tests run from `shadow-cli/`), not a defect.

### Decision
- adopt

### Follow-up
- IHD: Run full 5-fold CV for RAT (small/medium/large × cross_attention/gate) and compare against Phase 2 transformer baselines.
- Portraiture: Extract 40-sample relabel set from replay pool and run label ablation.
- Monitor Claude Code compaction — the loss of mid-session context mid-workflow remains the primary productivity bottleneck.

## 2026-06-25 — Meta: decision-before-verification trap

### What was checked
- The `.daily-advance-skip` incident (June 17-20): viora was classified as "qualitative-only" based on its plan.md content, then corrected 3 days later when the user pointed out it has 21K lines of code and 174 tests.

### What looked promising
- The `.daily-advance-skip` marker convention itself is still valid for genuinely non-code projects.
- The correction workflow was clean: user pointed out the error → the decision was updated in decisions.md → the marker was removed → viora re-entered daily rotation.

### What was not worth changing
- The existing decision.md and review-log structure handles corrections well. No process change needed.

### Decision
- adapt — the lesson is a meta-cognitive one: **don't infer project nature from plan.md alone when actual code exists**. When in doubt, check file count + test count before applying project-wide filters.

### Follow-up
- This is now a standing note: assertion about project classification should be verified against code reality, not just documents.
- The `.daily-advance-skip` marker stays as a convention for genuinely non-code projects.

## 2026-06-17 — Multi-day advancement workflow (5 sessions across 5 days)

### What was checked
- June 13–17: 5 consecutive daily project advancement sessions covering 7 projects
- Pattern: status snapshot → pick 2-3 → advance code → write reports
- NOW.md workflow (from project CLAUDE.md) used as primary orientation mechanism

### What looked promising
- **Multi-session incremental progress works**: a2a-hub Phase 6.2 identity system was built incrementally over 4 sessions (data model → MCP injection → reactions storage → blog author format), each session picking up where the last left off without conflict.
- **NOW.md + plan.md split works**: plan.md for long-term direction, NOW.md for current-next-blockers. The split prevents plan.md from becoming a stale progress board while keeping the next action unambiguous.
- **Consistent test pass counts are a strong stability signal**: a2a-hub 164 tests, IHD 168 tests, both unchanged across sessions — means identity and fusion changes are truly backward-compatible.
- **IHD Phase 4 → 5 progression**: Multi-task Transformer (Phase 4) → Retrieval Fusion Transformer (Phase 4→5) → Retrieval comparison analysis (Phase 5) → Gate vs Cross-attention analysis (Phase 5) shows a clean research pipeline where each session builds on the last.

### What was not worth changing
- Projects with no plan.md (personal_website) or only qualitative tasks (viora) get skipped every day. The daily workflow correctly filters them out, but they accumulate as "pending" noise in the project list. Consider whether they should remain in the daily rotation.

### Decision
- adopt — the NOW.md-based daily advancement pattern is effective and should stay as default workflow

### Follow-up
- If compact happens mid-workflow, the NOW.md of the current project should be the first thing the next session reads.
- Daily advancement works best when projects have concrete, code-level plan.md items. Qualitative-phase projects may need a different rotation mechanism.

## 2026-06-27 — Multi-project advancement: viora trajectory + a2a-hub reputation

### What was checked
- viora: 松散多气泡交互 — 移除 isSending 锁，用户可连发消息，2s 停手去抖后批量合并处理；230 测试全过
- viora: 用户轨迹建模 Phase A — EventNode/TrajectoryNode 两层数据模型 + 日/周/条件周期检测 + 3天状态窗内部聚合；25 项新测试
- viora: 轨迹架构设计确认 — 用户纠正轨迹不是简单重复而是周期性信号，改为两层架构（原始事件时间线 + 周期性轨迹）
- a2a-hub: 技能详情页 HTML 渲染 — SKILL_DETAIL_TEMPLATE 嵌入声誉评分/推荐度进度条/标签云；卡片链接从原始 SKILL.md 改为详情页

### What looked promising
- viora trajectory_graph.py 的两层架构（原始事件时间线 + 周期性轨迹）是干净的抽象，state 作为内部聚合不暴露降低了认知负担
- a2a-hub 技能详情页采用 HTML 渲染而非直接引用 SKILL.md，为后续前端增强（排序筛选、交互式标签云）留了空间

### What was not worth changing
- a2a-hub 的 JS 端技能排序功能虽未实现交互式，但 data JS 文件已生成，前端排序扩展随时可做

### Decision
- adapt

### Follow-up
- viora: Phase B — 聚合 Pipeline 集成到 app.py 聊天流程，EventNode 持久化
- a2a-hub: 前端排序控件可补充（skill-reputation-data.js 已就绪）

## 2026-06-27 — Multi-project advancement: trajectory modeling Phase A + skill detail pages

### What was checked
- viora: trajectory_graph.py — two-layer data model (EventNode + TrajectoryNode) with daily/weekly/conditional periodicity detection, 25 tests
- a2a-hub: skill detail pages — per-skill HTML pages with reputation data, links migrated from raw SKILL.md
- viora: loose multi-bubble interaction — user can send messages without waiting, AI batches via 2s debounce

### What looked promising
- trajectory_graph.py two-layer architecture (raw events → periodic patterns) is cleanly separable and testable
- skill detail page pattern (MD content → HTML detail with structured metadata overlay) is reusable for agent detail pages
- daily advancement consistently produces 2-3 concrete code changes per session

### What was not worth changing
- No observed regressions or workflow friction — test counts are stable across all projects

### Decision
- adopt

### Follow-up
- viora: Phase B — integrate trajectory_graph into app.py ingestion pipeline
- Project is in healthy maintenance mode; no systemic changes needed

## 2026-07-06 — Multi-project advancement: IHD Phase C + viora Phase A tests

### What was checked
- IHD_Trajectory_System: Phase C NetworkX graph built (20 states, 400 edges) — stable proportion vs mortality shows clear dose-response (Q1 8% → 21.1%, Q4 92% → 3.7%)
- viora: Phase A unit tests completed (39 tests, 12 psychological expression patterns)
- shadow-system: still Docker-blocked, no change
- personal_website: Nav mobile enhancements from previous session stable

### What looked promising
- IHD Phase C results show the graph-based approach is separating mortality trajectories effectively — Phase D comparison against patient-level kNN will be the real test
- daily advancement pattern is stable: each session produces 2-4 concrete changes with consistent test pass rates

### What was not worth changing
- self-development itself has no clear actionable next step
- shadow-system needs Docker permissions, not code changes

### Decision
- continue passive observation; revisit when a concrete pain point or improvement opportunity arises

### Follow-up
- none currently — waiting for Track B architecture decision or a real workflow friction

## 2026-07-14 — Multi-project advancement: IHD references.bib + daily pass

### What was checked
- selfdev.py syntax check: OK
- All log files: review(10), experiment(3), decision(5), maintenance(2) entries — stable, no gaps
- plan.md Phase 5 (external review) not yet executed

### What looked promising
- Project structure is stable. No active pain points in Claude Code or MetaBot workflow.
- selfdev.py continues to function correctly as status/entry tool.

### What was not worth changing
- No infrastructure, code, or workflow changes needed at this time

### Decision
- adopt

### Follow-up
- Continue passive observation. Next check: when a concrete pain point or Phase 5 external review opportunity arises.
- Phase 5 external ecosystem review remains available as next meaningful action — requires web research scope

## 2026-07-15 — Phase 5 — Claude Code ecosystem scan (Agent SDK, Teams, Channels)

### What was checked
- Claude Code Agent SDK (Python/TypeScript) - new library exposing same agent loop, tools, and context management as Claude Code. Includes subagents, hooks, MCP integration, checkpointing, structured outputs.\nAgent Teams (experimental) - multiple Claude Code sessions orchestrating together, lead coordinator model, split-pane mode.\nChannels - push external events (CI, webhooks, alerts) into running sessions via MCP.\nAgent View - multi-agent dashboard with background sessions.\nDesktop scheduled tasks.\nCheckpointing - track, rewind, summarize edits.

### What looked promising
- Agent SDK is directly relevant to Track B (Local Agent Platform). Instead of evaluating Dify/LangFlow from scratch, the SDK provides a ready-made harness with subagent isolation, tool execution, session persistence, and permission control - all capabilities Track B would need to build.\nChannels cover the proactive push pattern that Track B's A2A framework requires - external events routed into sessions.\nCheckpointing directly addresses Track A's session continuity goal - rewinding/restoring file state.

### What was not worth changing
- Agent Teams is experimental and disabled by default. Not production-ready for Track B deployment.\nDesktop-specific features (scheduled tasks, multi-pane) don't apply to CLI/server-side MetaBot deployment.

### Decision
- adapt

### Follow-up
- Evaluate Agent SDK as the primary framework for Track B's first agent (RA), replacing the Dify/LangFlow spike.\nTest Channels for proactive push in MetaBot workflow.\nFile checkpointing is worth adding to MetaBot's compact/resume strategy - rewrite session state rather than text summaries.\nRevisit Track B design in plan.md to incorporate Agent SDK findings.

## 2026-08-15 — Phase 5 pulse check (16 days post last pulse)

### What was checked
- Latest `@anthropic-ai/claude-code` npm version: **2.1.233** (was 2.1.220 at last pulse on 07-30)
- ~13 new versions since (2.1.221 → 2.1.233, Jul 24 – Aug 14)
- Read full changelog (2.1.224 → 2.1.233) via agent-browser; npm registry / docs.anthropic.com directly blocked, browser path works
- Local installed version still 2.1.139 (stable-track, unchanged)

### What looked promising
- **Cross-session `SendMessage` + `ListAgents` (2.1.224, refined 2.1.228/2.1.232):** Claude Code sessions can now message each other on any machine, discover peers by name, deliver to a bare name (`@` mention), and configure inbound routing (`crossSessionInbound` / `dialogExpiry`). This is a **native A2A primitive** — directly relevant to Track B's "agents talk to each other proactively" requirement.
- **`claude self-hosted-runner` (2.1.224):** turns your own machines/containers into session hosts (Team/Enterprise). Adds a Track B deployment option beyond plain FastAPI services.
- **Subagent forking on by default (2.1.232):** `subagent_type: "fork"` inherits full conversation + prompt cache; non-teammate spawns run in background. Relevant to Track B agent loop composition.
- **Subagent spawn cap removed (2.1.224):** the 200-cap added in 2.1.212 is gone; concurrency/depth limits remain. Long-running sessions no longer refuse new agents — good for Track B persistence.
- **Compaction continuity (2.1.224/2.1.228/2.1.229):** fullscreen keeps full pre-compaction history in scrollback across repeated compactions; compaction progress shows retry countdown + stall hint; "prompt is too long" errors now explain why auto-compaction couldn't recover. Directly serves Track A continuity goal.
- **Self-hosted runner + remote-control hardening:** session resume across machines is more robust (reconnect ~30 min after blips, replacement session on deleted resume).

### What was not worth changing
- GitLab MR/token/marketplace features, Voice mode fixes, VSCode session groups, screen-reader changes — not relevant to Track A/B.
- Plugin `command` sources, `archive` plugin source, WebFetch cache TTL — nice-to-haves, not architecture-relevant.
- **⚠️ Operational flag (not a change yet):** Todo/task-tracking tools (`TaskCreate/Get/Update/List`, `TodoWrite`) are **no longer available on Opus 4.8, Sonnet 5, Fable 5, Mythos 5, and newer models**; opt back in with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. This project and MetaBot rely on TodoWrite — worth tracking before migrating to those models.

### Decision
- adapt — cross-session SendMessage/ListAgents is a meaningful new native A2A option for Track B; compaction-continuity improvements reinforce Track A's direction. Both stay as inputs pending the Track B user decision.

### Follow-up
- Add cross-session SendMessage/ListAgents + self-hosted-runner to Track B Phase 1 spike evaluation scope in plan.md (native A2A vs custom-wired message bus).
- Re-verify `CLAUDE_CODE_ENABLE_TODO_TOOLS` when/if the active model moves to Opus 4.8/Sonnet 5 class.
- Next full Phase 5 scan: ~2026-09/01, or on a model migration / Track B confirmation.

## 2026-07-30 — Phase 5 mini pulse check (12 days post last pulse)

### What was checked
- Latest `@anthropic-ai/claude-code` npm version: **2.1.220** (was 2.1.212 at last check on July 18)
- 8 new versions since: 2.1.213 → 2.1.220 (Jul 17-24)
- Release cadence: ~1 version/day (consistent with prior rate)
- Installed local version: 2.1.139 (significantly behind — stable-track release)

### What looked promising
- 8 versions in 12 days suggests active development continues
- Could not access changelog content due to network restrictions on docs.anthropic.com
- Need to check whether Agent SDK, hosting, plugin system, or session persistence received updates

### What was not worth changing
- Without changelog content, no specific findings to act on
- The installed 2.1.139 is a stable-track release and not directly comparable to the npm latest (2.1.220)

### Decision
- ignore — insufficient data for a meaningful review. Schedule full scan when network access is available.

### Follow-up
- Re-attempt pulse check with network access in ~2 weeks (mid-August) or when a specific feature/issue motivates a changelog lookup
- Next full Phase 5 scan: 2026-08/09 as planned

## 2026-08-24 — Phase 5 pulse check (Claude Code ecosystem)

### What was checked
- npm latest @anthropic-ai/claude-code = 2.1.241 (2026-08-23); 上次 pulse (08-15) 为 2.1.233 → 8 个新版本 (2.1.234→2.1.241)
- installed local: 2.1.139 (stable-track, 与 08-15 相同, 未漂移)
- npm dist-tags: stable=2.1.231 / latest=2.1.241 / next=2.1.241; 逐版本读了 2.1.237/238/239 release notes

### What looked promising
- 原生 A2A 显著成熟: 2.1.239 起 Windows 也支持跨会话 SendMessage/ListAgents; ListAgents 现在会列出 live teammates (之前只列 subagent/其它 session); 跨会话 refuse/rate-limit 现在显式告知发送方 → Track B spike 应优先评估原生 A2A 方案
- 2.1.239 新增 /claude-api upgrade 把 anthropic 0.x 项目迁移到 1.x (timeouts 用 anthropic.Timeout) → Track B 若用 Agent SDK 1.x 需注意迁移
- 2.1.238 self-hosted-runner 增强: --defer-shutdown-max-min / --proxy-authorization-command; Managed Agents (Aug 19) 引入 web search/fetch 域设置与 memory stores → 自托管 Agent 能力在扩展

### What was not worth changing
- 本地 2.1.139 仍为 stable-track 稳定版, 无紧急升级需要; Todo 工具移除 (CLAUDE_CODE_ENABLE_TODO_TOOLS=1) 在 2.1.237-241 无新变化

### Decision
- adapt

### Follow-up
- Track B spike (待用户确认) 需评估原生 A2A SendMessage/ListAgents vs 自建消息总线 — 2.1.239 起已含 live teammates 列表与跨平台消息
- 下次 Phase 5 扫描 ~2026-09/01 或用户确认 Track B 时提前

## 2026-08-26 — Phase 5 pulse 08-26: npm 2.1.241→2.1.246 (bug-fix 批次, A2A 修复)

### What was checked
- npm latest 2.1.246 (08-24 记录 2.1.241, 5 个新版本; 2.1.242/2.1.244 无 changelog 条目)
- 2.1.246 大版本 bug-fix 批次: subagent 达 maxTurns 截断时返回 partial 输出并提示 SendMessage 续跑; 非交互会话 (-p/SDK) 断流自动续跑; self-hosted runner 轮询容错; Bash wildcard 规则启动告警; /permissions 新增 Auto mode tab
- 2.1.243: 修复 2.1.232 socket 目录硬化后跨会话消息在 user namespaces/rootless 容器静默关闭 (A2A 关键修复); /usage 新增 Loops 分解; modelPicker/promptCacheTtl/modelPricing 设置; 原生安装 zstd 压缩 340MB→75MB
- 2.1.245: 修复 glibc 2.44 Linux 启动崩溃 (Arch/CachyOS/Fedora Rawhide)

### What looked promising
- 原生 A2A SendMessage 链路修复 + maxTurns partial+SendMessage 续跑提示 → 再次印证 Track B 应优先评估原生 A2A
- 非交互会话断流自动续跑 → 对长跑 agent/RA 服务稳定性有益

### What was not worth changing
- 本次以 bug-fix 为主, 无新重大功能; 暂无需要立即采用的行为变化

### Decision
- adapt

### Follow-up
- 下次完整 Phase 5 扫描 ~2026-09-01
- Track B spike 确认后重点实测跨会话 SendMessage 在 rootless/容器环境的稳定性

## 2026-08-28 — Phase 5 pulse 2026-08-28: claude-code 2.1.246→2.1.250 (2 天 4 版, 2.1.248 重要)

### What was checked
- npm latest=2.1.250 (08-26 为 2.1.246); 2.1.248 发布说明 (08-27): 新增 --restricted/CLAUDE_CODE_RESTRICTED=1 受限模式 (移除命令/代码执行工具+WebFetch, 保留工作目录内文件工具, 拒绝 bypassPermissions, 忽略用户/项目/本地 settings); agent frontmatter 新增 experimental.cacheTtl; self-hosted-runner --client-label; 跨会话 SendMessage/ListAgents 在 Bedrock/Vertex/Foundry 及 telemetry disabled 下可用; /usage-credits (AWS Marketplace Enterprise); 修复长会话约每小时一次 prompt-cache miss (OAuth token refresh 后 tool def 重渲染); 修复 30 天后 Claude Desktop/Cowork 会话消失; Windows claude agents 键盘修复等。2.1.247: 新增 SendFeedback 工具 + /claude-api cost-optimize (配置档位评估 API 花费) + /claude-api Admin API 覆盖。

### What looked promising
- 原生 A2A 跨会话消息扩展到 Bedrock/Vertex/Foundry + telemetry disabled → Track B 应继续优先评估原生 A2A; --restricted 是 Track A 沙箱加固的现成参考; /claude-api cost-optimize 可用于 Agent 成本基线分析

### What was not worth changing
- 无

### Decision
- adapt

### Follow-up
- 下次完整扫描提前至 ~2026-09-01 (原定 09-01, 保持); Track B spike 可实测跨会话在 rootless 容器稳定性 (2.1.248 修复了 rootless 跨会话静默关闭)

## 2026-08-28 — Phase 5 pulse 2026-08-28: npm 2.1.246→2.1.250 (3 releases)

### What was checked
- 2.1.247 (08-26): SendFeedback tool 草稿反馈; /claude-api cost-optimize 成本分析; Admin API 覆盖; Sonnet5 默认 auto-compact 扩到全 1M; 跨会话 peer 消息默认折叠为一行预览 (Ctrl+O 展开)。2.1.248 (08-27): 新增 --restricted/CLAUDE_CODE_RESTRICTED=1 (移除代码执行工具, 文件仅限 cwd); agent frontmatter experimental.cacheTtl; self-hosted-runner --client-label; 跨会话 SendMessage/ListAgents 现支持 Bedrock/Vertex/Foundry + telemetry 关闭时; 修复长会话约每小时一次的 prompt-cache miss (OAuth token 刷新导致)。2.1.250 (08-28): bug-fix 批次

### What looked promising
- 跨会话消息覆盖面显著扩大 (Bedrock/Vertex/Foundry/telemetry-off), Track B 原生 A2A 方案更稳; --restricted 是新的受限沙箱工具面, 值得留意

### What was not worth changing
- 其余多为 bug-fix / 企业计费 / 远程控制细节, 对本项目无直接动作

### Decision
- adapt

### Follow-up
- Track B spike 评估原生 A2A 时覆盖 telemetry-disabled 与自托管 runner 场景

## 2026-08-30 — Phase 5 pulse 2026-08-30: npm 2.1.250→2.1.251 (security batch + hooks)

### What was checked
- npm latest=2.1.251 (08-28 发布, 08-30 轻量 pulse; 上次记录 2.1.250). 2.1.251 重点: ① 安全修复批次 — Read/Write/Edit 跟随工作目录内被替换的 symlink 可能越界读写 (已修复); plugin 命令 path traversal 越界拒绝; 项目 settings 不再能启用详细 beta tracing/raw API body 日志 (OTLP 绕过修复); Workflow scriptPath 越界读取修复; Grep/Glob 经 symlink 搜索路径绕过 Read(...) deny 规则修复 → Track A 沙箱加固直接参考 (与 2.1.248 --restricted 互补) ② 新增 PreModelSwitch/PostModelSwitch hook 事件 (block/confirm/annotate 模型切换) + SessionStart resume hooks 现收到 session staleness 与预估 re-cache 成本 → Track A hooks/自我改进循环可用 ③ /cost 新增 per-session prompt-cache 行 (hit ratio/misses/re-cached/warm-cold) + /usage Spend limit bar → Track B 成本基线 ④ 跨会话修复: SendMessage 到 Claude Desktop 转来的会话现可送达 (不再 not reachable); agent teams 队友最终回复到达 idle 通知; 无名 sibling/parent 消息可回复 ⑤ SDK/云会话在 SDK MCP server 握手 ack 丢失时无限挂起 → 现 70s 超时标记失败 ⑥ Bash 权限检查对整数 shell 变量赋算术表达式 (OPTIND=1/0) 自动放行 → 现需确认

### What looked promising
- symlink-swap 越界读写 + Grep/Glob 绕过 Read deny 修复 → Track A 沙箱加固参考; PreModelSwitch/PostModelSwitch hooks + SessionStart staleness/re-cache 成本 → selfdev 钩子/成本可视化可用; /cost prompt-cache 行 → 长会话 prompt-cache 成本可视化

### What was not worth changing
- 其余多为 Remote Control/企业计费/Bedrock/Vertex/Foundry/云会话细节 bug-fix, 对本项目无直接动作

### Decision
- adapt

### Follow-up
- 下次完整扫描 ~2026-09-01 (保持); Track A 沙箱加固可参考 symlink-swap 与 path-traversal 修复模式; Track B spike 评估原生 A2A 时覆盖 telemetry-disabled + 跨会话送达修复场景

## 2026-09-01 — Phase 5 pulse 2026-09-01: npm 2.1.251→2.1.252 (bug-fix batch)

### What was checked
- npm latest=2.1.252 (08-31 发布, 09-01 完整扫描; 上次记录 2.1.251 08-30). 2.1.252 为 bug-fix 批次: ① 修复 Mac 上 Bash 命令 'task output swap refused (tasks dir moved or linked)' 失败 ② 修复项目无 .claude/settings.local.json 时 'always allow' 不保存 ③ 修复 Claude Desktop/VS Code 托管的 Remote Control 会话在连接 claude.ai 降级时, 工具完成后停顿数分钟 ④ 修复后台任务通知输出过大 (如磁盘满时 git 错误) 导致对话超 API 请求大小上限。间隔: 08-28→08-31 3 天 1 版。

### What looked promising
- ④ 后台任务大失败输出导致对话超 API 请求大小上限 — 长会话/后台任务健壮性修复, 对每日推进这类长会话 agent 运行有直接意义; ② always-allow 持久化修复影响权限配置体验

### What was not worth changing
- 其余为 Mac 特定 Bash 修复与 Remote Control 连接降级细节, 对本项目无直接动作

### Decision
- adapt

### Follow-up
- 下次完整扫描视模型迁移/Track B 确认再提前; Track B spike 仍待用户确认

## 2026-09-04 — Phase 5 pulse 2026-09-04: npm 2.1.252→2.1.260 (8 releases / 3 days)

### What was checked
- npm latest=2.1.260 (09-03 发布; 上次记录 2.1.252 09-01, 3 天 8 版 = 明显版本活动). 重点 2.1.259/2.1.260: ① A2A 跨会话修复 — subagent 经 SendMessage 恢复的 agent 完成时从不唤醒该 subagent (通知误发主会话); 进程内 teammate 长 retry 等待期间 transcript 丢消息/变空白; 后台会话在 ListAgents 出现两次 (phantom interactive 孪生) 并在 viewer 收到 SendMessage 投递 → Track B 评估直接参考 ② 2.1.259 修复并发会话静默互相回退 ~/.claude.json (workspace trust 重置 / MCP 状态丢失) — 对每日多会话并行推进直接意义 ③ Track A 沙箱: 259 补 Bash Read() deny 规则对 option 值 (-f.env/@file)/git diff 操作数/cd&&cat 的覆盖; 260 修复 Edit/Write/Read 含括号路径权限规则被丢弃 (read-only 目录可写) + zsh REPORTTIME/REPORTMEMORY/DIRSTACKSIZE 命令替换自动放行→现需确认; 但 260 回滚 259 'Read() deny 应用到 Bash 参数' (过度拒绝 npm run build) ④ 成本/缓存: /cost 与 status 行 prompt_cache 给 miss 可能原因 (tool defs/system prompt 变/idle 超 TTL); telemetry-disabled 会话 OAuth refresh 不再失效 prompt cache; Opus/Fable 1M 上下文自动 compact ⑤ 新工具: /diff 全屏 diff 面板、headless /reload-plugins、文本 /advisor、--permission-prompts none (无人值守自动拒绝)

### What looked promising
- 并发 ~/.claude.json 冲突修复 + ListAgents 幻影孪生/跨会话唤醒修复 → Track B (原生 A2A) 与每日多会话工作流; /cost prompt_cache miss 原因 + 权限规则括号/option 值修复 → Track A

### What was not worth changing
- 大量企业/Desktop/Bedrock/Chrome/artifact/渲染/终端细节 bug-fix, 对本项目无直接动作

### Decision
- adapt

### Follow-up
- Track B spike 仍待用户确认 (A2A 修复清单已补充); 下次 pulse 视版本活动 (~2-3 天) 或 Track B 确认时提前; maintenance check ~2026-09-06
