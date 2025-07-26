import os
import re
from pathlib import Path
from lxml import etree
from lxml.etree import _Element


class KeilTool:
    def __init__(self, callback_func=None):
        self.uvprojx_path = ""
        self.etree_root = None
        self.callback_func = callback_func  # 用于向GUI发送消息的回调函数

    def set_project_file(self, project_path: str) -> bool:
        """
        手动设置项目文件路径
        :param project_path: .uvprojx 文件的路径
        :return: 是否成功
        """
        project_path = Path(project_path)
        if not project_path.exists():
            self.log_message(f"项目文件不存在: {project_path}")
            return False
        
        if not project_path.suffix.lower() == '.uvprojx':
            self.log_message(f"不是有效的 Keil 项目文件: {project_path}")
            return False
        
        self.uvprojx_path = str(project_path)
        self.log_message(f"已设置项目文件: {self.uvprojx_path}")
        
        # 自动加载项目
        try:
            self.get_root()
            return True
        except Exception as e:
            self.log_message(f"加载项目文件失败: {str(e)}")
            return False

    def log_message(self, message):
        """发送消息到GUI或控制台"""
        if self.callback_func:
            self.callback_func(message)
        else:
            print(message)

    def find_uvprojx_files(self) -> str:
        """
        搜索指定路径的.uvprojx文件
        :return: .uvprojx文件路径
        """
        current_dir = Path.cwd()
        uvprojx_files = []
        for file_path in current_dir.rglob("*.uvprojx"):
            uvprojx_files.append(str(file_path.relative_to(current_dir)))
        if not len(uvprojx_files) == 1:
            self.log_message("Keil-Tool: 请检查当前文件夹是否不存在或存在多个.uvprojx文件")
            return ""
        self.uvprojx_path = uvprojx_files[0]
        self.log_message(f"找到项目文件: {uvprojx_files[0]}")
        return uvprojx_files[0]

    def get_root(self, path: str = None) -> _Element:
        """
        获取uvprojx文件的根节点
        :param path:
        :return:
        """
        root_str = etree.tostring(etree.parse(path if path else self.uvprojx_path)).decode('utf-8')
        self.etree_root = etree.XML(root_str)
        return self.etree_root

    def get_file_type(self, suffix):
        """
        获取文件类型对应的映射值
        :param suffix: 文件后缀
        :return:
        """
        suffix_map = {".c": 1, ".h": 5}
        return str(suffix_map[suffix])

    def get_files_by_suffix(self, directory, suffix: list[str]):
        """
        搜索指定文件夹及子文件夹下所有特定后缀的文件
        :param directory: 要搜索的文件夹路径
        :param suffix: 指定的文件后缀
        :return:
        """
        file_info_list = []
        directory_path = Path(directory)
        for file_path in directory_path.rglob("*"):
            if file_path.suffix in suffix:
                file_info = {
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "file_type": self.get_file_type(file_path.suffix)
                }
                file_info_list.append(file_info)
        return file_info_list

    def get_folder_with_specific_files(self, root_dir, suffix: list[str]):
        """
        获取包含指定后缀文件的文件夹
        :param root_dir: 开始深度搜索的文件夹路径
        :param suffix: 文件后缀
        :return:
        """
        result = []
        root_path = Path(root_dir)
        for dir_path in root_path.rglob('*'):
            if dir_path.is_dir():
                for file_path in dir_path.glob('*'):
                    if file_path.is_file() and file_path.suffix in suffix:
                        result.append(str(dir_path).replace("\\", "/"))
                        break
        return result

    def creat_files_group(self, path: str, max_depth: int, group_root_name: str = None):
        """
        根据当前目录的格式和指定递归的深度，为uvprojx文件添加文件组
        :param path: 文件路径
        :param max_depth: 递归深度
        :param group_root_name: 组名字的前缀
        :return:
        """
        try:
            path = path.replace("\\", "/")
            folders = self.get_subfolders(path, max_depth)
            
            files_added = 0
            for folder in folders:
                infos = self.get_files_by_suffix(folder, [".c"])
                name = folder if not group_root_name else folder.replace(path, group_root_name)
                group = self.get_group(self.etree_root, name)

                files = group.xpath('.//Files')[0]
                for info in infos:
                    self.add_file_to_files(files, info)
                    files_added += 1

            self.write_to_file(self.etree_root, self.uvprojx_path)
            self.log_message(f"成功创建文件组，添加了 {files_added} 个文件")
            return True
        except Exception as e:
            self.log_message(f"创建文件组失败: {str(e)}")
            return False

    def is_group_exist(self, etree_root: _Element, group_name: str):
        groups_name = etree_root.xpath(f'//Groups//GroupName[text()="{group_name}"]')
        return len(groups_name) > 0

    def get_group(self, etree_root: _Element, name: str):
        group_name_el = etree_root.xpath(f'//Groups//GroupName[text()="{name}"]')
        if group_name_el:
            return group_name_el[0].getparent()

        groups = etree_root.xpath('//Groups')[0]
        group = etree.Element("Group")
        group_name = etree.Element("GroupName")
        group_name.text = name
        group.append(group_name)
        files = etree.Element("Files")
        group.append(files)
        groups.append(group)

        return group

    def add_file_to_files(self, files: _Element, info: dict):
        file_name_el = files.xpath(f'.//FileName[text()="{info["file_name"]}"]')
        if file_name_el:
            return

        file = etree.Element("File")

        file_name = etree.Element("FileName")
        file_name.text = info["file_name"]

        file_type = etree.Element("FileType")
        file_type.text = info["file_type"]

        file_path = etree.Element("FilePath")
        file_path.text = self.get_relative_path_uvprojx(info["file_path"]).replace("\\", "/")

        file.append(file_name)
        file.append(file_type)
        file.append(file_path)

        files.append(file)

    def del_exist_group(self, regex_pattern: str):
        try:
            # 检查项目文件是否已加载
            if not self.uvprojx_path:
                self.log_message("错误: 请先设置项目文件")
                return False
            
            # 确保根节点已加载
            if self.etree_root is None:
                try:
                    self.get_root()
                except Exception as e:
                    self.log_message(f"加载项目文件失败: {str(e)}")
                    return False
            
            groups = self.etree_root.xpath('//Groups')[0]
            group_name_list = self.etree_root.xpath('//Groups//GroupName')
            pattern = re.compile(regex_pattern)
            deleted_count = 0
            
            for group_name in group_name_list:
                if pattern.search(group_name.text):
                    groups.remove(group_name.getparent())
                    deleted_count += 1
                    
            self.write_to_file(self.etree_root, self.uvprojx_path)
            self.log_message(f"成功删除 {deleted_count} 个文件组")
            return True
        except Exception as e:
            self.log_message(f"删除文件组失败: {str(e)}")
            return False

    def refresh_group(self, group_name: str, path: str, max_depth: int = 3):
        """
        刷新指定的文件组，删除现有的组并重新创建
        :param group_name: 要刷新的组名
        :param path: 源文件路径
        :param max_depth: 搜索深度
        :return: 是否成功
        """
        try:
            # 检查项目文件是否已加载
            if not self.uvprojx_path:
                self.log_message("错误: 请先设置项目文件")
                return False
            
            # 确保根节点已加载
            if self.etree_root is None:
                try:
                    self.get_root()
                except Exception as e:
                    self.log_message(f"加载项目文件失败: {str(e)}")
                    return False
            
            # 标准化路径
            path = os.path.abspath(path).replace("\\", "/")
            
            # 先删除所有以该组名开头的组（包括子组）
            groups = self.etree_root.xpath('//Groups')[0]
            group_name_elements = self.etree_root.xpath('//Groups//GroupName')
            deleted_groups = []
            
            for group_el in group_name_elements:
                if group_el.text and (group_el.text == group_name or group_el.text.startswith(f"{group_name}/")):
                    deleted_groups.append(group_el.text)
                    groups.remove(group_el.getparent())
            
            if deleted_groups:
                self.log_message(f"删除了现有的组: {', '.join(deleted_groups)}")
            
            # 重新创建组并添加文件
            folders = self.get_subfolders(path, max_depth)
            
            files_added = 0
            groups_created = set()
            
            for folder in folders:
                # 标准化文件夹路径
                folder = os.path.abspath(folder).replace("\\", "/")
                
                # 获取 .c 和 .h 文件
                c_files = self.get_files_by_suffix(folder, [".c"])
                h_files = self.get_files_by_suffix(folder, [".h"])
                all_files = c_files + h_files
                
                if not all_files:  # 如果文件夹没有文件，跳过
                    continue
                
                # 计算相对路径来创建子组名
                try:
                    rel_path = os.path.relpath(folder, path).replace("\\", "/")
                    if rel_path == "." or rel_path == "":
                        sub_group_name = group_name
                    else:
                        sub_group_name = f"{group_name}/{rel_path}"
                except ValueError:
                    # 如果路径不在同一驱动器下，使用文件夹名
                    folder_name = os.path.basename(folder)
                    sub_group_name = f"{group_name}/{folder_name}"
                
                # 避免重复创建相同的组
                if sub_group_name in groups_created:
                    continue
                groups_created.add(sub_group_name)
                
                group = self.get_group(self.etree_root, sub_group_name)
                files_element = group.xpath('.//Files')[0]
                
                # 清空现有文件（以防万一）
                for file_element in files_element.xpath('.//File'):
                    files_element.remove(file_element)
                
                # 添加所有文件
                for file_info in all_files:
                    self.add_file_to_files(files_element, file_info)
                    files_added += 1
            
            self.write_to_file(self.etree_root, self.uvprojx_path)
            self.log_message(f"成功刷新组 '{group_name}'，创建了 {len(groups_created)} 个子组，添加了 {files_added} 个文件")
            
            # 同时更新头文件路径
            if self.add_include_path(path):
                self.log_message(f"同时更新了 '{path}' 的头文件路径")
            
            return True
            
        except Exception as e:
            self.log_message(f"刷新组失败: {str(e)}")
            return False

    def clean_rebuild_group(self, group_name: str, path: str, max_depth: int = 3):
        """
        完全清理并重建指定的文件组，确保没有重复组
        :param group_name: 要重建的组名
        :param path: 源文件路径
        :param max_depth: 搜索深度
        :return: 是否成功
        """
        try:
            # 检查项目文件是否已加载
            if not self.uvprojx_path:
                self.log_message("错误: 请先设置项目文件")
                return False
            
            # 确保根节点已加载
            if self.etree_root is None:
                try:
                    self.get_root()
                except Exception as e:
                    self.log_message(f"加载项目文件失败: {str(e)}")
                    return False
            
            # 标准化路径
            path = os.path.abspath(path).replace("\\", "/")
            self.log_message(f"开始清理重建组 '{group_name}'，路径: {path}")
            
            # 删除所有相关的组
            groups = self.etree_root.xpath('//Groups')[0]
            group_name_elements = self.etree_root.xpath('//Groups//GroupName')
            deleted_groups = []
            
            # 收集要删除的组
            groups_to_remove = []
            for group_el in group_name_elements:
                if group_el.text and (group_el.text == group_name or group_el.text.startswith(f"{group_name}/")):
                    deleted_groups.append(group_el.text)
                    groups_to_remove.append(group_el.getparent())
            
            # 删除组
            for group_to_remove in groups_to_remove:
                groups.remove(group_to_remove)
            
            if deleted_groups:
                self.log_message(f"清理了旧组: {', '.join(deleted_groups)}")
            
            # 获取所有文件夹
            folders = self.get_subfolders(path, max_depth)
            self.log_message(f"找到 {len(folders)} 个文件夹")
            
            # 按路径深度排序，确保父文件夹先处理
            folders.sort(key=lambda x: x.count('/'))
            
            files_added = 0
            groups_created = {}  # 用字典记录创建的组，避免重复
            
            for folder in folders:
                # 获取文件
                c_files = self.get_files_by_suffix(folder, [".c"])
                h_files = self.get_files_by_suffix(folder, [".h"])
                all_files = c_files + h_files
                
                if not all_files:
                    continue
                
                # 计算相对路径
                try:
                    rel_path = os.path.relpath(folder, path).replace("\\", "/")
                    if rel_path == "." or rel_path == "":
                        sub_group_name = group_name
                    else:
                        # 确保路径分隔符一致
                        rel_path = rel_path.replace("\\", "/")
                        sub_group_name = f"{group_name}/{rel_path}"
                except ValueError:
                    # 路径不在同一驱动器
                    folder_name = os.path.basename(folder)
                    sub_group_name = f"{group_name}/{folder_name}"
                
                # 检查是否已经创建过这个组
                if sub_group_name in groups_created:
                    self.log_message(f"跳过重复组: {sub_group_name}")
                    continue
                
                # 创建组
                group = self.get_group(self.etree_root, sub_group_name)
                files_element = group.xpath('.//Files')[0]
                
                # 添加文件
                for file_info in all_files:
                    self.add_file_to_files(files_element, file_info)
                    files_added += 1
                
                groups_created[sub_group_name] = len(all_files)
                self.log_message(f"创建组 '{sub_group_name}'，添加了 {len(all_files)} 个文件")
            
            # 保存文件
            self.write_to_file(self.etree_root, self.uvprojx_path)
            
            self.log_message(f"完成！创建了 {len(groups_created)} 个组，总共添加了 {files_added} 个文件")
            for group_name_created, file_count in groups_created.items():
                self.log_message(f"  - {group_name_created}: {file_count} 个文件")
            
            # 更新头文件路径
            if self.add_include_path(path):
                self.log_message("同时更新了头文件路径")
            
            return True
            
        except Exception as e:
            self.log_message(f"清理重建组失败: {str(e)}")
            return False

    def add_include_path(self, path: str):
        """
        为uvprojx添加目标编译的头文件路径
        :param path: 递归起始路径
        :return:
        """
        try:
            # 检查项目文件是否已加载
            if not self.uvprojx_path:
                self.log_message("错误: 请先设置项目文件")
                return False
            
            # 确保根节点已加载
            if self.etree_root is None:
                try:
                    self.get_root()
                except Exception as e:
                    self.log_message(f"加载项目文件失败: {str(e)}")
                    return False
            
            include_folders = self.get_folder_with_specific_files(path, [".h"])
            include_folders = [self.get_relative_path_uvprojx(folder).replace("\\", "/") for folder in include_folders]
            include_path_el = self.etree_root.xpath('//TargetArmAds//VariousControls/IncludePath')[0]

            include_path_list = include_path_el.text.split(";") + include_folders
            include_path_list = list(set(include_path_list))
            include_path_list.sort()
            include_path_el.text = ";".join(include_path_list)
            self.write_to_file(self.etree_root, self.uvprojx_path)
            self.log_message(f"成功添加 {len(include_folders)} 个头文件路径")
            return True
        except Exception as e:
            self.log_message(f"添加头文件路径失败: {str(e)}")
            return False

    def del_include_path(self, regex_pattern: str):
        """
        删除匹配正则表达式的头文件路径
        :param regex_pattern: 正则表达式
        :return:
        """
        try:
            # 检查项目文件是否已加载
            if not self.uvprojx_path:
                self.log_message("错误: 请先设置项目文件")
                return False
            
            # 确保根节点已加载
            if self.etree_root is None:
                try:
                    self.get_root()
                except Exception as e:
                    self.log_message(f"加载项目文件失败: {str(e)}")
                    return False
            
            include_path_el = self.etree_root.xpath('//TargetArmAds//VariousControls/IncludePath')[0]

            pattern = re.compile(regex_pattern)
            include_path_list = include_path_el.text.split(";")
            original_count = len(include_path_list)
            include_path_list = [item for item in include_path_list if not pattern.search(item)]
            deleted_count = original_count - len(include_path_list)
            
            include_path_el.text = ";".join(list(set(include_path_list)))
            self.write_to_file(self.etree_root, self.uvprojx_path)
            self.log_message(f"成功删除 {deleted_count} 个头文件路径")
            return True
        except Exception as e:
            self.log_message(f"删除头文件路径失败: {str(e)}")
            return False

    def get_relative_path(self, file_a, file_b):
        """
        获取文件的相对位置
        :param file_a:
        :param file_b:
        :return:
        """
        path_a = Path(file_a)
        path_b = Path(file_b)
        try:
            abs_path_a = path_a.resolve()
            abs_path_b = path_b.resolve()
            # 从文件 A 的绝对路径中移除文件 B 的父目录的绝对路径部分
            relative_path_parts = []
            i = 0
            while i < len(abs_path_a.parts) and i < len(abs_path_b.parts) and abs_path_a.parts[i] == abs_path_b.parts[
                i]:
                i += 1
            for j in range(i, len(abs_path_b.parts) - 1):
                relative_path_parts.append("..")
            relative_path_parts.extend(abs_path_a.parts[i:])
            relative_path = Path(*relative_path_parts)
            return str(relative_path)
        except Exception as e:
            self.log_message(f"Error occurred: {e}")
            return None

    def get_relative_path_uvprojx(self, file_a) -> str:
        return self.get_relative_path(file_a, self.uvprojx_path)

    def write_to_file(self, etree_root, output_file):
        """
        将 XML 元素树写入文件
        :param etree_root: XML 元素树的根节点
        :param output_file: 输出文件的路径
        """
        tree = etree.ElementTree(etree_root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

    def get_subfolders(self, path: str, max_depth: int):
        """
        获取指定深度的文件夹路径
        :param path: 递归路径
        :param max_depth: 最深层目录的层数
        :return:
        """
        result = []
        path = os.path.abspath(path)  # 标准化输入路径

        for root, dirs, files in os.walk(path):
            depth = root[len(path):].count(os.sep)
            if depth < max_depth:
                if not len(dirs):
                    result.append(root)
                    del dirs[:]

                if depth == max_depth - 1:
                    for dir_name in dirs:
                        result.append(os.path.join(root, dir_name))
                    del dirs[:]
            else:
                del dirs[:]

        # 标准化所有返回的路径
        return [os.path.abspath(p).replace('\\', '/') for p in result]
