"""
常量定义
"""

# 文件类型映射
FILE_TYPE_MAP = {
    ".c": 1,
    ".h": 5,
    ".cpp": 8,
    ".s": 2,
    ".asm": 2,
}

# 支持的文件扩展名
SUPPORTED_SOURCE_EXTENSIONS = [".c", ".cpp"]
SUPPORTED_HEADER_EXTENSIONS = [".h", ".hpp"]
SUPPORTED_ASSEMBLY_EXTENSIONS = [".s", ".asm"]

# 项目文件扩展名
PROJECT_FILE_EXTENSION = ".uvprojx"

# 默认搜索深度
DEFAULT_MAX_DEPTH = 3

# XML路径常量
XPATH_GROUPS = "//Groups"
XPATH_GROUP_NAME = "//Groups//GroupName"
XPATH_INCLUDE_PATH = "//TargetArmAds//VariousControls/IncludePath"

# 应用信息常量
APP_TITLE = "Keil 项目文件自动刷新工具"
APP_AUTHOR = "ZeroHzzzz"
APP_GITHUB = "https://github.com/ZeroHzzzz/KeilUpdateTool"
APP_VERSION = "1.0.0"
APP_CREATE_TIME = "2025_07_26"
