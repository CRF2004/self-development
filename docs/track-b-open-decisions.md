# Track B — Open Decisions: 推荐默认值 (2026-08-07)

> 目的：把 `docs/track-b-spike-plan.md` 里 4 个待你拍板的开放问题压缩成"一键确认"。
> 如果你同意下面的推荐默认值，直接回复「**全用推荐默认值**」即可启动 spike。

## 决策 1：Agent SDK 版本

**推荐：latest stable（最新稳定版）**

- 理由：Phase 5 评测显示 SDK 迭代很快（2.1.210→2.1.212 在数天内带来 hosting / plugin / persistence 能力）。Spike 目的是验证架构，用最新稳定版能覆盖当前能力面；锁定版本会低估 SDK 上限。
- 风险兜底：spike 产物用 `requirements.txt` 固定实际安装的版本号，失败时可回滚复现。

## 决策 2：持久化后端

**推荐：SQLite first（先 SQLite，S3/Redis 留到生产）**

- 理由：SQLite 零额外依赖、天然支持跨进程，满足 spike 的"agent 重启后状态可恢复"验收标准；S3/Redis 是部署期优化，与 spike 无关。
- 落地：`persistence.py` 内做薄抽象（`get_state` / `save_state`），后续换后端只改一个模块。

## 决策 3：MCP 作用域

**推荐：A2A Hub + 本地文件系统 MCP，两者都接**

- 理由：A2A Hub 是 RA 的知识来源（已有 a2a-fetch/a2a-share skill 可复用）；本地文件系统 MCP 让 RA 能读 `cc_dump/` 下的项目文档——这正好是 Track B"RA 主动研究并推送"的核心场景，值得在 spike 里一并验证。
- 成本：两个都是现成 MCP server，配置成本低。

## 决策 4：主动轮询范围

**推荐：GitHub releases + `docs.anthropic.com` changelog 都轮询**

- 理由：GitHub releases 覆盖 Claude Code / SDK 版本更新；docs changelog 覆盖能力面变化（Phase 5 的教训：pulse check 抓到了初始扫描遗漏的能力）。两者互补，spike 阶段各 6h 轮询一次成本可忽略。
- 落地：proactive_loop 里做成可配置的 poller 列表，后续加源只加一个函数。

---

## 如果你确认

回复「**全用推荐默认值**」→ 我按此安装 `anthropic` SDK 并在 `track-b/` 目录启动 Phase 1 spike（port 8201），完成后按验收标准评估并写入 `experiments.md`。

如果某一条你不同意，只指出那一条即可，其余按默认走。
