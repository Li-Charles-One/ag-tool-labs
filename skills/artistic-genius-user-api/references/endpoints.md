# Artistic Genius 用户接口参考

基地址：`https://artistic-genius.vip`。以下示例为 bash（macOS / Linux）；Windows PowerShell 请用 `curl.exe`，并把 `$AG_API_KEY` 写成 `$env:AG_API_KEY`。

## 凭证

| 凭证 | 获取位置 | 环境变量 |
|---|---|---|
| `sk-` 令牌 | 控制台 →「API 密钥」→ 新建，选好分组后复制密钥 | `AG_API_KEY` |
| 访问令牌（`nap_` 开头） | 控制台 →「安全」→「访问令牌」→「创建访问令牌」 | `AG_ACCESS_TOKEN` |

- 创建对话框里「个人」下的 10 项权限**默认全部选中**（含「API 密钥 · 查看完整密钥」「钱包 · 编辑」「账户安全 · 编辑」）。先点「清空」，再只勾「个人资料 · 查看」（`profile:read`，查余额）和「用量 · 查看」（`usage:read`，查日志、统计、按天用量）。本 skill 只需要这两项。
- 建议设有效期。令牌只在创建时显示一次，丢了就新建一个再撤销旧的；新建不会让已有的令牌失效。
- 2026-11-07 之前生成的旧访问令牌不以 `nap_` 开头，只在过渡期内可用（约到 2026-12-06），请尽早换成新令牌。
- 缺作用域时报 `ACCESS_TOKEN_SCOPE_DENIED`；令牌过期报 `ACCESS_TOKEN_EXPIRED`；旧令牌过了过渡期报 `ACCESS_TOKEN_LEGACY_RETIRED`。

## 金额换算

所有 `quota` 字段都是内部额度单位：

```text
¥ = quota / 500000 × 7
```

给用户的结论一律用人民币。

## 一、调用模型（sk- 令牌）

OpenAI 兼容，`/v1` 前缀：

```bash
curl -s https://artistic-genius.vip/v1/chat/completions \
  -H "Authorization: Bearer $AG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"<模型名>","messages":[{"role":"user","content":"hi"}]}'
```

可用模型：`GET /v1/models`（同样带 sk- 令牌），返回的就是这把令牌所在分组能用的模型。令牌分组要和模型对应，否则报“分组 … 下模型 … 无可用渠道”。

Claude 模型（Claude 尝鲜分组）也可以用 Anthropic 原生格式，令牌放 `x-api-key`，`max_tokens` 必填：

```bash
curl -s https://artistic-genius.vip/v1/messages \
  -H "x-api-key: $AG_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-5-5","max_tokens":1024,"messages":[{"role":"user","content":"hi"}]}'
```

## 二、查单把 key（sk- 令牌）

### 余额与限制

```bash
curl -s https://artistic-genius.vip/api/usage/token/ -H "Authorization: Bearer $AG_API_KEY"
```

路径必须带末尾斜杠，不带会返回 301 和一段 HTML。成功时顶层是 `code: true`、`message: "ok"`（没有 `success` 字段）。

返回 `data` 字段：`name`、`total_granted`、`total_used`、`total_available`、`unlimited_quota`、`model_limits`、`model_limits_enabled`、`expires_at`（0 = 永不过期）。`unlimited_quota: true` 时 `total_granted` 为 0、`total_available` 为负数，只有 `total_used` 有意义。

### 最近调用明细

```bash
curl -s https://artistic-genius.vip/api/log/token -H "Authorization: Bearer $AG_API_KEY"
```

返回 `data` 为日志数组，字段同下文“日志字段”。只含最近有限条数。

### OpenAI 风格余额（给第三方客户端用）

```bash
curl -s https://artistic-genius.vip/v1/dashboard/billing/subscription -H "Authorization: Bearer $AG_API_KEY"
curl -s https://artistic-genius.vip/v1/dashboard/billing/usage -H "Authorization: Bearer $AG_API_KEY"
```

`usage` 返回 `total_usage`，单位是人民币分（`¥ = total_usage / 100`），不是美元；本站当前按单把 key 统计。`subscription` 的 `hard_limit_usd` 等字段同样不是美元，不限额的 key 返回 100000000。金额以 `/api/usage/token/` 为准。

## 三、查整个账号（访问令牌）

以下请求都带 `-H "Authorization: Bearer $AG_ACCESS_TOKEN"`。各接口需要的作用域写在小节里。

### 账号余额

```bash
curl -s https://artistic-genius.vip/api/user/self -H "Authorization: Bearer $AG_ACCESS_TOKEN"
```

需要 `profile:read`。看 `data.quota`（剩余）、`data.used_quota`（累计已用）、`data.request_count`、`data.group`。

### 时段花费汇总

```bash
START=$(date -d '2026-09-01' +%s 2>/dev/null || date -j -f '%Y-%m-%d' '2026-09-01' +%s)
END=$(date +%s)
curl -s "https://artistic-genius.vip/api/log/self/stat?type=2&start_timestamp=$START&end_timestamp=$END" \
  -H "Authorization: Bearer $AG_ACCESS_TOKEN"
```

需要 `usage:read`。返回 `data.quota`（该时段消费额度）、`data.rpm`、`data.tpm`。可加 `model_name`、`token_name`、`group` 过滤。

### 消费明细（分页）

```bash
curl -s "https://artistic-genius.vip/api/log/self?p=1&page_size=50&type=2&start_timestamp=$START&end_timestamp=$END" \
  -H "Authorization: Bearer $AG_ACCESS_TOKEN"
```

- 需要 `usage:read`。
- `type`：`0` 全部、`1` 充值、`2` 消费、`3` 管理、`4` 系统（如注册赠送）、`5` 错误、`6` 退款、`7` 登录。算账只看 `2`（减去 `6` 退款）。
- 可选过滤：`model_name`、`token_name`、`group`、`request_id`。
- 返回 `data.items` 与 `data.total`；按 `total` 翻页。

### 按天 / 按模型用量

```bash
curl -s "https://artistic-genius.vip/api/data/self?start_timestamp=$START&end_timestamp=$END" \
  -H "Authorization: Bearer $AG_ACCESS_TOKEN"
```

- 需要 `usage:read`。
- 跨度上限由站点设置决定（2026-11-07 为 365 天），超出返回 `The time range cannot exceed N days`，按 N 分段。`/api/log/self` 与 `/api/log/self/stat` 同样受这个上限约束。
- 每行字段：`model_name`、`created_at`（小时粒度时间戳）、`count`、`token_used`、`quota`，另有 `cache_read_tokens`、`cache_creation_tokens`、`use_group`、`token_id`。按 `model_name` 或日期汇总即可。

## 日志字段

`created_at`、`type`、`model_name`、`token_name`、`quota`、`prompt_tokens`、`completion_tokens`、`use_time`（秒）、`is_stream`、`group`、`request_id`、`content`。

## 已废弃

- `/api/log/self/search`：恒返回“该接口已废弃”（英文环境为 `This API is deprecated`）。
