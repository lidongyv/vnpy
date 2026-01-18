#!/bin/bash
# VNPy Trader 启动脚本

# 配置Homebrew环境
eval "$(/opt/homebrew/bin/brew shellenv)"

# 启动VNPy Trader
cd "$(dirname "$0")"
python3.10 examples/veighna_trader/run.py
