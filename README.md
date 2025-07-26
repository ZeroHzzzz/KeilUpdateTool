# Keil 项目文件自动刷新工具

一个用于自动刷新和同步 Keil uVision 项目文件的 Python 工具，支持自动化管理项目中的文件组和头文件路径。

## 功能特性

- � **自动文件刷新**：根据文件系统变化自动更新项目文件组
- �🔧 **智能头文件同步**：自动更新和同步头文件路径配置
- 📁 **批量文件组管理**：根据目录结构批量创建和更新文件组
- 🖥️ **双界面支持**：提供命令行和图形界面两种使用方式
- 🎯 **正则表达式支持**：支持使用正则表达式批量操作文件组
- ⚡ **快速同步**：避免手动逐个添加文件，提高开发效率

## 项目结构

```
keil_update/
├── src/
│   └── keil_tool/
│       ├── __init__.py          # 主模块
│       ├── constants.py         # 常量定义
│       ├── exceptions.py        # 异常定义
│       ├── core/               # 核心功能
│       │   ├── __init__.py
│       │   └── keil_project.py # Keil项目管理核心类
│       ├── ui/                 # 用户界面
│       │   ├── __init__.py
│       │   ├── cli.py          # 命令行界面
│       │   └── gui.py          # 图形界面
│       └── utils/              # 工具函数
│           ├── __init__.py
│           └── file_utils.py   # 文件操作工具
├── main.py                     # 主入口文件
├── pyproject.toml              # 项目配置
└── README.md                   # 项目说明
```

## 安装依赖

```bash
pip install lxml
```

或者如果你使用 uv：

```bash
uv sync
```

## 打包

如果你想将工具打包为独立的可执行文件，可以使用 PyInstaller：

### 安装 PyInstaller

```bash
pip install pyinstaller
```

### 打包

项目中提供了打包需要的`main.spec`文件，因此可以直接使用该文件进行打包。

```bash
pyinstaller main.spec
```

如果你想为可执行文件指定自定义图标：

1. 准备一个 `.ico` 格式的图标文件，命名为 `icon.ico`
2. 将图标文件放在项目根目录下（与 `main.spec` 同级）
3. 运行打包命令即可

如果没有图标文件，可以注释掉 `main.spec` 文件中的 `icon='icon.ico',` 这一行。

打包完成后，可执行文件 `KeilUpdateTool.exe` 将位于 `dist/` 目录下。

## 使用方法

### GUI 模式（推荐）

```bash
python main.py --gui
```

### 命令行模式

```bash
python main.py --cli
```

### 可用命令（命令行模式）

- `set_project <path>` - 设置项目文件路径
- `create_files_group <path> <max_depth> [group_root_name]` - 创建文件组
- `refresh_group <group_name> <path> [max_depth]` - 刷新指定文件组（自动更新头文件路径）
- `clean_rebuild_group <group_name> <path> [max_depth]` - 清理重建文件组
- `del_exist_group <regex_pattern>` - 删除匹配的文件组
- `refresh_project` - 刷新项目
- `help` - 显示帮助信息
- `exit` - 退出程序

## 使用示例

### 命令行示例

```bash
# 设置项目文件
set_project ./MyProject.uvprojx

# 创建文件组（深度为2，组名前缀为"MyCode"）
create_files_group ./src 2 MyCode

# 刷新指定组（会自动更新头文件路径）
refresh_group MyCode ./src 3

# 删除以"Test"开头的文件组
del_exist_group ^Test.*
```

### GUI 界面使用

1. 启动程序后会自动搜索当前目录下的 `.uvprojx` 文件
2. 在"文件组管理"区域输入源代码路径和搜索深度
3. 使用"创建文件组"自动扫描并添加源文件到项目
4. 使用"刷新指定组"同步文件变更，自动更新头文件路径
5. 使用"清理重建组"完全重新构建文件组，避免重复文件
6. 所有操作结果会在日志输出区域显示
