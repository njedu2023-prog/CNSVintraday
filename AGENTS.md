# AGENTS.md instructions

请使用已授权的 ChatGPT Codex Connector 直接写入 GitHub 仓库。

不要使用 SSH。
不要使用普通 git push。
不要要求本地仓库权限。

仓库：`njedu2023-prog/CNSVintraday`
分支：`main`

请直接创建或更新文件。
如果更新已有文件，请先读取远端 sha，再更新。
如果涉及 `.github/workflows` 文件，也可以直接修改，因为 Connector 已有 workflows 写权限。
尽量合并为少量 commit。

## 仓库分工

- `njedu2023-prog/CNSV`：主程序仓库。
- `njedu2023-prog/CNSVdata`：数据仓库。
- `njedu2023-prog/CNSVintraday`：盘中观察、盘中辅助分析与相关自动化仓库。

## 操作边界

- 不使用 SSH remote。
- 不通过普通本地 `git push` 上传。
- 不要求或依赖本地 `.git` 写权限。
- 所有远端文件更新优先使用 GitHub Connector contents API。
