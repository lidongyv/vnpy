# AlphaGPT算子快速参考手册

> ⚡ AlphaGPT量化算子速查表 - VNPy集成版

---

## 🎯 核心算子（3个）

### 1. gate - 条件门控

```python
gate(condition, x, y)  # if condition > 0 then x else y
```

**应用场景**：
```python
# 流动性过滤
signal = gate(liquidity - 1000000, buy_signal, 0)

# 动量筛选
position = gate(momentum, momentum_signal, 0)

# 多条件组合
final = gate(condition1, gate(condition2, value1, value2), value3)
```

---

### 2. jump - 跳跃检测

```python
jump(feature, threshold=3.0)  # 检测超过N个σ的异常值
```

**应用场景**：
```python
# 闪崩检测
crash = jump(returns, 3.0)

# 成交量异常
vol_spike = jump(volume / ts_mean(volume, 20), 2.5)

# 价格断层
price_gap = jump(close / ts_delay(close, 1) - 1, 4.0)
```

---

### 3. decay - 指数衰减

```python
decay(feature, weights=[1.0, 0.8, 0.6])  # 加权历史值
```

**应用场景**：
```python
# 信号平滑
smooth_signal = decay(raw_signal)

# 趋势跟踪
trend = decay(returns)

# 自定义衰减
custom = decay(momentum, [1.0, 0.9, 0.8, 0.7, 0.6])
```

---

## 📊 MemeIndicators（7个）

### 1. liquidity_health - 流动性健康度

```python
liquidity_health(liquidity, fdv, scale=4.0)  # → [0, 1]
```

**阈值标准**：
- `> 0.5`: 流动性充足 ✅
- `0.2-0.5`: 流动性中等 ⚠️
- `< 0.2`: 流动性不足 ❌

**A股适配**：
```python
liquidity_health(turnover_rate * 100, market_cap, 10.0)
```

---

### 2. buy_sell_imbalance - 买卖压力

```python
buy_sell_imbalance(close, open, high, low)  # → [-1, 1]
```

**解读**：
- `> 0.5`: 强买盘 🟢
- `-0.5 to 0.5`: 平衡 ⚪
- `< -0.5`: 强卖盘 🔴

---

### 3. fomo_acceleration - FOMO加速度

```python
fomo_acceleration(volume, window=5)  # → [-5, 5]
```

**交易信号**：
- `> 1.0`: 强FOMO，追涨 🚀
- `< -1.0`: 恐慌加剧，止损 💥

---

### 4. pump_deviation - 泵出偏离度

```python
pump_deviation(close, window=20)  # → 偏离百分比
```

**风险阈值**：
- `> 0.5` (+50%): 严重超买 ⚠️
- `> 1.0` (+100%): 极端泵出 🚨
- `< -0.3` (-30%): 超卖反弹机会 💎

---

### 5. volatility_clustering - 波动率聚集

```python
volatility_clustering(close, window=10)  # → 波动率水平
```

**风险管理**：
```python
# 动态仓位调整
risk_factor = gate(vol - 0.03, 0.5, 1.0)
position = base_position * risk_factor
```

---

### 6. momentum_reversal - 动量反转

```python
momentum_reversal(close, window=5)  # → [0, 1]
```

**交易逻辑**：
```python
if reversal == 1 and momentum > 0:
    buy()  # 从下跌转上涨
elif reversal == 1 and momentum < 0:
    sell()  # 从上涨转下跌
```

---

### 7. relative_strength - 相对强度

```python
relative_strength(close, window=14)  # → [-1, 1]
```

**阈值**：
- `> 0.6`: 超买（RSI > 80）
- `-0.2 to 0.2`: 震荡区间
- `< -0.6`: 超卖（RSI < 20）

---

## 🔧 辅助函数

### robust_norm - 鲁棒归一化

```python
robust_norm(feature, clip_std=5.0)  # 基于MAD的标准化
```

**优势**：
- 对异常值不敏感
- 适合高波动资产
- 比Z-score更稳健

---

## 📝 组合策略示例

### A股选股策略

```python
dataset.add_feature("liq_health", "liquidity_health(turnover_rate * 100, market_cap, 10.0)")
dataset.add_feature("pressure", "buy_sell_imbalance(close, open, high, low)")
dataset.add_feature("momentum_rev", "momentum_reversal(close, 5)")

# 综合评分
dataset.add_feature(
    "stock_score",
    "robust_norm(pressure) + gate(liq_health - 0.2, 1, 0) * (1 - momentum_rev)"
)
```

---

### 期货CTA策略

```python
dataset.add_feature("trend", "decay(close / ts_delay(close, 20) - 1)")
dataset.add_feature("reversal", "momentum_reversal(close, 5)")
dataset.add_feature("vol", "volatility_clustering(close, 10)")

# 趋势跟踪 + 反转过滤 + 波动率调整
dataset.add_feature(
    "cta_signal",
    "gate(abs(trend) - 0.1, trend, trend * 0.5) * "
    "(1 - reversal * 0.5) * "
    "gate(vol - 0.05, 0.5, 1.0)"
)
```

---

### Meme币策略

```python
dataset.add_feature("safety", "liquidity_health(liquidity, fdv)")
dataset.add_feature("entry", "buy_sell_imbalance(close, open, high, low) * fomo_acceleration(volume)")
dataset.add_feature("exit", "pump_deviation(close, 20) + jump(returns, 3.0)")

# 安全过滤 + 入场信号 - 出场信号
dataset.add_feature(
    "meme_signal",
    "gate(safety - 0.5, entry - exit * 2, 0)"
)
```

---

## 🚀 快速入门

### 1. 安装（可选PyTorch加速）

```bash
pip install torch  # 可选，5-8倍加速
```

### 2. 导入算子

```python
from vnpy.alpha import AlphaDataset
from vnpy.alpha.dataset import (
    gate, jump, decay,
    liquidity_health, buy_sell_imbalance,
    fomo_acceleration, pump_deviation,
    volatility_clustering, momentum_reversal,
    relative_strength, robust_norm
)
```

### 3. 使用示例

```python
dataset = AlphaDataset(df, train, valid, test)

# 方式1：字符串表达式
dataset.add_feature("signal", "gate(momentum, buy_signal, 0)")

# 方式2：函数调用（高级用法）
signal = gate(momentum, buy_signal, 0)
dataset.add_feature("signal", result=signal.df)

# 准备数据
dataset.prepare_data()
```

---

## ⚡ 性能对比

| 算子 | Polars | PyTorch+JIT | 加速比 |
|-----|--------|-------------|-------|
| gate | 45 ms | 8 ms | **5.6x** |
| jump | 120 ms | 15 ms | **8.0x** |
| fomo | 150 ms | 20 ms | **7.5x** |

*测试：10万条数据，50个标的*

---

## 🎯 最佳实践

### ✅ 推荐用法

```python
# 1. 流动性保护
"gate(liquidity_health(...) - 0.5, signal, 0)"

# 2. 多层嵌套
"gate(cond1, gate(cond2, val1, val2), val3)"

# 3. 鲁棒归一化
"robust_norm(raw_feature)"

# 4. 信号平滑
"decay(noisy_signal)"
```

### ❌ 避免使用

```python
# 1. 过度嵌套（>4层）
gate(a, gate(b, gate(c, gate(d, gate(e, x, y), z), w), v), u)  # 太复杂

# 2. 循环依赖
signal_a = gate(signal_b, ...)
signal_b = gate(signal_a, ...)  # 错误！

# 3. 忘记过滤
buy_signal * volume  # 没有流动性检查，风险高
```

---

## 🔍 调试技巧

### 1. 查看因子表现

```python
dataset.show_feature_performance("your_factor")
```

### 2. 检查异常值

```python
# 添加检查因子
dataset.add_feature("outliers", "jump(returns, 3.0)")
dataset.prepare_data()

# 查看异常分布
outlier_df = dataset.raw_df.filter(pl.col("outliers") > 0)
print(outlier_df)
```

### 3. 分步测试

```python
# 分步构建复杂因子
dataset.add_feature("step1", "liquidity_health(...)")
dataset.add_feature("step2", "buy_sell_imbalance(...)")
dataset.add_feature("final", "step1 * step2")
```

---

## 📚 参考资料

### 完整文档

- [AlphaGPT算子集成到VNPy指南.md](./AlphaGPT算子集成到VNPy指南.md) - 详细说明文档
- [VNPy量化算子快速参考手册.md](./VNPy量化算子快速参考手册.md) - VNPy原生算子

### 外部资源

- AlphaGPT项目：https://github.com/imbue-bit/AlphaGPT
- VNPy官网：https://www.vnpy.com
- PyTorch JIT：https://pytorch.org/docs/stable/jit.html

---

## 🆘 常见问题

**Q: 为什么我的因子IC很低？**

A: 尝试：
1. 使用`robust_norm`标准化
2. 添加流动性过滤
3. 检查数据质量

**Q: 如何提高计算速度？**

A: 
1. 安装PyTorch使用JIT加速
2. 使用`max_workers`并行计算
3. 预计算常用因子

**Q: A股如何使用`liquidity_health`？**

A: 
```python
liquidity_health(turnover_rate * 100, market_cap, 10.0)
```

---

**版本**: v1.0  
**更新**: 2026年1月17日  
**适用**: VNPy 4.3.0+
