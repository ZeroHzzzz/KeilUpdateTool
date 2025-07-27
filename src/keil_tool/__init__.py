"""
Keil 项目文件自动刷新工具

一个用于自动刷新和同步 Keil uVision 项目文件的工具，支持：
- 自动刷新文件组
- 智能同步头文件路径
- 批量文件管理
- 命令行和GUI界面

作者: ZeroHzzzz
重构时间: 2025_07_26
GitHub: https://github.com/ZeroHzzzz/KeilUpdateTool
"""

__version__ = "1.0.0"
__author__ = "ZeroHzzzz"
__email__ = ""

from .core.keil_project import KeilProject

__all__ = ["KeilProject"]
