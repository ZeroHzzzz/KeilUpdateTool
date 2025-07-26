"""
异常定义
"""

class KeilToolError(Exception):
    """Keil工具基础异常"""
    pass

class ProjectFileNotFoundError(KeilToolError):
    """项目文件未找到异常"""
    pass

class InvalidProjectFileError(KeilToolError):
    """无效项目文件异常"""
    pass

class ProjectNotLoadedError(KeilToolError):
    """项目未加载异常"""
    pass

class FileOperationError(KeilToolError):
    """文件操作异常"""
    pass
