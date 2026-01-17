# VNPy从零到实战完整指南

> 🚀 手把手教你从安装到实盘交易的完整流程

---

## 目录

1. [环境准备](#第一步环境准备)
2. [安装VNPy](#第二步安装vnpy)
3. [启动VNPy Trader](#第三步启动vnpy-trader)
4. [数据准备](#第四步数据准备)
5. [开发第一个策略](#第五步开发第一个策略)
6. [策略回测](#第六步策略回测)
7. [参数优化](#第七步参数优化)
8. [模拟盘测试](#第八步模拟盘测试)
9. [实盘交易](#第九步实盘交易)
10. [风险管理](#第十步风险管理)

---

## 第一步：环境准备

### 1.1 系统要求检查

**最低要求：**
- Windows 10+ / Ubuntu 20.04+ / MacOS 11+
- Python 3.10+ (推荐3.13)
- 8GB RAM (推荐16GB)
- 20GB 硬盘空间

### 1.2 安装Python（如果未安装）

#### Windows用户

**方式A：使用VeighNa Studio（推荐新手）**

1. 下载VeighNa Studio：
   ```
   https://download.vnpy.com/veighna_studio-4.3.0.exe
   ```

2. 双击安装程序
   - 选择安装路径（建议：C:\VeighNa）
   - 勾选"Add to PATH"
   - 点击"Install"
   - 等待安装完成（约5-10分钟）

3. 验证安装
   ```cmd
   # 打开命令提示符（Win+R，输入cmd）
   python --version
   # 应该显示：Python 3.13.x
   ```

**方式B：手动安装Python**

1. 访问：https://www.python.org/downloads/
2. 下载Python 3.13（64位）
3. 安装时务必勾选"Add Python to PATH"
4. 验证：
   ```cmd
   python --version
   pip --version
   ```

#### Linux/Mac用户

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 python3-pip

# MacOS (使用Homebrew)
brew install python@3.13

# 验证
python3 --version
pip3 --version
```

### 1.3 创建工作目录

```cmd
# Windows
cd C:\
mkdir vnpy_workspace
cd vnpy_workspace

# Linux/Mac
cd ~
mkdir vnpy_workspace
cd vnpy_workspace
```

---

## 第二步：安装VNPy

### 2.1 方式一：使用pip安装（推荐）

```bash
# 1. 升级pip
python -m pip install --upgrade pip

# 2. 安装VNPy核心
pip install vnpy

# 3. 安装AI量化模块（可选）
pip install vnpy[alpha]

# 4. 验证安装
python -c "import vnpy; print(vnpy.__version__)"
# 应该显示：4.3.0
```

### 2.2 安装交易接口（Gateway）

根据您的交易需求选择：

#### CTP期货接口（国内期货）

```bash
pip install vnpy_ctp
```

#### XTP股票接口（A股）

```bash
pip install vnpy_xtp
```

#### IB接口（海外市场）

```bash
pip install vnpy_ib
```

#### 模拟交易接口（仿真测试）

```bash
pip install vnpy_paperaccount
```

### 2.3 安装策略应用（App）

```bash
# CTA策略引擎（必装）
pip install vnpy_ctastrategy

# CTA回测引擎（必装）
pip install vnpy_ctabacktester

# 数据管理（必装）
pip install vnpy_datamanager

# 数据录制（推荐）
pip install vnpy_datarecorder

# 风险管理（推荐）
pip install vnpy_riskmanager

# 组合策略（可选）
pip install vnpy_portfoliostrategy

# 算法交易（可选）
pip install vnpy_algotrading
```

### 2.4 安装数据服务（选择一个）

#### RQData（米筐数据）

```bash
pip install vnpy_rqdata
```

注册账号：https://www.ricequant.com/

#### 迅投研（XT数据）

```bash
pip install vnpy_xt
```

注册账号：https://www.xtquant.com/

#### TuShare

```bash
pip install vnpy_tushare
```

注册账号：https://tushare.pro/

### 2.5 验证安装

创建测试脚本 `test_install.py`：

```python
# test_install.py
import vnpy
print(f"VNPy版本: {vnpy.__version__}")

try:
    from vnpy_ctp import CtpGateway
    print("✓ CTP接口已安装")
except:
    print("✗ CTP接口未安装")

try:
    from vnpy_ctastrategy import CtaStrategyApp
    print("✓ CTA策略引擎已安装")
except:
    print("✗ CTA策略引擎未安装")

try:
    from vnpy_ctabacktester import CtaBacktesterApp
    print("✓ CTA回测引擎已安装")
except:
    print("✗ CTA回测引擎未安装")

try:
    from vnpy_datamanager import DataManagerApp
    print("✓ 数据管理器已安装")
except:
    print("✗ 数据管理器未安装")

print("\n安装检查完成！")
```

运行测试：

```bash
python test_install.py
```

---

## 第三步：启动VNPy Trader

### 3.1 创建启动脚本

创建 `run_vnpy.py`：

```python
"""
VNPy Trader启动脚本
"""
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# 导入交易接口
from vnpy_ctp import CtpGateway  # 期货
# from vnpy_xtp import XtpGateway  # 股票
# from vnpy_ib import IbGateway  # 海外

# 导入策略应用
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctabacktester import CtaBacktesterApp
from vnpy_datamanager import DataManagerApp
from vnpy_datarecorder import DataRecorderApp
from vnpy_riskmanager import RiskManagerApp

# 导入本地仿真
from vnpy_paperaccount import PaperAccountApp


def main():
    """启动VNPy Trader"""
    # 创建Qt应用
    qapp = create_qapp()
    
    # 创建事件引擎
    event_engine = EventEngine()
    
    # 创建主引擎
    main_engine = MainEngine(event_engine)
    
    # 添加交易接口
    main_engine.add_gateway(CtpGateway)
    # main_engine.add_gateway(XtpGateway)
    # main_engine.add_gateway(IbGateway)
    
    # 添加策略应用
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(RiskManagerApp)
    main_engine.add_app(PaperAccountApp)
    
    # 创建主窗口
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    
    # 运行Qt应用
    qapp.exec()


if __name__ == "__main__":
    main()
```

### 3.2 第一次启动

```bash
python run_vnpy.py
```

**启动后您会看到：**
- VNPy Trader主窗口
- 顶部菜单栏：系统、功能、帮助
- 左侧面板：活动委托、活动日志
- 右侧面板：行情、成交、委托、持仓等

### 3.3 配置数据库（可选）

VNPy默认使用SQLite，无需配置。如需使用MySQL/MongoDB：

创建 `vnpy_config.py`：

```python
# vnpy_config.py
from vnpy.trader.setting import SETTINGS

# 使用MySQL
SETTINGS["database.driver"] = "mysql"
SETTINGS["database.database"] = "vnpy"
SETTINGS["database.host"] = "localhost"
SETTINGS["database.port"] = 3306
SETTINGS["database.user"] = "root"
SETTINGS["database.password"] = "your_password"

# 或使用MongoDB
# SETTINGS["database.driver"] = "mongodb"
# SETTINGS["database.host"] = "localhost"
# SETTINGS["database.port"] = 27017
```

---

## 第四步：数据准备

### 4.1 注册SimNow模拟账号（期货仿真）

1. 访问：http://www.simnow.com.cn/
2. 点击"注册"
3. 填写信息获取账号密码
4. 记录以下信息：
   - 用户名：例如 123456
   - 密码：例如 abc123
   - 经纪商代码：9999
   - 交易服务器：180.168.146.187:10130
   - 行情服务器：180.168.146.187:10131

### 4.2 连接SimNow获取实时行情

1. 启动VNPy Trader
2. 点击菜单："系统" → "连接CTP"
3. 填写SimNow信息：
   ```
   用户名：您的SimNow账号
   密码：您的SimNow密码
   经纪商代码：9999
   交易服务器：180.168.146.187:10130
   行情服务器：180.168.146.187:10131
   产品名称：simnow_client_test
   授权编码：0000000000000000
   ```
4. 点击"连接"
5. 等待状态变为"已连接"

### 4.3 下载历史数据

**方式A：使用DataManager（GUI）**

1. 点击菜单："功能" → "数据管理"
2. 在"数据下载"标签页
3. 填写参数：
   ```
   代码：rb2505（螺纹钢主力合约）
   交易所：SHFE
   周期：1m（1分钟）或d（日线）
   开始日期：2024-01-01
   结束日期：2024-12-31
   ```
4. 点击"下载"
5. 等待下载完成

**方式B：使用脚本下载**

创建 `download_data.py`：

```python
"""
下载历史数据脚本
"""
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from vnpy_rqdata import RqdataDatafeed  # 或其他数据源

# 初始化数据源
datafeed = RqdataDatafeed()
datafeed.init("your_username", "your_password")  # RQData账号

# 下载数据
bars = datafeed.query_bar_history(
    symbol="rb2505",
    exchange=Exchange.SHFE,
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

print(f"下载了 {len(bars)} 条K线数据")

# 保存到数据库
from vnpy.trader.database import get_database

database = get_database()
database.save_bar_data(bars)

print("数据已保存到数据库")
```

运行：

```bash
python download_data.py
```

### 4.4 验证数据

1. 打开DataManager
2. 在"数据查询"标签页
3. 选择合约和周期
4. 点击"查询"
5. 应该能看到下载的历史数据

---

## 第五步：开发第一个策略

### 5.1 简单双均线策略

创建 `strategies/double_ma_strategy.py`：

```python
"""
双均线策略
作者：量化交易者
"""
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class DoubleMaStrategy(CtaTemplate):
    """
    双均线策略：
    - 快线上穿慢线：买入开仓
    - 快线下穿慢线：卖出平仓
    """
    
    author = "量化交易者"
    
    # 策略参数
    fast_window = 10      # 快线周期
    slow_window = 20      # 慢线周期
    
    # 策略变量
    fast_ma = 0.0         # 快线值
    slow_ma = 0.0         # 慢线值
    ma_trend = 0          # 均线趋势（1：多头，-1：空头）
    
    # 变量列表（会显示在GUI中）
    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma", "slow_ma", "ma_trend"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """构造函数"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        # K线生成器（Tick合成1分钟K线）
        self.bg = BarGenerator(self.on_bar)
        
        # 数组管理器（存储历史数据）
        self.am = ArrayManager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        
        # 加载历史数据（用于计算指标）
        self.load_bar(10)  # 加载10天历史数据
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
    
    def on_tick(self, tick: TickData):
        """Tick行情推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """K线推送"""
        # 更新数据到数组管理器
        self.am.update_bar(bar)
        
        # 如果数据不足，返回
        if not self.am.inited:
            return
        
        # 计算双均线
        self.fast_ma = self.am.sma(self.fast_window)
        self.slow_ma = self.am.sma(self.slow_window)
        
        # 判断趋势
        if self.fast_ma > self.slow_ma:
            self.ma_trend = 1  # 多头趋势
        else:
            self.ma_trend = -1  # 空头趋势
        
        # 交易逻辑
        if self.pos == 0:
            # 无持仓
            if self.ma_trend == 1:
                # 金叉：买入开仓
                self.buy(bar.close_price + 5, 1)
                self.write_log(f"买入开仓：价格 {bar.close_price + 5}")
        
        elif self.pos > 0:
            # 持有多头
            if self.ma_trend == -1:
                # 死叉：卖出平仓
                self.sell(bar.close_price - 5, abs(self.pos))
                self.write_log(f"卖出平仓：价格 {bar.close_price - 5}")
        
        # 更新图形界面
        self.put_event()
    
    def on_order(self, order: OrderData):
        """委托回报"""
        pass
    
    def on_trade(self, trade: TradeData):
        """成交回报"""
        self.write_log(f"成交：{trade.direction.value} {trade.volume}手 @ {trade.price}")
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """停止单回报"""
        pass
```

### 5.2 将策略文件放到正确位置

```bash
# 创建strategies目录
mkdir strategies

# 将策略文件移动到目录
# 文件位置：strategies/double_ma_strategy.py
```

### 5.3 在GUI中加载策略

1. 启动VNPy Trader
2. 点击菜单："功能" → "CTA策略"
3. 在CTA策略窗口，点击"添加策略"
4. 填写参数：
   ```
   策略类名：DoubleMaStrategy
   策略实例名：double_ma_rb
   合约代码：rb2505.SHFE
   参数设置：
     - fast_window: 10
     - slow_window: 20
   ```
5. 点击"添加"

---

## 第六步：策略回测

### 6.1 使用GUI回测

1. 点击菜单："功能" → "CTA回测"
2. 填写回测参数：
   ```
   交易合约：rb2505.SHFE
   K线周期：1m（1分钟）
   回测开始：2024-01-01
   回测结束：2024-12-31
   手续费率：0.0003
   滑点：2
   合约乘数：10
   价格跳动：1
   回测资金：1000000
   ```
3. 选择策略："DoubleMaStrategy"
4. 设置参数：
   ```
   fast_window: 10
   slow_window: 20
   ```
5. 点击"开始回测"

### 6.2 查看回测结果

回测完成后会显示：

```
总盈亏: 125,000 元
收益率: 12.5%
最大回撤: 8.5%
夏普比率: 1.85
总交易次数: 156
盈利次数: 89
亏损次数: 67
胜率: 57.05%
```

### 6.3 查看回测图表

点击"显示图表"，会显示：
- 资金曲线
- 回撤曲线
- 每日盈亏
- 交易分布

### 6.4 使用脚本回测（高级）

创建 `backtest_strategy.py`：

```python
"""
策略回测脚本
"""
from datetime import datetime
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.trader.constant import Interval
from strategies.double_ma_strategy import DoubleMaStrategy

# 创建回测引擎
engine = BacktestingEngine()

# 设置回测参数
engine.set_parameters(
    vt_symbol="rb2505.SHFE",
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    rate=0.0003,      # 手续费率
    slippage=2,       # 滑点
    size=10,          # 合约乘数
    pricetick=1,      # 最小价格变动
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

# 计算统计指标
df = engine.calculate_result()
statistics = engine.calculate_statistics()

# 显示结果
print("\n" + "="*50)
print("回测统计结果")
print("="*50)
for key, value in statistics.items():
    print(f"{key}: {value}")

# 显示图表
engine.show_chart()
```

运行：

```bash
python backtest_strategy.py
```

---

## 第七步：参数优化

### 7.1 使用GUI优化

1. 在CTA回测窗口
2. 点击"参数优化"标签
3. 设置优化参数：
   ```
   优化目标：总收益
   
   fast_window:
     - 起始值：5
     - 结束值：15
     - 步进：1
   
   slow_window:
     - 起始值：15
     - 结束值：30
     - 步进：1
   
   其他设置：
     - CPU核心数：4（根据您的CPU）
   ```
4. 点击"开始优化"
5. 等待优化完成（可能需要几分钟）

### 7.2 查看优化结果

优化完成后显示：

```
最佳参数组合：
fast_window: 8
slow_window: 21
总收益: 152,300 元
夏普比率: 2.13
```

### 7.3 使用脚本优化（高级）

创建 `optimize_strategy.py`：

```python
"""
策略参数优化脚本
"""
from datetime import datetime
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.trader.constant import Interval
from vnpy.trader.optimize import OptimizationSetting
from strategies.double_ma_strategy import DoubleMaStrategy

# 创建回测引擎
engine = BacktestingEngine()

# 设置回测参数
engine.set_parameters(
    vt_symbol="rb2505.SHFE",
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    rate=0.0003,
    slippage=2,
    size=10,
    pricetick=1,
    capital=1000000,
)

# 添加策略
engine.add_strategy(DoubleMaStrategy, {})

# 加载数据
engine.load_data()

# 设置优化参数
setting = OptimizationSetting()
setting.set_target("sharpe_ratio")  # 优化目标：夏普比率
setting.add_parameter("fast_window", 5, 15, 1)
setting.add_parameter("slow_window", 15, 30, 1)

# 运行优化（使用4个CPU核心）
results = engine.run_optimization(setting, max_workers=4)

# 显示优化结果
print("\n" + "="*70)
print("参数优化结果（按夏普比率排序）")
print("="*70)
print(f"{'fast_window':<12} {'slow_window':<12} {'夏普比率':<12} {'总收益':<12}")
print("-"*70)

for result in sorted(results, key=lambda x: x[1], reverse=True)[:10]:
    params, target_value, statistics = result
    print(f"{params['fast_window']:<12} {params['slow_window']:<12} {target_value:<12.2f} {statistics['total_return']:<12.0f}")
```

运行：

```bash
python optimize_strategy.py
```

---

## 第八步：模拟盘测试

### 8.1 启用本地仿真模块

1. 启动VNPy Trader
2. 点击菜单："功能" → "本地仿真"
3. 点击"启动"
4. 连接到SimNow获取实时行情

### 8.2 在仿真环境测试策略

1. 在CTA策略窗口
2. 找到您的策略实例："double_ma_rb"
3. 点击"初始化"
4. 点击"启动"
5. 策略开始运行

### 8.3 监控策略运行

观察以下信息：
- **策略日志**：查看策略的运行日志
- **活动委托**：查看当前挂单
- **成交记录**：查看成交情况
- **持仓状态**：查看当前持仓
- **策略变量**：观察fast_ma、slow_ma等变量

### 8.4 策略调试

如果策略不符合预期：

1. 查看日志：
   ```
   日志位置：C:\Users\{用户}\.vntrader\log\
   ```

2. 检查策略变量：
   - fast_ma和slow_ma是否正常计算
   - pos是否正确更新

3. 调整参数：
   - 点击"停止"
   - 修改参数
   - 重新"初始化"和"启动"

---

## 第九步：实盘交易

### 9.1 风险警告 ⚠️

**在实盘交易前，请确保：**
1. ✅ 策略已经过充分回测
2. ✅ 策略已在模拟盘稳定运行至少1个月
3. ✅ 您完全理解策略的逻辑和风险
4. ✅ 您有足够的风险承受能力
5. ✅ 您已设置止损和风控规则

### 9.2 申请实盘账户

**期货账户（CTP）**

1. 联系期货公司开户
2. 获取以下信息：
   - 用户名
   - 密码
   - 经纪商代码
   - 交易服务器地址
   - 行情服务器地址
   - 产品名称
   - 授权编码

**股票账户（XTP）**

1. 联系券商开通XTP
2. 获取账户信息

### 9.3 连接实盘账户

1. 启动VNPy Trader
2. 点击："系统" → "连接CTP"（或其他接口）
3. 填写**实盘**账户信息
4. 点击"连接"
5. 确认连接成功

### 9.4 启用风险管理

1. 点击菜单："功能" → "风险管理"
2. 设置风控规则：
   ```
   流控设置：
     - 每秒最多下单：5次
     - 撤单总数限制：100次/天
   
   数量限制：
     - 单笔委托最大数量：10手
     - 总成交限制：100手/天
   
   活动委托：
     - 活动委托上限：20个
   ```
3. 点击"启动风控"

### 9.5 启动实盘策略

1. 在CTA策略窗口
2. **小仓位测试**：将参数中的手数改为1手
3. 点击"初始化"
4. **再次确认**：
   - ✅ 连接的是实盘账户
   - ✅ 策略参数正确
   - ✅ 风控已启用
   - ✅ 仓位很小
5. 点击"启动"

### 9.6 实盘监控

**密切监控以下内容：**

1. **持仓监控**
   - 每小时检查一次持仓
   - 确保持仓与预期一致

2. **盈亏监控**
   - 设置盈亏报警
   - 单日亏损超过5%立即停止策略

3. **日志监控**
   - 每天查看策略日志
   - 关注异常报错

4. **资金监控**
   - 每天对账
   - 确保资金安全

### 9.7 紧急处理

**如果出现问题：**

1. **立即停止策略**
   - 点击"停止"按钮
   - 或关闭VNPy Trader

2. **手动平仓**
   - 在交易软件中手动平掉所有持仓

3. **分析原因**
   - 查看日志文件
   - 检查策略逻辑
   - 联系技术支持

---

## 第十步：风险管理

### 10.1 资金管理

**规则：**

1. **初始仓位**
   - 单个策略资金不超过总资金的20%
   - 单次开仓不超过策略资金的10%

2. **止损设置**
   ```python
   # 在策略中添加止损逻辑
   def on_bar(self, bar: BarData):
       # ... 其他代码 ...
       
       # 止损逻辑
       if self.pos > 0:
           # 多头止损：跌破入场价3%
           if bar.close_price < self.entry_price * 0.97:
               self.sell(bar.close_price - 5, abs(self.pos))
               self.write_log("触发止损")
   ```

3. **止盈设置**
   ```python
   # 移动止盈
   if self.pos > 0:
       # 价格涨超5%时，移动止损到盈利2%位置
       if bar.close_price > self.entry_price * 1.05:
           stop_price = self.entry_price * 1.02
           # 使用停止单
   ```

### 10.2 风控检查清单

**每日必做：**
- [ ] 检查策略是否正常运行
- [ ] 查看持仓是否正常
- [ ] 检查当日盈亏
- [ ] 查看委托成交情况
- [ ] 检查资金账户

**每周必做：**
- [ ] 统计策略表现
- [ ] 对比回测结果
- [ ] 检查滑点和手续费
- [ ] 评估策略有效性
- [ ] 考虑是否需要调整参数

**每月必做：**
- [ ] 全面评估策略收益
- [ ] 分析策略失效原因
- [ ] 优化策略参数
- [ ] 考虑是否继续使用该策略

### 10.3 常见问题处理

#### 问题1：策略不下单

**可能原因：**
1. 数据未连接
2. 策略逻辑问题
3. 风控限制

**解决方案：**
```python
# 添加调试日志
def on_bar(self, bar: BarData):
    self.write_log(f"收到K线：{bar.close_price}")
    self.write_log(f"fast_ma: {self.fast_ma}, slow_ma: {self.slow_ma}")
    self.write_log(f"当前持仓：{self.pos}")
```

#### 问题2：滑点过大

**解决方案：**
1. 使用限价单而非市价单
2. 设置合理的价格
3. 避免在开盘和收盘时交易

#### 问题3：频繁触发风控

**解决方案：**
1. 调整风控参数
2. 优化策略逻辑减少交易频率
3. 增加交易间隔

---

## 附录A：完整策略示例

### A.1 布林带策略

创建 `strategies/bollinger_strategy.py`：

```python
"""
布林带策略
"""
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class BollingerStrategy(CtaTemplate):
    """
    布林带策略：
    - 价格跌破下轨：买入
    - 价格涨破上轨：卖出
    """
    
    author = "量化交易者"
    
    # 策略参数
    bb_window = 20        # 布林带周期
    bb_dev = 2.0          # 布林带标准差倍数
    
    # 策略变量
    bb_up = 0.0           # 上轨
    bb_down = 0.0         # 下轨
    bb_mid = 0.0          # 中轨
    
    parameters = ["bb_window", "bb_dev"]
    variables = ["bb_up", "bb_down", "bb_mid"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        self.bg = BarGenerator(self.on_bar, 5, self.on_5min_bar)
        self.am = ArrayManager()
    
    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)
    
    def on_start(self):
        self.write_log("策略启动")
    
    def on_stop(self):
        self.write_log("策略停止")
    
    def on_tick(self, tick: TickData):
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)
    
    def on_5min_bar(self, bar: BarData):
        """5分钟K线回调"""
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 计算布林带
        self.bb_up, self.bb_down = self.am.boll(self.bb_window, self.bb_dev)
        self.bb_mid = self.am.sma(self.bb_window)
        
        # 交易逻辑
        if self.pos == 0:
            # 价格跌破下轨：买入
            if bar.close_price < self.bb_down:
                self.buy(bar.close_price + 5, 1)
                self.write_log(f"突破下轨买入：{bar.close_price}")
        
        elif self.pos > 0:
            # 价格回归中轨或涨破上轨：卖出
            if bar.close_price >= self.bb_mid or bar.close_price >= self.bb_up:
                self.sell(bar.close_price - 5, abs(self.pos))
                self.write_log(f"回归卖出：{bar.close_price}")
        
        self.put_event()
    
    def on_order(self, order: OrderData):
        pass
    
    def on_trade(self, trade: TradeData):
        self.write_log(f"成交：{trade.direction.value} {trade.volume}手")
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        pass
```

---

## 附录B：常用命令速查

### B.1 安装相关

```bash
# 安装VNPy
pip install vnpy

# 安装AI模块
pip install vnpy[alpha]

# 安装CTP接口
pip install vnpy_ctp

# 安装策略引擎
pip install vnpy_ctastrategy vnpy_ctabacktester

# 升级VNPy
pip install --upgrade vnpy
```

### B.2 启动相关

```bash
# 启动VNPy Trader
python run_vnpy.py

# 运行回测
python backtest_strategy.py

# 参数优化
python optimize_strategy.py
```

### B.3 数据相关

```bash
# 下载数据
python download_data.py

# 查看数据库内容
sqlite3 ~/.vntrader/database.db
```

---

## 附录C：资源链接

### C.1 官方资源

- **官网**: https://www.vnpy.com
- **文档**: https://www.vnpy.com/docs
- **论坛**: https://www.vnpy.com/forum
- **GitHub**: https://github.com/vnpy/vnpy

### C.2 数据服务

- **SimNow模拟**: http://www.simnow.com.cn/
- **RQData**: https://www.ricequant.com/
- **迅投研**: https://www.xtquant.com/
- **TuShare**: https://tushare.pro/

### C.3 学习资源

- **VNPy视频教程**: https://www.vnpy.com/forum/forum/45
- **策略分享**: https://www.vnpy.com/forum/forum/47
- **问题求助**: https://www.vnpy.com/forum/forum/46

---

## 附录D：故障排查

### D.1 安装问题

**问题：pip安装失败**

```bash
# 解决方案1：使用国内镜像
pip install vnpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 解决方案2：使用VNPy镜像
pip install vnpy -i https://pypi.vnpy.com

# 解决方案3：升级pip
python -m pip install --upgrade pip
```

**问题：ta-lib安装失败**

```bash
# Windows用户
pip install --extra-index-url https://pypi.vnpy.com ta_lib==0.6.4

# Linux用户
sudo apt-get install ta-lib
pip install ta-lib
```

### D.2 运行问题

**问题：无法连接CTP**

1. 检查网络连接
2. 确认账号密码正确
3. 检查服务器地址
4. 查看防火墙设置

**问题：策略不运行**

1. 检查策略是否初始化
2. 确认策略已启动
3. 查看策略日志
4. 检查数据是否正常

### D.3 数据问题

**问题：无历史数据**

1. 确认已下载数据
2. 检查数据库连接
3. 使用DataManager查看

**问题：行情不更新**

1. 检查是否连接交易接口
2. 确认合约代码正确
3. 检查交易时间

---

## 总结

**您现在已经学会：**

✅ 安装和配置VNPy环境  
✅ 启动VNPy Trader图形界面  
✅ 下载和管理历史数据  
✅ 开发自己的量化策略  
✅ 进行策略回测和优化  
✅ 在模拟盘测试策略  
✅ 谨慎进行实盘交易  
✅ 实施风险管理  

**下一步建议：**

1. 📖 深入学习更多策略类型
2. 💡 研究专业量化指标
3. 🔬 学习机器学习策略
4. 📊 掌握数据分析技巧
5. ⚡ 优化策略执行效率

**记住：**
- 量化交易需要持续学习和改进
- 永远不要用超出承受能力的资金
- 策略会失效，要不断更新和优化
- 风险管理永远是第一位的

**祝您量化交易成功！** 🚀📈

---

**文档版本**: v1.0  
**更新日期**: 2026年1月17日  
**适用版本**: VNPy 4.3.0  
**作者**: VNPy量化社区
