# VeighNa (vnpy) 量化交易快速入门 - 从零到实盘

> 本指南将一步步带你从安装到完成第一个量化策略的回测和实盘部署

---

## 目录

1. [环境准备](#第一步-环境准备)
2. [安装vnpy](#第二步-安装vnpy)
3. [准备数据](#第三步-准备数据)
4. [创建因子](#第四步-创建因子)
5. [训练模型](#第五步-训练模型)
6. [策略回测](#第六步-策略回测)
7. [优化策略](#第七步-优化策略)
8. [实盘部署](#第八步-实盘部署)
9. [常见问题](#第九步-常见问题解答)

---

## 第一步: 环境准备

### 1.1 安装Python

**Windows系统:**

1. 下载 Python 3.13 (64位): https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"
3. 验证安装:
```powershell
python --version
# 应显示: Python 3.13.x
```

**推荐**: 使用VeighNa官方Python发行版 **VeighNa Studio-4.3.0**

### 1.2 创建虚拟环境

```powershell
# 创建项目目录
mkdir G:\vnpy_project
cd G:\vnpy_project

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 激活后提示符变为: (venv) PS G:\vnpy_project>
```

### 1.3 升级pip

```powershell
python -m pip install --upgrade pip wheel setuptools
```

---

## 第二步: 安装vnpy

### 2.1 安装TA-Lib

TA-Lib是技术分析库，需要预编译版本:

```powershell
pip install --extra-index-url https://pypi.vnpy.com ta_lib==0.6.4
```

### 2.2 安装vnpy核心

```powershell
# 进入vnpy源码目录
cd G:\vnpy-1

# 安装核心模块
pip install .

# 安装Alpha量化投研模块 (推荐)
pip install ".[alpha]"
```

### 2.3 验证安装

```python
# 运行Python
python

>>> import vnpy
>>> print(vnpy.__version__)
4.3.0

>>> from vnpy.alpha import AlphaLab, AlphaDataset
>>> print("Alpha模块加载成功!")
```

### 2.4 安装可选依赖

```powershell
# 数据源适配器 (根据需要选择)
pip install vnpy_rqdata      # RQData
pip install vnpy_xt          # 迅投研
pip install vnpy_tushare     # TuShare

# 交易网关 (根据需要选择)
pip install vnpy_ctp         # CTP期货
pip install vnpy_ib          # Interactive Brokers
pip install vnpy_xtp         # XTP证券

# 数据库适配器 (根据需要选择)
pip install vnpy_sqlite      # SQLite (默认)
pip install vnpy_mysql       # MySQL
pip install vnpy_mongodb     # MongoDB
```

---

## 第三步: 准备数据

### 3.1 创建研究实验室

```python
from vnpy.alpha import AlphaLab

# 创建实验室 (自动创建目录结构)
lab = AlphaLab("G:/vnpy_project/lab/my_first_strategy")

# 目录结构:
# G:/vnpy_project/lab/my_first_strategy/
# ├── daily/        # 日线数据
# ├── minute/       # 分钟数据
# ├── component/    # 指数成分股
# ├── dataset/      # 数据集
# ├── model/        # 模型
# ├── signal/       # 信号
# └── contract.json # 合约配置
```

### 3.2 方法A: 从数据源下载数据

**使用RQData (推荐，需要账号):**

```python
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

# 配置RQData
import rqdatac
rqdatac.init("your_username", "your_password")

# 获取沪深300成分股
from rqdatac import index_components
components = index_components("000300.XSHG", date="2023-12-31")

# 下载数据
bars = []
for stock in components:
    # 转换代码格式
    symbol = stock.split(".")[0]
    exchange = Exchange.SSE if stock.endswith("XSHG") else Exchange.SZSE
    
    # 获取历史数据
    df = rqdatac.get_price(
        stock, 
        start_date="2018-01-01", 
        end_date="2023-12-31",
        frequency="1d"
    )
    
    for idx, row in df.iterrows():
        bar = BarData(
            symbol=symbol,
            exchange=exchange,
            datetime=idx,
            interval=Interval.DAILY,
            open_price=row["open"],
            high_price=row["high"],
            low_price=row["low"],
            close_price=row["close"],
            volume=row["volume"],
            gateway_name="RQDATA"
        )
        bars.append(bar)

# 保存数据
lab.save_bar_data(bars)
print(f"保存了 {len(bars)} 条K线数据")
```

### 3.3 方法B: 从CSV文件导入数据

准备CSV文件格式:
```csv
datetime,symbol,exchange,open,high,low,close,volume
2023-01-03,600000,SSE,7.85,7.92,7.80,7.88,12345678
2023-01-04,600000,SSE,7.90,7.95,7.85,7.92,11234567
...
```

导入代码:
```python
import pandas as pd
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData

# 读取CSV
df = pd.read_csv("G:/data/stock_daily.csv")

# 转换为BarData列表
bars = []
for _, row in df.iterrows():
    bar = BarData(
        symbol=row["symbol"],
        exchange=Exchange(row["exchange"]),
        datetime=datetime.strptime(row["datetime"], "%Y-%m-%d"),
        interval=Interval.DAILY,
        open_price=float(row["open"]),
        high_price=float(row["high"]),
        low_price=float(row["low"]),
        close_price=float(row["close"]),
        volume=float(row["volume"]),
        gateway_name="CSV"
    )
    bars.append(bar)

# 保存
lab.save_bar_data(bars)
```

### 3.4 方法C: 使用示例数据

```python
import numpy as np
import polars as pl
from datetime import datetime, timedelta

# 生成模拟数据
np.random.seed(42)
symbols = ["600000.SSE", "600036.SSE", "601318.SSE", "000001.SZSE", "000002.SZSE"]
dates = [datetime(2020, 1, 2) + timedelta(days=i) for i in range(1000)]

data = []
for symbol in symbols:
    price = 10.0 + np.random.randn() * 2  # 初始价格
    for dt in dates:
        ret = np.random.randn() * 0.02  # 日收益率
        price = price * (1 + ret)
        
        data.append({
            "datetime": dt,
            "vt_symbol": symbol,
            "open": price * (1 + np.random.randn() * 0.005),
            "high": price * (1 + abs(np.random.randn() * 0.01)),
            "low": price * (1 - abs(np.random.randn() * 0.01)),
            "close": price,
            "volume": np.random.randint(100000, 1000000)
        })

# 创建DataFrame
price_df = pl.DataFrame(data)
print(f"数据形状: {price_df.shape}")
print(price_df.head())
```

---

## 第四步: 创建因子

### 4.1 使用预定义因子集 (推荐新手)

```python
from vnpy.alpha.dataset.datasets.alpha_158 import Alpha158
from vnpy.alpha.dataset import process_drop_na, process_fill_na
from functools import partial

# 创建Alpha158数据集 (包含158个预定义因子)
dataset = Alpha158(
    df=price_df,
    train_period=("2020-01-01", "2022-06-30"),
    valid_period=("2022-07-01", "2022-12-31"),
    test_period=("2023-01-01", "2023-12-31")
)

# 添加数据预处理器
dataset.add_processor("learn", partial(process_drop_na, names=["label"]))
dataset.add_processor("infer", partial(process_fill_na, fill_value=0))

print(f"因子数量: {len(dataset.feature_names)}")
print(f"因子列表: {dataset.feature_names[:10]}...")  # 显示前10个
```

### 4.2 自定义因子

```python
from vnpy.alpha.dataset import AlphaDataset, process_drop_na, process_fill_na
from functools import partial

# 创建空白数据集
dataset = AlphaDataset(
    df=price_df,
    train_period=("2020-01-01", "2022-06-30"),
    valid_period=("2022-07-01", "2022-12-31"),
    test_period=("2023-01-01", "2023-12-31")
)

# ============================================
# 添加动量因子
# ============================================
dataset.add_feature("mom_5", "close / ts_delay(close, 5) - 1")
dataset.add_feature("mom_10", "close / ts_delay(close, 10) - 1")
dataset.add_feature("mom_20", "close / ts_delay(close, 20) - 1")

# ============================================
# 添加波动率因子
# ============================================
dataset.add_feature("vol_5", "ts_std(close / ts_delay(close, 1) - 1, 5)")
dataset.add_feature("vol_20", "ts_std(close / ts_delay(close, 1) - 1, 20)")

# ============================================
# 添加均线因子
# ============================================
dataset.add_feature("ma_ratio", "ts_mean(close, 5) / ts_mean(close, 20)")

# ============================================
# 添加量价因子
# ============================================
dataset.add_feature("vol_shock", "volume / ts_mean(volume, 20)")
dataset.add_feature("pv_corr", "ts_corr(close, volume, 10)")

# ============================================
# 添加AlphaGPT因子 (高级)
# ============================================
dataset.add_feature("fomo", "gpt_fomo_acceleration(volume, 5)")
dataset.add_feature("imbalance", "gpt_buy_sell_imbalance(close, open, high, low)")
dataset.add_feature("vol_cluster", "gpt_volatility_clustering(close, 10)")
dataset.add_feature("mom_reversal", "gpt_momentum_reversal(close, 5)")
dataset.add_feature("rsi_norm", "gpt_relative_strength(close, high, low, 14)")
dataset.add_feature("close_pos", "gpt_close_position(close, high, low)")

# ============================================
# 设置标签 (预测未来2期收益)
# ============================================
dataset.set_label("ts_delay(close, -2) / ts_delay(close, -1) - 1")

# ============================================
# 添加预处理器
# ============================================
dataset.add_processor("learn", partial(process_drop_na, names=["label"]))
dataset.add_processor("infer", partial(process_fill_na, fill_value=0))

print(f"自定义因子数量: {len(dataset.feature_names)}")
```

### 4.3 准备数据

```python
# 计算所有因子 (可能需要几分钟)
print("开始计算因子...")
dataset.prepare_data(max_workers=4)  # 使用4个CPU核心并行计算

# 处理数据 (应用预处理器)
print("处理数据...")
dataset.process_data()

# 保存数据集
lab.save_dataset("my_dataset", dataset)
print("数据集保存完成!")

# 查看数据
from vnpy.alpha import Segment
train_df = dataset.fetch_learn(Segment.TRAIN)
print(f"训练集形状: {train_df.shape}")
print(train_df.head())
```

### 4.4 因子分析 (可选)

```python
# 查看单因子表现
dataset.show_feature_performance("mom_5")
```

---

## 第五步: 训练模型

### 5.1 选择模型

vnpy提供三种内置模型:

| 模型 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| LassoModel | 快速、可解释、防过拟合 | 线性模型，表达能力有限 | 快速验证、因子筛选 |
| LgbModel | 高精度、自动特征交互 | 需要调参 | 生产环境首选 |
| MlpModel | 捕捉复杂非线性 | 需要GPU、易过拟合 | 深度学习研究 |

### 5.2 训练Lasso模型 (入门推荐)

```python
from vnpy.alpha.model.models.lasso_model import LassoModel

# 创建模型
model = LassoModel(
    alpha=0.0005,        # L1正则化系数
    max_iter=1000,       # 最大迭代次数
    random_state=42      # 随机种子
)

# 训练
print("开始训练Lasso模型...")
model.fit(dataset)

# 查看特征重要性
model.detail()

# 保存模型
lab.save_model("lasso_model", model)
```

### 5.3 训练LightGBM模型 (生产推荐)

```python
from vnpy.alpha.model.models.lgb_model import LgbModel

# 创建模型
model = LgbModel(
    learning_rate=0.05,         # 学习率
    num_leaves=31,              # 叶子节点数
    num_boost_round=500,        # 迭代轮数
    early_stopping_rounds=30,   # 早停轮数
    seed=42                     # 随机种子
)

# 训练
print("开始训练LightGBM模型...")
model.fit(dataset)

# 查看特征重要性
model.detail()

# 保存模型
lab.save_model("lgb_model", model)
```

### 5.4 训练MLP神经网络 (高级)

```python
from vnpy.alpha.model.models.mlp_model import MlpModel

# 创建模型
model = MlpModel(
    input_size=len(dataset.feature_names),  # 输入维度
    hidden_sizes=(256, 128),                # 隐藏层结构
    lr=0.001,                               # 学习率
    n_epochs=100,                           # 训练轮次
    batch_size=2000,                        # 批次大小
    early_stop_rounds=20,                   # 早停轮数
    optimizer="adam",                       # 优化器
    device="cuda"                           # GPU训练 (或 "cpu")
)

# 训练
print("开始训练MLP模型...")
model.fit(dataset)

# 查看特征重要性
model.detail()

# 保存模型
lab.save_model("mlp_model", model)
```

### 5.5 生成预测信号

```python
from vnpy.alpha import Segment
import polars as pl

# 预测测试集
print("生成预测信号...")
predictions = model.predict(dataset, Segment.TEST)

# 构建信号DataFrame
df_test = dataset.fetch_infer(Segment.TEST)
signal_df = df_test.select(["datetime", "vt_symbol"]).with_columns(
    pl.Series("signal", predictions)
)

# 保存信号
lab.save_signal("my_signal", signal_df)
print(f"信号生成完成! 共 {len(signal_df)} 条")
print(signal_df.head())

# 信号分析 (可选)
dataset.show_signal_performance(predictions)
```

---

## 第六步: 策略回测

### 6.1 创建回测引擎

```python
from datetime import datetime
from vnpy.trader.constant import Interval
from vnpy.alpha.strategy import BacktestingEngine
from vnpy.alpha.strategy.strategies.equity_demo_strategy import EquityDemoStrategy

# 创建回测引擎
engine = BacktestingEngine(lab)

# 设置回测参数
engine.set_parameters(
    vt_symbols=price_df["vt_symbol"].unique().to_list(),  # 股票池
    interval=Interval.DAILY,                               # K线周期
    start=datetime(2023, 1, 1),                           # 开始日期
    end=datetime(2023, 12, 31),                           # 结束日期
    capital=1_000_000,                                    # 初始资金 (100万)
    risk_free=0.02,                                       # 无风险利率
    annual_days=252                                       # 年交易日数
)
```

### 6.2 添加策略

```python
# 加载信号
signal_df = lab.load_signal("my_signal")

# 添加策略
engine.add_strategy(
    EquityDemoStrategy,
    setting={
        "top_k": 10,          # 持仓股票数量
        "n_drop": 3,          # 每次换仓最多卖出数量
        "min_days": 5,        # 最小持仓天数
        "cash_ratio": 0.95,   # 仓位比例
        "min_volume": 100,    # 最小交易量
        "open_rate": 0.0003,  # 开仓手续费率
        "close_rate": 0.0013, # 平仓手续费率 (含印花税)
        "price_add": 0.02     # 价格调整比例
    },
    signal_df=signal_df
)
```

### 6.3 运行回测

```python
# 加载数据
print("加载回测数据...")
engine.load_data()

# 运行回测
print("运行回测...")
engine.run_backtesting()

# 计算每日结果
print("计算回测结果...")
result_df = engine.calculate_result()

# 计算统计指标
stats = engine.calculate_statistics()
print("\n========== 回测统计 ==========")
for key, value in stats.items():
    print(f"{key}: {value}")
```

### 6.4 查看回测结果

```python
# 显示净值曲线
engine.show_chart()

# 显示详细业绩
engine.show_performance()

# 获取所有交易记录
trades = engine.get_all_trades()
print(f"\n总交易次数: {len(trades)}")

# 获取所有订单
orders = engine.get_all_orders()
print(f"总订单数: {len(orders)}")
```

### 6.5 理解回测指标

| 指标 | 含义 | 参考值 |
|------|------|--------|
| total_return | 总收益率 | >10%/年 |
| annual_return | 年化收益率 | >15%为优秀 |
| max_drawdown | 最大回撤 | <20%为良好 |
| sharpe_ratio | 夏普比率 | >1为良好, >2为优秀 |
| win_rate | 胜率 | >50% |
| profit_loss_ratio | 盈亏比 | >1.5 |

---

## 第七步: 优化策略

### 7.1 参数优化

```python
# 测试不同参数组合
param_grid = {
    "top_k": [5, 10, 20, 30],
    "n_drop": [2, 3, 5],
    "min_days": [3, 5, 10]
}

results = []
for top_k in param_grid["top_k"]:
    for n_drop in param_grid["n_drop"]:
        for min_days in param_grid["min_days"]:
            # 创建新引擎
            engine = BacktestingEngine(lab)
            engine.set_parameters(
                vt_symbols=price_df["vt_symbol"].unique().to_list(),
                interval=Interval.DAILY,
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
                capital=1_000_000
            )
            engine.add_strategy(
                EquityDemoStrategy,
                {"top_k": top_k, "n_drop": n_drop, "min_days": min_days},
                signal_df
            )
            
            engine.load_data()
            engine.run_backtesting()
            engine.calculate_result()
            stats = engine.calculate_statistics()
            
            results.append({
                "top_k": top_k,
                "n_drop": n_drop,
                "min_days": min_days,
                "sharpe": stats["sharpe_ratio"],
                "return": stats["total_return"],
                "drawdown": stats["max_drawdown"]
            })

# 显示最优参数
import pandas as pd
results_df = pd.DataFrame(results)
results_df = results_df.sort_values("sharpe", ascending=False)
print(results_df.head(10))
```

### 7.2 自定义策略

```python
from vnpy.alpha import AlphaStrategy
from vnpy.trader.object import BarData, TradeData
import polars as pl

class MyCustomStrategy(AlphaStrategy):
    """自定义策略"""
    
    # 策略参数
    top_k: int = 10
    rebalance_days: int = 5
    stop_loss_pct: float = -0.08      # 止损线
    take_profit_pct: float = 0.15     # 止盈线
    
    def on_init(self) -> None:
        """初始化"""
        self.day_count = 0
        self.entry_prices = {}
        self.write_log("策略初始化完成")
    
    def on_trade(self, trade: TradeData) -> None:
        """成交回调"""
        if trade.direction.value == "多":
            self.entry_prices[trade.vt_symbol] = trade.price
        self.write_log(f"成交: {trade.vt_symbol} {trade.direction.value} "
                      f"@ {trade.price} x {trade.volume}")
    
    def on_bars(self, bars: dict[str, BarData]) -> None:
        """K线推送"""
        self.day_count += 1
        
        # 检查止损止盈
        self._check_risk_management(bars)
        
        # 调仓日
        if self.day_count % self.rebalance_days == 0:
            self._rebalance(bars)
        
        # 执行交易
        self.execute_trading(bars, price_add=0.02)
    
    def _check_risk_management(self, bars: dict[str, BarData]) -> None:
        """风险管理"""
        for vt_symbol, pos in list(self.pos_data.items()):
            if pos <= 0 or vt_symbol not in bars:
                continue
            
            entry = self.entry_prices.get(vt_symbol)
            if not entry:
                continue
            
            current = bars[vt_symbol].close_price
            pnl_pct = (current - entry) / entry
            
            # 止损
            if pnl_pct <= self.stop_loss_pct:
                self.set_target(vt_symbol, 0)
                self.write_log(f"止损: {vt_symbol} 亏损 {pnl_pct:.2%}")
            
            # 止盈
            elif pnl_pct >= self.take_profit_pct:
                self.set_target(vt_symbol, 0)
                self.write_log(f"止盈: {vt_symbol} 盈利 {pnl_pct:.2%}")
    
    def _rebalance(self, bars: dict[str, BarData]) -> None:
        """调仓"""
        signal_df = self.get_signal()
        if signal_df.is_empty():
            return
        
        # 按信号排序选股
        signal_df = signal_df.sort("signal", descending=True)
        target_symbols = list(signal_df["vt_symbol"][:self.top_k])
        
        # 计算目标仓位
        portfolio_value = self.get_portfolio_value()
        target_value = portfolio_value * 0.95 / self.top_k
        
        # 设置目标
        for vt_symbol in target_symbols:
            if vt_symbol in bars:
                price = bars[vt_symbol].close_price
                if price > 0:
                    volume = int(target_value / price / 100) * 100
                    self.set_target(vt_symbol, volume)
        
        # 清空非目标持仓
        for vt_symbol in list(self.pos_data.keys()):
            if vt_symbol not in target_symbols:
                self.set_target(vt_symbol, 0)
```

---

## 第八步: 实盘部署

### 8.1 启动图形界面

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# 导入网关和应用
from vnpy_ctp import CtpGateway
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_datamanager import DataManagerApp
from vnpy_datarecorder import DataRecorderApp

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
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(DataRecorderApp)
    
    # 创建窗口
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    
    qapp.exec()

if __name__ == "__main__":
    main()
```

### 8.2 连接交易接口

1. 点击 **系统 → 连接CTP**
2. 填写账号信息:
   - 用户名: 期货账号
   - 密码: 交易密码
   - 经纪商代码: 9999 (SimNow模拟)
   - 交易服务器: tcp://180.168.146.187:10201
   - 行情服务器: tcp://180.168.146.187:10211
3. 点击连接

### 8.3 无界面模式运行

```python
from datetime import datetime, time
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Interval

# 初始化
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 添加网关
from vnpy_ctp import CtpGateway
main_engine.add_gateway(CtpGateway)

# 连接
main_engine.connect({
    "用户名": "your_account",
    "密码": "your_password",
    "经纪商代码": "9999",
    "交易服务器": "tcp://180.168.146.187:10201",
    "行情服务器": "tcp://180.168.146.187:10211",
    "产品名称": "",
    "授权编码": "",
    "产品信息": ""
}, "CTP")

# 等待连接
import time as t
t.sleep(5)

# 订阅行情
main_engine.subscribe(req=SubscribeRequest(
    symbol="IF2401",
    exchange=Exchange.CFFEX
), gateway_name="CTP")

# 发送订单
from vnpy.trader.object import OrderRequest
from vnpy.trader.constant import Direction, Offset, OrderType

order_req = OrderRequest(
    symbol="IF2401",
    exchange=Exchange.CFFEX,
    direction=Direction.LONG,
    type=OrderType.LIMIT,
    volume=1,
    price=3500.0,
    offset=Offset.OPEN
)

order_id = main_engine.send_order(order_req, "CTP")
print(f"订单已发送: {order_id}")
```

### 8.4 定时任务

```python
import schedule
import time

def run_strategy():
    """每日执行策略"""
    print(f"执行策略: {datetime.now()}")
    
    # 1. 更新数据
    # 2. 计算信号
    # 3. 执行交易

# 设置定时任务
schedule.every().day.at("09:25").do(run_strategy)  # 开盘前
schedule.every().day.at("13:00").do(run_strategy)  # 午盘

# 运行
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 第九步: 常见问题解答

### Q1: 安装TA-Lib失败

**解决方案:**
```powershell
# 使用预编译版本
pip install --extra-index-url https://pypi.vnpy.com ta_lib==0.6.4
```

### Q2: 导入vnpy报错

**检查:**
```python
import sys
print(sys.version)  # 确认Python 3.10+
print(sys.platform)  # 确认64位
```

### Q3: 数据加载很慢

**优化:**
```python
# 使用多进程
dataset.prepare_data(max_workers=8)

# 使用更高效的数据格式
# parquet比csv快10倍以上
```

### Q4: 回测结果不理想

**检查清单:**
1. 是否存在未来数据泄露
2. 手续费是否设置正确
3. 交易量限制是否合理
4. 是否过拟合训练集

### Q5: GPU训练MLP失败

**确认:**
```python
import torch
print(torch.cuda.is_available())  # 应为True
print(torch.cuda.get_device_name(0))  # 显示GPU名称
```

### Q6: 实盘连接失败

**检查:**
1. 网络是否通畅
2. 账号密码是否正确
3. 服务器地址是否正确
4. 是否在交易时间

---

## 完整示例代码

将以上所有步骤整合为一个完整脚本:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VeighNa量化交易完整示例
从数据准备到回测的一站式流程
"""

import numpy as np
import polars as pl
from datetime import datetime, timedelta
from functools import partial

from vnpy.alpha import AlphaLab, AlphaDataset, Segment
from vnpy.alpha.dataset import process_drop_na, process_fill_na
from vnpy.alpha.model.models.lgb_model import LgbModel
from vnpy.alpha.strategy import BacktestingEngine
from vnpy.alpha.strategy.strategies.equity_demo_strategy import EquityDemoStrategy
from vnpy.trader.constant import Interval


def main():
    # ============================================
    # 步骤1: 创建实验室
    # ============================================
    print("=" * 50)
    print("步骤1: 创建实验室")
    print("=" * 50)
    lab = AlphaLab("./lab/complete_example")
    
    # ============================================
    # 步骤2: 准备数据
    # ============================================
    print("\n" + "=" * 50)
    print("步骤2: 准备数据")
    print("=" * 50)
    
    np.random.seed(42)
    symbols = [f"00000{i}.SZSE" for i in range(1, 6)]
    dates = [datetime(2020, 1, 2) + timedelta(days=i) for i in range(1000)]
    
    data = []
    for symbol in symbols:
        price = 10.0 + np.random.randn() * 2
        for dt in dates:
            ret = np.random.randn() * 0.02
            price = max(price * (1 + ret), 1.0)
            data.append({
                "datetime": dt,
                "vt_symbol": symbol,
                "open": price * (1 + np.random.randn() * 0.005),
                "high": price * (1 + abs(np.random.randn() * 0.01)),
                "low": price * (1 - abs(np.random.randn() * 0.01)),
                "close": price,
                "volume": float(np.random.randint(100000, 1000000))
            })
    
    price_df = pl.DataFrame(data)
    print(f"数据形状: {price_df.shape}")
    
    # ============================================
    # 步骤3: 创建因子
    # ============================================
    print("\n" + "=" * 50)
    print("步骤3: 创建因子")
    print("=" * 50)
    
    dataset = AlphaDataset(
        df=price_df,
        train_period=("2020-01-01", "2021-12-31"),
        valid_period=("2022-01-01", "2022-06-30"),
        test_period=("2022-07-01", "2022-12-31")
    )
    
    # 添加因子
    dataset.add_feature("mom_5", "close / ts_delay(close, 5) - 1")
    dataset.add_feature("mom_10", "close / ts_delay(close, 10) - 1")
    dataset.add_feature("vol_5", "ts_std(close / ts_delay(close, 1) - 1, 5)")
    dataset.add_feature("ma_ratio", "ts_mean(close, 5) / ts_mean(close, 20)")
    dataset.add_feature("vol_shock", "volume / ts_mean(volume, 20)")
    dataset.add_feature("fomo", "gpt_fomo_acceleration(volume, 5)")
    dataset.add_feature("imbalance", "gpt_buy_sell_imbalance(close, open, high, low)")
    
    dataset.set_label("ts_delay(close, -2) / ts_delay(close, -1) - 1")
    
    dataset.add_processor("learn", partial(process_drop_na, names=["label"]))
    dataset.add_processor("infer", partial(process_fill_na, fill_value=0))
    
    print(f"因子数量: {len(dataset.feature_names)}")
    
    # ============================================
    # 步骤4: 准备数据
    # ============================================
    print("\n" + "=" * 50)
    print("步骤4: 准备数据")
    print("=" * 50)
    
    dataset.prepare_data(max_workers=4)
    dataset.process_data()
    lab.save_dataset("my_dataset", dataset)
    print("数据集准备完成!")
    
    # ============================================
    # 步骤5: 训练模型
    # ============================================
    print("\n" + "=" * 50)
    print("步骤5: 训练模型")
    print("=" * 50)
    
    model = LgbModel(
        learning_rate=0.05,
        num_leaves=31,
        num_boost_round=100,
        early_stopping_rounds=20
    )
    model.fit(dataset)
    lab.save_model("lgb_model", model)
    print("模型训练完成!")
    
    # ============================================
    # 步骤6: 生成信号
    # ============================================
    print("\n" + "=" * 50)
    print("步骤6: 生成信号")
    print("=" * 50)
    
    predictions = model.predict(dataset, Segment.TEST)
    df_test = dataset.fetch_infer(Segment.TEST)
    signal_df = df_test.select(["datetime", "vt_symbol"]).with_columns(
        pl.Series("signal", predictions)
    )
    lab.save_signal("my_signal", signal_df)
    print(f"信号生成完成! 共 {len(signal_df)} 条")
    
    # ============================================
    # 步骤7: 策略回测
    # ============================================
    print("\n" + "=" * 50)
    print("步骤7: 策略回测")
    print("=" * 50)
    
    engine = BacktestingEngine(lab)
    engine.set_parameters(
        vt_symbols=symbols,
        interval=Interval.DAILY,
        start=datetime(2022, 7, 1),
        end=datetime(2022, 12, 31),
        capital=1_000_000
    )
    engine.add_strategy(
        EquityDemoStrategy,
        {"top_k": 3, "n_drop": 1, "min_days": 5},
        signal_df
    )
    
    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    stats = engine.calculate_statistics()
    
    print("\n========== 回测统计 ==========")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 显示图表
    engine.show_chart()
    
    print("\n" + "=" * 50)
    print("完成! 🎉")
    print("=" * 50)


if __name__ == "__main__":
    main()
```

---

## 下一步

恭喜你完成了vnpy量化交易的入门学习！接下来可以：

1. 📚 阅读 `VNPY_DOCUMENTATION.md` 了解更多API细节
2. 📚 阅读 `ALPHAGPT_INTEGRATION.md` 学习高级因子
3. 🔬 尝试更多因子组合和模型
4. 📈 在模拟账户上验证策略
5. 💰 小资金实盘测试

**祝你量化交易之路顺利！** 🚀
