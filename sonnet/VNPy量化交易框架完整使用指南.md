# VNPy (VeighNa) 量化交易框架完整使用指南

> **版本**: 4.3.0  
> **作者**: VeighNa团队  
> **许可证**: MIT  
> **支持Python版本**: 3.10, 3.11, 3.12, 3.13 (推荐3.13)

---

## 目录

1. [项目概述](#1-项目概述)
2. [安装指南](#2-安装指南)
3. [架构解析](#3-架构解析)
4. [核心模块详解](#4-核心模块详解)
5. [AI量化模块 (vnpy.alpha)](#5-ai量化模块-vnpyalpha)
6. [量化交易算子详解](#6-量化交易算子详解)
7. [策略开发实战](#7-策略开发实战)
8. [数据管理](#8-数据管理)
9. [实盘交易](#9-实盘交易)
10. [常见问题](#10-常见问题)

---

## 1. 项目概述

### 1.1 VNPy是什么？

VeighNa (VNPy) 是一套基于Python的**开源量化交易系统开发框架**，提供从交易API对接到策略自动交易的完整量化解决方案。

**核心特点：**
- ✅ **多市场支持**：覆盖期货、股票、期权、外汇等多种金融市场
- ✅ **事件驱动架构**：高性能的异步事件处理引擎
- ✅ **丰富的策略引擎**：CTA策略、组合策略、价差套利、期权交易等
- ✅ **AI-Powered**：内置机器学习因子库和模型训练框架
- ✅ **开箱即用**：图形化界面，无需编写代码即可开始交易

### 1.2 适用场景

| 用户类型 | 应用场景 |
|---------|---------|
| **专业个人投资者** | 使用VeighNa Trader直连期货公司CTP柜台，实现CTA策略自动交易 |
| **创业型私募** | 基于RpcService构建服务器端统一报盘通道，多策略并行 |
| **券商资管部门** | 对接O32资管系统，开发复杂的多策略系统 |
| **量化研究员** | 利用Alpha模块进行因子挖掘和机器学习策略开发 |

### 1.3 技术栈

```python
# 核心依赖
- PySide6 (6.8.2.1)        # GUI界面
- pandas (>=2.2.3)         # 数据处理
- numpy (>=2.2.3)          # 数值计算
- ta-lib (>=0.6.4)         # 技术分析
- pyzmq (>=26.3.0)         # 跨进程通信

# AI量化模块额外依赖
- polars (>=1.26.0)        # 高性能数据处理
- scikit-learn (>=1.6.1)   # 机器学习
- lightgbm (>=4.6.0)       # 梯度提升树
- torch (>=2.6.0)          # 深度学习
```

---

## 2. 安装指南

### 2.1 环境准备

**系统要求：**
- Windows 11+ / Windows Server 2022+ / Ubuntu 22.04 LTS+
- Python 3.10+ (64位)，**推荐Python 3.13**

### 2.2 快速安装（推荐）

**方式一：使用VeighNa Studio（一键安装）**

下载 [VeighNa Studio-4.3.0](https://download.vnpy.com/veighna_studio-4.3.0.exe)，集成了VeighNa框架和VeighNa Station管理平台。

**方式二：从源码安装**

```bash
# 1. 下载源码
git clone https://github.com/vnpy/vnpy.git
cd vnpy

# 2. Windows安装
install.bat

# 3. Ubuntu安装
bash install.sh

# 4. MacOS安装
bash install_osx.sh
```

### 2.3 安装验证

```python
# 验证安装
python -c "import vnpy; print(vnpy.__version__)"
# 输出: 4.3.0
```

### 2.4 安装AI量化模块

```bash
# 安装完整的AI量化依赖
pip install vnpy[alpha]
```

---

## 3. 架构解析

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      VeighNa Trader                         │
│                    (主交易平台界面)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐  ┌───▼────┐  ┌─────▼──────┐
│   Gateway    │  │  App   │  │   Engine   │
│  (交易接口)   │  │ (策略)  │  │  (功能引擎) │
└──────────────┘  └────────┘  └────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
              ┌────────▼────────┐
              │  Event Engine   │
              │  (事件驱动引擎)   │
              └─────────────────┘
```

### 3.2 核心组件

#### 3.2.1 MainEngine（主引擎）

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine

# 创建事件引擎
event_engine = EventEngine()

# 创建主引擎
main_engine = MainEngine(event_engine)
```

**功能：**
- 管理所有Gateway（交易接口）
- 管理所有App（策略应用）
- 管理所有Engine（功能引擎）
- 协调事件分发

#### 3.2.2 EventEngine（事件引擎）

**事件驱动模式：**

```python
# 事件流示例
行情推送 → EVENT_TICK → 策略引擎 → 下单请求 → EVENT_ORDER → Gateway → 交易所
```

**关键事件类型：**
- `EVENT_TICK`: Tick行情推送
- `EVENT_BAR`: K线数据推送
- `EVENT_TRADE`: 成交回报
- `EVENT_ORDER`: 委托回报
- `EVENT_POSITION`: 持仓更新
- `EVENT_ACCOUNT`: 账户更新

#### 3.2.3 Gateway（交易接口）

VNPy支持30+交易接口：

| 接口类型 | 接口名称 | 支持市场 |
|---------|---------|---------|
| **期货** | CTP, Mini, Femas, UFT | 国内期货、期权 |
| **股票** | XTP, TORA, OST, EMT | A股、ETF期权 |
| **海外** | IB, TAP, DA | 海外证券、期货 |
| **数据** | RQData, XT | 跨市场实时行情 |

---

## 4. 核心模块详解

### 4.1 vnpy.trader（交易核心）

#### 4.1.1 数据对象（object.py）

**TickData - Tick行情数据**

```python
from vnpy.trader.object import TickData
from vnpy.trader.constant import Exchange
from datetime import datetime

tick = TickData(
    gateway_name="CTP",
    symbol="rb2505",
    exchange=Exchange.SHFE,
    datetime=datetime.now(),
    last_price=3500.0,
    volume=12345,
    bid_price_1=3499.0,
    bid_volume_1=100,
    ask_price_1=3501.0,
    ask_volume_1=50,
)
```

**BarData - K线数据**

```python
from vnpy.trader.object import BarData
from vnpy.trader.constant import Interval

bar = BarData(
    gateway_name="DB",
    symbol="rb2505",
    exchange=Exchange.SHFE,
    datetime=datetime.now(),
    interval=Interval.MINUTE,
    open_price=3500.0,
    high_price=3510.0,
    low_price=3495.0,
    close_price=3505.0,
    volume=1000,
)
```

**OrderData - 委托数据**

```python
from vnpy.trader.object import OrderData, OrderRequest
from vnpy.trader.constant import Direction, Offset, OrderType

# 创建委托请求
order_req = OrderRequest(
    symbol="rb2505",
    exchange=Exchange.SHFE,
    direction=Direction.LONG,
    type=OrderType.LIMIT,
    volume=10,
    price=3500.0,
    offset=Offset.OPEN,
)
```

#### 4.1.2 常量定义（constant.py）

```python
from vnpy.trader.constant import (
    Direction,    # 方向：LONG（多）, SHORT（空）
    Offset,       # 开平：OPEN（开）, CLOSE（平）
    Status,       # 状态：SUBMITTING, NOTTRADED, ALLTRADED等
    Product,      # 品种：EQUITY（股票）, FUTURES（期货）, OPTION（期权）
    OrderType,    # 订单类型：LIMIT（限价）, MARKET（市价）
    Exchange,     # 交易所：SHFE, DCE, CZCE, SSE, SZSE等
)
```

### 4.2 vnpy.event（事件引擎）

```python
from vnpy.event import Event, EventEngine

# 创建事件引擎
event_engine = EventEngine()
event_engine.start()

# 注册事件处理函数
def process_tick_event(event: Event):
    tick = event.data
    print(f"收到行情: {tick.symbol} {tick.last_price}")

event_engine.register(EVENT_TICK, process_tick_event)

# 发送事件
event = Event(EVENT_TICK, tick_data)
event_engine.put(event)
```

### 4.3 vnpy.chart（图表引擎）

高性能K线图表组件，支持：
- 大数据量图表显示
- 实时数据更新
- 技术指标叠加
- 交互式缩放

### 4.4 vnpy.rpc（分布式通信）

```python
# 服务端
from vnpy.rpc import RpcServer

server = RpcServer()
server.start()

# 客户端
from vnpy.rpc import RpcClient

client = RpcClient()
client.connect("localhost", 2014)
```

---

## 5. AI量化模块 (vnpy.alpha)

### 5.1 模块概述

**vnpy.alpha** 是VeighNa 4.0版本的重磅功能，提供一站式AI量化策略开发解决方案。

**核心组件：**

```
vnpy.alpha/
├── dataset/          # 因子特征工程
│   ├── template.py       # AlphaDataset模板
│   ├── ts_function.py    # 时序算子
│   ├── cs_function.py    # 截面算子
│   ├── ta_function.py    # 技术指标算子
│   ├── math_function.py  # 数学运算算子
│   └── datasets/
│       ├── alpha_101.py  # WorldQuant 101因子
│       └── alpha_158.py  # Qlib 158因子
├── model/            # 机器学习模型
│   ├── template.py       # AlphaModel模板
│   └── models/
│       ├── lasso_model.py    # Lasso回归
│       ├── lgb_model.py      # LightGBM
│       └── mlp_model.py      # 神经网络
├── strategy/         # 策略回测
│   ├── template.py       # AlphaStrategy模板
│   └── backtesting.py    # 回测引擎
└── lab.py            # 投研流程管理
```

### 5.2 AlphaLab - 投研实验室

**AlphaLab** 是核心管理类，负责：
- 数据存储与管理
- 数据集保存与加载
- 模型持久化
- 信号生成与管理

```python
from vnpy.alpha.lab import AlphaLab

# 创建实验室
lab = AlphaLab(lab_path="./alpha_lab")

# 保存K线数据
lab.save_bar_data(bars)

# 加载K线数据
bars = lab.load_bar_data(
    vt_symbol="000001.SSE",
    interval="d",
    start="2020-01-01",
    end="2024-12-31"
)

# 创建DataFrame
df = lab.create_dataframe(
    vt_symbols=["000001.SSE", "000002.SSE"],
    interval="d",
    start="2020-01-01",
    end="2024-12-31"
)

# 保存数据集
lab.save_dataset(dataset, "my_dataset")

# 加载数据集
dataset = lab.load_dataset("my_dataset")

# 保存模型
lab.save_model(model, "my_model")

# 加载模型
model = lab.load_model("my_model")
```

### 5.3 AlphaDataset - 因子数据集

**作用：** 因子特征工程，批量计算和处理特征。

#### 基本使用

```python
import polars as pl
from vnpy.alpha.dataset import AlphaDataset

# 创建数据集
dataset = AlphaDataset(
    df=df,  # polars.DataFrame
    train_period=("2020-01-01", "2022-12-31"),
    valid_period=("2023-01-01", "2023-06-30"),
    test_period=("2023-07-01", "2024-12-31")
)

# 添加因子特征
dataset.add_feature("returns", "(close / ts_delay(close, 1) - 1)")
dataset.add_feature("volatility", "ts_std(close / ts_delay(close, 1) - 1, 20)")
dataset.add_feature("momentum", "close / ts_delay(close, 20) - 1")

# 设置标签（预测目标）
dataset.set_label("ts_delay((close / ts_delay(close, 1) - 1), -1)")

# 准备数据（并行计算因子）
dataset.prepare_data(max_workers=4)

# 添加数据处理器
from vnpy.alpha.dataset.processor import MinMaxNormProcessor, DropNaLabelProcessor

dataset.add_processor("infer", DropNaLabelProcessor())
dataset.add_processor("learn", MinMaxNormProcessor())

# 处理数据
dataset.process_data()

# 获取数据
from vnpy.alpha.dataset import Segment

train_df = dataset.fetch_learn(Segment.TRAIN)
valid_df = dataset.fetch_learn(Segment.VALID)
test_df = dataset.fetch_learn(Segment.TEST)
```

#### 使用内置因子库

**Alpha101 - WorldQuant 101因子**

```python
from vnpy.alpha.dataset.datasets import Alpha101

# 创建101因子数据集
dataset = Alpha101(
    df=df,
    train_period=("2020-01-01", "2022-12-31"),
    valid_period=("2023-01-01", "2023-06-30"),
    test_period=("2023-07-01", "2024-12-31")
)

# 自动包含101个因子：alpha1, alpha2, ..., alpha101
dataset.prepare_data()
```

**Alpha158 - Qlib 158因子**

```python
from vnpy.alpha.dataset.datasets import Alpha158

# 创建158因子数据集
dataset = Alpha158(
    df=df,
    train_period=("2020-01-01", "2022-12-31"),
    valid_period=("2023-01-01", "2023-06-30"),
    test_period=("2023-07-01", "2024-12-31")
)

# 包含158个特征：KLEN、OPEN、CLOSE、HIGH、LOW、VWAP等
dataset.prepare_data()
```

### 5.4 AlphaModel - 机器学习模型

#### 5.4.1 Lasso模型

```python
from vnpy.alpha.model.models import LassoModel

# 创建模型
model = LassoModel(alpha=0.01)

# 训练模型
model.fit(dataset)

# 预测
predictions = model.predict(dataset, Segment.TEST)

# 查看特征重要性
model.detail()
```

#### 5.4.2 LightGBM模型

```python
from vnpy.alpha.model.models import LgbModel

# 创建模型
model = LgbModel(
    num_leaves=31,
    learning_rate=0.05,
    n_estimators=100
)

# 训练
model.fit(dataset)

# 预测
predictions = model.predict(dataset, Segment.TEST)

# 特征重要性
importances = model.detail()
```

#### 5.4.3 MLP神经网络模型

```python
from vnpy.alpha.model.models import MlpModel

# 创建模型
model = MlpModel(
    hidden_size=64,
    num_layers=3,
    dropout=0.5,
    lr=0.001,
    max_epoch=100
)

# 训练
model.fit(dataset)

# 预测
predictions = model.predict(dataset, Segment.TEST)
```

### 5.5 AlphaStrategy - 策略回测

```python
from vnpy.alpha.strategy import AlphaStrategy, BacktestingEngine
from vnpy.trader.object import BarData

class MyAlphaStrategy(AlphaStrategy):
    """自定义Alpha策略"""
    
    def on_init(self):
        """初始化回调"""
        self.write_log("策略初始化")
    
    def on_bars(self, bars: dict[str, BarData]):
        """K线切片回调"""
        # 获取信号
        signal_df = self.get_signal()
        
        # 根据信号设置目标仓位
        for vt_symbol in self.vt_symbols:
            if vt_symbol in signal_df["vt_symbol"].to_list():
                signal = signal_df.filter(
                    pl.col("vt_symbol") == vt_symbol
                )["signal"][0]
                
                # 信号 > 0: 做多; < 0: 做空
                target_pos = signal * 100  # 每个信号单位100股
                self.set_target(vt_symbol, target_pos)
        
        # 执行交易
        self.execute_trading(bars, price_add=0.01)
    
    def on_trade(self, trade: TradeData):
        """成交回调"""
        self.write_log(f"成交: {trade.vt_symbol} {trade.direction.value} {trade.volume}")

# 创建回测引擎
engine = BacktestingEngine()

# 加载数据
engine.load_data(bars_dict)

# 生成信号
signal_df = lab.generate_signal(model, dataset, Segment.TEST)
engine.load_signal(signal_df)

# 运行回测
engine.run_backtesting(
    strategy_class=MyAlphaStrategy,
    setting={},
    vt_symbols=["000001.SSE", "000002.SSE"],
    interval="d",
    start="2023-07-01",
    end="2024-12-31",
    capital=1000000
)

# 获取回测结果
results = engine.calculate_result()
statistics = engine.calculate_statistics()
```

---

## 6. 量化交易算子详解

### 6.1 时序算子（ts_function.py）

时序算子用于对**单个标的的时间序列**进行计算。

#### 6.1.1 ts_delay - 滞后

```python
# 获取N天前的值
ts_delay(close, 1)  # 昨收价
ts_delay(close, 5)  # 5天前收盘价
```

**工作原理：**
```
日期     close    ts_delay(close, 1)
Day1     100      NaN
Day2     102      100
Day3     105      102
Day4     103      105
```

#### 6.1.2 ts_delta - 差分

```python
# 计算变化量
ts_delta(close, 1)   # close - close[-1]
ts_delta(close, 5)   # close - close[-5]
```

**应用：**
```python
# 日收益率
returns = "ts_delta(close, 1) / ts_delay(close, 1)"
```

#### 6.1.3 ts_mean - 移动平均

```python
# N日移动平均
ts_mean(close, 20)   # 20日均线
ts_mean(volume, 5)   # 5日成交量均值
```

**应用：**
```python
# 均线偏离度
"(close - ts_mean(close, 20)) / ts_mean(close, 20)"
```

#### 6.1.4 ts_std - 移动标准差

```python
# N日标准差
ts_std(close, 20)    # 20日价格波动
ts_std(returns, 20)  # 20日收益率波动
```

**应用：**
```python
# 波动率
volatility = "ts_std(close / ts_delay(close, 1) - 1, 20)"
```

#### 6.1.5 ts_min / ts_max - 滚动最小/最大值

```python
# N日内最低/最高价
ts_min(low, 20)      # 20日最低价
ts_max(high, 20)     # 20日最高价
```

**应用：**
```python
# 价格相对位置
"(close - ts_min(low, 20)) / (ts_max(high, 20) - ts_min(low, 20))"
```

#### 6.1.6 ts_argmin / ts_argmax - 最值位置

```python
# 返回最值出现的位置（1到N）
ts_argmax(close, 10)  # 10日内最高价出现在第几天
ts_argmin(close, 10)  # 10日内最低价出现在第几天
```

#### 6.1.7 ts_rank - 百分位排名

```python
# 当前值在窗口内的百分位排名（0-1）
ts_rank(close, 20)   # 当前价格在20日内的排名
```

#### 6.1.8 ts_sum - 滚动求和

```python
# N日累计
ts_sum(volume, 5)    # 5日成交量
ts_sum(returns, 20)  # 20日累计收益
```

#### 6.1.9 ts_corr - 滚动相关系数

```python
# 两个序列的N日相关性
ts_corr(close, volume, 20)  # 价格与成交量的20日相关性
```

**应用：**
```python
# 量价背离
"ts_corr(close, volume, 10)"
```

#### 6.1.10 ts_cov - 滚动协方差

```python
# 两个序列的N日协方差
ts_cov(returns, market_returns, 20)
```

#### 6.1.11 ts_skewness - 滚动偏度

```python
# N日偏度（分布的对称性）
ts_skewness(returns, 20)
```

#### 6.1.12 ts_kurtosis - 滚动峰度

```python
# N日峰度（分布的尖峭性）
ts_kurtosis(returns, 20)
```

### 6.2 截面算子（cs_function.py）

截面算子用于对**同一时间点的多个标的**进行横向比较。

#### 6.2.1 cs_rank - 截面排名

```python
# 当前值在所有股票中的排名
cs_rank(close)       # 价格排名
cs_rank(volume)      # 成交量排名
```

**工作原理：**
```
时间      股票A   股票B   股票C   cs_rank(close)
Day1:     100     120     110     1, 3, 2
Day2:     105     118     112     1, 3, 2
```

#### 6.2.2 cs_mean - 截面均值

```python
# 所有股票的平均值
cs_mean(close)       # 市场平均价格
cs_mean(returns)     # 市场平均收益率
```

**应用：**
```python
# 相对强度
"close / cs_mean(close)"
```

#### 6.2.3 cs_std - 截面标准差

```python
# 所有股票的标准差
cs_std(returns)      # 市场收益率离散度
```

#### 6.2.4 cs_scale - 截面标准化

```python
# 按绝对值之和标准化（权重和为1）
cs_scale(signal)
```

**应用：**
```python
# 构建市场中性组合权重
"cs_scale(cs_rank(momentum) - 0.5)"
```

### 6.3 数学运算算子（math_function.py）

#### 6.3.1 基础数学函数

```python
# 对数
log(close)

# 绝对值
abs(returns)

# 符号函数
sign(returns)  # 返回1, 0, -1

# 最小值
less(close, 100)  # min(close, 100)

# 最大值
greater(close, 50)  # max(close, 50)
```

#### 6.3.2 条件函数 - quesval

```python
# if threshold < feature1 then feature2 else feature3
quesval(0, returns, 1, -1)  # if 0 < returns then 1 else -1
```

**应用：**
```python
# 条件选股
"quesval(0.02, momentum, 1, 0)"  # 动量>2%则选中
```

#### 6.3.3 幂运算 - pow1/pow2

```python
# pow1: 底数^指数（指数为常数）
pow1(close, 2)  # close^2

# pow2: 底数^指数（指数为变量）
pow2(close, exponent_feature)
```

### 6.4 技术分析算子（ta_function.py）

基于TA-Lib库，提供经典技术指标。

#### 6.4.1 ta_rsi - 相对强弱指标

```python
# RSI指标
ta_rsi(close, 14)  # 14日RSI
```

**解释：** RSI值在0-100之间，>70超买，<30超卖。

#### 6.4.2 ta_atr - 平均真实波幅

```python
# ATR指标
ta_atr(high, low, close, 14)  # 14日ATR
```

**解释：** 衡量市场波动性，用于设置止损位。

### 6.5 因子表达式示例

#### 6.5.1 动量因子

```python
# 20日动量
momentum_20 = "close / ts_delay(close, 20) - 1"

# 5日加速度
acceleration = "ts_delta(close, 5) - ts_delay(ts_delta(close, 5), 5)"

# 相对强度
relative_strength = "cs_rank(ts_sum(close / ts_delay(close, 1) - 1, 20))"
```

#### 6.5.2 反转因子

```python
# 短期反转
short_reversal = "(-1) * (close / ts_delay(close, 1) - 1)"

# 隔夜反转
overnight_reversal = "(open / ts_delay(close, 1) - 1) * (-1)"
```

#### 6.5.3 波动率因子

```python
# 历史波动率
volatility = "ts_std(close / ts_delay(close, 1) - 1, 20)"

# 相对波动率
relative_vol = "ts_std(close, 20) / cs_mean(ts_std(close, 20))"
```

#### 6.5.4 量价因子

```python
# 量价相关性
volume_price_corr = "ts_corr(close, volume, 20)"

# 成交量变化
volume_change = "volume / ts_mean(volume, 20) - 1"

# 价格加权成交量
vwap_deviation = "(close - vwap) / vwap"
```

#### 6.5.5 复合因子（Alpha101示例）

```python
# Alpha1
alpha1 = "(cs_rank(ts_argmax(pow1(quesval(0, returns, close, ts_std(returns, 20)), 2.0), 5)) - 0.5)"

# Alpha2
alpha2 = "(-1) * ts_corr(cs_rank(ts_delta(log(volume), 2)), cs_rank((close - open) / open), 6)"

# Alpha3
alpha3 = "ts_corr(cs_rank(open), cs_rank(volume), 10) * -1"
```

---

## 7. 策略开发实战

### 7.1 CTA策略开发

#### 7.1.1 简单双均线策略

```python
from vnpy_ctastrategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager,
)

class DoubleMaStrategy(CtaTemplate):
    """双均线策略"""
    
    # 策略参数
    fast_window = 10
    slow_window = 20
    
    # 策略变量
    fast_ma = 0.0
    slow_ma = 0.0
    
    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma", "slow_ma"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """构造函数"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(10)  # 加载10天历史数据
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
    
    def on_tick(self, tick: TickData):
        """Tick推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """K线推送"""
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 计算均线
        self.fast_ma = self.am.sma(self.fast_window)
        self.slow_ma = self.am.sma(self.slow_window)
        
        # 交易逻辑
        if self.pos == 0:
            if self.fast_ma > self.slow_ma:
                self.buy(bar.close_price + 5, 1)
        elif self.pos > 0:
            if self.fast_ma < self.slow_ma:
                self.sell(bar.close_price - 5, abs(self.pos))
        
        self.put_event()
```

#### 7.1.2 策略回测

```python
from vnpy_ctabacktester import BacktestingEngine
from datetime import datetime

# 创建回测引擎
engine = BacktestingEngine()

# 设置回测参数
engine.set_parameters(
    vt_symbol="rb2505.SHFE",
    interval="1m",
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    rate=0.0003,  # 手续费率
    slippage=2,   # 滑点
    size=10,      # 合约乘数
    pricetick=1,  # 最小价格变动
    capital=1000000,  # 初始资金
)

# 添加策略
engine.add_strategy(DoubleMaStrategy, {
    "fast_window": 10,
    "slow_window": 20
})

# 加载数据
engine.load_data()

# 运行回测
engine.run_backtesting()

# 计算结果
df = engine.calculate_result()
statistics = engine.calculate_statistics()

print(statistics)
```

### 7.2 组合策略开发

```python
from vnpy_portfoliostrategy import StrategyTemplate

class MultiFactorStrategy(StrategyTemplate):
    """多因子选股策略"""
    
    author = "VeighNa"
    
    # 策略参数
    rebalance_days = 5  # 调仓周期
    
    parameters = ["rebalance_days"]
    
    def on_init(self):
        """初始化"""
        self.write_log("策略初始化")
    
    def on_start(self):
        """启动"""
        self.write_log("策略启动")
    
    def on_stop(self):
        """停止"""
        self.write_log("策略停止")
    
    def on_bars(self, bars: dict):
        """K线切片推送"""
        # 每N天调仓一次
        if self.get_datetime().day % self.rebalance_days != 0:
            return
        
        # 计算因子值
        momentum_scores = {}
        for vt_symbol, bar in bars.items():
            # 这里可以调用AlphaDataset计算复杂因子
            momentum = bar.close_price / bar.open_price - 1
            momentum_scores[vt_symbol] = momentum
        
        # 排序选股
        sorted_symbols = sorted(
            momentum_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 选择前10名
        top_symbols = [s[0] for s in sorted_symbols[:10]]
        
        # 设置目标仓位（等权重）
        target_weight = 1.0 / len(top_symbols)
        for vt_symbol in self.vt_symbols:
            if vt_symbol in top_symbols:
                self.set_target(vt_symbol, target_weight)
            else:
                self.set_target(vt_symbol, 0)
        
        # 执行调仓
        self.rebalance_portfolio(bars)
```

---

## 8. 数据管理

### 8.1 数据库配置

VNPy支持多种数据库：

```python
# SQLite（默认，无需配置）
# 数据存储在：C:\Users\{用户}\.vntrader\database.db

# MySQL
from vnpy.trader.setting import SETTINGS

SETTINGS["database.driver"] = "mysql"
SETTINGS["database.database"] = "vnpy"
SETTINGS["database.host"] = "localhost"
SETTINGS["database.port"] = 3306
SETTINGS["database.user"] = "root"
SETTINGS["database.password"] = "password"

# MongoDB
SETTINGS["database.driver"] = "mongodb"
SETTINGS["database.database"] = "vnpy"
SETTINGS["database.host"] = "localhost"
SETTINGS["database.port"] = 27017
```

### 8.2 数据下载

#### 8.2.1 使用RQData

```python
from vnpy_rqdata import RqdataDatafeed
from vnpy.trader.engine import MainEngine

datafeed = RqdataDatafeed()
datafeed.init("your_username", "your_password")

# 下载历史数据
bars = datafeed.query_bar_history(
    symbol="600000",
    exchange=Exchange.SSE,
    interval=Interval.DAILY,
    start=datetime(2020, 1, 1),
    end=datetime(2024, 12, 31)
)

# 保存到数据库
for bar in bars:
    database.save_bar_data([bar])
```

#### 8.2.2 使用迅投研

```python
from vnpy_xt import XtDatafeed

datafeed = XtDatafeed()
datafeed.init("your_account", "your_password")

# 下载数据
bars = datafeed.query_bar_history(...)
```

### 8.3 数据录制

使用DataRecorder应用实时录制行情：

```python
from vnpy_datarecorder import DataRecorderApp

# 在MainWindow中添加应用
main_engine.add_app(DataRecorderApp)

# 通过GUI配置要录制的合约
# 支持录制Tick和Bar数据
```

---

## 9. 实盘交易

### 9.1 连接交易接口

#### 9.1.1 CTP期货接口

```python
from vnpy_ctp import CtpGateway

# 添加接口
main_engine.add_gateway(CtpGateway)

# 连接参数
setting = {
    "用户名": "your_account",
    "密码": "your_password",
    "经纪商代码": "9999",
    "交易服务器": "180.168.146.187:10130",
    "行情服务器": "180.168.146.187:10131",
    "产品名称": "simnow_client_test",
    "授权编码": "0000000000000000",
}

# 连接
main_engine.connect(setting, "CTP")
```

#### 9.1.2 模拟盘

使用SimNow：

1. 访问 http://www.simnow.com.cn/
2. 注册账号
3. 获取：经纪商代码、交易服务器、行情服务器
4. 使用上述配置连接

### 9.2 启动策略

```python
from vnpy_ctastrategy import CtaEngine

cta_engine = main_engine.add_app(CtaStrategyApp)

# 添加策略
cta_engine.add_strategy(
    class_name="DoubleMaStrategy",
    strategy_name="double_ma_rb",
    vt_symbol="rb2505.SHFE",
    setting={"fast_window": 10, "slow_window": 20}
)

# 初始化策略
cta_engine.init_strategy("double_ma_rb")

# 启动策略
cta_engine.start_strategy("double_ma_rb")
```

### 9.3 风险管理

使用RiskManager应用：

```python
from vnpy_riskmanager import RiskManagerApp

main_engine.add_app(RiskManagerApp)

# 设置风险规则
# - 流控：每秒最多下单次数
# - 单笔委托最大数量
# - 总成交限制
# - 活动委托限制
```

---

## 10. 常见问题

### 10.1 安装问题

**Q: ta-lib安装失败？**

A: Windows用户使用预编译包：
```bash
pip install --extra-index-url https://pypi.vnpy.com ta_lib==0.6.4
```

**Q: 如何安装GPU版本的PyTorch？**

A: 访问 https://pytorch.org/ 选择对应的CUDA版本：
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### 10.2 使用问题

**Q: 如何查看日志？**

A: 日志文件位置：
```
C:\Users\{用户}\.vntrader\log\
```

**Q: 如何清除数据库？**

A: 删除数据库文件（SQLite）：
```
C:\Users\{用户}\.vntrader\database.db
```

**Q: CTA策略不触发on_bar？**

A: 检查：
1. 是否调用了`load_bar()`加载历史数据
2. 是否连接了行情源
3. `BarGenerator`是否正确配置

### 10.3 性能优化

**Q: 回测速度慢？**

A: 
1. 使用`max_workers`并行计算因子
2. 使用Polars代替Pandas
3. 减少因子数量
4. 使用高性能数据库（TDengine、DolphinDB）

**Q: 实盘卡顿？**

A:
1. 减少策略数量
2. 优化策略逻辑
3. 使用独立进程运行策略
4. 升级硬件（SSD、更多内存）

---

## 附录A：完整示例项目

### A.1 基于Alpha101的量化策略

```python
import polars as pl
from vnpy.alpha.lab import AlphaLab
from vnpy.alpha.dataset.datasets import Alpha101
from vnpy.alpha.dataset.processor import (
    DropNaLabelProcessor,
    MinMaxNormProcessor
)
from vnpy.alpha.model.models import LgbModel
from vnpy.alpha.dataset import Segment

# 1. 创建实验室
lab = AlphaLab("./my_lab")

# 2. 下载数据（使用RQData）
from vnpy_rqdata import RqdataDatafeed
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval

datafeed = RqdataDatafeed()
datafeed.init("username", "password")

symbols = ["600000", "600016", "600019"]  # 沪市大盘股
for symbol in symbols:
    bars = datafeed.query_bar_history(
        symbol=symbol,
        exchange=Exchange.SSE,
        interval=Interval.DAILY,
        start=datetime(2018, 1, 1),
        end=datetime(2024, 12, 31)
    )
    lab.save_bar_data(bars)

# 3. 创建DataFrame
df = lab.create_dataframe(
    vt_symbols=[f"{s}.SSE" for s in symbols],
    interval="d",
    start="2018-01-01",
    end="2024-12-31"
)

# 4. 创建Alpha101数据集
dataset = Alpha101(
    df=df,
    train_period=("2018-01-01", "2021-12-31"),
    valid_period=("2022-01-01", "2022-12-31"),
    test_period=("2023-01-01", "2024-12-31")
)

# 5. 设置标签（预测次日收益率）
dataset.set_label("ts_delay((close / ts_delay(close, 1) - 1), -1)")

# 6. 准备数据
dataset.prepare_data(max_workers=4)

# 7. 添加处理器
dataset.add_processor("infer", DropNaLabelProcessor())
dataset.add_processor("learn", MinMaxNormProcessor())
dataset.process_data()

# 8. 训练模型
model = LgbModel(
    num_leaves=31,
    learning_rate=0.05,
    n_estimators=200,
    feature_fraction=0.8
)
model.fit(dataset)

# 9. 生成信号
signal_df = lab.generate_signal(model, dataset, Segment.TEST)

# 10. 保存
lab.save_dataset(dataset, "alpha101_dataset")
lab.save_model(model, "lgb_alpha101")
lab.save_signal(signal_df, "test_signal")

# 11. 回测
from vnpy.alpha.strategy import BacktestingEngine
from vnpy.alpha.strategy.strategies import EquityDemoStrategy

engine = BacktestingEngine()

# 加载Bar数据
bars_dict = {}
for symbol in symbols:
    vt_symbol = f"{symbol}.SSE"
    bars = lab.load_bar_data(
        vt_symbol=vt_symbol,
        interval="d",
        start="2023-01-01",
        end="2024-12-31"
    )
    bars_dict[vt_symbol] = bars

engine.load_data(bars_dict)
engine.load_signal(signal_df)

# 运行回测
engine.run_backtesting(
    strategy_class=EquityDemoStrategy,
    setting={"price_add": 0.01},
    vt_symbols=[f"{s}.SSE" for s in symbols],
    interval="d",
    start="2023-01-01",
    end="2024-12-31",
    capital=1000000,
    slippage=0.001,
    commission=0.0003
)

# 查看结果
results = engine.calculate_result()
statistics = engine.calculate_statistics()

print("\n=== 回测统计 ===")
for key, value in statistics.items():
    print(f"{key}: {value}")

# 12. 可视化
engine.show_chart()
```

---

## 附录B：常用因子库

### B.1 动量类因子

```python
# 简单动量
"close / ts_delay(close, 20) - 1"

# 加权动量
"ts_sum(close / ts_delay(close, 1) - 1, 20)"

# 相对动量
"cs_rank(close / ts_delay(close, 20) - 1)"
```

### B.2 波动率因子

```python
# 历史波动率
"ts_std(close / ts_delay(close, 1) - 1, 20)"

# 相对波动率
"ts_std(close, 20) / ts_mean(close, 20)"

# 波动率变化
"ts_std(close, 20) / ts_delay(ts_std(close, 20), 20) - 1"
```

### B.3 价值因子

```python
# 市盈率倒数（需要基本面数据）
"1 / pe_ratio"

# 市净率倒数
"1 / pb_ratio"
```

### B.4 成长因子

```python
# 收入增长率（需要基本面数据）
"(revenue - ts_delay(revenue, 4)) / ts_delay(revenue, 4)"
```

---

## 附录C：资源链接

### C.1 官方资源

- **官网**: https://www.vnpy.com
- **文档**: https://www.vnpy.com/docs
- **论坛**: https://www.vnpy.com/forum
- **GitHub**: https://github.com/vnpy/vnpy
- **知乎专栏**: https://zhuanlan.zhihu.com/vn-py

### C.2 数据服务

- **米筐RQData**: https://www.ricequant.com/
- **迅投研**: https://www.xtquant.com/
- **TuShare**: https://tushare.pro/
- **聚宽**: https://www.joinquant.com/

### C.3 交易接口

- **SimNow仿真**: http://www.simnow.com.cn/
- **盈透证券**: https://www.interactivebrokers.com/
- **东方财富**: https://www.18.cn/

---

## 结语

本文档详细介绍了VNPy框架的安装、架构、核心模块、AI量化模块以及量化交易算子的使用方法和工作原理。

**学习路径建议：**

1. **入门阶段**：熟悉框架结构，运行示例策略
2. **进阶阶段**：开发简单CTA策略，进行回测优化
3. **高级阶段**：使用Alpha模块开发机器学习策略
4. **实战阶段**：连接实盘接口，小资金验证策略

**注意事项：**

⚠️ **风险提示：** 量化交易存在风险，请充分测试后再进行实盘交易。  
⚠️ **资金管理：** 建议先用小资金验证策略有效性。  
⚠️ **持续学习：** 量化交易需要不断学习和迭代优化。

---

**联系与支持：**

如有问题，请访问：
- [官方论坛](https://www.vnpy.com/forum/) 提问
- [GitHub Issues](https://github.com/vnpy/vnpy/issues) 报告bug
- 加入官方QQ群：262656087

祝您量化交易顺利！🚀
