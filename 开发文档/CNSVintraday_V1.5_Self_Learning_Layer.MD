# CNSVintraday V1.5 Self Learning Layer 开发文档

版本：V1.5

阶段：Self Learning Layer

前置条件：

- V1.1.1 Data Connector 已通过
- V1.2 Feature Engine 已通过
- V1.3 Baseline Models 已通过
- V1.4 Path Distribution Layer 已通过

本阶段目标：

让 CNSVintraday 从“能预测”升级为“能复盘、能验证、能记录、能持续学习”。

V1.5 不开发新预测模型。

V1.5 不开发买卖信号。

V1.5 不开发自动交易。

V1.5 只负责：

- 记录 T 日 14:00 的预测
- 接入 T+1 真值
- 计算预测误差
- 计算模型表现
- 跟踪模型漂移
- 跟踪校准变化
- 生成自学习报告
- 为后续模型升级提供依据

---

# 一、核心业务闭环

CNSVintraday 的核心运行闭环：

T 日 14:00  
读取数据  
生成特征  
运行模型  
输出 T+1 概率与路径分布  
生成预测记录  

T+1 收盘后  
读取真值  
验证预测  
计算误差  
更新学习指标  
生成学习报告  

本阶段必须把这个闭环正式建立起来。

---

# 二、V1.5 的最高目标

V1.5 的最高目标不是提高一次预测的准确率。

V1.5 的最高目标是：

持续判断系统是否真的在进步。

必须回答：

- 哪个模型最近表现最好？
- 哪个模型最近退化？
- 哪些预测过度乐观？
- 哪些预测过度保守？
- Brier 是否下降？
- RMSE 是否下降？
- Coverage 是否改善？
- Calibration 是否改善？
- 最近 20 / 60 / 150 个交易日是否稳定？

---

# 三、禁止事项

V1.5 阶段禁止：

- 新增 XGBoost
- 新增 LightGBM
- 新增 CatBoost
- 新增神经网络
- 新增买入信号
- 新增卖出信号
- 新增仓位建议
- 新增自动交易
- 新增券商接口

这些内容不得进入 V1.5。

V1.5 只做自学习与验证闭环。

---

# 四、目录结构

新增目录：

```text
src/cnsvintraday/learning/
```

建议文件：

```text
src/cnsvintraday/learning/__init__.py
src/cnsvintraday/learning/prediction_log.py
src/cnsvintraday/learning/truth_joiner.py
src/cnsvintraday/learning/error_metrics.py
src/cnsvintraday/learning/calibration_tracker.py
src/cnsvintraday/learning/model_drift_monitor.py
src/cnsvintraday/learning/learning_state.py
src/cnsvintraday/learning/learning_dashboard.py
src/cnsvintraday/learning/build_learning.py
```

新增测试：

```text
tests/test_prediction_log.py
tests/test_truth_joiner.py
tests/test_error_metrics.py
tests/test_calibration_tracker.py
tests/test_model_drift_monitor.py
tests/test_learning_state.py
tests/test_learning_dashboard.py
```

---

# 五、输入文件

V1.5 读取上游阶段产物。

## 1. V1.3 预测输出

```text
data/models/prediction_snapshot_1400.parquet
```

至少包含：

- trade_date
- next_trade_date
- model_name
- prob_up
- prob_down
- expected_return
- confidence
- snapshot_time
- model_version

## 2. V1.4 路径输出

```text
data/paths/path_distribution_latest.parquet
```

至少包含：

- trade_date
- next_trade_date
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

## 3. T+1 真值

真值必须来自 CNSVdata。

建议路径优先使用：

```text
data/labels/t1_truth/t1_truth_vs_1400_latest.parquet
```

或 CNSVdata 已有等价 T+1 truth 文件。

真值字段必须至少包含：

- trade_date
- next_trade_date
- close_1400
- next_open
- next_high
- next_low
- next_close
- actual_return_t1
- actual_up_t1

如果真实文件字段名称不同，必须在 truth_joiner.py 中建立字段映射，但不得改变核心含义。

---

# 六、Prediction Log

建立：

```text
prediction_log.py
```

目标：

把每次 T 日 14:00 的预测结果记录成标准日志。

输出：

```text
data/learning/prediction_log_latest.parquet
data/learning/history/prediction_log_YYYYMMDD_1400.parquet
```

字段建议：

- run_id
- trade_date
- next_trade_date
- snapshot_time
- model_name
- model_version
- feature_version
- path_version
- prob_up
- prob_down
- expected_return
- confidence
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
- created_at
- formal_signal_allowed

硬性要求：

```text
formal_signal_allowed = false
```

---

# 七、Truth Joiner

建立：

```text
truth_joiner.py
```

目标：

把 T 日预测与 T+1 真值对齐。

必须严格使用：

```text
trade_date + next_trade_date
```

禁止使用自然日直接 +1。

输出：

```text
data/learning/prediction_truth_joined_latest.parquet
```

字段建议：

- trade_date
- next_trade_date
- model_name
- prob_up
- expected_return
- path_p10
- path_p50
- path_p90
- actual_return_t1
- actual_up_t1
- next_close
- joined_status

如果缺少真值：

```text
joined_status = PENDING_TRUTH
```

不得强行填充。

不得用未来模拟值替代真值。

---

# 八、误差指标 Error Metrics

建立：

```text
error_metrics.py
```

必须计算：

## 分类指标

- hit_rate
- brier_score
- log_loss_safe

## 回归指标

- rmse
- mae
- mean_error
- median_abs_error

## 路径指标

- coverage_p10_p90
- coverage_p25_p75
- interval_width_p10_p90
- interval_width_p25_p75
- p50_error
- p50_abs_error

输出：

```text
data/learning/learning_metrics_latest.json
```

统计窗口必须包括：

- latest
- last_20
- last_60
- last_150

如果样本不足，必须标记：

```text
sample_status = INSUFFICIENT
```

不得伪装成有效结论。

---

# 九、Calibration Tracker

建立：

```text
calibration_tracker.py
```

目标：

判断概率是否校准。

示例：

如果模型给出 70% 上涨概率，长期看是否接近 70% 实际上涨。

必须输出：

- calibration_bins
- bin_predicted_prob
- bin_actual_rate
- bin_count
- calibration_error
- over_confidence_flag
- under_confidence_flag

输出：

```text
data/learning/calibration_latest.json
```

要求：

分箱建议：

```text
0.0-0.1
0.1-0.2
0.2-0.3
0.3-0.4
0.4-0.5
0.5-0.6
0.6-0.7
0.7-0.8
0.8-0.9
0.9-1.0
```

样本不足时，不得强行判断校准好坏。

---

# 十、Model Drift Monitor

建立：

```text
model_drift_monitor.py
```

目标：

判断模型近期是否退化。

必须比较：

- last_20 vs last_60
- last_20 vs last_150
- last_60 vs last_150

核心指标：

- brier_score
- rmse
- hit_rate
- coverage_p10_p90

漂移状态：

```text
STABLE
IMPROVING
DEGRADING
INSUFFICIENT
```

输出：

```text
data/learning/model_drift_latest.json
```

判断规则建议：

如果 last_20 的 Brier 明显高于 last_60，同时 RMSE 上升，标记为 DEGRADING。

如果 last_20 的 Brier 下降，RMSE 下降，Coverage 稳定，标记为 IMPROVING。

如果样本不足，标记为 INSUFFICIENT。

---

# 十一、Learning State

建立：

```text
learning_state.py
```

目标：

生成系统学习状态总开关。

输出：

```text
metadata/learning_state_latest.json
```

字段建议：

- learning_ready
- learning_status
- latest_trade_date
- latest_truth_date
- sample_count
- last_20_status
- last_60_status
- last_150_status
- best_model_last_20
- best_model_last_60
- best_model_last_150
- drift_status
- calibration_status
- allowed_usage

allowed_usage 必须包含：

```json
{
  "can_review_predictions": true,
  "can_update_dashboard": true,
  "can_promote_model": false,
  "can_generate_formal_signal": false
}
```

本阶段禁止自动提升模型为正式生产模型。

---

# 十二、Learning Dashboard

建立：

```text
learning_dashboard.py
```

输出：

```text
docs/learning/learning_dashboard.html
docs/learning/README.md
```

Dashboard 必须展示：

- 最新预测日
- 最新真值日
- 样本数量
- last_20 / last_60 / last_150 指标
- Brier
- RMSE
- Hit Rate
- Coverage
- Calibration
- Drift Status
- 最佳模型
- 退化模型
- 当前系统状态
- 禁止正式信号说明

页面定位：

观察级学习报告。

不得出现：

- 买入
- 卖出
- 建仓
- 清仓
- 仓位
- 正式信号

---

# 十三、CLI 入口

建立：

```text
python -m cnsvintraday.learning.build_learning --data-root . --snapshot-time 1400
```

功能：

1. 读取 prediction_snapshot
2. 读取 path_distribution
3. 读取 t1 truth
4. 生成 prediction_log
5. 生成 joined truth
6. 计算 metrics
7. 计算 calibration
8. 计算 drift
9. 生成 learning_state
10. 生成 learning_dashboard

如果真值不存在：

允许生成 PENDING 状态。

但 metrics/calibration/drift 必须标记样本不足或等待真值。

---

# 十四、输出文件契约

V1.5 必须新增：

```text
data/learning/README.md
data/learning/prediction_log_latest.parquet
data/learning/prediction_truth_joined_latest.parquet
data/learning/learning_metrics_latest.json
data/learning/calibration_latest.json
data/learning/model_drift_latest.json
metadata/learning_state_latest.json
docs/learning/README.md
docs/learning/learning_dashboard.html
```

如果不提交 parquet 产物，至少必须提交：

```text
data/learning/README.md
docs/learning/README.md
```

并且测试必须验证 pipeline 在临时目录中能真实生成 parquet/json/html。

---

# 十五、未来函数与安全检查

V1.5 必须继续使用：

```text
future_guard
```

检查：

- prediction_log 不得包含未来 feature 字段
- joined 文件允许包含 truth 字段，但只能存在于验证层
- learning 输出不得回写到 feature_snapshot
- actual_return_t1 不得进入任何 feature 文件
- truth 字段不得进入模型训练输入

必须明确隔离：

```text
Feature 层
Prediction 层
Truth 层
Learning 层
```

不得混用。

---

# 十六、测试要求

新增测试：

```text
tests/test_prediction_log.py
tests/test_truth_joiner.py
tests/test_error_metrics.py
tests/test_calibration_tracker.py
tests/test_model_drift_monitor.py
tests/test_learning_state.py
tests/test_learning_dashboard.py
tests/test_build_learning.py
```

测试必须覆盖：

- prediction_log 能写出
- truth_joiner 能按 trade_date + next_trade_date 对齐
- 缺真值时标记 PENDING_TRUTH
- Brier 计算正确
- RMSE 计算正确
- Coverage 计算正确
- Calibration 分箱正确
- 样本不足时状态为 INSUFFICIENT
- drift 能识别 DEGRADING / IMPROVING / STABLE
- learning_state 中 can_generate_formal_signal=false
- dashboard 能生成
- pipeline 能完整跑通

覆盖率要求：

```text
>= 80%
```

---

# 十七、CI 要求

GitHub Actions 必须继续执行：

```text
pytest -q
coverage >= 80%
```

如已有 CI，则扩展现有 CI。

不要新增重复 workflow 造成混乱。

---

# 十八、验收标准

V1.5 完成后必须满足：

1. learning 模块完整存在
2. prediction_log 可生成
3. truth_joined 可生成
4. learning_metrics 可生成
5. calibration 可生成
6. drift 可生成
7. learning_state 可生成
8. learning_dashboard 可生成
9. 缺真值时不崩溃，状态清晰
10. 样本不足时不伪装有效结论
11. formal_signal_allowed 永远为 false
12. can_generate_formal_signal 永远为 false
13. 测试通过
14. CI 通过

---

# 十九、Codex 执行顺序

第一步：

建立 learning 目录。

第二步：

实现 prediction_log.py。

第三步：

实现 truth_joiner.py。

第四步：

实现 error_metrics.py。

第五步：

实现 calibration_tracker.py。

第六步：

实现 model_drift_monitor.py。

第七步：

实现 learning_state.py。

第八步：

实现 learning_dashboard.py。

第九步：

实现 build_learning.py CLI。

第十步：

补齐 data/learning 和 docs/learning README。

第十一步：

补齐测试。

第十二步：

跑 pytest 和 coverage。

第十三步：

提交。

建议 commit message：

```text
Implement CNSVintraday V1.5 self learning layer
```

---

# 二十、最终说明

V1.5 是 CNSVintraday 的学习闭环层。

它不负责让系统“看起来更聪明”。

它负责让系统知道：

- 自己哪里准
- 哪里不准
- 哪个模型变好
- 哪个模型变差
- 哪些概率不可信
- 哪些区间不可靠

只有 V1.5 通过后，后续高级模型才有资格进入比较和升级。
