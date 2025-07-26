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

## 使用场景

- 🆕 **新项目初始化**：快速将现有源码目录添加到Keil项目
- 🔄 **代码结构变更**：当源码目录结构发生变化时，快速同步到项目文件
- 📂 **批量文件管理**：避免在Keil IDE中逐个添加/删除文件的繁琐操作
- 🚀 **持续集成**：在自动化构建流程中保持项目文件同步

## 代码改进

本次重构包含以下改进：

### 1. 模块化结构
- 将代码按功能分离到不同模块
- 创建清晰的包结构
- 分离常量、异常和工具函数

### 2. 代码质量提升
- 添加完整的类型注解
- 改进错误处理机制
- 统一命名规范
- 添加详细的文档字符串

### 3. 架构优化
- 使用依赖注入模式（回调函数）
- 分离业务逻辑和UI逻辑
- 提高代码可测试性和可维护性

### 4. 用户体验改进
- 更好的错误提示
- 线程安全的GUI操作
- 统一的日志系统

## 注意事项

- 请确保在包含 `.uvprojx` 文件的目录中运行此工具
- 操作前建议备份项目文件
- 所有操作都会直接修改项目文件
- 支持的文件类型：`.c`、`.h`、`.cpp`、`.s`、`.asm`

## 作者信息

- 作者：ZeroHzzzz
- 重构时间：2025_07_26
- GitHub：https://github.com/ZeroHzzzz/KeilUpdateTool

## 许可证

本项目采用开源许可证，具体请查看项目仓库。
