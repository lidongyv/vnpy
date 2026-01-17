# VeighNa (vnpy) 量化交易系统完整指南

> 版本: 4.3.0  
> 许可证: MIT  
> Python: 3.10+ (推荐 3.13)

---

## 目录

1. [项目概述](#1-项目概述)
2. [安装指南](#2-安装指南)
3. [项目架构](#3-项目架构)
4. [核心模块详解](#4-核心模块详解)
5. [Alpha量化投研模块](#5-alpha量化投研模块)
6. [量化交易算子详解](#6-量化交易算子详解)
7. [快速入门示例](#7-快速入门示例)
8. [API参考](#8-api参考)

---

## 1. 项目概述

VeighNa是一套基于Python的开源量化交易系统开发框架，提供**一站式多因子机器学习（ML）策略开发、投研和实盘交易解决方案**。

### 1.1 核心特性

| 模块 | 功能描述 |
|------|----------|
| **trader** | 多功能量化交易平台，整合多种交易接口 |
| **alpha** | AI量化策略模块，支持因子特征工程和ML模型 |
| **event** | 事件驱动引擎，作为事件驱动型交易程序的核心 |
| **rpc** | 跨进程通讯组件，用于分布式部署 |
| **chart** | Python高性能K线图表 |

### 1.2 支持的市场

- **国内市场**: CTP期货、ETF期权、A股证券、黄金TD等
- **海外市场**: Interactive Brokers、海外期货
- **数据服务**: RQData、迅投研、TuShare、Wind、iFinD等

---

## 2. 安装指南

### 2.1 系统要求

- **操作系统**: Windows 11+ / Windows Server 2022+ / Ubuntu 22.04 LTS+ / macOS
- **Python版本**: 3.10+ (64位)，推荐 Python 3.13

### 2.2 依赖包

```
核心依赖:
- PySide6==6.8.2.1     # GUI框架
- pyqtgraph>=0.13.7    # 图表绘制
- numpy>=2.2.3         # 数值计算
- pandas>=2.2.3        # 数据处理
- ta-lib>=0.6.4        # 技术分析
- pyzmq>=26.3.0        # 网络通信
- plotly>=6.0.0        # 交互式图表
- loguru>=0.7.3        # 日志系统

Alpha模块扩展依赖 (可选):
- polars>=1.26.0       # 高性能DataFrame
- scipy>=1.15.2        # 科学计算
- scikit-learn>=1.6.1  # 机器学习
- lightgbm>=4.6.0      # 梯度提升树
- torch>=2.6.0         # 深度学习
```

### 2.3 安装步骤

**Windows系统:**
```batch
# 下载Release版本后运行
install.bat
```

**Ubuntu/Linux:**
```bash
bash install.sh
```

**macOS:**
```bash
bash install_osx.sh
```

**手动安装:**
```bash
# 升级pip和wheel
pip install --upgrade pip wheel

# 安装TA-Lib (预编译版本)
pip install --extra-index-url https://pypi.vnpy.com ta_lib==0.6.4

# 安装VeighNa核心
pip install .

# 安装Alpha模块扩展 (可选)
pip install ".[alpha]"
```

### 2.4 推荐方式

使用官方Python发行版 **VeighNa Studio-4.3.0**，已集成VeighNa框架和VeighNa Station量化管理平台。

---

## 3. 项目架构

```
vnpy/
├── __init__.py          # 版本信息
├── alpha/               # AI量化投研模块 ⭐
│   ├── dataset/         # 因子特征工程
│   │   ├── datasets/    # 预定义特征集
│   │   │   ├── alpha_101.py   # WorldQuant 101因子
│   │   │   └── alpha_158.py   # Qlib 158因子
│   │   ├── cs_function.py     # 截面算子
│   │   ├── ts_function.py     # 时序算子
│   │   ├── math_function.py   # 数学算子
│   │   ├── ta_function.py     # 技术分析算子
│   │   ├── processor.py       # 数据预处理器
│   │   └── template.py        # AlphaDataset模板
│   ├── model/           # 预测模型
│   │   └── models/
│   │       ├── lasso_model.py   # Lasso回归
│   │       ├── lgb_model.py     # LightGBM
│   │       └── mlp_model.py     # 多层感知机
│   ├── strategy/        # 策略模块
│   │   ├── template.py          # AlphaStrategy模板
│   │   └── backtesting.py       # 回测引擎
│   ├── lab.py           # 投研流程管理器
│   └── logger.py        # 日志系统
├── trader/              # 交易核心模块
│   ├── engine.py        # 主引擎
│   ├── gateway.py       # 交易网关基类
│   ├── object.py        # 数据对象定义
│   ├── constant.py      # 常量定义
│   ├── database.py      # 数据库接口
│   ├── datafeed.py      # 数据源接口
│   └── ui/              # 用户界面
├── event/               # 事件驱动引擎
│   └── engine.py        # EventEngine实现
├── chart/               # K线图表模块
└── rpc/                 # RPC通信模块
```

---

## 4. 核心模块详解

### 4.1 事件驱动引擎 (EventEngine)

VeighNa采用事件驱动架构，`EventEngine`是整个系统的核心。

```python
from vnpy.event import EventEngine, Event

# 创建事件引擎
engine = EventEngine(interval=1)  # 每1秒产生定时器事件

# 注册事件处理器
def on_tick(event: Event):
    tick = event.data
    print(f"收到行情: {tick.vt_symbol} @ {tick.last_price}")

engine.register("eTick", on_tick)

# 启动引擎
engine.start()

# 发送事件
event = Event(type="eTick", data=tick_data)
engine.put(event)
```

**事件类型:**
- `EVENT_TICK`: 行情推送
- `EVENT_ORDER`: 委托更新
- `EVENT_TRADE`: 成交推送
- `EVENT_POSITION`: 持仓更新
- `EVENT_ACCOUNT`: 账户更新
- `EVENT_LOG`: 日志事件

### 4.2 主引擎 (MainEngine)

`MainEngine`是交易平台的核心控制器，负责管理网关、引擎和应用模块。

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# 创建应用
qapp = create_qapp()

# 创建事件引擎和主引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 添加交易网关
from vnpy_ctp import CtpGateway
main_engine.add_gateway(CtpGateway)

# 添加应用模块
from vnpy_ctastrategy import CtaStrategyApp
main_engine.add_app(CtaStrategyApp)

# 创建主窗口
main_window = MainWindow(main_engine, event_engine)
main_window.showMaximized()

qapp.exec()
```

### 4.3 数据对象 (Object)

系统定义了标准化的数据对象:

| 类名 | 描述 | 关键字段 |
|------|------|----------|
| `TickData` | Tick行情数据 | symbol, last_price, volume, bid/ask价格 |
| `BarData` | K线数据 | datetime, open/high/low/close, volume |
| `OrderData` | 委托订单 | direction, offset, price, volume, status |
| `TradeData` | 成交记录 | price, volume, direction, offset |
| `PositionData` | 持仓数据 | direction, volume, frozen, pnl |
| `AccountData` | 账户数据 | balance, available, frozen |
| `ContractData` | 合约信息 | size, pricetick, min_volume |

---

## 5. Alpha量化投研模块

### 5.1 AlphaLab - 投研实验室

`AlphaLab`是量化投研的核心管理器，提供完整的数据和模型生命周期管理。

```python
from vnpy.alpha import AlphaLab

# 创建实验室
lab = AlphaLab("./lab/my_strategy")

# 目录结构自动创建:
# ./lab/my_strategy/
# ├── daily/        # 日线数据 (parquet格式)
# ├── minute/       # 分钟数据
# ├── component/    # 指数成分股数据
# ├── dataset/      # 数据集缓存 (.pkl)
# ├── model/        # 训练模型 (.pkl)
# ├── signal/       # 预测信号 (.parquet)
# └── contract.json # 合约配置
```

**核心方法:**

| 方法 | 功能 |
|------|------|
| `save_bar_data(bars)` | 保存K线数据 |
| `load_bar_data(symbol, interval, start, end)` | 加载K线数据 |
| `load_bar_df(symbols, interval, start, end, extended_days)` | 批量加载为DataFrame |
| `save_component_data(index, components)` | 保存指数成分股 |
| `load_component_symbols(index, start, end)` | 获取成分股列表 |
| `save_dataset(name, dataset)` | 保存数据集 |
| `load_dataset(name)` | 加载数据集 |
| `save_model(name, model)` | 保存模型 |
| `load_model(name)` | 加载模型 |
| `save_signal(name, signal)` | 保存信号 |
| `load_signal(name)` | 加载信号 |

### 5.2 AlphaDataset - 数据集管理

```python
from vnpy.alpha.dataset import AlphaDataset, process_drop_na, process_fill_na
from functools import partial

# 创建数据集
dataset = AlphaDataset(
    df=price_df,                            # 价格数据DataFrame
    train_period=("2018-01-01", "2020-12-31"),
    valid_period=("2021-01-01", "2021-12-31"),
    test_period=("2022-01-01", "2023-12-31")
)

# 添加因子特征 (表达式方式)
dataset.add_feature("momentum_5", "close / ts_delay(close, 5) - 1")
dataset.add_feature("vol_ratio", "volume / ts_mean(volume, 20)")

# 添加因子特征 (Polars表达式)
import polars as pl
dataset.add_feature("high_low_range", 
    pl.col("high") / pl.col("low") - 1)

# 设置标签 (预测未来收益)
dataset.set_label("ts_delay(close, -3) / ts_delay(close, -1) - 1")

# 添加数据预处理器
dataset.add_processor("learn", partial(process_drop_na, names=["label"]))
dataset.add_processor("infer", partial(process_fill_na, fill_value=0))

# 计算特征
dataset.prepare_data(filters=component_filters, max_workers=4)
dataset.process_data()

# 获取数据
from vnpy.alpha import Segment
train_df = dataset.fetch_learn(Segment.TRAIN)
test_df = dataset.fetch_infer(Segment.TEST)
```

### 5.3 预定义特征集

#### Alpha 158 (来自Qlib)

包含158个量化因子，覆盖:
- **K线形态**: kmid, klen, kup, klow, ksft
- **价格变化**: open_0, high_0, low_0, vwap_0
- **动量因子**: roc_5/10/20/30/60
- **均线因子**: ma_5/10/20/30/60
- **波动因子**: std_5/10/20/30/60
- **趋势因子**: beta_5/10/20/30/60, rsqr_5/10/20/30/60
- **极值因子**: max_5/10/20/30/60, min_5/10/20/30/60
- **量价因子**: corr_5/10/20/30/60, vma_5/10/20/30/60

```python
from vnpy.alpha.dataset.datasets.alpha_158 import Alpha158

dataset = Alpha158(
    df, 
    train_period, 
    valid_period, 
    test_period
)
```

#### Alpha 101 (来自WorldQuant)

包含101个复杂因子表达式，如:

```python
# Alpha1: 条件波动率排名
"cs_rank(ts_argmax(pow1(quesval(0, returns, close, ts_std(returns, 20)), 2.0), 5)) - 0.5"

# Alpha12: 量价背离
"sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1))"

# Alpha41: VWAP与成交量的关系
"pow1((high * low), 0.5) - vwap"
```

### 5.4 机器学习模型

#### Lasso回归模型

```python
from vnpy.alpha.model.models.lasso_model import LassoModel

model = LassoModel(
    alpha=0.0005,        # L1正则化系数
    max_iter=1000,       # 最大迭代次数
    random_state=42      # 随机种子
)

# 训练
model.fit(dataset)

# 预测
predictions = model.predict(dataset, Segment.TEST)

# 查看特征重要性
model.detail()
```

#### LightGBM模型

```python
from vnpy.alpha.model.models.lgb_model import LgbModel

model = LgbModel(
    learning_rate=0.1,
    num_leaves=31,
    num_boost_round=1000,
    early_stopping_rounds=50,
    seed=42
)

model.fit(dataset)
predictions = model.predict(dataset, Segment.TEST)

# 显示特征重要性图表
model.detail()
```

#### MLP神经网络模型

```python
from vnpy.alpha.model.models.mlp_model import MlpModel

model = MlpModel(
    input_size=158,           # 输入特征维度
    hidden_sizes=(256, 128),  # 隐藏层结构
    lr=0.001,                 # 学习率
    n_epochs=300,             # 训练轮次
    batch_size=2000,          # 批次大小
    early_stop_rounds=50,     # 早停轮数
    optimizer="adam",         # 优化器
    device="cuda"             # 训练设备
)

model.fit(dataset)
predictions = model.predict(dataset, Segment.TEST)
```

---

## 6. 量化交易算子详解

### 6.1 时序算子 (ts_function)

时序算子在单个标的的时间维度上进行计算。

| 算子 | 语法 | 功能描述 |
|------|------|----------|
| `ts_delay` | `ts_delay(feature, n)` | 获取n期前的值 |
| `ts_delta` | `ts_delta(feature, n)` | 当前值与n期前的差 |
| `ts_min` | `ts_min(feature, n)` | n期滚动最小值 |
| `ts_max` | `ts_max(feature, n)` | n期滚动最大值 |
| `ts_argmin` | `ts_argmin(feature, n)` | 最小值所在位置 |
| `ts_argmax` | `ts_argmax(feature, n)` | 最大值所在位置 |
| `ts_sum` | `ts_sum(feature, n)` | n期滚动求和 |
| `ts_mean` | `ts_mean(feature, n)` | n期滚动均值 |
| `ts_std` | `ts_std(feature, n)` | n期滚动标准差 |
| `ts_rank` | `ts_rank(feature, n)` | 当前值在n期内的百分位排名 |
| `ts_corr` | `ts_corr(f1, f2, n)` | n期滚动相关系数 |
| `ts_cov` | `ts_cov(f1, f2, n)` | n期滚动协方差 |
| `ts_slope` | `ts_slope(feature, n)` | n期线性回归斜率 |
| `ts_rsquare` | `ts_rsquare(feature, n)` | n期线性回归R² |
| `ts_resi` | `ts_resi(feature, n)` | n期线性回归残差 |
| `ts_quantile` | `ts_quantile(feature, n, q)` | n期滚动分位数 |
| `ts_decay_linear` | `ts_decay_linear(feature, n)` | 线性衰减加权平均 |
| `ts_product` | `ts_product(feature, n)` | n期滚动乘积 |

**示例:**

```python
# 5日动量因子
"close / ts_delay(close, 5) - 1"

# 20日波动率
"ts_std(close / ts_delay(close, 1) - 1, 20)"

# RSV指标 (随机指标)
"(close - ts_min(low, 9)) / (ts_max(high, 9) - ts_min(low, 9) + 1e-12)"

# 量价相关性
"ts_corr(close, ts_log(volume + 1), 20)"
```

### 6.2 截面算子 (cs_function)

截面算子在同一时间点对不同标的进行计算。

| 算子 | 语法 | 功能描述 |
|------|------|----------|
| `cs_rank` | `cs_rank(feature)` | 截面排名 |
| `cs_mean` | `cs_mean(feature)` | 截面均值 |
| `cs_std` | `cs_std(feature)` | 截面标准差 |
| `cs_sum` | `cs_sum(feature)` | 截面求和 |
| `cs_scale` | `cs_scale(feature)` | 截面标准化 (除以绝对值之和) |

**示例:**

```python
# 收益率的截面排名
"cs_rank(close / ts_delay(close, 1) - 1)"

# 相对强弱指标
"(close - cs_mean(close)) / cs_std(close)"

# 市值中性化的动量
"cs_scale(close / ts_delay(close, 20) - 1)"
```

### 6.3 数学算子 (math_function)

| 算子 | 语法 | 功能描述 |
|------|------|----------|
| `log` | `log(feature)` | 自然对数 |
| `abs` | `abs(feature)` | 绝对值 |
| `sign` | `sign(feature)` | 符号函数 (-1, 0, 1) |
| `less` | `less(f1, f2)` | 取较小值 |
| `greater` | `greater(f1, f2)` | 取较大值 |
| `pow1` | `pow1(base, exp)` | 安全幂运算 (支持负底数) |
| `pow2` | `pow2(base, exp)` | 两个DataProxy的幂运算 |
| `quesval` | `quesval(thresh, f1, f2, f3)` | 条件选择: if thresh < f1 then f2 else f3 |
| `quesval2` | `quesval2(f0, f1, f2, f3)` | 条件选择: if f0 < f1 then f2 else f3 |

**示例:**

```python
# 收益率对数
"ts_log(close / ts_delay(close, 1))"

# 条件因子: 如果趋势向上则取动量，否则取波动率
"quesval(0, ts_slope(close, 20), close / ts_delay(close, 5), ts_std(close, 20))"
```

### 6.4 技术分析算子 (ta_function)

基于TA-Lib实现的技术指标:

| 算子 | 语法 | 功能描述 |
|------|------|----------|
| `ta_rsi` | `ta_rsi(close, n)` | RSI相对强弱指标 |
| `ta_atr` | `ta_atr(high, low, close, n)` | ATR真实波动幅度 |

**示例:**

```python
# 14日RSI
"ta_rsi(close, 14)"

# 14日ATR
"ta_atr(high, low, close, 14)"
```

### 6.5 AlphaGPT算子 (alphagpt_ops)

从AlphaGPT项目移植的高级量化算子，特别适合加密货币和高波动市场：

#### 基础运算算子

| 算子 | 语法 | 功能描述 |
|------|------|----------|
| `gpt_gate` | `gpt_gate(cond, x, y)` | 条件选择: cond>0返回x，否则返回y |
| `gpt_jump` | `gpt_jump(feature, threshold)` | 跳跃检测: 超过阈值的Z-Score |
| `gpt_decay` | `gpt_decay(feature)` | 指数衰减加权 [1.0, 0.8, 0.6] |
| `gpt_max_n` | `gpt_max_n(feature, n)` | N期滚动最大值 |

#### 市场因子算子

| 算子 | 语法 | 功能描述 | 返回范围 |
|------|------|----------|----------|
| `gpt_buy_sell_imbalance` | `gpt_buy_sell_imbalance(close, open, high, low)` | 买卖失衡度 | [-1, 1] |
| `gpt_fomo_acceleration` | `gpt_fomo_acceleration(volume, window)` | FOMO加速度 | [-5, 5] |
| `gpt_pump_deviation` | `gpt_pump_deviation(close, window)` | 价格偏离均线 | 无限制 |
| `gpt_volatility_clustering` | `gpt_volatility_clustering(close, window)` | 波动率聚类 | ≥0 |
| `gpt_momentum_reversal` | `gpt_momentum_reversal(close, window)` | 动量反转信号 | {0, 1} |
| `gpt_relative_strength` | `gpt_relative_strength(close, high, low, window)` | 相对强度(RSI变体) | [-1, 1] |

#### 数据预处理算子

| 算子 | 语法 | 功能描述 |
|------|------|----------|
| `gpt_robust_norm` | `gpt_robust_norm(feature, clip)` | 稳健标准化(基于MAD) |
| `gpt_cs_robust_norm` | `gpt_cs_robust_norm(feature, clip)` | 截面稳健标准化 |
| `gpt_log_return` | `gpt_log_return(close)` | 对数收益率 |
| `gpt_vol_shock` | `gpt_vol_shock(volume, window)` | 成交量冲击(相对均值倍数) |
| `gpt_trend` | `gpt_trend(close, window)` | 趋势方向 {-1, 1} |
| `gpt_close_position` | `gpt_close_position(close, high, low)` | 收盘价在振幅中的位置 [0, 1] |
| `gpt_high_low_range` | `gpt_high_low_range(high, low, close)` | 高低振幅比 |
| `gpt_volume_trend` | `gpt_volume_trend(volume)` | 成交量变化趋势 |

**AlphaGPT算子示例:**

```python
# FOMO加速度因子
"gpt_fomo_acceleration(volume, 5)"

# 买卖失衡因子
"gpt_buy_sell_imbalance(close, open, high, low)"

# 波动率聚类因子
"gpt_volatility_clustering(close, 10)"

# 动量反转信号
"gpt_momentum_reversal(close, 5)"

# 相对强度(改进RSI)
"gpt_relative_strength(close, high, low, 14)"

# 稳健标准化的收益率
"gpt_robust_norm(close / ts_delay(close, 1) - 1, 5.0)"

# 条件因子: 趋势向上用动量，否则用均值回归
"gpt_gate(gpt_trend(close, 60), ts_mean(close, 5) / ts_mean(close, 20), gpt_pump_deviation(close, 20) * -1)"

# 组合因子
"cs_rank(gpt_fomo_acceleration(volume, 5)) * gpt_momentum_reversal(close, 5)"
```

### 6.5 数据预处理器

| 处理器 | 功能描述 |
|--------|----------|
| `process_drop_na` | 删除指定列的缺失值行 |
| `process_fill_na` | 用指定值填充缺失值 |
| `process_cs_norm` | 截面标准化 (zscore或robust) |
| `process_robust_zscore_norm` | 稳健Z-Score标准化 |
| `process_cs_rank_norm` | 截面排名标准化 |

```python
from vnpy.alpha.dataset import (
    process_drop_na,
    process_fill_na,
    process_cs_norm,
    process_robust_zscore_norm
)

# 删除标签缺失的样本
dataset.add_processor("learn", partial(process_drop_na, names=["label"]))

# 截面标准化特征
dataset.add_processor("learn", partial(
    process_cs_norm, 
    names=feature_names, 
    method="zscore"  # 或 "robust"
))

# 填充预测数据的缺失值
dataset.add_processor("infer", partial(process_fill_na, fill_value=0))
```

---

## 7. 快速入门示例

### 7.1 完整的量化投研流程

```python
# ===================
# 步骤1: 准备数据
# ===================
from vnpy.alpha import AlphaLab
from vnpy.trader.constant import Interval

lab = AlphaLab("./lab/demo")

# 配置参数
index_symbol = "000300.SSE"    # 沪深300
start = "2018-01-01"
end = "2023-12-31"
interval = Interval.DAILY

# 加载成分股代码
component_symbols = lab.load_component_symbols(index_symbol, start, end)

# 加载价格数据
import polars as pl
df: pl.DataFrame = lab.load_bar_df(
    component_symbols, 
    interval, 
    start, 
    end, 
    extended_days=100  # 额外加载100天用于特征计算
)

# ===================
# 步骤2: 特征工程
# ===================
from vnpy.alpha.dataset.datasets.alpha_158 import Alpha158
from vnpy.alpha.dataset import process_drop_na, process_fill_na
from functools import partial

# 创建数据集
dataset = Alpha158(
    df,
    train_period=("2018-01-01", "2020-12-31"),
    valid_period=("2021-01-01", "2021-12-31"),
    test_period=("2022-01-01", "2023-12-31")
)

# 添加预处理器
dataset.add_processor("learn", partial(process_drop_na, names=["label"]))
dataset.add_processor("infer", partial(process_fill_na, fill_value=0))

# 准备数据
filters = lab.load_component_filters(index_symbol, start, end)
dataset.prepare_data(filters=filters, max_workers=4)
dataset.process_data()

# 保存数据集
lab.save_dataset("demo_dataset", dataset)

# ===================
# 步骤3: 模型训练
# ===================
from vnpy.alpha.model.models.lgb_model import LgbModel

model = LgbModel(
    learning_rate=0.05,
    num_leaves=31,
    num_boost_round=500,
    early_stopping_rounds=30
)

model.fit(dataset)
lab.save_model("demo_model", model)

# ===================
# 步骤4: 生成信号
# ===================
import numpy as np
from vnpy.alpha import Segment

# 预测
predictions = model.predict(dataset, Segment.TEST)

# 构建信号DataFrame
df_test = dataset.fetch_infer(Segment.TEST)
signal = df_test.with_columns(
    pl.Series(predictions).alias("signal")
).select(["datetime", "vt_symbol", "signal"])

lab.save_signal("demo_signal", signal)

# ===================
# 步骤5: 策略回测
# ===================
from datetime import datetime
from vnpy.alpha.strategy import BacktestingEngine
from vnpy.alpha.strategy.strategies.equity_demo_strategy import EquityDemoStrategy

# 创建回测引擎
engine = BacktestingEngine(lab)

engine.set_parameters(
    vt_symbols=component_symbols,
    interval=Interval.DAILY,
    start=datetime(2022, 1, 1),
    end=datetime(2023, 12, 31),
    capital=10_000_000  # 1000万初始资金
)

# 添加策略
engine.add_strategy(
    EquityDemoStrategy, 
    setting={"top_k": 30, "n_drop": 3},
    signal_df=signal
)

# 执行回测
engine.load_data()
engine.run_backtesting()
engine.calculate_result()
engine.calculate_statistics()
engine.show_chart()
```

### 7.2 自定义策略开发

```python
from collections import defaultdict
import polars as pl
from vnpy.trader.object import BarData, TradeData
from vnpy.trader.constant import Direction
from vnpy.alpha import AlphaStrategy

class MyStrategy(AlphaStrategy):
    """自定义策略示例"""
    
    # 策略参数
    top_k: int = 30              # 持仓股票数量
    rebalance_days: int = 5      # 调仓周期
    price_add: float = 0.02      # 价格调整比例

    def on_init(self) -> None:
        """初始化"""
        self.day_count = 0
        self.write_log("策略初始化完成")

    def on_trade(self, trade: TradeData) -> None:
        """成交回调"""
        self.write_log(f"成交: {trade.vt_symbol} {trade.direction.value} "
                      f"价格:{trade.price} 数量:{trade.volume}")

    def on_bars(self, bars: dict[str, BarData]) -> None:
        """K线推送回调"""
        self.day_count += 1
        
        # 非调仓日跳过
        if self.day_count % self.rebalance_days != 0:
            return
        
        # 获取信号
        signal_df = self.get_signal()
        if signal_df.is_empty():
            return
        
        # 按信号排序
        signal_df = signal_df.sort("signal", descending=True)
        
        # 选取top_k股票
        target_symbols = list(signal_df["vt_symbol"][:self.top_k])
        
        # 计算目标持仓
        portfolio_value = self.get_portfolio_value()
        target_value = portfolio_value * 0.95 / self.top_k
        
        # 设置目标仓位
        for vt_symbol in target_symbols:
            if vt_symbol in bars:
                price = bars[vt_symbol].close_price
                if price > 0:
                    target_volume = int(target_value / price / 100) * 100
                    self.set_target(vt_symbol, target_volume)
        
        # 清空非目标持仓
        for vt_symbol in self.pos_data:
            if vt_symbol not in target_symbols:
                self.set_target(vt_symbol, 0)
        
        # 执行交易
        self.execute_trading(bars, self.price_add)
```

### 7.3 实盘交易启动

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# 导入交易网关
from vnpy_ctp import CtpGateway

# 导入策略应用
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_portfoliostrategy import PortfolioStrategyApp

def main():
    # 创建Qt应用
    qapp = create_qapp()
    
    # 创建引擎
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    
    # 添加网关
    main_engine.add_gateway(CtpGateway)
    
    # 添加应用
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(PortfolioStrategyApp)
    
    # 创建窗口
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    
    qapp.exec()

if __name__ == "__main__":
    main()
```

---

## 8. API参考

### 8.1 AlphaLab API

```python
class AlphaLab:
    def __init__(self, lab_path: str) -> None
    
    # 数据管理
    def save_bar_data(self, bars: list[BarData]) -> None
    def load_bar_data(self, vt_symbol, interval, start, end) -> list[BarData]
    def load_bar_df(self, vt_symbols, interval, start, end, extended_days) -> pl.DataFrame
    
    # 成分股管理
    def save_component_data(self, index_symbol, index_components) -> None
    def load_component_data(self, index_symbol, start, end) -> dict[datetime, list[str]]
    def load_component_symbols(self, index_symbol, start, end) -> list[str]
    def load_component_filters(self, index_symbol, start, end) -> dict[str, list[tuple]]
    
    # 合约配置
    def add_contract_setting(self, vt_symbol, long_rate, short_rate, size, pricetick) -> None
    def load_contract_settings(self) -> dict
    
    # 数据集/模型/信号管理
    def save_dataset(self, name, dataset) -> None
    def load_dataset(self, name) -> AlphaDataset | None
    def save_model(self, name, model) -> None
    def load_model(self, name) -> AlphaModel | None
    def save_signal(self, name, signal) -> None
    def load_signal(self, name) -> pl.DataFrame | None
```

### 8.2 AlphaDataset API

```python
class AlphaDataset:
    def __init__(self, df, train_period, valid_period, test_period, process_type="append")
    
    def add_feature(self, name, expression=None, result=None) -> None
    def set_label(self, expression) -> None
    def add_processor(self, task, processor) -> None
    
    def prepare_data(self, filters=None, max_workers=None) -> None
    def process_data(self) -> None
    
    def fetch_raw(self, segment) -> pl.DataFrame
    def fetch_infer(self, segment) -> pl.DataFrame
    def fetch_learn(self, segment) -> pl.DataFrame
    
    def show_feature_performance(self, name) -> None
    def show_signal_performance(self, signal) -> None
```

### 8.3 AlphaModel API

```python
class AlphaModel(ABC):
    @abstractmethod
    def fit(self, dataset: AlphaDataset) -> None
    
    @abstractmethod
    def predict(self, dataset: AlphaDataset, segment: Segment) -> np.ndarray
    
    def detail(self) -> Any
```

### 8.4 AlphaStrategy API

```python
class AlphaStrategy(ABC):
    @abstractmethod
    def on_init(self) -> None
    
    @abstractmethod
    def on_bars(self, bars: dict[str, BarData]) -> None
    
    @abstractmethod
    def on_trade(self, trade: TradeData) -> None
    
    # 交易方法
    def buy(self, vt_symbol, price, volume) -> list[str]
    def sell(self, vt_symbol, price, volume) -> list[str]
    def short(self, vt_symbol, price, volume) -> list[str]
    def cover(self, vt_symbol, price, volume) -> list[str]
    def cancel_order(self, vt_orderid) -> None
    def cancel_all(self) -> None
    
    # 持仓管理
    def get_pos(self, vt_symbol) -> float
    def get_target(self, vt_symbol) -> float
    def set_target(self, vt_symbol, target) -> None
    def execute_trading(self, bars, price_add) -> None
    
    # 账户查询
    def get_cash_available(self) -> float
    def get_holding_value(self) -> float
    def get_portfolio_value(self) -> float
    def get_signal(self) -> pl.DataFrame
```

### 8.5 BacktestingEngine API

```python
class BacktestingEngine:
    def __init__(self, lab: AlphaLab) -> None
    
    def set_parameters(self, vt_symbols, interval, start, end, 
                       capital=1_000_000, risk_free=0, annual_days=240) -> None
    def add_strategy(self, strategy_class, setting, signal_df) -> None
    
    def load_data(self) -> None
    def run_backtesting(self) -> None
    def calculate_result(self) -> pl.DataFrame
    def calculate_statistics(self) -> dict
    
    def show_chart(self) -> None
    def show_performance(self, benchmark_symbol) -> None
    
    def get_all_trades(self) -> list[TradeData]
    def get_all_orders(self) -> list[OrderData]
```

---

## 总结

VeighNa是一个功能完善的Python量化交易框架，提供:

1. **事件驱动架构** - 高效的实时交易系统
2. **丰富的因子库** - 158+101个预定义量化因子
3. **灵活的表达式引擎** - 支持自定义因子计算
4. **多种ML模型** - Lasso、LightGBM、MLP开箱即用
5. **完整的回测系统** - 支持多标的组合策略
6. **可视化分析** - Plotly交互式图表
7. **模块化设计** - 易于扩展和二次开发

通过本文档，你可以快速上手vnpy进行量化策略研究和实盘交易。更多详细信息请参考[官方文档](https://www.vnpy.com/docs/cn/index.html)。
