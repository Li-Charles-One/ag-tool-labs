# AG Tool Labs

[Artistic Genius](https://artistic-genius.vip) 的 Skill 与 MCP。这里只收 Artistic Genius 自己的工具。

下载页：<https://toollabs.artistic-genius.vip>　接入教程：<https://docs.artistic-genius.vip>

## Skill

| 名称 | 用途 | 需要的凭证 | 下载 |
|---|---|---|---|
| [artistic-genius-user-api](skills/artistic-genius-user-api/) | 费用与余额查询：让你的 Agent 用你自己的令牌查余额、已用额度和调用记录，统计某个任务花了多少，金额一律换算成人民币。 | `sk-` 令牌（环境变量 `AG_API_KEY`）；查整个账号的花费还需要系统访问令牌（`AG_ACCESS_TOKEN`） | [v1.0.1](https://github.com/Li-Charles-One/ag-tool-labs/releases/download/artistic-genius-user-api-v1.0.1/artistic-genius-user-api-v1.0.1.zip) |

## MCP

暂无。

## 安装

把下面这句话发给你的 Agent，它会按自己所处的环境判断该装到哪里：

```text
请阅读 https://github.com/Li-Charles-One/ag-tool-labs 的 README，把其中的 artistic-genius-user-api 这个 skill 安装到你自己的 skill 目录里，装好后告诉我装在了哪里。
```

也可以手动安装：下载上表的 zip，解压后把整个 `artistic-genius-user-api` 文件夹放进你的 Agent 的 skill 目录。

## 凭证

- `sk-` 令牌：登录 <https://artistic-genius.vip> → 控制台 → 令牌 → 新建令牌。
- 系统访问令牌：控制台 → 个人设置 → 访问令牌 → 生成。它等于账号全部权限，请按密码保管。

凭证只放在环境变量里，不要贴进聊天，也不要写进会提交到 Git 的文件。
