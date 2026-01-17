"""
AlphaGPT Operators - 从AlphaGPT项目移植的量化算子

该模块包含从AlphaGPT项目中提取的高效GPU加速量化算子,
已适配vnpy的DataProxy架构，支持表达式引擎调用。

原始来源: https://github.com/imbue-bit/AlphaGPT
"""

import numpy as np
import polars as pl
from scipy import stats

from .utility import DataProxy


# =============================================================================
# 基础运算算子 (来自 AlphaGPT ops.py)
# =============================================================================

def gpt_gate(condition: DataProxy, x: DataProxy, y: DataProxy) -> DataProxy:
    """
    条件选择算子 (Gate Operator)
    
    根据条件选择返回x或y的值:
    - 当 condition > 0 时返回 x
    - 当 condition <= 0 时返回 y
    
    参数:
        condition: 条件DataProxy
        x: 条件为真时的值
        y: 条件为假时的值
    
    返回:
        DataProxy: 条件选择结果
        
    示例:
        # 当收益率为正时取动量，否则取波动率
        "gpt_gate(close - ts_delay(close, 1), momentum, volatility)"
    """
    df_merged = condition.df.join(x.df, on=["datetime", "vt_symbol"], suffix="_x")
    df_merged = df_merged.join(y.df, on=["datetime", "vt_symbol"], suffix="_y")
    
    df: pl.DataFrame = df_merged.with_columns(
        pl.when(pl.col("data") > 0)
        .then(pl.col("data_x"))
        .otherwise(pl.col("data_y"))
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_jump(feature: DataProxy, threshold: float = 3.0) -> DataProxy:
    """
    跳跃检测算子 (Jump Detector)
    
    检测异常跳跃信号，使用Z-Score标准化后检测超过阈值的跳跃:
    - 计算时间序列的Z-Score
    - 返回超过阈值部分的值 (ReLU截断)
    
    参数:
        feature: 输入特征
        threshold: Z-Score阈值，默认3.0 (3个标准差)
    
    返回:
        DataProxy: 跳跃信号，正常情况为0，异常跳跃时为正值
        
    用途:
        - 检测价格异常波动
        - 识别突发行情
        - 过滤噪音交易信号
    """
    df: pl.DataFrame = feature.df.with_columns([
        pl.col("data").mean().over("vt_symbol").alias("mean"),
        pl.col("data").std().over("vt_symbol").alias("std")
    ])
    
    df = df.with_columns(
        ((pl.col("data") - pl.col("mean")) / (pl.col("std") + 1e-6)).alias("zscore")
    )
    
    df = df.with_columns(
        pl.when(pl.col("zscore") > threshold)
        .then(pl.col("zscore") - threshold)
        .otherwise(0.0)
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_decay(feature: DataProxy, decay_weights: list[float] = None) -> DataProxy:
    """
    指数衰减加权算子 (Decay Operator)
    
    对时间序列应用指数衰减权重，近期数据权重更高:
    - 默认权重: [1.0, 0.8, 0.6] (当前、1期前、2期前)
    - 支持自定义衰减权重
    
    参数:
        feature: 输入特征
        decay_weights: 衰减权重列表，默认[1.0, 0.8, 0.6]
    
    返回:
        DataProxy: 衰减加权后的值
        
    用途:
        - 构建指数加权移动平均
        - 强调近期信号的重要性
        - 平滑时间序列
    """
    if decay_weights is None:
        decay_weights = [1.0, 0.8, 0.6]
    
    # 构建衰减表达式
    exprs = []
    for i, w in enumerate(decay_weights):
        if i == 0:
            exprs.append(pl.col("data") * w)
        else:
            exprs.append(pl.col("data").shift(i).over("vt_symbol") * w)
    
    df: pl.DataFrame = feature.df.with_columns(
        pl.sum_horizontal(exprs).alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_max_n(feature: DataProxy, window: int) -> DataProxy:
    """
    N期滚动最大值算子
    
    计算过去N期的最大值 (包含当期)
    
    参数:
        feature: 输入特征
        window: 窗口大小
    
    返回:
        DataProxy: N期最大值
    """
    df: pl.DataFrame = feature.df.select(
        pl.col("datetime"),
        pl.col("vt_symbol"),
        pl.col("data").rolling_max(window, min_samples=1).over("vt_symbol")
    )
    return DataProxy(df)


# =============================================================================
# Meme/加密货币专用因子 (来自 AlphaGPT factors.py)
# =============================================================================

def gpt_liquidity_health(liquidity: DataProxy, fdv: DataProxy) -> DataProxy:
    """
    流动性健康度因子 (Liquidity Health Score)
    
    衡量流动性相对于完全稀释估值(FDV)的健康程度:
    - ratio = liquidity / fdv
    - 返回 clamp(ratio * 4, 0, 1)
    
    参数:
        liquidity: 流动性数据
        fdv: 完全稀释估值
    
    返回:
        DataProxy: 0-1范围的健康度分数
        
    解释:
        - 0.0: 流动性极差，可能无法交易
        - 0.5: 中等流动性
        - 1.0: 流动性充足
        
    用途:
        - 过滤低流动性标的
        - 评估交易滑点风险
        - 作为仓位规模的调节因子
    """
    df_merged = liquidity.df.join(fdv.df, on=["datetime", "vt_symbol"], suffix="_fdv")
    
    df: pl.DataFrame = df_merged.with_columns(
        (pl.col("data") / (pl.col("data_fdv") + 1e-6) * 4.0)
        .clip(0.0, 1.0)
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_buy_sell_imbalance(close: DataProxy, open_: DataProxy, 
                           high: DataProxy, low: DataProxy) -> DataProxy:
    """
    买卖失衡因子 (Buy-Sell Imbalance)
    
    基于K线形态计算买卖力量失衡:
    - body = close - open (实体)
    - range = high - low (振幅)
    - strength = body / range
    - 返回 tanh(strength * 3) 归一化到 [-1, 1]
    
    参数:
        close: 收盘价
        open_: 开盘价
        high: 最高价
        low: 最低价
    
    返回:
        DataProxy: -1到1之间的失衡度
        
    解释:
        - 正值: 买方力量占优
        - 负值: 卖方力量占优
        - 接近0: 买卖均衡
    """
    # 合并所有价格数据
    df_merged = close.df.rename({"data": "close"})
    df_merged = df_merged.join(
        open_.df.rename({"data": "open"}), 
        on=["datetime", "vt_symbol"]
    )
    df_merged = df_merged.join(
        high.df.rename({"data": "high"}), 
        on=["datetime", "vt_symbol"]
    )
    df_merged = df_merged.join(
        low.df.rename({"data": "low"}), 
        on=["datetime", "vt_symbol"]
    )
    
    df: pl.DataFrame = df_merged.with_columns(
        ((pl.col("close") - pl.col("open")) / 
         (pl.col("high") - pl.col("low") + 1e-9) * 3.0)
        .tanh()
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_fomo_acceleration(volume: DataProxy, window: int = 5) -> DataProxy:
    """
    FOMO加速度因子 (FOMO Acceleration)
    
    检测成交量的加速变化，用于识别FOMO情绪:
    - vol_chg = (volume - volume_prev) / volume_prev  (成交量变化率)
    - acc = vol_chg - vol_chg_prev  (变化率的变化 = 加速度)
    - 返回 clamp(acc, -5, 5)
    
    参数:
        volume: 成交量
        window: 平滑窗口 (保留参数，当前未使用)
    
    返回:
        DataProxy: FOMO加速度，正值表示加速放量
        
    用途:
        - 识别市场恐慌或贪婪情绪
        - 检测成交量异常放大
        - 作为趋势加速的信号
    """
    df: pl.DataFrame = volume.df.with_columns([
        pl.col("data").shift(1).over("vt_symbol").alias("vol_prev")
    ])
    
    df = df.with_columns(
        ((pl.col("data") - pl.col("vol_prev")) / (pl.col("vol_prev") + 1.0))
        .alias("vol_chg")
    )
    
    df = df.with_columns(
        pl.col("vol_chg").shift(1).over("vt_symbol").alias("vol_chg_prev")
    )
    
    df = df.with_columns(
        (pl.col("vol_chg") - pl.col("vol_chg_prev"))
        .clip(-5.0, 5.0)
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_pump_deviation(close: DataProxy, window: int = 20) -> DataProxy:
    """
    泵偏离因子 (Pump Deviation)
    
    计算价格相对于移动平均线的偏离程度:
    - ma = 移动平均线
    - dev = (close - ma) / ma
    
    参数:
        close: 收盘价
        window: 移动平均窗口，默认20
    
    返回:
        DataProxy: 偏离度，正值表示价格高于均线
        
    用途:
        - 识别超买/超卖状态
        - 检测价格异常偏离
        - 均值回归策略信号
    """
    df: pl.DataFrame = close.df.with_columns(
        pl.col("data").rolling_mean(window, min_samples=1)
        .over("vt_symbol").alias("ma")
    )
    
    df = df.with_columns(
        ((pl.col("data") - pl.col("ma")) / (pl.col("ma") + 1e-9))
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_volatility_clustering(close: DataProxy, window: int = 10) -> DataProxy:
    """
    波动率聚类因子 (Volatility Clustering)
    
    检测波动率聚类模式，基于收益率平方的移动平均:
    - ret = log(close / close_prev)
    - ret_sq = ret^2
    - vol = sqrt(rolling_mean(ret_sq))
    
    参数:
        close: 收盘价
        window: 滚动窗口，默认10
    
    返回:
        DataProxy: 实现波动率
        
    用途:
        - 波动率预测
        - 风险度量
        - 期权定价参考
    """
    df: pl.DataFrame = close.df.with_columns(
        pl.col("data").shift(1).over("vt_symbol").alias("prev_close")
    )
    
    df = df.with_columns(
        (pl.col("data") / (pl.col("prev_close") + 1e-9)).log().alias("ret")
    )
    
    df = df.with_columns(
        (pl.col("ret") ** 2).alias("ret_sq")
    )
    
    df = df.with_columns(
        (pl.col("ret_sq").rolling_mean(window, min_samples=1)
         .over("vt_symbol") + 1e-9).sqrt()
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_momentum_reversal(close: DataProxy, window: int = 5) -> DataProxy:
    """
    动量反转因子 (Momentum Reversal Signal)
    
    检测动量方向发生反转的信号:
    - mom = sum(ret, window)  (窗口内累计动量)
    - reversal = 1 if mom * mom_prev < 0 else 0
    
    参数:
        close: 收盘价
        window: 动量计算窗口，默认5
    
    返回:
        DataProxy: 反转信号，1表示发生反转，0表示未反转
        
    用途:
        - 趋势反转检测
        - 入场/出场信号
        - 与其他因子组合使用
    """
    df: pl.DataFrame = close.df.with_columns(
        pl.col("data").shift(1).over("vt_symbol").alias("prev_close")
    )
    
    df = df.with_columns(
        (pl.col("data") / (pl.col("prev_close") + 1e-9)).log().alias("ret")
    )
    
    df = df.with_columns(
        pl.col("ret").rolling_sum(window, min_samples=1)
        .over("vt_symbol").alias("mom")
    )
    
    df = df.with_columns(
        pl.col("mom").shift(1).over("vt_symbol").alias("mom_prev")
    )
    
    df = df.with_columns(
        pl.when(pl.col("mom") * pl.col("mom_prev") < 0)
        .then(1.0)
        .otherwise(0.0)
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_relative_strength(close: DataProxy, high: DataProxy, 
                          low: DataProxy, window: int = 14) -> DataProxy:
    """
    相对强度因子 (Relative Strength Index - RSI变体)
    
    改进的RSI指标，输出归一化到[-1, 1]:
    - gains = max(ret, 0)
    - losses = max(-ret, 0)
    - rs = avg_gain / avg_loss
    - rsi = 100 - 100/(1+rs)
    - 返回 (rsi - 50) / 50  归一化
    
    参数:
        close: 收盘价
        high: 最高价 (保留参数)
        low: 最低价 (保留参数)
        window: RSI计算窗口，默认14
    
    返回:
        DataProxy: -1到1之间的相对强度
        
    解释:
        - 正值: 上涨动能强
        - 负值: 下跌动能强
        - 接近0: 多空均衡
    """
    df: pl.DataFrame = close.df.with_columns(
        pl.col("data").shift(1).over("vt_symbol").alias("prev_close")
    )
    
    df = df.with_columns(
        (pl.col("data") - pl.col("prev_close")).alias("ret")
    )
    
    df = df.with_columns([
        pl.when(pl.col("ret") > 0).then(pl.col("ret")).otherwise(0.0).alias("gain"),
        pl.when(pl.col("ret") < 0).then(-pl.col("ret")).otherwise(0.0).alias("loss")
    ])
    
    df = df.with_columns([
        pl.col("gain").rolling_mean(window, min_samples=1).over("vt_symbol").alias("avg_gain"),
        pl.col("loss").rolling_mean(window, min_samples=1).over("vt_symbol").alias("avg_loss")
    ])
    
    df = df.with_columns(
        ((pl.col("avg_gain") + 1e-9) / (pl.col("avg_loss") + 1e-9)).alias("rs")
    )
    
    df = df.with_columns(
        ((100.0 - 100.0 / (1.0 + pl.col("rs"))) - 50.0) / 50.0
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


# =============================================================================
# 数据预处理因子 (来自 AlphaGPT factors.py)
# =============================================================================

def gpt_robust_norm(feature: DataProxy, clip_value: float = 5.0) -> DataProxy:
    """
    稳健标准化 (Robust Normalization)
    
    使用中位数和MAD(中位数绝对偏差)进行标准化，
    比标准Z-Score更抗异常值:
    - median = 中位数
    - mad = median(|x - median|)
    - norm = (x - median) / mad
    - 返回 clamp(norm, -clip_value, clip_value)
    
    参数:
        feature: 输入特征
        clip_value: 截断阈值，默认5.0
    
    返回:
        DataProxy: 稳健标准化后的值
        
    优势:
        - 对异常值不敏感
        - 保持数据分布的形状
        - 适合金融数据预处理
    """
    df: pl.DataFrame = feature.df.with_columns([
        pl.col("data").median().over("vt_symbol").alias("median")
    ])
    
    df = df.with_columns(
        (pl.col("data") - pl.col("median")).abs().alias("abs_dev")
    )
    
    df = df.with_columns(
        pl.col("abs_dev").median().over("vt_symbol").alias("mad")
    )
    
    df = df.with_columns(
        ((pl.col("data") - pl.col("median")) / (pl.col("mad") + 1e-6))
        .clip(-clip_value, clip_value)
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_cs_robust_norm(feature: DataProxy, clip_value: float = 5.0) -> DataProxy:
    """
    截面稳健标准化 (Cross-Sectional Robust Normalization)
    
    在截面维度(同一时间点的不同标的)进行稳健标准化
    
    参数:
        feature: 输入特征
        clip_value: 截断阈值，默认5.0
    
    返回:
        DataProxy: 截面稳健标准化后的值
    """
    df: pl.DataFrame = feature.df.with_columns([
        pl.col("data").median().over("datetime").alias("median")
    ])
    
    df = df.with_columns(
        (pl.col("data") - pl.col("median")).abs().alias("abs_dev")
    )
    
    df = df.with_columns(
        pl.col("abs_dev").median().over("datetime").alias("mad")
    )
    
    df = df.with_columns(
        ((pl.col("data") - pl.col("median")) / (pl.col("mad") + 1e-6))
        .clip(-clip_value, clip_value)
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


# =============================================================================
# 高级数据处理 (来自 AlphaGPT processor.py)
# =============================================================================

def gpt_log_return(close: DataProxy) -> DataProxy:
    """
    对数收益率
    
    计算对数收益率: log(close / close_prev)
    
    参数:
        close: 收盘价
    
    返回:
        DataProxy: 对数收益率
    """
    df: pl.DataFrame = close.df.with_columns(
        pl.col("data").shift(1).over("vt_symbol").alias("prev")
    )
    
    df = df.with_columns(
        (pl.col("data") / (pl.col("prev") + 1e-9)).log()
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_vol_shock(volume: DataProxy, window: int = 20) -> DataProxy:
    """
    成交量冲击因子 (Volume Shock)
    
    当前成交量相对于历史均值的倍数:
    - vol_ma = rolling_mean(volume, window)
    - vol_shock = volume / vol_ma
    
    参数:
        volume: 成交量
        window: 均值计算窗口，默认20
    
    返回:
        DataProxy: 成交量倍数
        
    解释:
        - > 1: 成交量放大
        - < 1: 成交量萎缩
        - = 1: 正常水平
    """
    df: pl.DataFrame = volume.df.with_columns(
        pl.col("data").rolling_mean(window, min_samples=1)
        .over("vt_symbol").alias("vol_ma")
    )
    
    df = df.with_columns(
        (pl.col("data") / (pl.col("vol_ma") + 1e-6))
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_trend(close: DataProxy, window: int = 60) -> DataProxy:
    """
    趋势方向因子 (Trend Direction)
    
    判断价格相对于长期均线的位置:
    - ma = rolling_mean(close, window)
    - trend = 1 if close > ma else -1
    
    参数:
        close: 收盘价
        window: 均线周期，默认60
    
    返回:
        DataProxy: 趋势方向，1为上涨趋势，-1为下跌趋势
    """
    df: pl.DataFrame = close.df.with_columns(
        pl.col("data").rolling_mean(window, min_samples=1)
        .over("vt_symbol").alias("ma")
    )
    
    df = df.with_columns(
        pl.when(pl.col("data") > pl.col("ma"))
        .then(1.0)
        .otherwise(-1.0)
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_high_low_range(high: DataProxy, low: DataProxy, close: DataProxy) -> DataProxy:
    """
    高低点振幅比 (High-Low Range Ratio)
    
    计算K线振幅相对于收盘价的比例:
    - range = (high - low) / close
    
    参数:
        high: 最高价
        low: 最低价
        close: 收盘价
    
    返回:
        DataProxy: 振幅比
    """
    df_merged = high.df.rename({"data": "high"})
    df_merged = df_merged.join(
        low.df.rename({"data": "low"}),
        on=["datetime", "vt_symbol"]
    )
    df_merged = df_merged.join(
        close.df.rename({"data": "close"}),
        on=["datetime", "vt_symbol"]
    )
    
    df: pl.DataFrame = df_merged.with_columns(
        ((pl.col("high") - pl.col("low")) / (pl.col("close") + 1e-9))
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_close_position(close: DataProxy, high: DataProxy, low: DataProxy) -> DataProxy:
    """
    收盘价位置因子 (Close Position in Range)
    
    收盘价在当日振幅中的相对位置:
    - position = (close - low) / (high - low)
    
    参数:
        close: 收盘价
        high: 最高价
        low: 最低价
    
    返回:
        DataProxy: 0-1之间的位置值
        
    解释:
        - 接近1: 收盘在高点附近，看涨
        - 接近0: 收盘在低点附近，看跌
        - 0.5: 收盘在中间位置
    """
    df_merged = close.df.rename({"data": "close"})
    df_merged = df_merged.join(
        high.df.rename({"data": "high"}),
        on=["datetime", "vt_symbol"]
    )
    df_merged = df_merged.join(
        low.df.rename({"data": "low"}),
        on=["datetime", "vt_symbol"]
    )
    
    df: pl.DataFrame = df_merged.with_columns(
        ((pl.col("close") - pl.col("low")) / 
         (pl.col("high") - pl.col("low") + 1e-9))
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)


def gpt_volume_trend(volume: DataProxy) -> DataProxy:
    """
    成交量趋势因子 (Volume Trend)
    
    计算成交量的变化趋势:
    - vol_trend = (volume - volume_prev) / volume_prev
    
    参数:
        volume: 成交量
    
    返回:
        DataProxy: 成交量变化率
    """
    df: pl.DataFrame = volume.df.with_columns(
        pl.col("data").shift(1).over("vt_symbol").alias("vol_prev")
    )
    
    df = df.with_columns(
        ((pl.col("data") - pl.col("vol_prev")) / (pl.col("vol_prev") + 1.0))
        .alias("data")
    ).select(["datetime", "vt_symbol", "data"])
    
    return DataProxy(df)
