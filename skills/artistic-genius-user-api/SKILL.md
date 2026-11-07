---
name: artistic-genius-user-api
description: "Artistic Genius（artistic-genius.vip）普通用户自助：用自己的 sk- 令牌调用模型，并用 curl 查询余额、已用额度、消费明细、按模型/按天的费用，以及统计某个任务或某次请求用了多少 token、花了多少人民币。用户说“查余额”“还剩多少钱”“这个 key 花了多少”“今天/本月用了多少”“这个任务花了多少”“这次调用多少 token”“看调用记录”“AG 的 key 怎么用”时使用。不要用于站点管理员操作（改倍率、渠道、其他用户的额度）或充值付款；也不要用于其他中转站。"
---

# Artistic Genius 用户 API 与费用查询

_Package 1.1.0 — 2026-11-07 适配新版访问令牌：按作用域授权、`nap_` 开头、旧访问令牌到期退役（1.0.1 为 2026-10-02，首版 1.0.0 为 2026-09-25）。新版访问令牌查询账号余额、日志、统计、按天用量已于 2026-11-07 在生产实测（ag-new-api 911dbf31b）；sk- 令牌查询接口沿用 2026-10-02 的实测（68f980bec），源码未变。_

## Overview

教 Agent 用用户**自己的**凭证调用 Artistic Genius，并查询余额与费用。只用 curl，不装任何工具。

## Start Here

先判断用户手里是哪种凭证，再选模式：

| 模式 | 凭证 | 典型问题 |
|---|---|---|
| 调用模型 | `sk-` 令牌 | “用 AG 的 key 调 gpt” |
| 查单把 key | `sk-` 令牌 | “这个 key 还剩多少 / 最近调了什么” |
| 查整个账号 | 访问令牌（`nap_` 开头） | “账号余额 / 本月花了多少 / 哪个模型最贵” |
| 统计任务成本 | 访问令牌（仅 sk- 时降级） | “这个任务用了多少 token、多少钱” |

没有凭证时，告诉用户去哪拿（见 `references/endpoints.md` 的“凭证”），不要猜。

## Non-Negotiables

- 凭证只从环境变量读：`AG_API_KEY`（sk- 令牌）、`AG_ACCESS_TOKEN`（访问令牌）。不要把凭证写进文件、命令历史示例或回复里。
- 只读查询。不要替用户创建、修改或撤销访问令牌，也不要增删 sk- 令牌，除非用户明确要求。访问令牌只能由用户在网页登录后创建。
- 结论一律用**人民币**：`¥ = quota / 500000 × 7`，保留 4 位小数。不要只给 quota 或美元。
- 接口返回 `success: false` 时，原样报告 `message`，不要编数字。`/api/usage/token/` 例外：它没有 `success` 字段，成功时是 `code: true`、`message: "ok"`，`code` 不为 `true` 才算失败。

## Workflow

1. 确认凭证类型与环境变量已设置（`echo ${AG_API_KEY:+set}`，只看是否存在）。
2. 按 `references/endpoints.md` 选接口并执行 curl。基地址 `https://artistic-genius.vip`。
3. 时间范围用 Unix 秒时间戳。`/api/log/self`、`/api/log/self/stat`、`/api/data/self` 的跨度有上限（站点设置，2026-11-07 为 365 天），超出时按报错里的天数分段查再相加；不传 `start_timestamp` 时从上限天数前算起。
4. 统计任务或单次请求成本时，按 `references/recipes.md` 的对应技巧做。
5. 汇总：余额、已用、所选时段花费（按模型或按天排序），金额全部用 ¥。

## Gotchas

- 用户说要去建访问令牌时，提醒：创建对话框默认全选 10 项个人权限，要先点「清空」，只勾「个人资料 · 查看」和「用量 · 查看」。
- 访问令牌按作用域授权：查账号余额要「个人资料 · 查看」（`profile:read`），查日志、统计、按天用量要「用量 · 查看」（`usage:read`）。缺作用域时报 `ACCESS_TOKEN_SCOPE_DENIED`，让用户新建一个带上该作用域的令牌，不是令牌坏了。
- 2026-11-07 之前生成的旧访问令牌（不以 `nap_` 开头）只在过渡期内可用，过渡期约到 2026-12-06；之后报 `ACCESS_TOKEN_LEGACY_RETIRED` 或未授权。遇到旧令牌，提醒用户按 `references/endpoints.md` 新建。
- `/api/log/self/search` 在本站已废弃，恒返回“该接口已废弃”（英文环境为 `This API is deprecated`）。查明细用 `/api/log/self` 加筛选参数。
- `/api/log/token` 只返回这把 key 最近的有限条数，不适合算月度总账；月度总账用访问令牌。
- `/v1/dashboard/billing/usage` 的 `total_usage` 单位是人民币分（`¥ = total_usage / 100`），不是美元；本站当前按单把 key 统计。字段名里的 `usd` 不可信，金额以 `/api/usage/token/` 为准。
- `/api/usage/token/` 必须带末尾斜杠，不带会返回 301 和一段 HTML。
- `/api/usage/token/` 的 `expires_at` 为 0 表示永不过期；`unlimited_quota: true` 时剩余额度无意义，应改查账号余额。
- `/api/data/self` 定时写入（默认每 5 分钟），刚发生的调用查不到；返回空数组不代表没花钱，改用 `/api/log/self` 或 `/api/log/self/stat`。
- macOS 自带 Python 3.9：`python3 -c` 里的 f-string 不能在花括号内再用同种引号（如 `f"{x["quota"]}"`），会报语法错误；先取到变量再格式化。

## Resource Map

- `references/endpoints.md`：凭证获取、每个接口的 curl、参数与返回字段。
- `references/recipes.md`：任务成本、单次请求成本、日志明细解读、今日/本月花费、模型排行、余额可用天数、回答模板。
- `evals/evals.json`：触发与行为测试提示。
- `agents/openai.yaml`：Codex/UI 元数据。

## Final Response

给出：凭证类型、查询的时间范围、余额 / 已用 / 时段花费（人民币 ¥），任务成本还要写请求次数、输入/输出 tokens；如有异常则原样附上接口 `message`。格式参考 `references/recipes.md` 第 7 节。
