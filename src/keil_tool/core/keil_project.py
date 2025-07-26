"""
Keil 项目管理核心类
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Callable
from lxml import etree
from lxml.etree import _Element

from ..constants import (
    PROJECT_FILE_EXTENSION,
    DEFAULT_MAX_DEPTH,
    XPATH_GROUPS,
    XPATH_GROUP_NAME,
    XPATH_INCLUDE_PATH,
    SUPPORTED_SOURCE_EXTENSIONS,
    SUPPORTED_HEADER_EXTENSIONS
)
from ..exceptions import (
    ProjectFileNotFoundError,
    InvalidProjectFileError,
    ProjectNotLoadedError,
    FileOperationError
)
from ..utils import (
    normalize_path,
    get_relative_path,
    validate_regex_pattern,
    get_subfolders,
    find_files_by_extensions,
    find_folders_with_files
)


class KeilProject:
    """Keil 项目管理类"""
    
    def __init__(self, callback_func: Optional[Callable[[str], None]] = None):
        """
        初始化 Keil 项目管理器
        
        Args:
            callback_func: 日志回调函数，用于向 GUI 发送消息
        """
        self.project_path: str = ""
        self.etree_root: Optional[_Element] = None
        self.callback_func = callback_func
    
    def _log_message(self, message: str) -> None:
        """发送日志消息"""
        if self.callback_func:
            self.callback_func(message)
        else:
            print(message)
    
    def _ensure_project_loaded(self) -> None:
        """确保项目已加载"""
        if not self.project_path:
            raise ProjectNotLoadedError("项目文件路径未设置")
        
        if self.etree_root is None:
            try:
                self._load_project()
            except Exception as e:
                raise ProjectNotLoadedError(f"无法加载项目文件: {str(e)}")
    
    def set_project_file(self, project_path: str) -> bool:
        """
        设置项目文件路径
        
        Args:
            project_path: .uvprojx 文件的路径
            
        Returns:
            是否成功设置
        """
        try:
            project_path = Path(project_path)
            
            if not project_path.exists():
                raise ProjectFileNotFoundError(f"项目文件不存在: {project_path}")
            
            if not project_path.suffix.lower() == PROJECT_FILE_EXTENSION:
                raise InvalidProjectFileError(f"不是有效的 Keil 项目文件: {project_path}")
            
            self.project_path = str(project_path)
            self._log_message(f"已设置项目文件: {self.project_path}")
            
            # 自动加载项目
            return self._load_project()
            
        except Exception as e:
            self._log_message(f"设置项目文件失败: {str(e)}")
            return False
    
    def find_uvprojx_files(self) -> str:
        """
        在当前目录搜索 .uvprojx 文件
        
        Returns:
            找到的项目文件路径，如果没找到返回空串
        """
        try:
            current_dir = Path.cwd()
            uvprojx_files = list(current_dir.rglob(f"*{PROJECT_FILE_EXTENSION}"))
            
            if len(uvprojx_files) == 0:
                self._log_message("当前文件夹中未找到 .uvprojx 文件")
                return ""
            elif len(uvprojx_files) > 1:
                self._log_message("当前文件夹中存在多个 .uvprojx 文件，请手动指定")
                return ""
            
            project_file = str(uvprojx_files[0])
            self.project_path = project_file
            self._log_message(f"找到项目文件: {project_file}")
            return project_file
            
        except Exception as e:
            self._log_message(f"搜索项目文件失败: {str(e)}")
            return ""
    
    def _load_project(self) -> bool:
        """
        加载项目文件
        
        Returns:
            是否成功加载
        """
        try:
            root_str = etree.tostring(etree.parse(self.project_path)).decode('utf-8')
            self.etree_root = etree.XML(root_str)
            return True
        except Exception as e:
            self._log_message(f"加载项目文件失败: {str(e)}")
            return False
    
    def refresh_project(self) -> bool:
        """
        刷新项目文件
        
        Returns:
            是否成功刷新
        """
        if self.project_path:
            return self._load_project()
        else:
            project_file = self.find_uvprojx_files()
            if project_file:
                return self._load_project()
            return False
    
    def create_files_group(self, path: str, max_depth: int, group_root_name: Optional[str] = None) -> bool:
        """
        创建文件组
        
        Args:
            path: 文件路径
            max_depth: 递归深度
            group_root_name: 组名前缀
            
        Returns:
            是否成功创建
        """
        try:
            self._ensure_project_loaded()
            
            path = normalize_path(path)
            folders = get_subfolders(path, max_depth)
            
            files_added = 0
            for folder in folders:
                source_files = find_files_by_extensions(folder, SUPPORTED_SOURCE_EXTENSIONS)
                if not source_files:
                    continue
                
                group_name = folder if not group_root_name else folder.replace(path, group_root_name)
                group = self._get_or_create_group(group_name)
                
                files_element = group.xpath('.//Files')[0]
                for file_info in source_files:
                    self._add_file_to_group(files_element, file_info)
                    files_added += 1
            
            self._save_project()
            self._log_message(f"成功创建文件组，添加了 {files_added} 个文件")
            return True
            
        except Exception as e:
            self._log_message(f"创建文件组失败: {str(e)}")
            return False
    
    def refresh_group(self, group_name: str, path: str, max_depth: int = DEFAULT_MAX_DEPTH) -> bool:
        """
        刷新指定的文件组
        
        Args:
            group_name: 要刷新的组名
            path: 源文件路径
            max_depth: 搜索深度
            
        Returns:
            是否成功刷新
        """
        try:
            self._ensure_project_loaded()
            
            path = normalize_path(path)
            
            # 删除现有组
            self._delete_groups_by_prefix(group_name)
            
            # 重新创建组
            folders = get_subfolders(path, max_depth)
            files_added = 0
            groups_created = set()
            
            for folder in folders:
                all_files = (find_files_by_extensions(folder, SUPPORTED_SOURCE_EXTENSIONS) +
                           find_files_by_extensions(folder, SUPPORTED_HEADER_EXTENSIONS))
                
                if not all_files:
                    continue
                
                # 计算子组名
                try:
                    rel_path = os.path.relpath(folder, path).replace("\\", "/")
                    if rel_path in [".", ""]:
                        sub_group_name = group_name
                    else:
                        sub_group_name = f"{group_name}/{rel_path}"
                except ValueError:
                    folder_name = os.path.basename(folder)
                    sub_group_name = f"{group_name}/{folder_name}"
                
                if sub_group_name in groups_created:
                    continue
                
                groups_created.add(sub_group_name)
                group = self._get_or_create_group(sub_group_name)
                files_element = group.xpath('.//Files')[0]
                
                # 清空现有文件
                for file_element in files_element.xpath('.//File'):
                    files_element.remove(file_element)
                
                # 添加文件
                for file_info in all_files:
                    self._add_file_to_group(files_element, file_info)
                    files_added += 1
            
            self._save_project()
            self._log_message(f"成功刷新组 '{group_name}'，创建了 {len(groups_created)} 个子组，添加了 {files_added} 个文件")
            
            # 同时更新头文件路径
            if self.add_include_path(path):
                self._log_message(f"同时更新了头文件路径: {path}")
            
            return True
            
        except Exception as e:
            self._log_message(f"刷新组失败: {str(e)}")
            return False
    
    def clean_rebuild_group(self, group_name: str, path: str, max_depth: int = DEFAULT_MAX_DEPTH) -> bool:
        """
        完全清理并重建指定的文件组
        
        Args:
            group_name: 要重建的组名
            path: 源文件路径
            max_depth: 搜索深度
            
        Returns:
            是否成功重建
        """
        try:
            self._ensure_project_loaded()
            
            path = normalize_path(path)
            self._log_message(f"开始清理重建组 '{group_name}'，路径: {path}")
            
            # 删除所有相关组
            deleted_groups = self._delete_groups_by_prefix(group_name)
            if deleted_groups:
                self._log_message(f"清理了旧组: {', '.join(deleted_groups)}")
            
            # 获取文件夹并排序
            folders = get_subfolders(path, max_depth)
            folders.sort(key=lambda x: x.count('/'))
            
            self._log_message(f"找到 {len(folders)} 个文件夹")
            
            files_added = 0
            groups_created = {}
            
            for folder in folders:
                all_files = (find_files_by_extensions(folder, SUPPORTED_SOURCE_EXTENSIONS) +
                           find_files_by_extensions(folder, SUPPORTED_HEADER_EXTENSIONS))
                
                if not all_files:
                    continue
                
                # 计算相对路径
                try:
                    rel_path = os.path.relpath(folder, path).replace("\\", "/")
                    if rel_path in [".", ""]:
                        sub_group_name = group_name
                    else:
                        sub_group_name = f"{group_name}/{rel_path}"
                except ValueError:
                    folder_name = os.path.basename(folder)
                    sub_group_name = f"{group_name}/{folder_name}"
                
                if sub_group_name in groups_created:
                    continue
                
                # 创建组并添加文件
                group = self._get_or_create_group(sub_group_name)
                files_element = group.xpath('.//Files')[0]
                
                for file_info in all_files:
                    self._add_file_to_group(files_element, file_info)
                    files_added += 1
                
                groups_created[sub_group_name] = len(all_files)
                self._log_message(f"创建组 '{sub_group_name}'，添加了 {len(all_files)} 个文件")
            
            self._save_project()
            self._log_message(f"完成！创建了 {len(groups_created)} 个组，总共添加了 {files_added} 个文件")
            
            # 更新头文件路径
            if self.add_include_path(path):
                self._log_message("同时更新了头文件路径")
            
            return True
            
        except Exception as e:
            self._log_message(f"清理重建组失败: {str(e)}")
            return False
    
    def delete_existing_groups(self, regex_pattern: str) -> bool:
        """
        删除匹配正则表达式的文件组
        
        Args:
            regex_pattern: 正则表达式模式
            
        Returns:
            是否成功删除
        """
        try:
            self._ensure_project_loaded()
            
            if not validate_regex_pattern(regex_pattern):
                raise ValueError(f"无效的正则表达式: {regex_pattern}")
            
            pattern = re.compile(regex_pattern)
            groups = self.etree_root.xpath(XPATH_GROUPS)[0]
            group_name_list = self.etree_root.xpath(XPATH_GROUP_NAME)
            
            deleted_count = 0
            for group_name_element in group_name_list:
                if pattern.search(group_name_element.text):
                    groups.remove(group_name_element.getparent())
                    deleted_count += 1
            
            self._save_project()
            self._log_message(f"成功删除 {deleted_count} 个文件组")
            return True
            
        except Exception as e:
            self._log_message(f"删除文件组失败: {str(e)}")
            return False
    
    def add_include_path(self, path: str) -> bool:
        """
        添加头文件路径
        
        Args:
            path: 递归起始路径
            
        Returns:
            是否成功添加
        """
        try:
            self._ensure_project_loaded()
            
            include_folders = find_folders_with_files(path, SUPPORTED_HEADER_EXTENSIONS)
            include_folders = [get_relative_path(folder, self.project_path) for folder in include_folders]
            
            include_path_element = self.etree_root.xpath(XPATH_INCLUDE_PATH)[0]
            current_paths = include_path_element.text.split(";") if include_path_element.text else []
            
            all_paths = list(set(current_paths + include_folders))
            all_paths.sort()
            
            include_path_element.text = ";".join(all_paths)
            self._save_project()
            
            self._log_message(f"成功添加 {len(include_folders)} 个头文件路径")
            return True
            
        except Exception as e:
            self._log_message(f"添加头文件路径失败: {str(e)}")
            return False
    
    def delete_include_path(self, regex_pattern: str) -> bool:
        """
        删除匹配正则表达式的头文件路径
        
        Args:
            regex_pattern: 正则表达式模式
            
        Returns:
            是否成功删除
        """
        try:
            self._ensure_project_loaded()
            
            if not validate_regex_pattern(regex_pattern):
                raise ValueError(f"无效的正则表达式: {regex_pattern}")
            
            include_path_element = self.etree_root.xpath(XPATH_INCLUDE_PATH)[0]
            pattern = re.compile(regex_pattern)
            
            current_paths = include_path_element.text.split(";") if include_path_element.text else []
            original_count = len(current_paths)
            
            filtered_paths = [path for path in current_paths if not pattern.search(path)]
            deleted_count = original_count - len(filtered_paths)
            
            include_path_element.text = ";".join(list(set(filtered_paths)))
            self._save_project()
            
            self._log_message(f"成功删除 {deleted_count} 个头文件路径")
            return True
            
        except Exception as e:
            self._log_message(f"删除头文件路径失败: {str(e)}")
            return False
    
    def _get_or_create_group(self, name: str) -> _Element:
        """获取或创建文件组"""
        group_name_element = self.etree_root.xpath(f'{XPATH_GROUP_NAME}[text()="{name}"]')
        if group_name_element:
            return group_name_element[0].getparent()
        
        # 创建新组
        groups = self.etree_root.xpath(XPATH_GROUPS)[0]
        group = etree.Element("Group")
        
        group_name = etree.Element("GroupName")
        group_name.text = name
        group.append(group_name)
        
        files = etree.Element("Files")
        group.append(files)
        
        groups.append(group)
        return group
    
    def _add_file_to_group(self, files_element: _Element, file_info: dict) -> None:
        """向文件组添加文件"""
        # 检查文件是否已存在
        file_name_element = files_element.xpath(f'.//FileName[text()="{file_info["file_name"]}"]')
        if file_name_element:
            return
        
        file_element = etree.Element("File")
        
        file_name = etree.Element("FileName")
        file_name.text = file_info["file_name"]
        
        file_type = etree.Element("FileType")
        file_type.text = file_info["file_type"]
        
        file_path = etree.Element("FilePath")
        file_path.text = get_relative_path(file_info["file_path"], self.project_path)
        
        file_element.append(file_name)
        file_element.append(file_type)
        file_element.append(file_path)
        
        files_element.append(file_element)
    
    def _delete_groups_by_prefix(self, prefix: str) -> List[str]:
        """删除指定前缀的所有组"""
        groups = self.etree_root.xpath(XPATH_GROUPS)[0]
        group_name_elements = self.etree_root.xpath(XPATH_GROUP_NAME)
        
        deleted_groups = []
        groups_to_remove = []
        
        for group_element in group_name_elements:
            if group_element.text and (group_element.text == prefix or 
                                     group_element.text.startswith(f"{prefix}/")):
                deleted_groups.append(group_element.text)
                groups_to_remove.append(group_element.getparent())
        
        for group_to_remove in groups_to_remove:
            groups.remove(group_to_remove)
        
        return deleted_groups
    
    def _save_project(self) -> None:
        """保存项目文件"""
        try:
            tree = etree.ElementTree(self.etree_root)
            tree.write(self.project_path, encoding='utf-8', xml_declaration=True)
        except Exception as e:
            raise FileOperationError(f"保存项目文件失败: {str(e)}")
