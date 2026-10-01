# 常用技巧

所有金额最后都报**人民币**：`¥ = quota / 500000 × 7`（等价于 `quota / 71428.57`），保留 4 位小数；不足 ¥0.01 时照实写，如 `¥0.0032`。

示例沿用 `references/endpoints.md` 的 `B=https://artistic-genius.vip`、`$AG_API_KEY`、`$AG_ACCESS_TOKEN`。汇总用 `python3` 单行即可，不需要装别的。

## 1. 这个任务用了多少 token、花了多少钱

适合“帮我跑完这个任务，顺便告诉我花了多少”。

1. **任务开始前**记时间：`START=$(date +%s)`。
2. 执行任务（所有调用都用同一把 sk- 令牌）。
3. **任务结束后**记时间：`END=$(date +%s)`；刚结束查不到时稍等几秒再查。
4. 用访问令牌拉这段时间的消费日志，按令牌名过滤，翻页直到取完 `total`：

```bash
curl -s "$B/api/log/self?p=1&page_size=100&type=2&token_name=<令牌名>&start_timestamp=$START&end_timestamp=$END" \
  -H "Authorization: Bearer $AG_ACCESS_TOKEN" | python3 -c '
import json,sys
it=json.load(sys.stdin)["data"]["items"]
p=sum(i["prompt_tokens"] for i in it); c=sum(i["completion_tokens"] for i in it); q=sum(i["quota"] for i in it)
print(f"请求 {len(it)} 次｜输入 {p} tokens｜输出 {c} tokens｜合计 ¥{q/500000*7:.4f}")'
```

5. 需要细分时按 `model_name` 分组再汇总。

**技巧：** 给每个项目或 Agent 单独建一把 sk- 令牌，按 `token_name` 过滤，就不会把同时段的其他用量算进来。网页操练场（Playground）的调用在日志里的令牌名形如 `playground-<模型>`，不会出现在令牌列表里。

**不要用 `/api/data/self` 统计刚结束的任务**：它按小时汇总且定时写入（默认每 5 分钟），会漏掉最近的调用。任务成本一律用 `/api/log/self`。

**只有 sk- 令牌时：** 改用 `GET /api/log/token`，在本地按 `created_at` 落在 `[START, END]` 内过滤后汇总。它只返回最近有限条，长任务可能不全，要提示用户。

## 2. 某一次请求花了多少钱

每次调用的响应头都会带 `X-Oneapi-Request-Id`。调用时加 `-D -` 把响应头打出来，记下这个值，再查：

```bash
curl -s "$B/api/log/self?type=2&request_id=<X-Oneapi-Request-Id>" -H "Authorization: Bearer $AG_ACCESS_TOKEN"
```

返回的那一条里：`prompt_tokens`、`completion_tokens`、`quota`（换算成 ¥）、`use_time`（秒）。

## 3. 读懂一条日志的明细

`other` 是 JSON 字符串，可能为空或 `null`（如登录日志），解析时用 `json.loads(i.get("other") or "{}") or {}`。常用字段：

| 字段 | 含义 |
|---|---|
| `cache_tokens` | 命中缓存的输入 tokens（价格更低） |
| `cache_creation_tokens` | 写入缓存的 tokens |
| `model_ratio` / `completion_ratio` / `cache_ratio` | 模型输入、输出、缓存倍率 |
| `group_ratio` | 分组倍率（如 mimo 分组 0.5 = 半价） |
| `model_price` | 按次计费模型的单价；`-1` 表示按 token 计费 |
| `frt` | 首字耗时（毫秒） |
| `reasoning_effort` | 推理强度 |

按 token 计费时，单条金额可以这样核算（非阶梯模型）：

```text
quota ≈ (输入 − cache_tokens + cache_tokens × cache_ratio + 输出 × completion_ratio) × model_ratio × group_ratio
¥ = quota / 500000 × 7
```

实测样例：输入 285、输出 158、`completion_ratio` 4、`model_ratio` 0.142857、`group_ratio` 0.5 → quota 65.5 → 日志记 66 → ¥0.0009。
阶梯计价模型（如 gpt-6 系列）不适用这个公式，以日志里的 `quota` 为准。

回答“为什么这么贵”时，先看输出 tokens 是否很多（输出通常比输入贵好几倍），再看有没有命中缓存、分组倍率是多少。

## 4. 今天 / 本月花了多少

```bash
TODAY=$(python3 -c 'import time;t=time.localtime();print(int(time.mktime((t.tm_year,t.tm_mon,t.tm_mday,0,0,0,0,0,-1))))')
MONTH=$(python3 -c 'import time;t=time.localtime();print(int(time.mktime((t.tm_year,t.tm_mon,1,0,0,0,0,0,-1))))')
curl -s "$B/api/log/self/stat?type=2&start_timestamp=$MONTH&end_timestamp=$(date +%s)" -H "Authorization: Bearer $AG_ACCESS_TOKEN"
```

`data.quota` 换算成 ¥ 即本月花费；把 `$MONTH` 换成 `$TODAY` 即今日花费。

## 5. 本月哪个模型最花钱

`GET /api/data/self`（跨度 ≤ 30 天，超出就分段），按 `model_name` 汇总 `quota` 和 `token_used`，按金额从高到低列出，每行写：模型、请求次数、tokens、¥。

## 6. 余额还能用多久

1. `/api/user/self` 取 `quota`，得到余额 ¥。
2. `/api/log/self/stat` 取最近 7 天消费，除以 7 得到日均 ¥。
3. 余额 ÷ 日均 = 大约还能用几天。日均为 0 时写“近 7 天无消费”。

## 7. 回答模板

```text
本次任务：请求 12 次｜输入 48,210 tokens｜输出 6,905 tokens（其中缓存命中 30,000）｜花费 ¥0.2140
主要花在：gpt-6-sol ¥0.1900，mimo-v2.6-flash ¥0.0240
账户余额：¥12.35
```
