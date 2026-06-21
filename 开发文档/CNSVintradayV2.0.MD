# CNSVintraday V2.0 Intraday Decision Report Layer 开发文档

版本：V2.0

阶段：Intraday Decision Report Layer

定位：盘中线观察级人工决策报告层

前置条件：

- V1.1.1 Data Connector 已通过
- V1.2 Feature Engine 已通过
- V1.3 Baseline Models 已通过
- V1.4 Path Distribution Layer 已通过
- V1.5 Self Learning Layer 已通过

---

# 一、V2.0 的核心定位

V2.0 是 CNSVintraday 第一个真正给人使用的报告层。

它不是新模型层。

它不是自动交易层。

它不是正式买卖信号层。

它的目标是：

把 V1.1 到 V1.5 的所有结果整合成一个 T 日 14:00 后可阅读、可判断、可复盘的 HTML 决策辅助报告。

报告服务对象：

人工操作者。

报告使用时间：

T 日 14:00 后。

报告预测对象：

T+1 交易日。

核心回答：

- 明天上涨概率是多少？
- 明天预期涨跌幅是多少？
- 明天价格大概落在哪个区间？
- 当前模型可信度如何？
- 当前预测有没有数据风险？
- 当前模型最近是否退化？
- 当前结果能不能用于人工观察？
- 当前是否禁止正式信号？

---

# 二、必须坚持的边界

V2.0 可以输出：

- 观察结论
- 概率判断
- 路径区间
- 风险提示
- 数据状态
- 模型状态
- 学习状态
- 人工观察提示

V2.0 禁止输出：

- 买入信号
- 卖出信号
- 建仓指令
- 清仓指令
- 仓位建议
- 自动下单
- 券商接口
- 正式交易信号

所有报告必须明确：

本报告仅用于人工观察与辅助分析，不构成正式交易信号。

---

# 三、业务流程

标准流程：

T 日 14:00  
读取 CNSVdata 快照  
读取 V1.1 IntradayContext  
读取 V1.2 Feature Snapshot  
读取 V1.3 Baseline Predictions  
读取 V1.4 Path Distribution  
读取 V1.5 Learning State  
生成 V2.0 Decision Report  
人工阅读报告  
人工自行决策  
T+1 收盘后进入 V1.5 真值验证闭环  

注意：

V2.0 不改变 V1.1 到 V1.5 的底层产物。

V2.0 只做聚合、解释、展示、风险提示。

---

# 四、输入文件

V2.0 必须读取以下文件。

## 1. Context

```text
data/runtime/context/intraday_context_latest.json
```

用途：

- trade_date
- next_trade_date
- snapshot_time
- ready
- status
- allowed_to_run
- future_guard_passed
- formal_signal_allowed

## 2. Feature Snapshot

```text
data/features/feature_snapshot_1400.parquet
```

用途：

- 核心特征摘要
- 特征质量提示
- 解释主要盘中特征状态

## 3. Feature Quality

```text
data/features/feature_quality_latest.json
```

用途：

- 缺失率
- 异常值
- 常数列
- Future Guard 状态

## 4. Baseline Model Prediction

```text
data/models/prediction_snapshot_1400.parquet
```

用途：

- model_name
- prob_up
- prob_down
- expected_return
- confidence

## 5. Model Leaderboard

```text
data/models/model_leaderboard.json
```

用途：

- B0/B1/B2/B3 模型表现
- AUC
- Brier
- RMSE
- Hit Rate

## 6. Path Distribution

```text
data/paths/path_distribution_latest.parquet
```

用途：

- path_p10
- path_p25
- path_p50
- path_p75
- path_p90
- price_p10
- price_p25
- price_p50
- price_p75
- price_p90
- downside_risk
- upside_potential
- expected_range

## 7. Path Metrics

```text
data/paths/path_metrics_latest.json
```

用途：

- Coverage
- Interval Width
- RMSE
- Calibration

## 8. Learning State

```text
metadata/learning_state_latest.json
```

用途：

- learning_ready
- learning_status
- sample_count
- drift_status
- calibration_status
- best_model_last_20
- best_model_last_60
- best_model_last_150
- can_generate_formal_signal

如果该文件不存在：

报告不得崩溃。

必须显示：

Learning State Missing

并将整体报告状态降为 WARN 或 FAIL，具体规则由 decision_gate 决定。

## 9. Learning Metrics

```text
data/learning/learning_metrics_latest.json
```

用途：

- last_20
- last_60
- last_150
- Brier
- RMSE
- Hit Rate
- Coverage

---

# 五、输出文件

V2.0 必须输出：

```text
docs/decision/intraday_decision_latest.html
docs/decision/reports/YYYYMMDD/intraday_decision_1400.html
data/decision/intraday_decision_latest.json
data/decision/history/YYYYMMDD/intraday_decision_1400.json
```

同时新增：

```text
docs/decision/README.md
data/decision/README.md
```

如果不提交自动生成 HTML/JSON，至少必须提交 README。

但测试必须验证 pipeline 在临时目录中真实生成 HTML/JSON。

---

# 六、代码目录结构

新增目录：

```text
src/cnsvintraday/decision/
```

建议文件：

```text
src/cnsvintraday/decision/__init__.py
src/cnsvintraday/decision/decision_loader.py
src/cnsvintraday/decision/decision_summary.py
src/cnsvintraday/decision/decision_gate.py
src/cnsvintraday/decision/risk_summary.py
src/cnsvintraday/decision/model_summary.py
src/cnsvintraday/decision/path_summary.py
src/cnsvintraday/decision/learning_summary.py
src/cnsvintraday/decision/decision_report.py
src/cnsvintraday/decision/build_decision.py
```

---

# 七、Decision Loader

建立：

```text
decision_loader.py
```

目标：

统一读取 V1.1 到 V1.5 的产物。

要求：

- 文件存在则读取
- 文件缺失不得直接崩溃
- 必须返回 missing_files 列表
- 必须返回 warning_messages
- 必须返回 fail_reasons
- 关键文件缺失时由 decision_gate 判定是否 FAIL

关键文件：

- context
- feature_snapshot
- prediction_snapshot
- path_distribution

非关键但重要文件：

- feature_quality
- model_leaderboard
- path_metrics
- learning_state
- learning_metrics

---

# 八、Decision Gate

建立：

```text
decision_gate.py
```

目标：

统一判断报告状态。

报告状态：

```text
PASS
WARN
FAIL
```

## FAIL 条件

以下任一条件成立，报告必须 FAIL：

- context.ready = false
- context.status = FAIL
- context.future_guard_passed = false
- prediction_snapshot 缺失
- path_distribution 缺失
- feature_snapshot 缺失
- formal_signal_allowed = true
- can_generate_formal_signal = true
- 发现未来字段污染
- trade_date 与 next_trade_date 不匹配
- 使用自然日推断 T+1

## WARN 条件

以下条件成立，报告 WARN：

- learning_state 缺失
- learning_metrics 缺失
- feature_quality 缺失
- model_leaderboard 缺失
- path_metrics 缺失
- sample_count 不足
- drift_status = DEGRADING
- calibration_status = INSUFFICIENT
- status = WARN
- 部分模型表现不足

## PASS 条件

必须同时满足：

- context ready
- context PASS
- future_guard PASS
- feature/prediction/path 三大核心产物存在
- learning_state 不阻断
- 无未来字段污染
- 禁止正式信号
- 仅观察级输出

---

# 九、Decision Summary

建立：

```text
decision_summary.py
```

目标：

形成报告核心摘要。

建议字段：

```text
trade_date
next_trade_date
snapshot_time
report_status
prob_up
prob_down
expected_return
path_p10
path_p50
path_p90
price_p10
price_p50
price_p90
confidence
risk_level
drift_status
calibration_status
allowed_for_observation
formal_signal_allowed
```

注意：

formal_signal_allowed 永远必须为 false。

allowed_for_observation 只代表允许人工观察，不代表允许交易。

---

# 十、Model Summary

建立：

```text
model_summary.py
```

目标：

把 V1.3 模型结果整理为报告可读内容。

必须展示：

- 最终采用模型
- B0/B1/B2/B3 概览
- prob_up
- prob_down
- expected_return
- confidence
- 最近表现
- 是否优于随机模型 B0

如果没有模型显著优于 B0：

报告必须提示：

当前模型优势不足，预测仅供观察。

---

# 十一、Path Summary

建立：

```text
path_summary.py
```

目标：

把 V1.4 路径分布转成人可读的价格区间。

必须展示：

- P10
- P25
- P50
- P75
- P90
- price_p10
- price_p25
- price_p50
- price_p75
- price_p90
- expected_range

解释要求：

P10 表示偏悲观情形。

P50 表示中位情形。

P90 表示偏乐观情形。

不得把 P90 解释为必然目标价。

---

# 十二、Risk Summary

建立：

```text
risk_summary.py
```

目标：

形成风险提示。

风险等级建议：

```text
LOW
MEDIUM
HIGH
UNKNOWN
```

风险来源：

- downside_risk
- expected_range
- drift_status
- calibration_status
- feature_quality
- sample_count
- prediction_confidence
- path_coverage

风险提示必须明确：

风险高不等于必跌。

风险低不等于必涨。

---

# 十三、Learning Summary

建立：

```text
learning_summary.py
```

目标：

整合 V1.5 自学习状态。

展示：

- sample_count
- last_20 hit rate
- last_60 hit rate
- last_150 hit rate
- Brier
- RMSE
- Coverage
- drift_status
- calibration_status
- best_model_last_20
- best_model_last_60
- best_model_last_150

如果样本不足：

必须显示：

样本不足，不能得出稳定结论。

不得伪装成高置信结论。

---

# 十四、HTML 报告结构

建立：

```text
decision_report.py
```

输出 HTML。

页面标题：

```text
CNSVintraday V2.0 Intraday Decision Report
```

报告结构必须包含：

## 1. 顶部状态卡

- report_status
- trade_date
- next_trade_date
- snapshot_time
- ready
- future_guard
- observation_allowed
- formal_signal_allowed = false

## 2. 核心预测卡

- T+1 上涨概率
- T+1 下跌概率
- T+1 预期涨跌幅
- 置信度

## 3. 路径分布卡

- P10 / P25 / P50 / P75 / P90
- price_p10 / price_p25 / price_p50 / price_p75 / price_p90

## 4. 风险卡

- downside_risk
- upside_potential
- expected_range
- risk_level
- risk_notes

## 5. 模型状态卡

- B0/B1/B2/B3
- best_model
- leaderboard 摘要

## 6. 自学习卡

- sample_count
- last_20
- last_60
- last_150
- drift_status
- calibration_status

## 7. 数据质量卡

- feature_quality
- missing_files
- warning_messages
- fail_reasons

## 8. 人工观察说明

必须写明：

本报告仅用于 T 日 14:00 后人工观察与辅助分析。

本报告不构成正式买入、卖出或持仓建议。

---

# 十五、JSON 报告结构

输出：

```text
data/decision/intraday_decision_latest.json
```

建议字段：

```json
{
  "version": "V2.0",
  "trade_date": "",
  "next_trade_date": "",
  "snapshot_time": "1400",
  "report_status": "",
  "observation_allowed": false,
  "formal_signal_allowed": false,
  "prediction": {},
  "path_distribution": {},
  "risk": {},
  "model_summary": {},
  "learning_summary": {},
  "data_quality": {},
  "missing_files": [],
  "warning_messages": [],
  "fail_reasons": [],
  "created_at": ""
}
```

---

# 十六、CLI 入口

建立：

```text
python -m cnsvintraday.decision.build_decision --data-root . --snapshot-time 1400
```

参数：

```text
--data-root
--trade-date
--snapshot-time
--output-html
--output-json
```

默认输出：

```text
docs/decision/intraday_decision_latest.html
data/decision/intraday_decision_latest.json
```

同时归档：

```text
docs/decision/reports/YYYYMMDD/intraday_decision_1400.html
data/decision/history/YYYYMMDD/intraday_decision_1400.json
```

---

# 十七、Future Guard

V2.0 必须继续执行未来字段检查。

检查对象：

- feature_snapshot
- prediction_snapshot
- path_distribution
- decision_summary

注意：

Learning truth 文件中可以存在 truth/actual 字段。

但这些字段不得回流到：

- feature
- model input
- decision prediction core

如果发现 decision core 中存在 actual_return_t1、truth、label、next_close 等字段：

报告必须 FAIL。

---

# 十八、测试要求

新增测试：

```text
tests/test_decision_loader.py
tests/test_decision_gate.py
tests/test_decision_summary.py
tests/test_model_summary.py
tests/test_path_summary.py
tests/test_risk_summary.py
tests/test_learning_summary.py
tests/test_decision_report.py
tests/test_build_decision.py
```

测试必须覆盖：

- 核心文件缺失时 FAIL
- 非核心文件缺失时 WARN
- context FAIL 时报告 FAIL
- future_guard FAIL 时报告 FAIL
- formal_signal_allowed=true 时报告 FAIL
- can_generate_formal_signal=true 时报告 FAIL
- learning_state 缺失时 WARN
- 样本不足时显示 INSUFFICIENT
- 路径 P10/P50/P90 正确展示
- JSON 报告能生成
- HTML 报告能生成
- CLI 能跑通
- 报告中不得出现正式买入/卖出指令

覆盖率要求：

```text
>= 80%
```

---

# 十九、CI 要求

继续使用现有 workflow。

不得新增重复 workflow 造成混乱。

CI 必须执行：

```text
pytest -q
coverage >= 80%
```

如当前 workflow 已具备，则只需保证新增测试纳入现有 CI。

---

# 二十、输出目录契约

新增：

```text
data/decision/README.md
docs/decision/README.md
```

README 必须说明：

```text
data/decision/ 为 V2.0 决策报告 JSON 输出目录。
docs/decision/ 为 V2.0 决策报告 HTML 输出目录。
自动生成文件不一定提交，但 pipeline 必须可以生成。
```

---

# 二十一、验收标准

V2.0 完成后必须满足：

1. decision 模块完整存在
2. 能读取 V1.1 到 V1.5 的核心产物
3. 能生成 HTML 报告
4. 能生成 JSON 报告
5. 能归档历史报告
6. 能识别 PASS/WARN/FAIL
7. 能显示 T+1 上涨概率
8. 能显示 T+1 预期涨跌幅
9. 能显示 P10/P50/P90 价格区间
10. 能显示模型状态
11. 能显示自学习状态
12. 能显示风险等级
13. 能显示数据质量
14. formal_signal_allowed 永远为 false
15. 报告不得出现正式买入/卖出指令
16. 测试通过
17. CI 通过

---

# 二十二、Codex 执行顺序

第一步：

建立 decision 目录。

第二步：

实现 decision_loader.py。

第三步：

实现 decision_gate.py。

第四步：

实现 decision_summary.py。

第五步：

实现 model_summary.py。

第六步：

实现 path_summary.py。

第七步：

实现 risk_summary.py。

第八步：

实现 learning_summary.py。

第九步：

实现 decision_report.py。

第十步：

实现 build_decision.py CLI。

第十一步：

新增 data/decision 和 docs/decision README。

第十二步：

补齐测试。

第十三步：

跑 pytest 和 coverage。

第十四步：

提交。

建议 commit message：

```text
Implement CNSVintraday V2.0 intraday decision report layer
```

---

# 二十三、最终说明

V2.0 是 CNSVintraday 第一版完整可读的盘中线报告层。

它把：

- 数据状态
- 特征状态
- 模型概率
- 路径分布
- 风险判断
- 自学习状态

合成一个人能直接看的 T 日 14:00 后报告。

它的价值不是替人下单。

它的价值是：

让人工决策有结构、有依据、有风险边界、有复盘闭环。
