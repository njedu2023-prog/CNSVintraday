# CNSVintraday

CNSVintraday 是中国船舶 `600150.SH` 盘中观察与实盘辅助分析仓库。

本仓库用于承载盘中数据接线、分钟级观察、临时运行产物整理、盘中看板与后续自动化流程。它与以下仓库分工保持独立：

- `njedu2023-prog/CNSV`：主程序与中长期人工量化波段系统。
- `njedu2023-prog/CNSVdata`：数据仓库。
- `njedu2023-prog/CNSVintraday`：盘中观察、盘中辅助分析与相关自动化。

## 当前状态

仓库已初始化到 `main` 分支，并配置为通过已授权的 ChatGPT Codex Connector 直接创建或更新文件。

## 写入约束

- 使用已授权的 ChatGPT Codex Connector 直接写入 GitHub 仓库。
- 不使用 SSH。
- 不使用普通 `git push`。
- 不要求本地仓库权限。
- 更新已有文件时，先读取远端文件 `sha`，再提交更新。
- 涉及 `.github/workflows` 文件时，也通过 Connector 直接修改。
- 尽量合并为少量 commit。

## 当前不做

- 不自动下单。
- 不连接券商接口。
- 不输出正式买卖指令。
- 不绕过 `CNSVdata` 的数据职责。
