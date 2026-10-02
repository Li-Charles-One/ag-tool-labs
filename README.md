# AG Tool Labs

[Artistic Genius](https://artistic-genius.vip) 的 Skill 与 MCP。这里收 Artistic Genius 的专属工具，以及自制的通用 skill。

下载页：<https://toollabs.artistic-genius.vip>　接入教程：<https://docs.artistic-genius.vip>

## Skill

### Artistic Genius 专属

| 名称 | 用途 | 需要的凭证 | 下载 |
|---|---|---|---|
| [artistic-genius-user-api](skills/artistic-genius-user-api/) | 费用与余额查询：让你的 Agent 用你自己的令牌查余额、已用额度和调用记录，统计某个任务花了多少，金额一律换算成人民币。 | `sk-` 令牌（环境变量 `AG_API_KEY`）；查整个账号的花费还需要系统访问令牌（`AG_ACCESS_TOKEN`） | [v1.0.1](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/artistic-genius-user-api-v1.0.1/artistic-genius-user-api-v1.0.1.zip) |
| [ag-omni](skills/ag-omni/) | 视听分析：让你的 Agent 看图、读 PDF、听音频、看视频，做图片理解与 OCR、UI 截图点评、音视频总结与转写，支持 YouTube 链接。 | Gemini 分组的 `sk-` 令牌（环境变量 `AG_GEMINI_KEY`）；想用 MiMo 时另需 mimo 分组的令牌（`AG_MIMO_KEY`）。本机需要 Python 3.9+ 与 ffmpeg | [v1.0.0](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/ag-omni-v1.0.0/ag-omni-v1.0.0.zip) |
| [ag-x-search](skills/ag-x-search/) | X 实时搜索：让你的 Agent 通过 Grok 搜 X（Twitter），按关键词找帖子、看某个账号的最近动态、出话题热度与情绪简报，结果带原帖链接。 | Grok 分组的 `sk-` 令牌（环境变量 `AG_GROK_KEY`）。本机需要 Python 3.9+ | [v1.0.1](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/ag-x-search-v1.0.1/ag-x-search-v1.0.1.zip) |

### 通用

不依赖 Artistic Genius 账号，任何 Agent 都能用。

| 名称 | 用途 | 需要的环境 | 下载 |
|---|---|---|---|
| [genius-brief-thinking](skills/genius-brief-thinking/) | 设计简报：需求不清时先比较 2–3 个方案并给出推荐，把要做什么、为什么做写成带编号需求的简报。只到简报为止，不写代码。 | 无；可选的浏览器可视化伴侣需要 Node.js | [v2.1.0](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/genius-brief-thinking-v2.1.0/genius-brief-thinking-v2.1.0.zip) |
| [genius-impl-plans](skills/genius-impl-plans/) | 实现计划：把已确认的简报拆成逐步可执行的计划，写明具体文件、完整代码、命令和预期结果。只到计划为止。 | 无 | [v1.1.0](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/genius-impl-plans-v1.1.0/genius-impl-plans-v1.1.0.zip) |
| [genius-weplaning](skills/genius-weplaning/) | 项目记忆：在项目的 `.agent-memory/` 里维护当前状态、变更账本和决策，换会话、换 Agent 也能接着干。 | Node.js | [v3.1.1](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/genius-weplaning-v3.1.1/genius-weplaning-v3.1.1.zip) |
| [genius-design](skills/genius-design/) | 设计规范：生成、审查或更新 `DESIGN.md`，可按品牌资料适配、从现有网站逆向，或按产品场景推荐。只出规范，不实现页面。 | Python 3.9+ 与 PyYAML | [v3.4.1](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/genius-design-v3.4.1/genius-design-v3.4.1.zip) |
| [genius-github-usage](skills/genius-github-usage/) | GitHub 操作：用 GitHub CLI 管理仓库、Issue、PR 审查与 Release，检索开源项目；合并、删除等高风险操作先问你。 | 已登录的 `gh` | [v1.1.0](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/genius-github-usage-v1.1.0/genius-github-usage-v1.1.0.zip) |
| [genius-lark-use](skills/genius-lark-use/) | 飞书 / Lark：通过官方 `lark-cli` 读写云文档和多维表格、收发消息、管理日程任务。 | 已安装并登录的 `lark-cli`（skill 不会替你安装或登录） | [v1.1.0](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/genius-lark-use-v1.1.0/genius-lark-use-v1.1.0.zip) |
| [genius-skill-creator](skills/genius-skill-creator/) | Skill 制作：创建、修复、审计、评测与优化 skill 包，自带结构校验和安全扫描脚本。 | Python 3 | [v2.0.0](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/genius-skill-creator-v2.0.0/genius-skill-creator-v2.0.0.zip) |

`genius-brief-thinking` → `genius-impl-plans` → 动手实现 → `genius-weplaning` 可以连成一条流程，交接约定见 [skills/WORKFLOW.md](skills/WORKFLOW.md)；也可以各自单独使用。

## MCP

暂无。

## 安装

把下面这句话发给你的 Agent（把 skill 名换成你要装的那个），它会按自己所处的环境判断该装到哪里：

```text
请阅读 https://github.com/Li-Charles-One/ag-tool-labs 的 README，把其中的 artistic-genius-user-api 这个 skill 安装到你自己的 skill 目录里，装好后告诉我装在了哪里。
```

也可以手动安装：下载上表的 zip，解压后把整个 skill 文件夹放进你的 Agent 的 skill 目录。

## 凭证（Artistic Genius 专属 skill）

- `sk-` 令牌：登录 <https://artistic-genius.vip> → 控制台 → 令牌 → 新建令牌。建令牌时要选分组，一把令牌只能调用所属分组的模型：`ag-omni` 用 Gemini 分组（或 mimo 分组）的令牌，`ag-x-search` 用 Grok 分组的令牌。
- 系统访问令牌（仅 `artistic-genius-user-api` 查整个账号时需要）：控制台 → 个人设置 → 访问令牌 → 生成。它等于账号全部权限，请按密码保管。

凭证只放在环境变量里，不要贴进聊天，也不要写进会提交到 Git 的文件。
