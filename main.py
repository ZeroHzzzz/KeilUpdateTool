import argparse
from keil_tool_core import KeilTool


def manual(language: str = None):
    def print_help_en():
        print("Available Commands:")
        print("\tset_project <path>")
        print("\t\t- Set project file path. <path> is the path to the .uvprojx file, such as './MyProject.uvprojx' or 'C:\\path\\to\\project.uvprojx'.")
        print("\tadd_include_path <path>")
        print(
            "\t\t- Add header file path. <path> is the file system path to be added, such as '/path/to/include' or 'C:\\path\\to\\include'.")
        print("\tdel_include_path <regex_pattern>")
        print(
            "\t\t- Delete header file path. <regex_pattern> is a regular expression, for example, '^/path/to/.*' can be used to match paths that start with '/path/to/'.")
        print("\tcreat_files_group <path> <max_depth> [group_root_name]")
        print(
            "\t\t- Create a file group. <path> is the starting file system path, <max_depth> is the maximum search depth (an integer), and [group_root_name] is the optional root name of the group, for example, '/path/to/directory 2 MyGroup'.")
        print("\trefresh_group <group_name> <path> [max_depth]")
        print(
            "\t\t- Refresh a specific file group. <group_name> is the name of the group to refresh, <path> is the file path, [max_depth] is the optional search depth (default 3), for example, 'refresh_group MyGroup ./src 2'.")
        print("\tclean_rebuild_group <group_name> <path> [max_depth]")
        print(
            "\t\t- Clean and rebuild a specific file group to avoid duplicates. <group_name> is the name of the group to rebuild, <path> is the file path, [max_depth] is the optional search depth (default 3), for example, 'clean_rebuild_group MyGroup ./src 2'.")
        print("\tdel_exist_group <regex_pattern>")
        print(
            "\t\t- Delete an existing file group. <regex_pattern> is a regular expression, for example, '^RRD*' can be used to match groups that start with 'RRD'.")
        print("\tupdate_root")
        print("\t\t- Update the root node.")
        print("\texit")
        print("\t\t- Exit the program.")
        print("Project Information:")
        print("\t- Author: Rev_RoastDuck")
        print("\t- Creation Time: 2024_01_08")
        print("\t- Github: https://github.com/Rev-RoastedDuck")

    def print_help_cn():
        print("可用的命令:")
        print("\tset_project <path>")
        print("\t\t- 设置项目文件路径。<path> 是 .uvprojx 文件的路径，例如 './MyProject.uvprojx' 或 'C:\\path\\to\\project.uvprojx'。")
        print("\tadd_include_path <path>")
        print("\t\t- 添加头文件路径。<path> 是要添加的文件系统路径，例如 '/path/to/include' 或 'C:\\path\\to\\include'。")
        print("\tdel_include_path <regex_pattern>")
        print("\t\t- 删除头文件路径。<regex_pattern> 是一个正则表达式，例如 '^/path/to/.*' 可用于匹配以 '/path/to/' 开头的路径。")
        print("\tcreat_files_group <path> <max_depth> [group_root_name]")
        print(
            "\t\t- 创建文件组。<path> 是起始文件系统路径，<max_depth> 是查找的最大深度（整数），[group_root_name] 是可选的组根名称，例如 '/path/to/directory 2 MyGroup'。")
        print("\trefresh_group <group_name> <path> [max_depth]")
        print(
            "\t\t- 刷新指定文件组。<group_name> 是要刷新的组名，<path> 是文件路径，[max_depth] 是可选的搜索深度（默认3），例如 'refresh_group MyGroup ./src 2'。")
        print("\tclean_rebuild_group <group_name> <path> [max_depth]")
        print(
            "\t\t- 清理重建指定文件组，确保没有重复组。<group_name> 是要重建的组名，<path> 是文件路径，[max_depth] 是可选的搜索深度（默认3），例如 'clean_rebuild_group MyGroup ./src 2'。")
        print("\tdel_exist_group <regex_pattern>")
        print("\t\t- 删除存在的文件组。<regex_pattern> 是一个正则表达式，例如 '^RRD*' 可用于匹配以 'RRD' 开头的组。")
        print("\tupdate_root")
        print("\t\t- 更新根节点。")
        print("\texit")
        print("\t\t- 退出程序。")
        print("项目信息:")
        print("\t- 作者：Rev_RoastDuck")
        print("\t- 创建时间：2024_01_08")
        print("\t- Github：https://github.com/Rev-RoastedDuck")

    if "en" == language:
        print_help_en()
    else:
        print_help_cn()


def main_cli():
    """命令行模式的主函数"""
    manual()
    tool = KeilTool()
    
    # 尝试自动搜索项目文件
    g_file_path = tool.find_uvprojx_files()
    if g_file_path:
        tool.get_root(g_file_path)
        print(f"已自动加载项目: {g_file_path}")
    else:
        print("未找到项目文件，请使用 'set_project <path>' 命令手动指定项目文件")

    command_table = {
        "set_project": tool.set_project_file,
        "add_include_path": tool.add_include_path,
        "del_include_path": tool.del_include_path,
        "creat_files_group": tool.creat_files_group,
        "refresh_group": tool.refresh_group,
        "clean_rebuild_group": tool.clean_rebuild_group,
        "del_exist_group": tool.del_exist_group,
        "update_root": tool.get_root,
        "help": manual
    }

    def parse_param(cmd: str, params: list):
        if "set_project" == cmd:
            return [params[0]]
        elif "add_include_path" == cmd:
            return [params[0]]
        elif "creat_files_group" == cmd:
            return [params[0], int(params[1]), None if not len(params) == 3 else params[2]]
        elif "refresh_group" == cmd:
            # refresh_group <group_name> <path> [max_depth]
            if len(params) < 2:
                raise ValueError("refresh_group 需要至少2个参数: <group_name> <path> [max_depth]")
            group_name = params[0]
            path = params[1]
            max_depth = int(params[2]) if len(params) >= 3 else 3
            return [group_name, path, max_depth]
        elif "clean_rebuild_group" == cmd:
            # clean_rebuild_group <group_name> <path> [max_depth]
            if len(params) < 2:
                raise ValueError("clean_rebuild_group 需要至少2个参数: <group_name> <path> [max_depth]")
            group_name = params[0]
            path = params[1]
            max_depth = int(params[2]) if len(params) >= 3 else 3
            return [group_name, path, max_depth]
        elif "del_exist_group" == cmd:
            return [params[0]]
        elif "del_include_path" == cmd:
            return [params[0]]
        elif "update_root" == cmd:
            return []
        elif "help" == cmd:
            return ["" if not len(params) == 1 else params[0]]
        return []

    while True:
        user_input = input("keil tool: ")
        if user_input.lower() == 'exit':
            break

        try:
            parts = user_input.split()
            if not parts:
                continue
            command = parts[0]
            if command not in command_table:
                print("无效的指令")
                continue
            
            # 检查是否需要项目文件（除了 set_project 和 help 命令）
            if command not in ["set_project", "help"] and not tool.uvprojx_path:
                print("请先使用 'set_project <path>' 命令设置项目文件")
                continue
            
            # 对于需要根节点的命令，确保根节点已加载
            if command not in ["set_project", "help"] and not tool.etree_root:
                tool.get_root()
            
            func = command_table[command]
            params = parse_param(command, parts[1:])
            if params is not None:
                func(*params)

        except IndexError:
            print("Keil-Tool: 输入格式错误，输入`help`或`help en`查看帮助文档。")
        except Exception as e:
            print(f"执行命令时出错: {e}")


def main_gui():
    """GUI模式的主函数"""
    try:
        from keil_tool_gui import KeilToolGUI
        import tkinter as tk
        
        root = tk.Tk()
        KeilToolGUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"启动GUI失败，缺少依赖: {e}")
        print("请使用命令行模式: python main.py --cli")
    except Exception as e:
        print(f"启动GUI时出错: {e}")


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description="Keil 项目管理工具")
    parser.add_argument("--cli", action="store_true", help="使用命令行模式")
    parser.add_argument("--gui", action="store_true", help="使用GUI模式")
    
    args = parser.parse_args()
    
    # 如果没有指定模式，默认使用GUI模式
    if not args.cli and not args.gui:
        args.gui = True
    
    if args.cli:
        main_cli()
    elif args.gui:
        main_gui()


if __name__ == "__main__":
    main()