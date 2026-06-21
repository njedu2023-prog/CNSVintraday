# CNSVintraday V1.1 Data Connector 开发文档

## 一、开发目标

本阶段目标是完成 CNSVintraday 与 CNSVdata 的数据接线。

V1.1 只做 Data Connector。

本阶段不开发模型。

本阶段不开发正式预测。

本阶段不开发买卖信号。

本阶段只完成：

- 读取 CNSVdata 盘中线数据
- 严格识别 A 股交易日
- 识别 T 日与 T+1交易日
- 读取 T 日 14:00 快照
- 构建统一 IntradayContext
- 检查 ready 状态
- 检查数据质量状态
- 检查未来函数风险
- 生成基础 HTML 接线报告
- 建立自动测试

---

## 二、仓库边界

### CNSVdata

CNSVdata 是统一数据底座。

CNSVintraday 只能从 CNSVdata 读取数据。

CNSVintraday 禁止直接采集 Tushare 或其他外部数据源。

### CNSVintraday

CNSVintraday 是盘中线完整系统仓库。

本阶段只开发数据接线能力。

---

## 三、核心业务规则

### 1. 必须使用 A 股交易日历

系统必须严格使用 CNSVdata 提供的 A 股交易日历。

禁止使用自然日判断 T、T+1、T+2。

如果 1 日、2 日、3 日均为 A 股交易日：

- 1 日 = T 日
- 2 日 = T+1 交易日
- 3 日 = T+2 交易日

如果中间遇到周末、节假日、休市日，必须自动跳过。

### 2. T 日 14:00 快照规则

T 日 14:00 后运行主程序。

允许读取：

- T 日 09:30 至 11:30 数据
- T 日 13:00 至 14:00 数据
- T 日 14:00 快照
- T 日 14:00 以前已经形成的历史特征原料
- T 日以前的历史数据

禁止读取：

- T 日 14:00 之后的数据
- T 日收盘后数据
- T+1 数据
- T+1 真值
- T+1 收盘价
- 未来标签字段

### 3. ready 状态规则

CNSVintraday 必须先读取 ready 文件。

只有 ready 文件存在且状态合格，才允许继续读取快照数据。

ready 文件建议路径：

metadata/intraday/intraday_ready_1400.json

判断规则：

- ready = true 且 status = PASS：允许读取
- status = WARN：允许观察级读取，但必须在报告中标红提示
- ready = false 或 status = FAIL：禁止继续运行预测链路

---

## 四、需要读取的数据文件

### 1. 交易日历

建议读取：

data/processed/trade_calendar.parquet

用途：

- 判断当前日期是否交易日
- 获取 T 日
- 获取 T+1 交易日
- 获取 T+2 交易日
- 禁止自然日推断

### 2. ready 文件

建议读取：

metadata/intraday/intraday_ready_1400.json

用途：

- 判断盘中线数据是否可读取
- 判断状态 PASS/WARN/FAIL
- 获取数据版本
- 获取快照日期
- 获取快照时间

### 3. 14:00 快照文件

建议读取：

data/intraday/snapshots/YYYYMMDD/1400/cnsv_1min_asof_1400.parquet

data/intraday/snapshots/YYYYMMDD/1400/cnsv_5min_asof_1400.parquet

data/intraday/snapshots/YYYYMMDD/1400/cnsv_15min_asof_1400.parquet

data/intraday/snapshots/YYYYMMDD/1400/intraday_snapshot_1400.json

data/intraday/snapshots/YYYYMMDD/1400/intraday_quality_1400.json

data/intraday/snapshots/YYYYMMDD/1400/intraday_manifest_1400.json

---

## 五、代码目录结构

请在 CNSVintraday 仓库中建立如下结构：

src/cnsvintraday/

建议目录：

- core/
- data/
- validation/
- reports/
- utils/

具体文件建议：

src/cnsvintraday/core/context.py

src/cnsvintraday/data/calendar.py

src/cnsvintraday/data/ready_reader.py

src/cnsvintraday/data/snapshot_reader.py

src/cnsvintraday/validation/future_guard.py

src/cnsvintraday/reports/connector_report.py

src/cnsvintraday/utils/paths.py

---

## 六、核心对象设计

### IntradayContext

必须建立统一上下文对象。

建议字段：

- trade_date
- next_trade_date
- next2_trade_date
- ts_code
- snapshot_time
- data_cutoff_time
- ready
- status
- allowed_to_run
- warning_messages
- fail_reasons
- data_root
- ready_path
- calendar_path
- snapshot_1min_path
- snapshot_5min_path
- snapshot_15min_path
- quality_path
- manifest_path
- model_allowed
- formal_signal_allowed

### 关键约束

formal_signal_allowed 必须默认为 false。

allowed_to_run 只能表示允许观察级运行。

不能代表正式交易信号允许。

---

## 七、未来函数检查

必须建立 future_guard。

检查内容：

- 所有分钟数据时间必须 <= 14:00
- feature_time 必须 <= T 日 14:00
- label_time 不得出现在 T 日预测上下文中
- T+1 数据不得进入 T 日上下文
- T 日 14:00 后数据不得进入 T 日上下文

如果发现违规：

- context.status 标记为 FAIL
- allowed_to_run = false
- 记录 fail_reasons
- HTML 报告必须显示未来函数污染

---

## 八、基础 HTML 报告

V1.1 必须生成基础接线报告。

报告路径建议：

docs/reports/YYYYMMDD/connector_report_1400.html

latest 入口：

docs/connector_latest.html

报告必须包含：

- 当前 T 日
- 目标 T+1 交易日
- 数据截止时间
- ready 状态
- PASS/WARN/FAIL 状态
- 1min 文件是否存在
- 5min 文件是否存在
- 15min 文件是否存在
- quality 文件是否存在
- manifest 文件是否存在
- 未来函数检查结果
- 是否允许进入下一阶段
- 当前禁止正式信号说明

报告标题建议：

CNSVintraday V1.1 Data Connector Report

---

## 九、命令行入口

建议建立命令：

python -m cnsvintraday.data.build_context --trade-date YYYYMMDD --snapshot-time 1400

如果不传 trade-date，则自动使用 CNSVdata ready 文件中的最新交易日。

输出：

- 控制台摘要
- JSON context 文件
- HTML connector report

建议输出文件：

data/runtime/context/intraday_context_latest.json

data/runtime/context/YYYYMMDD/intraday_context_1400.json

---

## 十、测试要求

必须建立 tests/ 目录。

至少包含：

tests/test_trade_calendar.py

tests/test_ready_reader.py

tests/test_snapshot_reader.py

tests/test_context_builder.py

tests/test_future_guard.py

tests/test_connector_report.py

测试必须覆盖：

- 正确识别 T+1 交易日
- 周末和节假日不能被当作 T+1
- ready=false 时禁止运行
- status=FAIL 时禁止运行
- WARN 时允许观察级运行但必须提示
- 14:00 后数据进入时必须 FAIL
- T+1 label 不得进入 context
- HTML 报告能生成

---

## 十一、依赖文件

请补充或更新：

requirements.txt

建议依赖：

pandas

pyarrow

jinja2

pytest

python-dateutil

---

## 十二、CI 要求

新增 GitHub Actions：

.github/workflows/test.yml

触发条件：

- push
- pull_request
- workflow_dispatch

执行：

pip install -r requirements.txt

pytest

如果测试失败，CI 必须失败。

---

## 十三、V1.1 验收标准

V1.1 完成后必须满足：

1. 能读取 A 股交易日历

2. 能正确识别 T、T+1、T+2 交易日

3. 能读取 ready 文件

4. 能识别 PASS/WARN/FAIL

5. 能读取 1min、5min、15min 盘中快照

6. 能构建 IntradayContext

7. 能执行未来函数检查

8. 能生成 connector HTML 报告

9. 能输出 context JSON

10. pytest 全部通过

11. GitHub Actions 测试通过

---

## 十四、本阶段禁止开发内容

V1.1 阶段禁止开发：

- 预测模型
- 机器学习训练
- T+1 概率预测
- 涨跌幅预测
- 路径分布模型
- 买卖建议
- 正式信号
- 自动交易
- 券商接口

这些内容放到 V1.2 之后逐步开发。

---

## 十五、Codex 执行顺序

请 Codex 按以下顺序开发：

第一步：

创建项目目录结构。

第二步：

创建 requirements.txt。

第三步：

开发交易日历读取模块。

第四步：

开发 ready 文件读取模块。

第五步：

开发快照文件读取模块。

第六步：

开发 IntradayContext。

第七步：

开发 future_guard。

第八步：

开发 connector HTML 报告。

第九步：

开发命令行入口。

第十步：

补全 pytest 测试。

第十一步：

新增 GitHub Actions。

第十二步：

本地或 CI 自检。

第十三步：

提交代码。

---

## 十六、最终交付物

本阶段完成后，仓库中至少应新增：

src/cnsvintraday/core/context.py

src/cnsvintraday/data/calendar.py

src/cnsvintraday/data/ready_reader.py

src/cnsvintraday/data/snapshot_reader.py

src/cnsvintraday/validation/future_guard.py

src/cnsvintraday/reports/connector_report.py

src/cnsvintraday/utils/paths.py

tests/test_trade_calendar.py

tests/test_ready_reader.py

tests/test_snapshot_reader.py

tests/test_context_builder.py

tests/test_future_guard.py

tests/test_connector_report.py

.github/workflows/test.yml

requirements.txt

---

## 十七、最终说明

V1.1 的核心不是预测。

V1.1 的核心是保证：

CNSVdata 到 CNSVintraday 的数据链路安全、稳定、可验收。

只有 V1.1 验收通过后，才允许进入：

V1.2 Feature Engine。
