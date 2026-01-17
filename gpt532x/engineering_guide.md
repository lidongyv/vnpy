# VeighNa/vn.py 工程解析与使用指南（基于本仓库源码）

本文档用于帮助你在本仓库中完成**安装、启动、实盘/回测使用**，并对工程模块与核心“量化算子（因子表达式引擎）”给出**使用方式与工作原理**说明。

> 说明：本文档内容来自对仓库源码与示例的阅读整理。外部网关与部分 App（如 `vnpy_ctp`、`vnpy_ctastrategy` 等）属于独立插件仓库，需另行安装。

---

## 1. 安装与启动（Windows）

### 1.1 安装方式A：VeighNa Studio（推荐新手）

- 官方一站式环境：VeighNa Studio + VeighNa Station（文档路径：`docs/community/install/windows_install.md`）。
- 优点：依赖、GUI 工具、常用组件基本一次装好，适合快速上手。

### 1.2 安装方式B：手动安装本仓库（源码安装）

#### 前置条件

- Python **3.10+ 64位**（见 `pyproject.toml`：`requires-python = ">=3.10"`）

#### 一键安装

在仓库根目录执行：

```bat
install.bat
```

该脚本会：

- 升级 pip/wheel
- 安装 `ta_lib==0.6.4`（通过额外索引源）
- `pip install .` 安装本仓库包 `vnpy`

#### 可选：安装 AI 量化（`vnpy.alpha`）额外依赖

本仓库在 `pyproject.toml` 中提供了可选依赖组 `alpha`。建议在仓库根目录执行：

```bash
pip install ".[alpha]"
```

---

## 2. 启动方式（Trader GUI / 无UI脚本）

### 2.1 启动 GUI Trader（加载网关 + App）

示例脚本：`examples/veighna_trader/run.py`

核心拼装模式：

- 创建 `EventEngine`
- 创建 `MainEngine`
- `main_engine.add_gateway(...)` 注册交易/行情网关
- `main_engine.add_app(...)` 注册应用（CTA、回测、数据管理等）
- 创建并显示 `MainWindow`

运行命令：

```bash
python examples/veighna_trader/run.py
```

### 2.2 无UI实盘守护（CTA示例）

示例脚本：`examples/no_ui/run.py`

特点：

- 父进程根据交易时段拉起/关闭子进程
- 子进程中创建引擎、连接网关、初始化并启动策略

适合：需要“无人值守”运行的 CTA 类策略部署形态参考。

---

## 3. 工程模块全景（建议阅读路径）

### 3.1 `vnpy/event`（事件引擎）

核心：`vnpy/event/engine.py`

- 事件队列与线程循环
- 按间隔产生 `EVENT_TIMER` 定时事件
- 支持按事件类型注册回调（handler）与通用回调（general handler）

### 3.2 `vnpy/trader`（交易核心框架）

关键模块：

- `vnpy/trader/engine.py`：`MainEngine`（平台中枢）与基础引擎（日志、OMS、邮件等）
- `vnpy/trader/gateway.py`：`BaseGateway`（网关抽象，定义连接、订阅、下单、撤单、查询等接口与回调约定）
- `vnpy/trader/object.py`：交易数据结构（Tick/Bar/Order/Trade/Position/Account/Contract/Request 等）
- `vnpy/trader/event.py`：交易事件类型常量（如 `EVENT_TICK`、`EVENT_ORDER` 等）
- `vnpy/trader/ui`：Qt UI（Trader 主窗口等）

### 3.3 `vnpy/alpha`（AI量化：因子/模型/策略/回测）

对外主要入口（见 `vnpy/alpha/__init__.py`）：

- `AlphaLab`：投研工作区与数据落盘（parquet、component、dataset、model、signal）
- `AlphaDataset`：特征工程（表达式因子引擎 + 数据处理流水线）
- `AlphaModel`：模型模板（`fit/predict`）
- `AlphaStrategy` + `BacktestingEngine`：信号驱动的组合策略模板与回测引擎

### 3.4 `vnpy/rpc` 与 `vnpy/chart`

- `vnpy/rpc`：跨进程通讯组件，适合分布式部署/多进程架构
- `vnpy/chart`：高性能 K 线与图表组件

---

## 4. 交易主链路（事件驱动架构）

### 4.1 核心链路

1) **网关（Gateway）** 从底层交易/行情 API 收到回调  
2) 网关将回调封装为 `vnpy.trader.object.*Data` 对象，并通过 `on_tick/on_order/on_trade/...` 推送事件  
3) **事件引擎（EventEngine）** 分发事件给已注册的处理器  
4) **主引擎（MainEngine）** 提供统一调用入口（connect/subscribe/send_order/query_history...）并挂载各类功能引擎与 App  
5) **应用/App/策略引擎** 订阅与处理事件，驱动交易逻辑

### 4.2 关键数据结构（策略/风控/撮合都围绕它们）

见 `vnpy/trader/object.py`：

- 行情：`TickData`、`BarData`
- 交易：`OrderData`、`TradeData`
- 账户/持仓：`AccountData`、`PositionData`
- 合约：`ContractData`
- 请求：`OrderRequest`、`CancelRequest`、`SubscribeRequest`、`HistoryRequest`、`QuoteRequest`

### 4.3 网关接口约定（实现自己的网关时必须遵守）

见 `vnpy/trader/gateway.py`：

- `connect(setting)`：连接并在必要时查询合约、资金、持仓、委托、成交并触发相应回调
- `subscribe(req)`：订阅行情
- `send_order(req)`：创建 `OrderData`，分配唯一 id，发送到服务器并推送 `on_order`
- `cancel_order(req)`：撤单

并通过 `on_tick/on_trade/on_order/on_position/on_account/on_contract` 将数据推送到事件引擎。

---

## 5. `vnpy.alpha` 投研/回测流水线（从数据到策略）

### 5.1 `AlphaLab`（投研工作区）

见 `vnpy/alpha/lab.py`，主要能力：

- `save_bar_data/load_bar_data`：保存/加载 K 线数据（parquet）
- component（指数成分）保存与过滤区间生成
- `save_dataset/load_dataset`（pkl）
- `save_model/load_model`（pkl）
- `save_signal/load_signal`（parquet）
- 合约交易配置（手续费、合约乘数、最小变动价位等）

### 5.2 `AlphaDataset`（因子特征工程与数据处理）

见 `vnpy/alpha/dataset/template.py`：

- `add_feature(name, expression=...)`：添加特征表达式（字符串或 Polars Expr）
- `set_label(expression)`：设置标签表达式（常用“未来收益率”）
- `prepare_data(...)`：并行计算所有表达式特征并合并成结果 DataFrame
- `process_data()`：按 processors 对数据做清洗/归一化等
- `fetch_raw/fetch_infer/fetch_learn(segment)`：按训练/验证/测试区间取数据

### 5.3 `AlphaModel`（模型模板）

见 `vnpy/alpha/model/template.py`：

- `fit(dataset)`
- `predict(dataset, segment)` -> `np.ndarray`

### 5.4 `AlphaStrategy` + `BacktestingEngine`（信号驱动回测）

见：

- `vnpy/alpha/strategy/template.py`
- `vnpy/alpha/strategy/backtesting.py`

核心概念：

- 策略维护 `pos_data`（实际持仓）与 `target_data`（目标持仓）
- 策略在 `on_bars` 中读取模型信号并设置目标仓位
- `execute_trading` 会根据目标与实际差额生成买/卖/开/平订单
- 回测引擎负责：
  - 加载历史 K 线
  - 撮合限价单（按 bar 的 high/low/open/涨跌停约束）
  - 逐日盯市计算（资金曲线、回撤、Sharpe 等）
  - 生成绩效图表

---

## 6. 核心量化算子（因子表达式引擎）：使用方式与工作原理

本仓库的“核心算子”集中于 `vnpy/alpha/dataset/*_function.py`，并通过表达式引擎注入到 `eval()` 的局部环境，实现“像写公式一样写因子”。

### 6.1 表达式引擎如何工作

实现位置：`vnpy/alpha/dataset/utility.py` -> `calculate_by_expression(df, expression)`

核心机制：

1) 输入 `df` 必须包含索引列：`datetime`、`vt_symbol`，以及表达式使用到的字段列（如 `open/high/low/close/volume/...`）  
2) 每个字段列会被包装为 `DataProxy`（统一命名为 `data` 列）  
3) 表达式字符串通过 `eval(expression, {}, locals)` 执行，返回 `DataProxy`  
4) 最终返回 `DataProxy.df`（`datetime/vt_symbol/data`）并作为新特征列合并回结果

> 注意：表达式里为了避免除 0，常见写法是加 `1e-12`（内置 Alpha158/Alpha101 中大量使用）。

### 6.2 `DataProxy` 的意义

`DataProxy` 是“特征数据代理”，实现了：

- `+ - * /` 等运算符重载
- `abs()` 与比较运算（比较结果会转成 0/1）

使得表达式可以写成数学公式的形式，且在内部保持 `datetime/vt_symbol` 对齐。

### 6.3 算子分类与清单（以表达式引擎注入为准）

#### A) 时间序列算子（`ts_*`，按 `vt_symbol` 分组滚动）

实现：`vnpy/alpha/dataset/ts_function.py`

- `ts_delay(x, n)`：取 n 期前值（`shift`），n 可为负（用于未来 label）
- `ts_min/ts_max(x, window)`：滚动最小/最大
- `ts_argmax/ts_argmin(x, window)`：窗口内最大/最小位置（从 1 开始计数）
- `ts_rank(x, window)`：窗口内当前值的百分位
- `ts_sum/ts_mean/ts_std(x, window)`：滚动和/均值/标准差（对 NaN 做兼容）
- `ts_slope(x, window)`：窗口线性回归斜率（做了常数预计算优化）
- `ts_quantile(x, window, q)`：滚动分位数
- `ts_rsquare(x, window)`：回归 \(R^2\)（会处理 inf/nan）
- `ts_resi(x, window)`：回归残差（最后一个点）
- `ts_corr(x, y, window)`：滚动相关系数
- `ts_delta(x, n)`：差分（`x - delay(x,n)`）
- `ts_cov(x, y, window)`：协方差（由 corr 与 std 推导）
- `ts_decay_linear(x, window)`：线性衰减加权均值
- `ts_product(x, window)`：滚动乘积
- `ts_less/ts_greater(x, y)`：逐点 min/max（支持 y 为常数）
- `ts_log/ts_abs(x)`：log/abs

#### B) 横截面算子（`cs_*`，按 `datetime` 分组）

实现：`vnpy/alpha/dataset/cs_function.py`

- `cs_rank(x)`：截面排序
- `cs_mean/cs_std/cs_sum(x)`：截面统计
- `cs_scale(x)`：按截面绝对值和缩放：\(x / \sum |x|\)（分母为 0 返回 0）

#### C) 技术指标算子（`ta_*`）

实现：`vnpy/alpha/dataset/ta_function.py`

- `ta_rsi(close, window)`：RSI（TA-Lib）
- `ta_atr(high, low, close, window)`：ATR（TA-Lib）

#### D) 数学/条件算子（`math_function.py`）

实现：`vnpy/alpha/dataset/math_function.py`

- `less/greater(x, y)`：逐点 min/max（与 ts_less/ts_greater 类似）
- `log/abs/sign(x)`：对数/绝对值/符号（-1/0/1）
- `quesval(threshold_const, cond, a, b)`：若 `threshold < cond` 取 `a` 否则取 `b`
- `quesval2(threshold_feature, cond, a, b)`：同上但 threshold 可为特征
- `pow1(base, exponent_float)`：安全幂（负数 base 做符号保持）
- `pow2(base, exponent_feature)`：仅当 exponent 为整数时允许负 base 幂，否则置 0/None（实现做了 NaN 防护）

---

## 7. 算子怎么用：两条最实用路径

### 7.1 直接用内置因子集（Alpha158/Alpha101）

实现：

- `vnpy/alpha/dataset/datasets/alpha_158.py`
- `vnpy/alpha/dataset/datasets/alpha_101.py`

特点：

- Alpha158：Qlib 风格的基础特征集合（K线形态/趋势/波动/量价等）
- Alpha101：WorldQuant 风格公式（大量嵌套，验证表达式引擎能力）

两者都设置了类似的未来收益 label（用于监督学习）。

### 7.2 自己写表达式因子（最灵活、最快落地）

你只需要保证输入 df 的列名匹配（`datetime`、`vt_symbol`、以及 open/high/low/close/volume 等），然后：

```python
import polars as pl
from vnpy.alpha.dataset.template import AlphaDataset
from vnpy.alpha.dataset.utility import Segment

# df: polars.DataFrame
# 必需列：datetime, vt_symbol, open, high, low, close, volume(以及你表达式中用到的列)
dataset = AlphaDataset(
    df=df,
    train_period=("2020-01-01", "2022-12-31"),
    valid_period=("2023-01-01", "2023-06-30"),
    test_period=("2023-07-01", "2023-12-31"),
)

dataset.add_feature(
    "my_factor",
    "cs_rank(ts_mean(close, 20) / close) - cs_rank(ts_std(close, 20) / close)"
)

# 常见未来收益标签（示例）
dataset.set_label("ts_delay(close, -3) / ts_delay(close, -1) - 1")

dataset.prepare_data(max_workers=8)
dataset.process_data()

train_df = dataset.fetch_learn(Segment.TRAIN)
```

---

## 8. 如何用本仓库做量化交易（落地建议）

### 8.1 传统事件驱动/CTA 实盘

走 `vnpy.trader`：

- 选择并安装合适的网关插件（例如 CTP：`vnpy_ctp`）
- 选择并安装策略引擎插件（例如 CTA：`vnpy_ctastrategy`）
- 参考 `examples/veighna_trader/run.py`（GUI）或 `examples/no_ui/run.py`（无UI守护）拼装启动

### 8.2 AI 多因子/机器学习

走 `vnpy.alpha`：

- 用 `AlphaLab` 管理数据与投研目录（parquet 数据、信号、模型）
- 用 `AlphaDataset` + 表达式算子批量生成训练集/验证集/测试集
- 用 `AlphaModel` 训练并预测得到信号
- 用 `BacktestingEngine` + `AlphaStrategy` 回测评估绩效（资金曲线、回撤、Sharpe、换手等）

---

## 9. 你下一步需要补充的信息（我可以据此给你一份“可直接跑通”的脚手架）

为了把“从数据→因子→模型→回测→实盘”整理成你可复制执行的最短路径，请告诉我：

- 你交易市场：A股/期货/期权/外盘？
- 数据频率：日线/分钟线/更高频？
- 你已有数据字段与格式（列名是否与 open/high/low/close/volume 一致）？
- 目标：先回测验证，还是直接接实盘？

