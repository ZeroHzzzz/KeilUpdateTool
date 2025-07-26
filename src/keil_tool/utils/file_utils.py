"""
工具函数
"""

import os
import re
from pathlib import Path
from typing import List

def normalize_path(path: str) -> str:
    """标准化路径"""
    return os.path.abspath(path).replace('\\', '/')

def get_relative_path(target_path: str, base_path: str) -> str:
    """获取相对路径"""
    try:
        target = Path(target_path).resolve()
        base = Path(base_path).resolve()
        
        # 计算相对路径
        relative_path_parts = []
        i = 0
        while i < len(target.parts) and i < len(base.parts) and target.parts[i] == base.parts[i]:
            i += 1
        
        # 添加 .. 来回到公共父目录
        for j in range(i, len(base.parts) - 1):
            relative_path_parts.append("..")
        
        # 添加从公共父目录到目标的路径
        relative_path_parts.extend(target.parts[i:])
        
        return str(Path(*relative_path_parts)).replace('\\', '/')
    except Exception:
        return target_path

def validate_regex_pattern(pattern: str) -> bool:
    """验证正则表达式是否有效"""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

def get_subfolders(path: str, max_depth: int) -> List[str]:
    """获取指定深度的子文件夹"""
    result = []
    path = normalize_path(path)
    
    for root, dirs, files in os.walk(path):
        depth = root[len(path):].count(os.sep)
        if depth < max_depth:
            # 如果没有子目录，添加当前目录
            if not dirs:
                result.append(root)
                del dirs[:]
            # 如果达到最大深度-1，添加所有子目录
            if depth == max_depth - 1:
                for dir_name in dirs:
                    result.append(os.path.join(root, dir_name))
                del dirs[:]
        else:
            del dirs[:]
    
    return [normalize_path(p) for p in result]

def find_files_by_extensions(directory: str, extensions: List[str]) -> List[dict]:
    """根据扩展名查找文件"""
    from ..constants import FILE_TYPE_MAP
    
    file_info_list = []
    directory_path = Path(directory)
    
    for file_path in directory_path.rglob("*"):
        if file_path.suffix in extensions:
            file_info = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_type": str(FILE_TYPE_MAP.get(file_path.suffix, 1))
            }
            file_info_list.append(file_info)
    
    return file_info_list

def find_folders_with_files(root_dir: str, extensions: List[str]) -> List[str]:
    """查找包含指定扩展名文件的文件夹"""
    result = []
    root_path = Path(root_dir)
    
    for dir_path in root_path.rglob('*'):
        if dir_path.is_dir():
            for file_path in dir_path.glob('*'):
                if file_path.is_file() and file_path.suffix in extensions:
                    result.append(normalize_path(str(dir_path)))
                    break
    
    return result
