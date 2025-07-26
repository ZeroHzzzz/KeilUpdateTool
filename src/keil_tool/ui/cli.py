"""
命令行界面
"""

from typing import Dict, Callable, List, Any

from ..constants import APP_AUTHOR, APP_GITHUB, APP_CREATE_TIME
from ..core import KeilProject


class KeilCLI:
    """Keil 工具命令行界面"""
    
    def __init__(self):
        self.keil_project = KeilProject()
        self.command_table = self._setup_commands()
    
    def _setup_commands(self) -> Dict[str, Callable]:
        """设置命令表"""
        return {
            "set_project": self.keil_project.set_project_file,
            "create_files_group": self.keil_project.create_files_group,
            "refresh_group": self.keil_project.refresh_group,
            "clean_rebuild_group": self.keil_project.clean_rebuild_group,
            "del_exist_group": self.keil_project.delete_existing_groups,
            "refresh_project": self.keil_project.refresh_project,
            "help": self.show_help
        }
    
    def show_help(self, language: str = "cn") -> None:
        """显示帮助信息"""
        if language == "en":
            self._print_help_en()
        else:
            self._print_help_cn()
    
    def _print_help_en(self) -> None:
        """打印英文帮助"""
        print("Available Commands:")
        print("\tset_project <path>")
        print("\t\t- Set project file path. <path> is the path to the .uvprojx file.")
        print("\tcreate_files_group <path> <max_depth> [group_root_name]")
        print("\t\t- Create a file group. <path> is the starting path, <max_depth> is max search depth.")
        print("\trefresh_group <group_name> <path> [max_depth]")
        print("\t\t- Refresh a specific file group (automatically updates include paths).")
        print("\tclean_rebuild_group <group_name> <path> [max_depth]")
        print("\t\t- Clean and rebuild a specific file group.")
        print("\tdel_exist_group <regex_pattern>")
        print("\t\t- Delete existing file groups using regex pattern.")
        print("\trefresh_project")
        print("\t\t- Refresh the project.")
        print("\texit")
        print("\t\t- Exit the program.")
        print("Project Information:")
        print(f"\\t- Author: {APP_AUTHOR}")
        print(f"\\t- Creation Time: {APP_CREATE_TIME}")
        print(f"\\t- Github: {APP_GITHUB}")
    
    def _print_help_cn(self) -> None:
        """打印中文帮助"""
        print("可用的命令:")
        print("\tset_project <path>")
        print("\t\t- 设置项目文件路径。<path> 是 .uvprojx 文件的路径。")
        print("\tcreate_files_group <path> <max_depth> [group_root_name]")
        print("\t\t- 创建文件组。<path> 是起始路径，<max_depth> 是查找的最大深度。")
        print("\trefresh_group <group_name> <path> [max_depth]")
        print("\t\t- 刷新指定文件组（自动更新头文件路径）。<group_name> 是要刷新的组名。")
        print("\tclean_rebuild_group <group_name> <path> [max_depth]")
        print("\t\t- 清理重建指定文件组，确保没有重复组。")
        print("\tdel_exist_group <regex_pattern>")
        print("\t\t- 删除存在的文件组。<regex_pattern> 是一个正则表达式。")
        print("\trefresh_project")
        print("\t\t- 刷新项目。")
        print("\texit")
        print("\t\t- 退出程序。")
        print("项目信息:")
        print(f"\\t- 作者：{APP_AUTHOR}")
        print(f"\\t- 创建时间：{APP_CREATE_TIME}")
        print(f"\\t- Github：{APP_GITHUB}")
    
    def _parse_parameters(self, command: str, params: List[str]) -> List[Any]:
        """解析命令参数"""
        if command == "set_project":
            return [params[0]]
        elif command == "create_files_group":
            return [params[0], int(params[1]), None if len(params) < 3 else params[2]]
        elif command in ["refresh_group", "clean_rebuild_group"]:
            if len(params) < 2:
                raise ValueError(f"{command} 需要至少2个参数: <group_name> <path> [max_depth]")
            group_name = params[0]
            path = params[1]
            max_depth = int(params[2]) if len(params) >= 3 else 3
            return [group_name, path, max_depth]
        elif command == "del_exist_group":
            return [params[0]]
        elif command == "refresh_project":
            return []
        elif command == "help":
            return [params[0] if len(params) >= 1 else "cn"]
        return []
    
    def run(self) -> None:
        """运行命令行界面"""
        self.show_help()
        
        # 尝试自动搜索项目文件
        project_file = self.keil_project.find_uvprojx_files()
        if project_file:
            if self.keil_project.set_project_file(project_file):
                print(f"已自动加载项目: {project_file}")
            else:
                print("项目文件加载失败")
        else:
            print("未找到项目文件，请使用 'set_project <path>' 命令手动指定项目文件")
        
        while True:
            try:
                user_input = input("keil tool: ").strip()
                if user_input.lower() == 'exit':
                    break
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0]
                
                if command not in self.command_table:
                    print("无效的指令，输入 'help' 查看帮助")
                    continue
                
                # 检查是否需要项目文件
                if command not in ["set_project", "help"] and not self.keil_project.project_path:
                    print("请先使用 'set_project <path>' 命令设置项目文件")
                    continue
                
                # 执行命令
                func = self.command_table[command]
                params = self._parse_parameters(command, parts[1:])
                
                if params is not None:
                    func(*params)
                
            except (IndexError, ValueError) as e:
                print(f"参数错误: {e}")
                print("输入 'help' 查看帮助文档")
            except KeyboardInterrupt:
                print("\n程序被用户中断")
                break
            except Exception as e:
                print(f"执行命令时出错: {e}")


def run_cli() -> None:
    """运行命令行界面"""
    cli = KeilCLI()
    cli.run()
