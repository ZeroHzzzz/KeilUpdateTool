import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from keil_tool_core import KeilTool


class KeilToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keil 项目管理工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 初始化Keil工具
        self.keil_tool = KeilTool(callback_func=self.log_message)
        
        self.setup_ui()
        self.init_project()
    
    def setup_ui(self):
        """设置UI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置grid权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # 项目信息区域
        info_frame = ttk.LabelFrame(main_frame, text="项目信息", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="项目文件:").grid(row=0, column=0, sticky=tk.W)
        self.project_path_var = tk.StringVar()
        self.project_path_label = ttk.Label(info_frame, textvariable=self.project_path_var, foreground="blue")
        self.project_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        
        # 项目文件选择按钮
        project_button_frame = ttk.Frame(info_frame)
        project_button_frame.grid(row=0, column=2, padx=(5, 0))
        ttk.Button(project_button_frame, text="选择项目", command=self.select_project_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(project_button_frame, text="自动搜索", command=self.auto_find_project).pack(side=tk.LEFT)
        
        # 头文件路径管理
        include_frame = ttk.LabelFrame(main_frame, text="头文件路径管理", padding="5")
        include_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        include_frame.columnconfigure(1, weight=1)
        
        # 添加头文件路径
        ttk.Label(include_frame, text="添加路径:").grid(row=0, column=0, sticky=tk.W)
        self.include_path_var = tk.StringVar()
        ttk.Entry(include_frame, textvariable=self.include_path_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(include_frame, text="浏览", command=self.browse_include_path).grid(row=0, column=2)
        ttk.Button(include_frame, text="添加", command=self.add_include_path).grid(row=0, column=3)
        
        # 删除头文件路径
        ttk.Label(include_frame, text="删除路径(正则):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.del_include_pattern_var = tk.StringVar()
        ttk.Entry(include_frame, textvariable=self.del_include_pattern_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(5, 0))
        ttk.Button(include_frame, text="删除", command=self.del_include_path).grid(row=1, column=3, pady=(5, 0))
        
        # 文件组管理
        group_frame = ttk.LabelFrame(main_frame, text="文件组管理", padding="5")
        group_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        group_frame.columnconfigure(1, weight=1)
        
        # 创建文件组
        ttk.Label(group_frame, text="路径:").grid(row=0, column=0, sticky=tk.W)
        self.group_path_var = tk.StringVar()
        ttk.Entry(group_frame, textvariable=self.group_path_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(group_frame, text="浏览", command=self.browse_group_path).grid(row=0, column=2)
        
        ttk.Label(group_frame, text="深度:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.max_depth_var = tk.StringVar(value="2")
        depth_spinbox = ttk.Spinbox(group_frame, from_=1, to=10, textvariable=self.max_depth_var, width=10)
        depth_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        
        ttk.Label(group_frame, text="组名前缀:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.group_name_var = tk.StringVar()
        ttk.Entry(group_frame, textvariable=self.group_name_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(5, 0))
        
        # 按钮框架
        button_group_frame = ttk.Frame(group_frame)
        button_group_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_group_frame, text="创建文件组", command=self.create_files_group).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_group_frame, text="刷新指定组", command=self.refresh_group).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_group_frame, text="清理重建组", command=self.clean_rebuild_group).pack(side=tk.LEFT)
        
        # 删除文件组
        ttk.Label(group_frame, text="删除组(正则):").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        self.del_group_pattern_var = tk.StringVar()
        ttk.Entry(group_frame, textvariable=self.del_group_pattern_var).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=(10, 0))
        ttk.Button(group_frame, text="删除", command=self.del_exist_group).grid(row=4, column=2, pady=(10, 0))
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 10))
        
        ttk.Button(button_frame, text="刷新项目", command=self.refresh_project).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="帮助", command=self.show_help).pack(side=tk.LEFT)
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(main_frame, text="日志输出", padding="5")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def log_message(self, message):
        """向日志区域添加消息"""
        def update_log():
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        
        # 如果是在子线程中调用，需要使用after方法
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update_log)
        else:
            update_log()
    
    def init_project(self):
        """初始化项目"""
        def init():
            project_file = self.keil_tool.find_uvprojx_files()
            if project_file:
                self.keil_tool.get_root(project_file)
                self.project_path_var.set(project_file)
            else:
                self.project_path_var.set("未找到项目文件，请手动选择")
        
        threading.Thread(target=init, daemon=True).start()
    
    def select_project_file(self):
        """选择项目文件"""
        file_path = filedialog.askopenfilename(
            title="选择 Keil 项目文件",
            filetypes=[("Keil Project Files", "*.uvprojx"), ("All Files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            def load_project():
                self.log_message(f"正在加载项目文件: {file_path}")
                if self.keil_tool.set_project_file(file_path):
                    self.project_path_var.set(file_path)
                    self.log_message("项目文件加载成功")
                else:
                    self.log_message("项目文件加载失败")
            
            threading.Thread(target=load_project, daemon=True).start()
    
    def auto_find_project(self):
        """自动搜索项目文件"""
        def find():
            self.log_message("正在搜索项目文件...")
            project_file = self.keil_tool.find_uvprojx_files()
            if project_file:
                self.keil_tool.get_root(project_file)
                self.project_path_var.set(project_file)
                self.log_message("自动搜索完成")
            else:
                self.project_path_var.set("未找到项目文件")
        
        threading.Thread(target=find, daemon=True).start()
    
    def refresh_project(self):
        """刷新项目"""
        def refresh():
            self.log_message("正在刷新项目...")
            project_file = self.keil_tool.find_uvprojx_files()
            if project_file:
                self.keil_tool.get_root(project_file)
                self.project_path_var.set(project_file)
                self.log_message("项目刷新完成")
            else:
                self.project_path_var.set("未找到项目文件")
        
        threading.Thread(target=refresh, daemon=True).start()
    
    def browse_include_path(self):
        """浏览选择头文件路径"""
        path = filedialog.askdirectory(title="选择头文件路径")
        if path:
            self.include_path_var.set(path)
    
    def browse_group_path(self):
        """浏览选择文件组路径"""
        path = filedialog.askdirectory(title="选择文件组路径")
        if path:
            self.group_path_var.set(path)
    
    def add_include_path(self):
        """添加头文件路径"""
        path = self.include_path_var.get().strip()
        if not path:
            messagebox.showwarning("警告", "请输入或选择头文件路径")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "指定的路径不存在")
            return
        
        def add_path():
            self.log_message(f"正在添加头文件路径: {path}")
            if self.keil_tool.add_include_path(path):
                self.log_message("添加头文件路径成功")
            else:
                self.log_message("添加头文件路径失败")
        
        threading.Thread(target=add_path, daemon=True).start()
    
    def del_include_path(self):
        """删除头文件路径"""
        pattern = self.del_include_pattern_var.get().strip()
        if not pattern:
            messagebox.showwarning("警告", "请输入正则表达式")
            return
        
        def del_path():
            self.log_message(f"正在删除匹配的头文件路径: {pattern}")
            if self.keil_tool.del_include_path(pattern):
                self.log_message("删除头文件路径成功")
            else:
                self.log_message("删除头文件路径失败")
        
        threading.Thread(target=del_path, daemon=True).start()
    
    def create_files_group(self):
        """创建文件组"""
        path = self.group_path_var.get().strip()
        max_depth = self.max_depth_var.get().strip()
        group_name = self.group_name_var.get().strip()
        
        if not path:
            messagebox.showwarning("警告", "请输入或选择文件组路径")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "指定的路径不存在")
            return
        
        try:
            depth = int(max_depth)
        except ValueError:
            messagebox.showerror("错误", "深度必须是整数")
            return
        
        def create_group():
            self.log_message(f"正在创建文件组: 路径={path}, 深度={depth}, 组名={group_name or '默认'}")
            group_root_name = group_name if group_name else None
            if self.keil_tool.creat_files_group(path, depth, group_root_name):
                self.log_message("创建文件组成功")
            else:
                self.log_message("创建文件组失败")
        
        threading.Thread(target=create_group, daemon=True).start()
    
    def refresh_group(self):
        """刷新指定文件组"""
        path = self.group_path_var.get().strip()
        max_depth = self.max_depth_var.get().strip()
        group_name = self.group_name_var.get().strip()
        
        if not path:
            messagebox.showwarning("警告", "请输入或选择文件组路径")
            return
        
        if not group_name:
            messagebox.showwarning("警告", "刷新组时必须指定组名")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "指定的路径不存在")
            return
        
        try:
            depth = int(max_depth)
        except ValueError:
            messagebox.showerror("错误", "深度必须是整数")
            return
        
        # 确认操作
        result = messagebox.askyesno("确认", f"确定要刷新组 '{group_name}' 吗？\n这将删除现有组并重新创建。")
        if not result:
            return
        
        def refresh():
            self.log_message(f"正在刷新文件组: 组名={group_name}, 路径={path}, 深度={depth}")
            if self.keil_tool.refresh_group(group_name, path, depth):
                self.log_message("刷新文件组成功")
            else:
                self.log_message("刷新文件组失败")
        
        threading.Thread(target=refresh, daemon=True).start()
    
    def clean_rebuild_group(self):
        """清理并重建指定文件组"""
        path = self.group_path_var.get().strip()
        max_depth = self.max_depth_var.get().strip()
        group_name = self.group_name_var.get().strip()
        
        if not path:
            messagebox.showwarning("警告", "请输入或选择文件组路径")
            return
        
        if not group_name:
            messagebox.showwarning("警告", "清理重建组时必须指定组名")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "指定的路径不存在")
            return
        
        try:
            depth = int(max_depth)
        except ValueError:
            messagebox.showerror("错误", "深度必须是整数")
            return
        
        # 确认操作
        result = messagebox.askyesno("确认", f"确定要清理重建组 '{group_name}' 吗？\n这将删除所有相关的子组并重新创建，确保没有重复。")
        if not result:
            return
        
        def clean_rebuild():
            self.log_message(f"正在清理重建文件组: 组名={group_name}, 路径={path}, 深度={depth}")
            if self.keil_tool.clean_rebuild_group(group_name, path, depth):
                self.log_message("清理重建文件组成功")
            else:
                self.log_message("清理重建文件组失败")
        
        threading.Thread(target=clean_rebuild, daemon=True).start()
    
    def del_exist_group(self):
        """删除文件组"""
        pattern = self.del_group_pattern_var.get().strip()
        if not pattern:
            messagebox.showwarning("警告", "请输入正则表达式")
            return
        
        def del_group():
            self.log_message(f"正在删除匹配的文件组: {pattern}")
            if self.keil_tool.del_exist_group(pattern):
                self.log_message("删除文件组成功")
            else:
                self.log_message("删除文件组失败")
        
        threading.Thread(target=del_group, daemon=True).start()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """Keil 项目管理工具使用说明

1. 头文件路径管理:
   - 添加路径: 选择包含头文件的文件夹，工具会自动搜索子文件夹
   - 删除路径: 使用正则表达式匹配要删除的路径

2. 文件组管理:
   - 路径: 选择要添加到项目的源代码文件夹
   - 深度: 指定搜索子文件夹的最大深度
   - 组名前缀: 可选，用于自定义文件组的名称前缀
   - 删除组: 使用正则表达式匹配要删除的文件组名称

3. 常用正则表达式示例:
   - '^path/to/.*' - 匹配以 'path/to/' 开头的路径
   - '.*Test.*' - 匹配包含 'Test' 的路径或组名
   - '^RRD' - 匹配以 'RRD' 开头的组名

4. 注意事项:
   - 请确保在包含 .uvprojx 文件的目录中运行此工具
   - 操作前建议备份项目文件
   - 所有操作都会在后台执行，请查看日志输出

作者: Rev_RoastDuck
GitHub: https://github.com/Rev-RoastedDuck
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助")
        help_window.geometry("600x500")
        help_window.resizable(True, True)
        
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    KeilToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
