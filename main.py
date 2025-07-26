"""
Keil 项目管理工具主入口
"""

import argparse
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from keil_tool.ui import run_cli, run_gui
from keil_tool.constants import APP_TITLE, APP_VERSION, APP_AUTHOR


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description=APP_TITLE,
        epilog=f"版本: {APP_VERSION} | 作者: {APP_AUTHOR}"
    )
    parser.add_argument("--cli", action="store_true", help="使用命令行模式")
    parser.add_argument("--gui", action="store_true", help="使用GUI模式")
    parser.add_argument("--version", action="version", version=f"{APP_TITLE} {APP_VERSION}")
    
    args = parser.parse_args()
    
    # 如果没有指定模式，默认使用GUI模式
    if not args.cli and not args.gui:
        args.gui = True
    
    try:
        if args.cli:
            run_cli()
        elif args.gui:
            run_gui()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
