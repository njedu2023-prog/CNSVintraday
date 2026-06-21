# CNSVintraday V1.0 总体架构设计

## 一、项目定位

项目名称：

CNSVintraday

定位：

中国船舶（600150.SH）盘中观察级量化分析系统。

本项目独立于 CNSV 日线系统。

本项目专门负责：

- 盘中数据处理
- 盘中特征工程
- 盘中训练集
- 盘中预测模型
- 盘中路径分布
- 盘中Replay回测
- 盘中Dashboard
- 盘中验收体系

本项目不负责：

- 自动交易
- 券商接口
- 自动下单
- 正式交易信号

所有正式交易决策最终由人工完成。

---

## 二、仓库边界

### CNSVdata

职责：

统一数据底座。

负责：

- 数据采集
- 数据清洗
- 数据质量检查
- Manifest
- Ready文件
- Replay快照
- 标签生成

禁止：

- 模型
- 预测
- 回测
- 信号

---

### CNSV

职责：

中国船舶日线波段系统。

负责：

- 日线预测
- 5D路径
- 10D路径
- 20D路径
- 波段决策辅助

---

### CNSVintraday

职责：

盘中线完整系统。

负责：

- 数据读取
- 特征工程
- 模型训练
- 概率预测
- 路径预测
- 回测验证
- Dashboard

---

## 三、总体架构

数据流：

CNSVdata
↓
CNSVintraday
↓
人工观察与决策

不允许：

CNSVintraday
↓
自动下单

---

## 四、核心原则

### 原则1

严格使用14:00快照。

禁止使用：

14:00之后任何数据。

---

### 原则2

禁止未来函数。

T+1数据只能用于Label。

禁止进入Feature。

---

### 原则3

所有模型必须Replay验证。

未经Replay验证：

禁止进入主流程。

---

### 原则4

任何预测均属于观察级结果。

不得描述为：

买入信号
卖出信号
交易指令

---

## 五、目录结构

src/cnsvintraday/

建议结构：

core/
data/
features/
models/
backtest/
dashboard/
validation/
utils/

---

## 六、V1阶段路线图

### V1.1

Data Connector

目标：

读取CNSVdata。

---

### V1.2

Feature Engine

目标：

构建盘中特征。

---

### V1.3

Baseline Models

目标：

建立基准模型体系。

包括：

B0
B1
B2
B3

---

### V1.4

Path Distribution

目标：

建立未来路径分布。

输出：

P10
P25
P50
P75
P90

---

### V1.5

Replay Backtest

目标：

验证过去150个交易日。

输出：

Coverage

Brier

RMSE

Hit Rate

---

### V1.6

Dashboard

目标：

自动生成盘中分析看板。

---

## 七、第一优先级

Codex当前只允许开发：

V1.1 Data Connector

不得提前开发：

V1.3模型

V1.4路径预测

V1.5回测

先打通数据链路。

再开发模型。

避免未来返工。

---

## 八、验收标准

V1.1验收通过条件：

1.
能够读取ready文件

2.
能够识别PASS/WARN/FAIL

3.
能够读取14:00快照

4.
能够形成统一DataContext

5.
能够通过自动测试

满足以上条件后：

进入V1.2 Feature Engine开发。

未通过验收：

禁止进入下一阶段。
