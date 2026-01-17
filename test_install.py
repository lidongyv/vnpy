"""
VNPy安装验证脚本
"""
import sys
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("VNPy安装验证")
print("="*60)

# 检查Python版本
print(f"\nPython版本: {sys.version}")

# 检查VNPy核心
try:
    import vnpy
    print(f"✓ VNPy核心: {vnpy.__version__}")
except Exception as e:
    print(f"✗ VNPy核心安装失败: {e}")
    sys.exit(1)

# 检查应用模块
modules = {
    "CTA策略引擎": "vnpy_ctastrategy",
    "CTA回测引擎": "vnpy_ctabacktester",
    "数据管理器": "vnpy_datamanager",
    "数据录制器": "vnpy_datarecorder",
    "本地仿真": "vnpy_paperaccount",
}

print("\n应用模块:")
for name, module in modules.items():
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except:
        print(f"  ✗ {name} (未安装)")

# 检查AI量化模块
print("\nAI量化模块:")
ai_modules = {
    "Polars": "polars",
    "Scikit-learn": "sklearn",
    "LightGBM": "lightgbm",
    "PyTorch": "torch",
    "Alphalens": "alphalens",
}

for name, module in ai_modules.items():
    try:
        mod = __import__(module)
        version = getattr(mod, "__version__", "已安装")
        print(f"  ✓ {name}: {version}")
    except:
        print(f"  ✗ {name} (未安装)")

# 检查关键依赖
print("\n关键依赖:")
deps = {
    "NumPy": "numpy",
    "Pandas": "pandas",
    "TA-Lib": "talib",
    "PySide6": "PySide6",
}

for name, module in deps.items():
    try:
        mod = __import__(module)
        version = getattr(mod, "__version__", "已安装")
        print(f"  ✓ {name}: {version}")
    except:
        print(f"  ✗ {name} (未安装)")

print("\n" + "="*60)
print("安装验证完成！")
print("="*60)
print("\n✅ 您可以开始使用VNPy进行量化交易了！")
print("\n下一步：运行 'python run_vnpy.py' 启动VNPy Trader")
