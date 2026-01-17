# AlphaGPT 量化算子集成文档

> 本文档详细说明从 AlphaGPT 项目提取的量化算子及其在 vnpy 中的使用方式

---

## 目录

1. [项目来源](#1-项目来源)
2. [集成概述](#2-集成概述)
3. [算子分类与详解](#3-算子分类与详解)
4. [使用方式](#4-使用方式)
5. [实战示例](#5-实战示例)
6. [风险管理逻辑](#6-风险管理逻辑)
7. [API参考](#7-api参考)

---

## 1. 项目来源

### 1.1 AlphaGPT 简介

**AlphaGPT** 是一个基于深度学习的量化因子挖掘项目，主要特点：

- 使用 GPT 架构自动生成量化因子表达式
- 基于强化学习优化因子性能
- 专注于加密货币/Meme币市场
- 提供完整的回测和实盘交易框架

**GitHub**: https://github.com/imbue-bit/AlphaGPT

### 1.2 核心模块结构

```
AlphaGPT/
├── model_core/
│   ├── ops.py          # 基础运算算子 (PyTorch实现)
│   ├── factors.py      # 量化因子计算
│   ├── vm.py           # 因子表达式虚拟机
│   ├── alphagpt.py     # GPT模型架构
│   ├── backtest.py     # 回测引擎
│   └── engine.py       # 训练引擎
├── strategy_manager/
│   ├── portfolio.py    # 仓位管理
│   ├── risk.py         # 风险控制
│   └── runner.py       # 策略执行器
└── data_pipeline/
    └── processor.py    # 数据预处理
```

---

## 2. 集成概述

### 2.1 集成文件

已将 AlphaGPT 的核心算子移植到 vnpy，集成文件位置：

```
vnpy/alpha/dataset/alphagpt_ops.py
```

### 2.2 集成的算子类别

| 类别 | 数量 | 说明 |
|------|------|------|
| 基础运算算子 | 4 | gate, jump, decay, max_n |
| 市场因子 | 7 | 流动性、买卖失衡、FOMO等 |
| 数据预处理 | 6 | 标准化、收益率、趋势等 |
| **总计** | **17** | 所有算子已适配vnpy表达式引擎 |

### 2.3 修改的vnpy文件

```
vnpy/alpha/dataset/utility.py  # 添加了AlphaGPT算子的导入
```

---

## 3. 算子分类与详解

### 3.1 基础运算算子

#### `gpt_gate(condition, x, y)` - 条件选择算子

**功能**: 根据条件选择返回值

**数学表达式**:
```
result = x  if condition > 0
       = y  otherwise
```

**参数**:
- `condition`: 条件DataProxy
- `x`: 条件为真时的返回值
- `y`: 条件为假时的返回值

**使用示例**:
```python
# 当收益率为正时取动量，否则取波动率
"gpt_gate(close - ts_delay(close, 1), ts_mean(close, 5), ts_std(close, 20))"
```

**应用场景**:
- 条件策略切换
- 市场状态适应性因子
- 组合多个信号

---

#### `gpt_jump(feature, threshold=3.0)` - 跳跃检测算子

**功能**: 检测异常跳跃信号

**数学表达式**:
```
z_score = (x - mean) / std
jump = max(z_score - threshold, 0)
```

**参数**:
- `feature`: 输入特征
- `threshold`: Z-Score阈值，默认3.0

**使用示例**:
```python
# 检测价格异常跳跃
"gpt_jump(close / ts_delay(close, 1) - 1, 3.0)"
```

**应用场景**:
- 异常波动检测
- 黑天鹅事件识别
- 噪音过滤

---

#### `gpt_decay(feature, decay_weights=None)` - 指数衰减算子

**功能**: 对时间序列应用指数衰减权重

**数学表达式**:
```
result = w[0]*x[t] + w[1]*x[t-1] + w[2]*x[t-2] + ...
默认权重: [1.0, 0.8, 0.6]
```

**参数**:
- `feature`: 输入特征
- `decay_weights`: 衰减权重列表

**使用示例**:
```python
# 对成交量应用衰减
"gpt_decay(volume)"
```

**应用场景**:
- 指数加权移动平均
- 近期信号强化
- 时间序列平滑

---

#### `gpt_max_n(feature, window)` - N期最大值算子

**功能**: 计算过去N期的最大值

**参数**:
- `feature`: 输入特征
- `window`: 窗口大小

**使用示例**:
```python
# 5日最高价
"gpt_max_n(high, 5)"
```

---

### 3.2 市场因子算子

#### `gpt_liquidity_health(liquidity, fdv)` - 流动性健康度

**功能**: 衡量流动性相对于完全稀释估值的健康程度

**数学表达式**:
```
ratio = liquidity / fdv
health = clamp(ratio * 4, 0, 1)
```

**返回值解释**:
- 0.0: 流动性极差
- 0.5: 中等流动性
- 1.0: 流动性充足

**使用示例**:
```python
# 需要自定义liquidity和fdv字段
"gpt_liquidity_health(liquidity, fdv)"
```

**应用场景**:
- 流动性风险评估
- 交易滑点预估
- 仓位规模调节

---

#### `gpt_buy_sell_imbalance(close, open_, high, low)` - 买卖失衡因子

**功能**: 基于K线形态计算买卖力量失衡

**数学表达式**:
```
body = close - open
range = high - low
strength = body / range
imbalance = tanh(strength * 3)  # 归一化到[-1, 1]
```

**返回值解释**:
- 正值: 买方力量占优
- 负值: 卖方力量占优
- 接近0: 买卖均衡

**使用示例**:
```python
"gpt_buy_sell_imbalance(close, open, high, low)"
```

**应用场景**:
- 短期方向预测
- 市场情绪分析
- K线形态量化

---

#### `gpt_fomo_acceleration(volume, window=5)` - FOMO加速度因子

**功能**: 检测成交量的加速变化，识别FOMO情绪

**数学表达式**:
```
vol_chg = (volume - volume_prev) / volume_prev
acceleration = vol_chg - vol_chg_prev
result = clamp(acceleration, -5, 5)
```

**返回值解释**:
- 正值: 成交量加速放大（FOMO情绪）
- 负值: 成交量加速萎缩（恐慌情绪）

**使用示例**:
```python
"gpt_fomo_acceleration(volume, 5)"
```

**应用场景**:
- 情绪极端检测
- 趋势加速信号
- 反转预警

---

#### `gpt_pump_deviation(close, window=20)` - 泵偏离因子

**功能**: 计算价格相对于移动平均线的偏离程度

**数学表达式**:
```
ma = rolling_mean(close, window)
deviation = (close - ma) / ma
```

**使用示例**:
```python
"gpt_pump_deviation(close, 20)"
```

**应用场景**:
- 超买/超卖检测
- 均值回归策略
- 泡沫预警

---

#### `gpt_volatility_clustering(close, window=10)` - 波动率聚类因子

**功能**: 检测波动率聚类模式

**数学表达式**:
```
ret = log(close / close_prev)
realized_vol = sqrt(rolling_mean(ret^2, window))
```

**使用示例**:
```python
"gpt_volatility_clustering(close, 10)"
```

**应用场景**:
- 波动率预测
- 风险度量
- 期权策略

---

#### `gpt_momentum_reversal(close, window=5)` - 动量反转因子

**功能**: 检测动量方向发生反转的信号

**数学表达式**:
```
mom = sum(ret, window)
reversal = 1 if mom * mom_prev < 0 else 0
```

**返回值**: 
- 1: 发生反转
- 0: 未反转

**使用示例**:
```python
"gpt_momentum_reversal(close, 5)"
```

**应用场景**:
- 趋势反转检测
- 入场/出场信号
- 止损触发

---

#### `gpt_relative_strength(close, high, low, window=14)` - 相对强度因子

**功能**: 改进的RSI指标，输出归一化到[-1, 1]

**数学表达式**:
```
gains = max(ret, 0)
losses = max(-ret, 0)
rs = avg_gain / avg_loss
rsi = 100 - 100/(1+rs)
result = (rsi - 50) / 50  # 归一化
```

**返回值解释**:
- 正值: 上涨动能强
- 负值: 下跌动能强
- 接近0: 多空均衡

**使用示例**:
```python
"gpt_relative_strength(close, high, low, 14)"
```

---

### 3.3 数据预处理算子

#### `gpt_robust_norm(feature, clip_value=5.0)` - 稳健标准化

**功能**: 使用中位数和MAD进行标准化，抗异常值

**数学表达式**:
```
median = median(x)
mad = median(|x - median|)
norm = (x - median) / mad
result = clamp(norm, -clip_value, clip_value)
```

**使用示例**:
```python
"gpt_robust_norm(close / ts_delay(close, 1) - 1, 5.0)"
```

**优势**:
- 对异常值不敏感
- 保持数据分布形状
- 适合金融数据

---

#### `gpt_cs_robust_norm(feature, clip_value=5.0)` - 截面稳健标准化

**功能**: 在截面维度进行稳健标准化

**使用示例**:
```python
"gpt_cs_robust_norm(close / ts_delay(close, 5) - 1)"
```

---

#### `gpt_log_return(close)` - 对数收益率

**数学表达式**:
```
log_ret = log(close / close_prev)
```

**使用示例**:
```python
"gpt_log_return(close)"
```

---

#### `gpt_vol_shock(volume, window=20)` - 成交量冲击因子

**功能**: 当前成交量相对于历史均值的倍数

**数学表达式**:
```
vol_shock = volume / rolling_mean(volume, window)
```

**返回值解释**:
- \> 1: 成交量放大
- < 1: 成交量萎缩
- = 1: 正常水平

**使用示例**:
```python
"gpt_vol_shock(volume, 20)"
```

---

#### `gpt_trend(close, window=60)` - 趋势方向因子

**功能**: 判断价格相对于长期均线的位置

**数学表达式**:
```
trend = 1 if close > ma else -1
```

**使用示例**:
```python
"gpt_trend(close, 60)"
```

---

#### `gpt_high_low_range(high, low, close)` - 高低点振幅比

**数学表达式**:
```
range = (high - low) / close
```

**使用示例**:
```python
"gpt_high_low_range(high, low, close)"
```

---

#### `gpt_close_position(close, high, low)` - 收盘价位置因子

**功能**: 收盘价在当日振幅中的相对位置

**数学表达式**:
```
position = (close - low) / (high - low)
```

**返回值解释**:
- 接近1: 收盘在高点附近（看涨）
- 接近0: 收盘在低点附近（看跌）
- 0.5: 收盘在中间位置

**使用示例**:
```python
"gpt_close_position(close, high, low)"
```

---

#### `gpt_volume_trend(volume)` - 成交量趋势因子

**数学表达式**:
```
vol_trend = (volume - volume_prev) / volume_prev
```

**使用示例**:
```python
"gpt_volume_trend(volume)"
```

---

## 4. 使用方式

### 4.1 在表达式中使用

所有AlphaGPT算子已集成到vnpy的表达式引擎，可直接在`add_feature`中使用：

```python
from vnpy.alpha.dataset import AlphaDataset

dataset = AlphaDataset(
    df=price_df,
    train_period=("2020-01-01", "2022-12-31"),
    valid_period=("2023-01-01", "2023-06-30"),
    test_period=("2023-07-01", "2023-12-31")
)

# 使用AlphaGPT算子
dataset.add_feature("fomo", "gpt_fomo_acceleration(volume, 5)")
dataset.add_feature("pump_dev", "gpt_pump_deviation(close, 20)")
dataset.add_feature("imbalance", "gpt_buy_sell_imbalance(close, open, high, low)")
dataset.add_feature("vol_cluster", "gpt_volatility_clustering(close, 10)")
dataset.add_feature("mom_reversal", "gpt_momentum_reversal(close, 5)")
dataset.add_feature("rsi_norm", "gpt_relative_strength(close, high, low, 14)")
```

### 4.2 直接调用函数

也可以直接导入函数使用：

```python
from vnpy.alpha.dataset.alphagpt_ops import (
    gpt_fomo_acceleration,
    gpt_pump_deviation,
    gpt_buy_sell_imbalance,
    gpt_volatility_clustering,
    gpt_momentum_reversal,
    gpt_relative_strength,
    gpt_robust_norm
)
from vnpy.alpha.dataset.utility import DataProxy
import polars as pl

# 准备数据
close_df = df[["datetime", "vt_symbol", "close"]]
close_proxy = DataProxy(close_df)

# 计算因子
vol_cluster = gpt_volatility_clustering(close_proxy, window=10)
result_df = vol_cluster.df
```

---

## 5. 实战示例

### 5.1 构建加密货币多因子策略

```python
from vnpy.alpha import AlphaLab, AlphaDataset, Segment
from vnpy.alpha.dataset import process_drop_na, process_fill_na
from vnpy.alpha.model.models.lgb_model import LgbModel
from functools import partial

# 创建实验室
lab = AlphaLab("./lab/crypto_strategy")

# 创建数据集
dataset = AlphaDataset(
    df=crypto_df,
    train_period=("2022-01-01", "2023-06-30"),
    valid_period=("2023-07-01", "2023-09-30"),
    test_period=("2023-10-01", "2023-12-31")
)

# ============================================
# 添加AlphaGPT因子
# ============================================

# 市场情绪因子
dataset.add_feature("fomo", "gpt_fomo_acceleration(volume, 5)")
dataset.add_feature("imbalance", "gpt_buy_sell_imbalance(close, open, high, low)")

# 技术因子
dataset.add_feature("pump_dev", "gpt_pump_deviation(close, 20)")
dataset.add_feature("vol_cluster", "gpt_volatility_clustering(close, 10)")
dataset.add_feature("mom_reversal", "gpt_momentum_reversal(close, 5)")
dataset.add_feature("rsi", "gpt_relative_strength(close, high, low, 14)")

# 量价因子
dataset.add_feature("vol_shock", "gpt_vol_shock(volume, 20)")
dataset.add_feature("vol_trend", "gpt_volume_trend(volume)")
dataset.add_feature("close_pos", "gpt_close_position(close, high, low)")
dataset.add_feature("hl_range", "gpt_high_low_range(high, low, close)")

# 趋势因子
dataset.add_feature("trend_20", "gpt_trend(close, 20)")
dataset.add_feature("trend_60", "gpt_trend(close, 60)")

# 对数收益率
dataset.add_feature("log_ret", "gpt_log_return(close)")

# 稳健标准化的收益率
dataset.add_feature("ret_norm", "gpt_robust_norm(close / ts_delay(close, 1) - 1, 5.0)")

# ============================================
# 组合vnpy原生因子
# ============================================
dataset.add_feature("ma_ratio", "ts_mean(close, 5) / ts_mean(close, 20)")
dataset.add_feature("vol_ratio", "ts_std(close, 5) / ts_std(close, 20)")
dataset.add_feature("corr_pv", "ts_corr(close, volume, 10)")

# 设置标签 (未来2期收益)
dataset.set_label("ts_delay(close, -2) / ts_delay(close, -1) - 1")

# 添加预处理器
dataset.add_processor("learn", partial(process_drop_na, names=["label"]))
dataset.add_processor("infer", partial(process_fill_na, fill_value=0))

# 准备数据
dataset.prepare_data(max_workers=4)
dataset.process_data()

# 训练模型
model = LgbModel(
    learning_rate=0.05,
    num_leaves=31,
    num_boost_round=500,
    early_stopping_rounds=30
)
model.fit(dataset)

# 预测
predictions = model.predict(dataset, Segment.TEST)
```

### 5.2 条件因子组合

使用`gpt_gate`构建条件因子：

```python
# 趋势跟踪 + 均值回归 自适应策略
# 当趋势明确时使用动量因子，否则使用均值回归因子
dataset.add_feature(
    "adaptive_signal",
    "gpt_gate(gpt_trend(close, 60), "
    "ts_mean(close, 5) / ts_mean(close, 20) - 1, "  # 趋势因子
    "gpt_pump_deviation(close, 20) * -1)"            # 均值回归因子
)
```

### 5.3 异常检测

使用`gpt_jump`过滤异常信号：

```python
# 检测价格异常跳跃
dataset.add_feature("price_jump", "gpt_jump(close / ts_delay(close, 1) - 1, 3.0)")

# 检测成交量异常
dataset.add_feature("vol_jump", "gpt_jump(gpt_vol_shock(volume, 20), 2.5)")
```

---

## 6. 风险管理逻辑

### 6.1 来自AlphaGPT的风险管理逻辑

AlphaGPT项目包含完整的风险管理框架，核心逻辑如下：

#### 仓位管理 (来自 portfolio.py)

```python
@dataclass
class Position:
    token_address: str      # 标的地址
    symbol: str             # 符号
    entry_price: float      # 入场价格
    entry_time: float       # 入场时间
    amount_held: float      # 持仓数量
    initial_cost: float     # 初始成本
    highest_price: float    # 最高价格 (用于追踪止损)
    is_moonbag: bool        # 是否已部分止盈
```

#### 风险控制策略 (来自 runner.py)

| 策略 | 触发条件 | 操作 |
|------|----------|------|
| **止损** | PnL <= -10% | 全部平仓 |
| **止盈** | PnL >= 100% | 卖出50%，剩余让利润奔跑 |
| **追踪止损** | 从最高点回撤 > 30% | 全部平仓 |
| **AI信号止损** | 信号分数 < 阈值 | 全部平仓 |

#### 流动性过滤 (来自 risk.py)

```python
# 最低流动性要求
if liquidity_usd < 5000:
    return False  # 拒绝交易

# 验证卖出路径 (防止蜜罐)
if not can_sell:
    return False  # 拒绝交易
```

### 6.2 在vnpy策略中应用

```python
from vnpy.alpha import AlphaStrategy
from vnpy.trader.object import BarData, TradeData

class CryptoAlphaStrategy(AlphaStrategy):
    # 风险参数
    stop_loss_pct: float = -0.10      # 止损 -10%
    take_profit_pct: float = 1.00     # 止盈 +100%
    trailing_activation: float = 0.50  # 追踪止损激活 +50%
    trailing_drop: float = 0.30       # 追踪止损触发回撤 30%
    
    def on_init(self):
        self.highest_prices = {}
        self.entry_prices = {}
    
    def on_bars(self, bars: dict[str, BarData]):
        for vt_symbol, bar in bars.items():
            pos = self.get_pos(vt_symbol)
            
            if pos > 0:
                # 更新最高价
                if vt_symbol not in self.highest_prices:
                    self.highest_prices[vt_symbol] = bar.close_price
                else:
                    self.highest_prices[vt_symbol] = max(
                        self.highest_prices[vt_symbol],
                        bar.close_price
                    )
                
                # 计算PnL
                entry = self.entry_prices.get(vt_symbol, bar.close_price)
                pnl_pct = (bar.close_price - entry) / entry
                
                # 止损检查
                if pnl_pct <= self.stop_loss_pct:
                    self.set_target(vt_symbol, 0)
                    continue
                
                # 止盈检查
                if pnl_pct >= self.take_profit_pct:
                    # 卖出一半
                    self.set_target(vt_symbol, pos * 0.5)
                    continue
                
                # 追踪止损检查
                highest = self.highest_prices[vt_symbol]
                max_gain = (highest - entry) / entry
                drawdown = (highest - bar.close_price) / highest
                
                if max_gain > self.trailing_activation and drawdown > self.trailing_drop:
                    self.set_target(vt_symbol, 0)
                    continue
        
        # 执行交易
        self.execute_trading(bars, price_add=0.02)
    
    def on_trade(self, trade: TradeData):
        if trade.direction.value == "多":
            self.entry_prices[trade.vt_symbol] = trade.price
```

---

## 7. API参考

### 7.1 基础运算算子

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `gpt_gate(cond, x, y)` | condition, x, y | DataProxy | 条件选择 |
| `gpt_jump(feature, threshold)` | feature, threshold=3.0 | DataProxy | 跳跃检测 |
| `gpt_decay(feature, weights)` | feature, weights=None | DataProxy | 指数衰减 |
| `gpt_max_n(feature, window)` | feature, window | DataProxy | N期最大值 |

### 7.2 市场因子算子

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `gpt_liquidity_health(liq, fdv)` | liquidity, fdv | DataProxy | 流动性健康度 [0,1] |
| `gpt_buy_sell_imbalance(c,o,h,l)` | close, open, high, low | DataProxy | 买卖失衡 [-1,1] |
| `gpt_fomo_acceleration(vol, w)` | volume, window=5 | DataProxy | FOMO加速度 |
| `gpt_pump_deviation(close, w)` | close, window=20 | DataProxy | 泵偏离 |
| `gpt_volatility_clustering(c, w)` | close, window=10 | DataProxy | 波动率聚类 |
| `gpt_momentum_reversal(close, w)` | close, window=5 | DataProxy | 动量反转 {0,1} |
| `gpt_relative_strength(c,h,l,w)` | close, high, low, window=14 | DataProxy | 相对强度 [-1,1] |

### 7.3 数据预处理算子

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `gpt_robust_norm(feature, clip)` | feature, clip_value=5.0 | DataProxy | 稳健标准化 |
| `gpt_cs_robust_norm(feature, clip)` | feature, clip_value=5.0 | DataProxy | 截面稳健标准化 |
| `gpt_log_return(close)` | close | DataProxy | 对数收益率 |
| `gpt_vol_shock(volume, w)` | volume, window=20 | DataProxy | 成交量冲击 |
| `gpt_trend(close, w)` | close, window=60 | DataProxy | 趋势方向 {-1,1} |
| `gpt_high_low_range(h, l, c)` | high, low, close | DataProxy | 高低振幅比 |
| `gpt_close_position(c, h, l)` | close, high, low | DataProxy | 收盘位置 [0,1] |
| `gpt_volume_trend(volume)` | volume | DataProxy | 成交量趋势 |

---

---

## 8. 高级技术：Low-Rank Decay (LoRD) 正则化

### 8.1 技术背景

AlphaGPT项目包含一个创新的正则化方法：**Newton-Schulz Low-Rank Decay (LoRD)**，用于改善Transformer模型的泛化能力。

### 8.2 核心原理

LoRD通过Newton-Schulz迭代计算权重矩阵的正交投影，然后对其应用衰减：

```python
# Newton-Schulz迭代 (收敛到正交矩阵)
for _ in range(num_iterations):
    A = Y.T @ Y
    Y = 0.5 * Y @ (3.0 * I - A)

# 应用低秩衰减
W -= decay_rate * Y
```

### 8.3 优势

| 对比项 | L2正则化 | LoRD正则化 |
|--------|----------|------------|
| 作用对象 | 所有参数均匀衰减 | 仅针对QK注意力参数 |
| 效果 | 压缩所有权重 | 鼓励低秩结构 |
| 泛化 | 一般 | 更好的泛化能力 |
| Grokking | 慢 | 加速Grokking |

### 8.4 在PyTorch中使用

```python
import torch
import torch.nn as nn

class NewtonSchulzLowRankDecay:
    """LoRD正则化器"""
    
    def __init__(self, named_parameters, decay_rate=1e-3, 
                 num_iterations=5, target_keywords=None):
        self.decay_rate = decay_rate
        self.num_iterations = num_iterations
        self.target_keywords = target_keywords or ["q_proj", "k_proj"]
        self.params_to_decay = []
        
        for name, param in named_parameters:
            if not param.requires_grad or param.ndim != 2:
                continue
            if not any(k in name for k in self.target_keywords):
                continue
            self.params_to_decay.append(param)
    
    @torch.no_grad()
    def step(self):
        """应用LoRD正则化"""
        for W in self.params_to_decay:
            orig_dtype = W.dtype
            X = W.float()
            r, c = X.shape
            
            # 转置优化
            transposed = r > c
            if transposed:
                X = X.T
                
            # 归一化
            norm = X.norm() + 1e-8
            X = X / norm
            
            # Newton-Schulz迭代
            Y = X
            I = torch.eye(min(r, c), device=X.device)
            for _ in range(self.num_iterations):
                A = Y.T @ Y
                Y = 0.5 * Y @ (3.0 * I - A)
            
            if transposed:
                Y = Y.T
            
            # 应用衰减
            W.sub_(self.decay_rate * Y.to(orig_dtype))

# 使用示例
model = YourTransformerModel()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
lord_opt = NewtonSchulzLowRankDecay(
    model.named_parameters(),
    decay_rate=1e-3,
    target_keywords=["q_proj", "k_proj", "attention"]
)

for batch in dataloader:
    loss = model(batch)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    lord_opt.step()  # 在优化器步骤后应用LoRD
```

---

## 9. 策略配置参考

### 9.1 AlphaGPT默认策略参数

```python
class StrategyConfig:
    # 仓位管理
    MAX_OPEN_POSITIONS = 3          # 最大同时持仓数
    ENTRY_AMOUNT_SOL = 2.0          # 单次入场金额
    
    # 止损止盈
    STOP_LOSS_PCT = -0.05           # 止损: -5%
    TAKE_PROFIT_Target1 = 0.10      # 第一止盈目标: +10%
    TP_Target1_Ratio = 0.5          # 第一止盈时卖出比例: 50%
    
    # 追踪止损
    TRAILING_ACTIVATION = 0.05      # 追踪止损激活: +5%
    TRAILING_DROP = 0.03            # 追踪止损触发回撤: 3%
    
    # 信号阈值
    BUY_THRESHOLD = 0.85            # 买入信号阈值
    SELL_THRESHOLD = 0.45           # 卖出信号阈值
```

### 9.2 参数调优建议

| 市场类型 | STOP_LOSS | TAKE_PROFIT | TRAILING |
|----------|-----------|-------------|----------|
| 加密货币 | -10%~-20% | +50%~+100% | 20%~30%回撤 |
| A股 | -5%~-8% | +10%~+20% | 5%~10%回撤 |
| 美股 | -7%~-10% | +15%~+30% | 10%~15%回撤 |
| 期货 | -3%~-5% | +5%~+10% | 3%~5%回撤 |

---

## 10. 完整工作流示例

### 10.1 从数据到回测的完整流程

```python
from vnpy.alpha import AlphaLab, AlphaDataset, BacktestingEngine, Segment
from vnpy.alpha.dataset import process_drop_na, process_fill_na
from vnpy.alpha.model.models.lgb_model import LgbModel
from vnpy.alpha.strategy.strategies.equity_demo_strategy import EquityDemoStrategy
from functools import partial

# ============================================
# 第1步: 初始化研究环境
# ============================================
lab = AlphaLab("./research_lab")

# ============================================
# 第2步: 加载数据
# ============================================
# 假设已有价格数据
price_df = lab.load_bar_df("000300.SSE")  # 或从其他数据源加载

# ============================================
# 第3步: 创建数据集并添加AlphaGPT因子
# ============================================
dataset = AlphaDataset(
    df=price_df,
    train_period=("2020-01-01", "2022-12-31"),
    valid_period=("2023-01-01", "2023-06-30"),
    test_period=("2023-07-01", "2023-12-31")
)

# 添加AlphaGPT因子组合
alphagpt_factors = [
    ("fomo", "gpt_fomo_acceleration(volume, 5)"),
    ("imbalance", "gpt_buy_sell_imbalance(close, open, high, low)"),
    ("pump_dev", "gpt_pump_deviation(close, 20)"),
    ("vol_cluster", "gpt_volatility_clustering(close, 10)"),
    ("mom_reversal", "gpt_momentum_reversal(close, 5)"),
    ("rsi", "gpt_relative_strength(close, high, low, 14)"),
    ("vol_shock", "gpt_vol_shock(volume, 20)"),
    ("close_pos", "gpt_close_position(close, high, low)"),
    ("trend", "gpt_trend(close, 60)"),
    ("ret_norm", "gpt_robust_norm(close / ts_delay(close, 1) - 1, 5.0)"),
]

for name, expr in alphagpt_factors:
    dataset.add_feature(name, expr)

# 添加vnpy原生因子
dataset.add_feature("ma_ratio", "ts_mean(close, 5) / ts_mean(close, 20)")
dataset.add_feature("vol_ratio", "ts_std(close, 5) / ts_std(close, 20)")

# 设置标签
dataset.set_label("ts_delay(close, -2) / ts_delay(close, -1) - 1")

# 添加预处理器
dataset.add_processor("learn", partial(process_drop_na, names=["label"]))
dataset.add_processor("infer", partial(process_fill_na, fill_value=0))

# ============================================
# 第4步: 准备和处理数据
# ============================================
dataset.prepare_data(max_workers=4)
dataset.process_data()

# ============================================
# 第5步: 训练模型
# ============================================
model = LgbModel(
    learning_rate=0.05,
    num_leaves=31,
    num_boost_round=500,
    early_stopping_rounds=30
)
model.fit(dataset)

# 查看因子重要性
model.detail()

# ============================================
# 第6步: 生成预测信号
# ============================================
signal_df = model.predict(dataset, Segment.TEST)

# 保存模型和信号
lab.save_model(model, "alphagpt_lgb_model")
lab.save_signal(signal_df, "alphagpt_signal")

# ============================================
# 第7步: 回测
# ============================================
symbols = price_df["vt_symbol"].unique().tolist()

engine = BacktestingEngine()
engine.set_parameters(
    symbols=symbols,
    interval="1d",
    start="2023-07-01",
    end="2023-12-31",
    capital=1_000_000
)

engine.add_strategy(
    EquityDemoStrategy,
    {
        "top_k": 10,
        "n_drop": 3,
        "min_days": 5,
        "cash_ratio": 0.95
    },
    signal_df
)

# 执行回测
engine.load_data()
engine.run_backtesting()
result = engine.calculate_result()
stats = engine.calculate_statistics()

# 显示结果
print(stats)
engine.show_chart()
engine.show_performance()
```

---

## 总结

本次集成从AlphaGPT项目中提取了17个有效的量化算子，涵盖：

1. **基础运算**: 条件选择、跳跃检测、指数衰减等
2. **市场因子**: FOMO加速度、买卖失衡、动量反转等创新因子
3. **数据预处理**: 稳健标准化、对数收益率等实用工具

同时还整理了：

4. **LoRD正则化**: 用于改善深度学习模型泛化能力的创新技术
5. **策略配置参考**: 止损止盈、追踪止损等参数建议
6. **完整工作流**: 从数据加载到回测的端到端示例

这些算子已完全适配vnpy的表达式引擎，可以在策略开发中直接使用。AlphaGPT的风险管理逻辑也已整理成文档，可作为策略开发的参考。

**注意**: AlphaGPT原始项目主要面向加密货币市场，部分因子（如流动性健康度）需要特定字段支持。在A股等传统市场使用时，建议选择适用的因子或进行适当调整。

---

## 附录A: 文件清单

### 新增文件

| 文件路径 | 说明 |
|----------|------|
| `vnpy/alpha/dataset/alphagpt_ops.py` | AlphaGPT算子实现 |
| `opus/ALPHAGPT_INTEGRATION.md` | 本说明文档 |

### 修改文件

| 文件路径 | 修改内容 |
|----------|----------|
| `vnpy/alpha/dataset/utility.py` | 添加AlphaGPT算子导入 |

---

## 附录B: AlphaGPT项目结构

```
AlphaGPT/
├── model_core/           # 核心模型模块
│   ├── ops.py           # 基础运算算子 ✅ 已集成
│   ├── factors.py       # 量化因子计算 ✅ 已集成
│   ├── vm.py            # 因子表达式虚拟机
│   ├── alphagpt.py      # GPT模型架构 (参考)
│   ├── backtest.py      # 回测引擎 (参考)
│   ├── engine.py        # 训练引擎
│   └── config.py        # 配置参数
├── strategy_manager/     # 策略管理模块
│   ├── portfolio.py     # 仓位管理 (参考)
│   ├── risk.py          # 风险控制 (参考)
│   ├── config.py        # 策略配置 (参考)
│   └── runner.py        # 策略执行器
├── data_pipeline/        # 数据管道
│   └── processor.py     # 数据预处理 ✅ 部分集成
├── execution/            # 交易执行 (Solana链上)
│   └── trader.py        # 交易器
└── lord/                 # LoRD实验
    └── experiment.py    # 正则化实验 (参考)
```

---

*文档版本: 1.0*
*最后更新: 2026-01-17*
*作者: AI Assistant*
