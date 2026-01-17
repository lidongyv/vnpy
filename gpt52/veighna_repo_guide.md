# VeighNa Repo 使用与核心算子说明

下面是基于当前 repo 内容整理的一份文档式说明，覆盖安装/使用、工程结构与模块解析，以及核心量化交易算子的用法与工作原理。

---

## 安装与运行（Windows 为主）

### 推荐方式：VeighNa Studio
官方建议使用 VeighNa Studio（含 Python + VeighNa + Station）。安装步骤详见 `docs/community/install/windows_install.md`。核心要点：
- 适配 Windows 10/11 / Server 2019
- 内置 Python 与依赖，适合入门和快速部署

### 手动安装（源码 + install.bat）
按 README 的说明下载 Release 包解压，进入目录执行：
```
install.bat
```
该脚本会安装核心依赖与 vnpy 本体。

### 启动 Trader（图形化或脚本）
- 图形化：VeighNa Station → VeighNa Trader
- 脚本：可直接写 `run.py` 启动（示例在 README）

---

## 工程结构与模块全览（repo 级别）

顶层核心目录：
- `vnpy/alpha`：AI/多因子研究与训练/回测
- `vnpy/trader`：主交易框架与数据结构
- `vnpy/event`：事件驱动引擎
- `vnpy/rpc`：跨进程通信
- `vnpy/chart`：高性能 K 线图表
- `docs/`：官方文档源
- `examples/`：脚本、回测、研究 Notebook 示例

### 1) `vnpy.trader`（主交易框架）
核心职责：交易对象模型、事件分发、交易引擎、网关抽象、UI。

- `MainEngine` 是系统核心，聚合网关、应用、OMS、日志、邮件等
- `BaseGateway` 是所有交易接口适配层的抽象基类
- 基础交易对象模型：`TickData / BarData / OrderData / TradeData / PositionData` 等
- 事件系统联动 `vnpy.event`

典型使用流程：
1. `MainEngine` 初始化事件引擎
2. 添加 Gateway（如 CTP）和 App（如 CTA）
3. `BaseGateway` 推送 `Tick/Order/Trade` → 事件引擎
4. OMS/策略模块消费事件进行交易决策

### 2) `vnpy.event`（事件驱动核心）
系统运行主干，通过事件队列分发各类交易/行情事件。
- 支持定时事件，便于做轮询任务/监控

### 3) `vnpy.alpha`（多因子/AI 研究与交易）
用途：数据管理 → 特征计算 → 模型训练 → 信号生成 → 策略回测

核心组件：
- `AlphaLab`：管理数据/模型/信号的存取与路径
- `AlphaDataset`：因子表达式计算与数据集构建
- `AlphaModel`：模型训练接口（Lasso / LightGBM / MLP）
- `AlphaStrategy`：策略模板（回测引擎驱动）

### 4) `vnpy.chart`
提供 K 线、指标绘制的图表组件，用于 UI 展示与回测可视化。

### 5) `vnpy.rpc`
RPC 客户端/服务端，便于多进程部署或分布式交易系统。

### 6) `docs` 与 `examples`
- `docs/community` 提供安装、应用、网关等文档
- `examples` 提供策略回测、数据下载、alpha research 等 demo
  - `examples/alpha_research`：完整机器学习因子实验
  - `examples/cta_backtesting`：CTA 回测
  - `examples/veighna_trader`：运行 Trader

---

## 核心量化交易算子（重点）

在本 repo 里，“核心算子”主要有两类：

### A) Alpha 因子表达式算子（主推荐）
用于构造多因子/特征的算子引擎，基于 DataProxy + expression eval 实现。

**入口：** `vnpy/alpha/dataset/utility.py` 中 `calculate_by_expression`

#### 1. DataProxy（表达式计算核心）
- 每个字段包装成 `DataProxy`，支持运算符重载
- 表达式会在本地变量空间里 `eval`

#### 2. 时序算子（ts_*)
位置：`vnpy/alpha/dataset/ts_function.py`

常用函数：
- `ts_delay` 滞后
- `ts_mean / ts_std / ts_sum / ts_rank` 滚动均值/标准差/求和/排名
- `ts_corr / ts_cov` 滚动相关/协方差
- `ts_slope / ts_rsquare / ts_resi` 滚动回归斜率、R²、残差
- `ts_decay_linear` 线性衰减加权

原理：
- 基于 polars 的 rolling + over("vt_symbol")
- 以合约为分组做滚动时序统计
- 适合单品种时序特征

#### 3. 截面算子（cs_*)
位置：`vnpy/alpha/dataset/cs_function.py`

- `cs_rank / cs_mean / cs_std / cs_sum / cs_scale`
- 按交易日（datetime）聚合做横截面处理

#### 4. 数学算子（math）
位置：`vnpy/alpha/dataset/math_function.py`

- `less / greater`
- `log / abs / sign`
- 条件算子 `quesval / quesval2`（类似 if-else）
- 安全幂 `pow1 / pow2`（处理负数与 NaN）

#### 5. 技术指标算子（ta_*)
位置：`vnpy/alpha/dataset/ta_function.py`

- `ta_rsi`
- `ta_atr`
依赖 TA-Lib

---

### B) Trader 技术指标与 K 线算子（策略实时计算）
位置：`vnpy/trader/utility.py`

#### 1) `BarGenerator`：Tick → Bar / 多周期合成
- Tick 合成 1min
- 1min 合成 5/15/60min 或日线
- 常用于 CTA 实盘策略里构造 K 线序列

#### 2) `ArrayManager`：指标计算容器
封装 TA-Lib 指标，常用于 CTA 策略中：
- 均线类：`sma, ema, wma, kama`
- 震荡类：`rsi, macd, cci`
- 波动类：`atr, std`
- 通道类：`boll, donchian, keltner`

---

## 核心算子使用方式（Alpha表达式）

在 `AlphaDataset.add_feature` 里可以直接写表达式，例如：

```
(-1) * ts_corr(cs_rank(ts_delta(log(volume), 2)), cs_rank((close - open) / open), 6)
```

用法范式：
```
(表达式) = 运算符/算子 + 字段 + 常数
```
字段来自原始数据列：`open, high, low, close, volume, vwap` 等。

表达式运行流程：
1. `calculate_by_expression` 将每列封装成 `DataProxy`
2. 执行表达式 `eval`
3. 输出新的特征列

---

## 用例建议与学习路径

1. **新手/实盘流程**
- 先用 Station 启动 Trader，配置 CTP 仿真
- 熟悉行情订阅、下单、持仓
- 使用 `examples/veighna_trader` 作为启动模板

2. **CTA 策略开发**
- 使用 `ArrayManager` + `BarGenerator`
- 关注 `cta_strategy` 应用模块（在独立仓库）

3. **AI 多因子路线**
- 参考 `examples/alpha_research` 的 notebook
- 从 `AlphaDataset → AlphaModel → AlphaStrategy` 走完整链路

---

## 可继续深入的关键文件

- `vnpy/alpha/dataset/utility.py`：表达式引擎
- `vnpy/alpha/dataset/ts_function.py`：时序算子
- `vnpy/alpha/dataset/cs_function.py`：截面算子
- `vnpy/alpha/dataset/math_function.py`：数学算子
- `vnpy/alpha/strategy/template.py`：策略模板
- `vnpy/trader/engine.py`：系统核心引擎
- `vnpy/trader/utility.py`：K 线合成与指标
