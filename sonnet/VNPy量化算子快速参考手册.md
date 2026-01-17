# VNPy量化算子快速参考手册

> 快速查找和使用VNPy Alpha模块中的所有量化交易算子

---

## 目录

- [时序算子 (TS)](#时序算子-ts)
- [截面算子 (CS)](#截面算子-cs)
- [数学函数](#数学函数)
- [技术指标 (TA)](#技术指标-ta)
- [常用因子组合](#常用因子组合)

---

## 时序算子 (TS)

时序算子对**单个标的的时间序列**进行计算。

### 基础时序算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **ts_delay** | `ts_delay(feature, N)` | 获取N期前的值 | `ts_delay(close, 1)` # 昨收 |
| **ts_delta** | `ts_delta(feature, N)` | 计算N期变化量 | `ts_delta(close, 1)` # 涨跌额 |
| **ts_pct_change** | `ts_pct_change(feature, N)` | 计算N期变化率 | `ts_pct_change(close, 1)` # 涨跌幅 |

### 统计类算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **ts_mean** | `ts_mean(feature, N)` | N期移动平均 | `ts_mean(close, 20)` # MA20 |
| **ts_std** | `ts_std(feature, N)` | N期标准差 | `ts_std(close, 20)` # 波动率 |
| **ts_sum** | `ts_sum(feature, N)` | N期累计和 | `ts_sum(volume, 5)` # 5日成交量 |
| **ts_prod** | `ts_prod(feature, N)` | N期累计乘积 | `ts_prod(1 + returns, 20)` # 累计收益 |
| **ts_min** | `ts_min(feature, N)` | N期最小值 | `ts_min(low, 20)` # 20日最低 |
| **ts_max** | `ts_max(feature, N)` | N期最大值 | `ts_max(high, 20)` # 20日最高 |

### 位置类算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **ts_argmin** | `ts_argmin(feature, N)` | N期最小值位置(1-N) | `ts_argmin(close, 10)` |
| **ts_argmax** | `ts_argmax(feature, N)` | N期最大值位置(1-N) | `ts_argmax(close, 10)` |
| **ts_rank** | `ts_rank(feature, N)` | 当前值在N期内的百分位排名(0-1) | `ts_rank(close, 20)` |

### 相关性算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **ts_corr** | `ts_corr(f1, f2, N)` | N期相关系数 | `ts_corr(close, volume, 20)` |
| **ts_cov** | `ts_cov(f1, f2, N)` | N期协方差 | `ts_cov(close, volume, 20)` |

### 分布特征算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **ts_skewness** | `ts_skewness(feature, N)` | N期偏度 | `ts_skewness(returns, 20)` |
| **ts_kurtosis** | `ts_kurtosis(feature, N)` | N期峰度 | `ts_kurtosis(returns, 20)` |

### 回归类算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **ts_regression** | `ts_regression(Y, X, N, rettype)` | 线性回归 | `ts_regression(close, range(20), 20, 0)` |

**ts_regression 返回类型 (rettype):**
- `0`: 截距
- `1`: 斜率
- `2`: R方
- `3`: 残差
- `4`: 预测值
- `5`: 标准误差

---

## 截面算子 (CS)

截面算子对**同一时间点的多个标的**进行横向比较。

### 基础截面算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **cs_rank** | `cs_rank(feature)` | 截面排名 | `cs_rank(close)` # 价格排名 |
| **cs_mean** | `cs_mean(feature)` | 截面均值 | `cs_mean(close)` # 平均价格 |
| **cs_std** | `cs_std(feature)` | 截面标准差 | `cs_std(returns)` # 离散度 |
| **cs_sum** | `cs_sum(feature)` | 截面求和 | `cs_sum(volume)` # 总成交量 |

### 标准化算子

| 算子 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **cs_scale** | `cs_scale(feature)` | 按绝对值之和标准化（权重和为1） | `cs_scale(signal)` |
| **cs_zscore** | `cs_zscore(feature)` | Z-score标准化 | `cs_zscore(momentum)` |

---

## 数学函数

### 基础数学运算

| 函数 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **log** | `log(feature)` | 自然对数 | `log(close)` |
| **abs** | `abs(feature)` | 绝对值 | `abs(returns)` |
| **sign** | `sign(feature)` | 符号函数(1/0/-1) | `sign(returns)` |
| **sqrt** | `sqrt(feature)` | 平方根 | `sqrt(volume)` |

### 比较函数

| 函数 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **less** | `less(f1, f2)` | 返回较小值 | `less(close, 100)` |
| **greater** | `greater(f1, f2)` | 返回较大值 | `greater(close, 50)` |

### 条件函数

| 函数 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **quesval** | `quesval(threshold, f1, f2, f3)` | if threshold < f1 then f2 else f3 | `quesval(0, returns, 1, -1)` |
| **quesval2** | `quesval2(threshold_feature, f1, f2, f3)` | threshold为变量的条件函数 | `quesval2(ma5, close, 1, 0)` |

### 幂运算

| 函数 | 语法 | 说明 | 示例 |
|-----|------|------|------|
| **pow1** | `pow1(base, exp)` | base^exp（exp为常数，支持负数base） | `pow1(close, 2)` |
| **pow2** | `pow2(base, exp)` | base^exp（exp为变量） | `pow2(close, exponent)` |

---

## 技术指标 (TA)

基于TA-Lib库的经典技术指标。

### 趋势指标

| 指标 | 语法 | 说明 | 参数范围 |
|-----|------|------|---------|
| **ta_sma** | `ta_sma(close, N)` | 简单移动平均 | N: 周期 |
| **ta_ema** | `ta_ema(close, N)` | 指数移动平均 | N: 周期 |
| **ta_wma** | `ta_wma(close, N)` | 加权移动平均 | N: 周期 |

### 动量指标

| 指标 | 语法 | 说明 | 参数范围 |
|-----|------|------|---------|
| **ta_rsi** | `ta_rsi(close, N)` | 相对强弱指标 | N: 14（典型）<br>值域: 0-100 |
| **ta_mom** | `ta_mom(close, N)` | 动量指标 | N: 10（典型） |
| **ta_roc** | `ta_roc(close, N)` | 变动率指标 | N: 12（典型） |

### 波动率指标

| 指标 | 语法 | 说明 | 参数范围 |
|-----|------|------|---------|
| **ta_atr** | `ta_atr(high, low, close, N)` | 平均真实波幅 | N: 14（典型） |
| **ta_natr** | `ta_natr(high, low, close, N)` | 标准化ATR | N: 14（典型） |

### 成交量指标

| 指标 | 语法 | 说明 | 参数范围 |
|-----|------|------|---------|
| **ta_ad** | `ta_ad(high, low, close, volume)` | 累积/派发线 | - |
| **ta_obv** | `ta_obv(close, volume)` | 能量潮 | - |

---

## 常用因子组合

### 动量因子

```python
# 1. 简单动量
momentum_20 = "close / ts_delay(close, 20) - 1"

# 2. 加速动量
acceleration = "ts_delta(close, 5) - ts_delay(ts_delta(close, 5), 5)"

# 3. 相对强度指标
rsi_14 = "ta_rsi(close, 14)"

# 4. 动量排名
momentum_rank = "cs_rank(close / ts_delay(close, 20) - 1)"

# 5. 反转因子
reversal = "(-1) * (close / ts_delay(close, 1) - 1)"

# 6. 加权动量
weighted_momentum = "ts_sum(close / ts_delay(close, 1) - 1, 20) / 20"
```

### 波动率因子

```python
# 1. 历史波动率
volatility = "ts_std(close / ts_delay(close, 1) - 1, 20)"

# 2. 相对波动率
relative_vol = "ts_std(close, 20) / cs_mean(ts_std(close, 20))"

# 3. ATR指标
atr_14 = "ta_atr(high, low, close, 14)"

# 4. 波动率变化
vol_change = "ts_std(close, 20) / ts_delay(ts_std(close, 20), 20) - 1"

# 5. 高低波幅
hl_range = "(high - low) / close"

# 6. 真实波幅
true_range = "greater(high - low, abs(high - ts_delay(close, 1)))"
```

### 量价因子

```python
# 1. 量价相关性
volume_price_corr = "ts_corr(close, volume, 20)"

# 2. 成交量变化
volume_change = "volume / ts_mean(volume, 20) - 1"

# 3. 价格加权成交量
vwap_deviation = "(close - vwap) / vwap"

# 4. 成交量动量
volume_momentum = "volume / ts_delay(volume, 5) - 1"

# 5. 能量潮
obv = "ta_obv(close, volume)"

# 6. 量价背离
vp_divergence = "sign(ts_delta(close, 5)) != sign(ts_delta(volume, 5))"
```

### 趋势因子

```python
# 1. 双均线
ma_cross = "ts_mean(close, 5) / ts_mean(close, 20) - 1"

# 2. 价格相对位置
price_position = "(close - ts_min(low, 20)) / (ts_max(high, 20) - ts_min(low, 20))"

# 3. 均线偏离度
ma_deviation = "(close - ts_mean(close, 20)) / ts_mean(close, 20)"

# 4. 趋势强度
trend_strength = "ts_regression(close, range(20), 20, 1)"  # 斜率

# 5. 新高新低
new_high = "close == ts_max(high, 20)"
new_low = "close == ts_min(low, 20)"

# 6. 突破信号
breakout = "(close - ts_max(high, 20)) / ts_max(high, 20)"
```

### 反转因子

```python
# 1. 短期反转
short_reversal = "(-1) * ts_sum(close / ts_delay(close, 1) - 1, 5)"

# 2. 隔夜反转
overnight_reversal = "(open / ts_delay(close, 1) - 1) * (-1)"

# 3. 超买超卖
overbought = "ta_rsi(close, 14) > 70"
oversold = "ta_rsi(close, 14) < 30"

# 4. 均值回归
mean_reversion = "(close - ts_mean(close, 20)) / ts_std(close, 20) * (-1)"

# 5. 振荡器
oscillator = "(close - ts_mean(close, 20)) / (ts_max(high, 20) - ts_min(low, 20))"
```

### 质量因子

```python
# 1. 价格稳定性
price_stability = "1 / ts_std(close / ts_delay(close, 1) - 1, 60)"

# 2. 收益质量
return_quality = "ts_mean(close / ts_delay(close, 1) - 1, 20) / ts_std(close / ts_delay(close, 1) - 1, 20)"

# 3. 收益偏度
return_skewness = "ts_skewness(close / ts_delay(close, 1) - 1, 60)"

# 4. 收益峰度
return_kurtosis = "ts_kurtosis(close / ts_delay(close, 1) - 1, 60)"

# 5. 流动性
liquidity = "volume * close"

# 6. 换手率稳定性
turnover_stability = "1 / ts_std(volume / ts_mean(volume, 60), 20)"
```

### 市场微观结构因子

```python
# 1. 买卖压力
buy_pressure = "(close - low) / (high - low)"
sell_pressure = "(high - close) / (high - low)"

# 2. 价格效率
price_efficiency = "abs(close - ts_delay(close, 10)) / ts_sum(abs(ts_delta(close, 1)), 10)"

# 3. 波动率不对称
vol_asymmetry = "ts_std(quesval(0, returns, returns, 0), 20) / ts_std(quesval(0, returns, 0, returns), 20)"

# 4. 尾部风险
tail_risk = "less(close / ts_delay(close, 1) - 1, ts_mean(close / ts_delay(close, 1) - 1, 20) - 2 * ts_std(close / ts_delay(close, 1) - 1, 20))"
```

---

## 因子组合技巧

### 1. 多因子合成

```python
# 等权重合成
composite_factor = "(factor1 + factor2 + factor3) / 3"

# 加权合成
weighted_factor = "0.5 * factor1 + 0.3 * factor2 + 0.2 * factor3"

# 排名合成
rank_composite = "(cs_rank(factor1) + cs_rank(factor2) + cs_rank(factor3)) / 3"
```

### 2. 因子正交化

```python
# 去除市场风险
market_neutral = "factor - ts_regression(factor, market_returns, 20, 4)"

# 去除行业影响
industry_neutral = "factor - cs_mean(factor)"
```

### 3. 因子标准化

```python
# Z-score标准化
zscore_factor = "(factor - cs_mean(factor)) / cs_std(factor)"

# 排名标准化
rank_factor = "cs_rank(factor) / cs_sum(cs_rank(factor))"

# Min-Max标准化
minmax_factor = "(factor - cs_min(factor)) / (cs_max(factor) - cs_min(factor))"
```

### 4. 因子增强

```python
# 趋势增强
trend_enhanced = "factor * sign(ts_mean(factor, 5))"

# 波动率调整
vol_adjusted = "factor / ts_std(factor, 20)"

# 动量增强
momentum_enhanced = "factor * (1 + ts_mean(ts_delta(factor, 1), 5))"
```

---

## Alpha101因子示例

### 精选高效因子

```python
# Alpha1: 排名动量
alpha1 = "cs_rank(ts_argmax(pow1(quesval(0, returns, close, ts_std(returns, 20)), 2.0), 5)) - 0.5"

# Alpha2: 成交量-价格相关性
alpha2 = "(-1) * ts_corr(cs_rank(ts_delta(log(volume), 2)), cs_rank((close - open) / open), 6)"

# Alpha3: 开盘价-成交量相关性
alpha3 = "ts_corr(cs_rank(open), cs_rank(volume), 10) * -1"

# Alpha6: 开盘价-成交量相关性
alpha6 = "(-1) * ts_corr(open, volume, 10)"

# Alpha12: 成交量-价格变化
alpha12 = "sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1))"

# Alpha13: 价格-成交量协方差排名
alpha13 = "-1 * cs_rank(ts_cov(cs_rank(close), cs_rank(volume), 5))"
```

---

## 因子性能评估

### 1. IC值（信息系数）

```python
# 计算因子与未来收益的相关性
ic = ts_corr(factor, ts_delay(returns, -1), 20)
```

### 2. RankIC（排名信息系数）

```python
# 计算因子排名与收益排名的相关性
rank_ic = ts_corr(cs_rank(factor), cs_rank(ts_delay(returns, -1)), 20)
```

### 3. 因子单调性

```python
# 检查因子值与收益的单调关系
# 使用dataset.show_feature_performance(factor_name)
```

### 4. 因子衰减

```python
# 检查因子预测能力随时间的衰减
ic_1d = ts_corr(factor, ts_delay(returns, -1), 20)
ic_5d = ts_corr(factor, ts_delay(ts_sum(returns, 5), -5), 20)
ic_10d = ts_corr(factor, ts_delay(ts_sum(returns, 10), -10), 20)
```

---

## 调试技巧

### 1. 检查缺失值

```python
# 使用DropNaLabelProcessor去除标签缺失的样本
from vnpy.alpha.dataset.processor import DropNaLabelProcessor
dataset.add_processor("learn", DropNaLabelProcessor())
```

### 2. 检查异常值

```python
# 使用WinsorizeProcessor限制极端值
from vnpy.alpha.dataset.processor import WinsorizeProcessor
dataset.add_processor("learn", WinsorizeProcessor(0.01, 0.99))
```

### 3. 可视化因子分布

```python
# 查看因子的IC曲线和分层收益
dataset.show_feature_performance("your_factor_name")
```

### 4. 因子相关性检查

```python
# 计算多个因子之间的相关性
correlation_matrix = "ts_corr(factor1, factor2, 60)"
```

---

## 性能优化建议

### 1. 并行计算

```python
# 使用max_workers参数并行计算因子
dataset.prepare_data(max_workers=8)
```

### 2. 数据类型优化

```python
# Polars自动优化数据类型，无需手动干预
```

### 3. 避免重复计算

```python
# 将中间结果保存为新特征
dataset.add_feature("returns", "close / ts_delay(close, 1) - 1")
dataset.add_feature("momentum", "ts_sum(returns, 20)")  # 使用已计算的returns
```

### 4. 减少数据量

```python
# 使用filters参数筛选成分股
dataset.prepare_data(filters=component_filters)
```

---

## 常见错误与解决

### 错误1: 表达式语法错误

```python
# 错误示例
"close / ts_delay(close 1) - 1"  # 缺少逗号

# 正确示例
"close / ts_delay(close, 1) - 1"
```

### 错误2: 窗口期过长导致数据不足

```python
# 如果数据只有100天，避免使用超过100的窗口
ts_mean(close, 200)  # 错误

# 解决方案：调整窗口大小或增加历史数据
ts_mean(close, 60)   # 正确
```

### 错误3: 除零错误

```python
# 可能除零的表达式
"factor1 / factor2"

# 安全的写法
"quesval(0.001, abs(factor2), factor1 / factor2, 0)"
```

### 错误4: 类型不匹配

```python
# 错误：截面算子用于时序
"ts_corr(cs_rank(close), volume, 20)"  # cs_rank结果不应直接用于ts_corr

# 正确：先时序后截面
"cs_rank(ts_corr(close, volume, 20))"
```

---

## 快速查询索引

### 按功能分类

- **滞后与差分**: ts_delay, ts_delta, ts_pct_change
- **统计量**: ts_mean, ts_std, ts_sum, ts_min, ts_max
- **排名**: ts_rank, cs_rank
- **相关性**: ts_corr, ts_cov
- **技术指标**: ta_rsi, ta_atr, ta_sma, ta_ema
- **数学运算**: log, abs, sign, pow1, pow2
- **条件逻辑**: quesval, quesval2, less, greater

### 按应用场景分类

- **趋势跟踪**: ts_mean, ts_regression, ma_cross
- **均值回归**: mean_reversion, oscillator
- **动量策略**: momentum, acceleration, rsi
- **波动率**: volatility, atr, vol_change
- **量价分析**: volume_price_corr, obv, vp_divergence
- **市场中性**: market_neutral, cs_scale

---

## 参考资源

- **VNPy官方文档**: https://www.vnpy.com/docs
- **Alpha101论文**: "101 Formulaic Alphas" by WorldQuant
- **Qlib项目**: https://github.com/microsoft/qlib
- **TA-Lib文档**: https://ta-lib.org/

---

**最后更新**: 2026年1月

**版本**: v4.3.0

**使用提示**: 建议收藏本手册，在开发因子时快速查询。
