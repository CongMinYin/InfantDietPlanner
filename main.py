import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from database import Database
from ai_service import AIService

class DatabaseSelectDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        # 创建弹窗
        self.window = tk.Toplevel(parent)
        self.window.title("选择数据库")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 数据库类型选择
        type_frame = ttk.LabelFrame(self.main_frame, text="数据库类型", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.db_type_var = tk.StringVar(value="sqlite")
        
        ttk.Radiobutton(type_frame, text="SQLite (嵌入式，无需安装)", variable=self.db_type_var, value="sqlite").pack(anchor=tk.W, pady=(5, 0))
        ttk.Radiobutton(type_frame, text="MySQL (需要安装MySQL服务)", variable=self.db_type_var, value="mysql").pack(anchor=tk.W, pady=(5, 0))
        
        # MySQL连接参数
        self.mysql_frame = ttk.LabelFrame(self.main_frame, text="MySQL连接参数", padding="10")
        self.mysql_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 主机
        host_frame = ttk.Frame(self.mysql_frame)
        host_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(host_frame, text="主机：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(host_frame, textvariable=self.host_var, width=30).pack(side=tk.LEFT)
        
        # 用户名
        user_frame = ttk.Frame(self.mysql_frame)
        user_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(user_frame, text="用户名：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.user_var = tk.StringVar(value="root")
        ttk.Entry(user_frame, textvariable=self.user_var, width=30).pack(side=tk.LEFT)
        
        # 密码
        password_frame = ttk.Frame(self.mysql_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(password_frame, text="密码：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.password_var = tk.StringVar(value="123456")
        ttk.Entry(password_frame, textvariable=self.password_var, show="*", width=30).pack(side=tk.LEFT)
        
        # 数据库
        db_frame = ttk.Frame(self.mysql_frame)
        db_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(db_frame, text="数据库：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.db_var = tk.StringVar(value="infant_health")
        ttk.Entry(db_frame, textvariable=self.db_var, width=30).pack(side=tk.LEFT)
        
        # 按钮区域 - 增加垂直空间
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        # 创建更大的按钮
        ttk.Button(button_frame, text="连接", command=self.connect, width=15).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel, width=15).pack(side=tk.RIGHT)
        
        # 强制更新窗口大小
        self.window.update_idletasks()
        
        # 显示窗口
        self.window.wait_window()
    
    def connect(self):
        self.result = {
            'db_type': self.db_type_var.get(),
            'host': self.host_var.get(),
            'user': self.user_var.get(),
            'password': self.password_var.get(),
            'db': self.db_var.get()
        }
        self.window.destroy()
    
    def cancel(self):
        self.result = None
        self.window.destroy()

class InfantHealthSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("婴幼儿健康系统")
        self.root.geometry("1920x1920")
        self.root.minsize(1920, 1920)
        
        # 初始化属性
        self.current_infant_name = None
        self.current_infant_id = None
        self.infant_names = []
        
        # 显示数据库连接对话框
        self.db = None
        self.connect_database()
        
        if not self.db:
            messagebox.showerror("错误", "数据库连接失败，程序将退出")
            root.destroy()
            return
        
        # 初始化AI服务
        self.ai_service = AIService()
        
        # AI上下文数量设置
        self.context_limit = 20
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧婴幼儿信息管理区域 - 增大宽度
        self.left_frame = ttk.LabelFrame(self.main_frame, text="婴幼儿档案管理", padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10), ipadx=20)
        
        # 创建右侧聊天区域
        self.right_frame = ttk.LabelFrame(self.main_frame, text="AI健康顾问", padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 初始化左侧婴幼儿管理界面
        self.init_infant_management()
        
        # 初始化右侧聊天界面
        self.init_chat_interface()
        
        # 加载婴幼儿列表
        self.load_infant_list()
    
    def _get_who_growth_standards(self):
        """
        获取WHO儿童生长标准数据
        返回0-36月龄的WHO生长标准百分位数
        """
        # 数据来源：WHO儿童生长标准
        return {
            'weight': {
                'boys': {
                    'p3': [2.4, 3.1, 3.7, 4.2, 4.6, 5.0, 5.3, 5.6, 5.9, 6.1, 6.3, 6.5, 6.7, 6.9, 7.0, 7.2, 7.3, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0, 9.1, 9.2, 9.3],
                    'p50': [3.3, 4.3, 5.0, 5.6, 6.1, 6.6, 7.0, 7.4, 7.7, 8.0, 8.3, 8.6, 8.8, 9.1, 9.3, 9.5, 9.7, 9.9, 10.1, 10.3, 10.4, 10.6, 10.8, 10.9, 11.1, 11.2, 11.4, 11.5, 11.7, 11.8, 11.9, 12.1, 12.2, 12.3, 12.4, 12.6],
                    'p97': [4.3, 5.4, 6.3, 7.0, 7.7, 8.3, 8.8, 9.3, 9.7, 10.1, 10.5, 10.8, 11.2, 11.5, 11.8, 12.1, 12.4, 12.7, 13.0, 13.3, 13.5, 13.8, 14.0, 14.3, 14.5, 14.8, 15.0, 15.2, 15.5, 15.7, 15.9, 16.2, 16.4, 16.6, 16.8, 17.1]
                },
                'girls': {
                    'p3': [2.3, 3.0, 3.6, 4.0, 4.4, 4.8, 5.1, 5.4, 5.6, 5.8, 6.0, 6.2, 6.3, 6.5, 6.6, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8],
                    'p50': [3.2, 4.1, 4.8, 5.3, 5.7, 6.1, 6.5, 6.8, 7.1, 7.3, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 8.9, 9.1, 9.3, 9.4, 9.6, 9.7, 9.9, 10.0, 10.1, 10.3, 10.4, 10.5, 10.6, 10.8, 10.9, 11.0, 11.1, 11.2, 11.4],
                    'p97': [4.1, 5.2, 6.0, 6.6, 7.1, 7.6, 8.0, 8.4, 8.8, 9.1, 9.4, 9.7, 10.0, 10.3, 10.5, 10.8, 11.0, 11.3, 11.5, 11.7, 12.0, 12.2, 12.4, 12.6, 12.8, 13.0, 13.2, 13.4, 13.6, 13.8, 14.0, 14.2, 14.4, 14.6, 14.8, 15.0]
                }
            },
            'height': {
                'boys': {
                    'p3': [45.9, 51.2, 55.3, 58.6, 61.3, 63.7, 65.8, 67.6, 69.2, 70.6, 71.9, 73.1, 74.2, 75.3, 76.3, 77.2, 78.1, 79.0, 79.8, 80.6, 81.3, 82.1, 82.8, 83.5, 84.2, 84.8, 85.5, 86.1, 86.7, 87.3, 87.9, 88.5, 89.1, 89.6, 90.2, 90.7],
                    'p50': [49.9, 55.5, 59.8, 63.2, 66.0, 68.6, 70.9, 72.9, 74.7, 76.3, 77.7, 79.0, 80.3, 81.5, 82.7, 83.8, 84.8, 85.8, 86.8, 87.7, 88.6, 89.5, 90.3, 91.1, 91.9, 92.7, 93.5, 94.2, 95.0, 95.7, 96.4, 97.1, 97.8, 98.4, 99.1, 99.7],
                    'p97': [53.9, 59.8, 64.3, 67.9, 70.9, 73.7, 76.2, 78.4, 80.4, 82.2, 83.9, 85.4, 86.9, 88.3, 89.6, 90.9, 92.1, 93.3, 94.4, 95.5, 96.6, 97.6, 98.6, 99.6, 100.5, 101.4, 102.3, 103.2, 104.0, 104.8, 105.6, 106.4, 107.1, 107.9, 108.6, 109.3]
                },
                'girls': {
                    'p3': [45.4, 50.5, 54.4, 57.6, 60.2, 62.5, 64.5, 66.2, 67.8, 69.2, 70.5, 71.7, 72.8, 73.8, 74.8, 75.7, 76.6, 77.5, 78.3, 79.1, 79.8, 80.6, 81.3, 82.0, 82.6, 83.3, 83.9, 84.5, 85.1, 85.7, 86.3, 86.9, 87.5, 88.0, 88.6, 89.1],
                    'p50': [49.4, 54.7, 58.8, 62.0, 64.7, 67.1, 69.3, 71.2, 72.9, 74.5, 75.9, 77.2, 78.5, 79.7, 80.9, 82.0, 83.1, 84.1, 85.1, 86.0, 86.9, 87.8, 88.6, 89.5, 90.3, 91.1, 91.8, 92.6, 93.3, 94.0, 94.7, 95.4, 96.1, 96.7, 97.4, 98.0],
                    'p97': [53.4, 59.0, 63.1, 66.4, 69.2, 71.7, 73.9, 75.9, 77.8, 79.4, 81.0, 82.5, 83.9, 85.2, 86.5, 87.7, 88.9, 90.0, 91.1, 92.2, 93.2, 94.2, 95.2, 96.1, 97.0, 97.9, 98.8, 99.6, 100.5, 101.3, 102.1, 102.8, 103.6, 104.3, 105.0, 105.7]
                }
            },
            'head_circumference': {
                'boys': {
                    'p3': [30.9, 34.4, 36.9, 38.7, 40.0, 41.1, 42.0, 42.8, 43.4, 44.0, 44.5, 45.0, 45.4, 45.8, 46.2, 46.5, 46.8, 47.1, 47.4, 47.6, 47.9, 48.1, 48.3, 48.5, 48.7, 48.9, 49.1, 49.2, 49.4, 49.6, 49.7, 49.9, 50.0, 50.2, 50.3, 50.4],
                    'p50': [33.9, 37.3, 39.6, 41.2, 42.5, 43.5, 44.3, 45.0, 45.6, 46.1, 46.6, 47.0, 47.4, 47.7, 48.1, 48.4, 48.7, 48.9, 49.2, 49.4, 49.7, 49.9, 50.1, 50.3, 50.5, 50.7, 50.8, 51.0, 51.2, 51.3, 51.5, 51.6, 51.8, 51.9, 52.0, 52.1],
                    'p97': [36.9, 40.2, 42.3, 43.7, 44.9, 45.8, 46.6, 47.3, 47.8, 48.3, 48.8, 49.2, 49.6, 49.9, 50.3, 50.6, 50.9, 51.1, 51.4, 51.6, 51.9, 52.1, 52.3, 52.5, 52.7, 52.9, 53.1, 53.2, 53.4, 53.5, 53.7, 53.8, 53.9, 54.1, 54.2, 54.3]
                },
                'girls': {
                    'p3': [30.5, 33.8, 36.2, 37.9, 39.1, 40.1, 40.9, 41.7, 42.3, 42.8, 43.3, 43.8, 44.1, 44.5, 44.8, 45.1, 45.4, 45.7, 45.9, 46.1, 46.4, 46.6, 46.8, 47.0, 47.2, 47.3, 47.5, 47.7, 47.8, 48.0, 48.1, 48.3, 48.4, 48.5, 48.6, 48.7],
                    'p50': [33.5, 36.8, 39.0, 40.5, 41.7, 42.6, 43.4, 44.1, 44.7, 45.1, 45.6, 46.0, 46.4, 46.7, 47.0, 47.3, 47.6, 47.9, 48.1, 48.3, 48.6, 48.8, 49.0, 49.2, 49.4, 49.6, 49.7, 49.9, 50.0, 50.2, 50.3, 50.5, 50.6, 50.7, 50.8, 50.9],
                    'p97': [36.5, 39.7, 41.7, 43.2, 44.3, 45.2, 46.0, 46.6, 47.2, 47.7, 48.1, 48.5, 48.9, 49.2, 49.5, 49.8, 50.1, 50.3, 50.6, 50.8, 51.0, 51.3, 51.5, 51.7, 51.9, 52.1, 52.2, 52.4, 52.6, 52.7, 52.9, 53.0, 53.1, 53.3, 53.4, 53.5]
                }
            }
        }

    def connect_database(self):
        """
        连接数据库
        """
        dialog = DatabaseSelectDialog(self.root)
        if dialog.result:
            db_type = dialog.result['db_type']
            if db_type == 'sqlite':
                # SQLite连接
                self.db = Database(
                    db_type='sqlite',
                    db=dialog.result['db']
                )
                if not self.db.connect():
                    # 连接失败，重新显示对话框
                    retry = messagebox.askretrycancel("连接失败", "SQLite数据库连接失败，是否重试？")
                    if retry:
                        self.connect_database()
                    else:
                        self.db = None
            else:
                # MySQL连接
                self.db = Database(
                    db_type='mysql',
                    host=dialog.result['host'],
                    user=dialog.result['user'],
                    password=dialog.result['password'],
                    db=dialog.result['db']
                )
                if not self.db.connect():
                    # 连接失败，重新显示对话框
                    retry = messagebox.askretrycancel("连接失败", "MySQL数据库连接失败，是否重试？")
                    if retry:
                        self.connect_database()
                    else:
                        self.db = None
        else:
            self.db = None
    
    def init_infant_management(self):
        # 婴幼儿选择区域
        select_frame = ttk.Frame(self.left_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(select_frame, text="选择婴幼儿：").pack(side=tk.LEFT, padx=(0, 5))
        
        self.infant_var = tk.StringVar()
        self.infant_combobox = ttk.Combobox(select_frame, textvariable=self.infant_var, width=30)
        self.infant_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.infant_combobox.bind("<<ComboboxSelected>>", self.on_infant_selected)
        
        # 操作按钮
        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="添加", command=self.add_infant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="修改", command=self.edit_infant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除", command=self.delete_infant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除历史档案", command=self.delete_history_records).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="历史档案", command=self.view_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加示例", command=self.add_sample_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # 导出和统计按钮
        export_frame = ttk.Frame(self.left_frame)
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(export_frame, text="导出生长曲线", command=self.export_growth_curve).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="导出婴儿信息", command=self.export_infant_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="导出聊天记录", command=self.export_chat_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(export_frame, text="数据统计", command=self.display_statistics).pack(side=tk.LEFT)
        
        # 婴幼儿信息显示区域
        self.info_frame = ttk.LabelFrame(self.left_frame, text="基本信息", padding="10")
        self.info_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.info_text = tk.Text(self.info_frame, wrap=tk.WORD, state=tk.DISABLED, height=12, font=("SimHei", 12))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 生长曲线区域
        self.growth_frame = ttk.LabelFrame(self.left_frame, text="生长曲线", padding="10")
        self.growth_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建生长曲线画布
        self.growth_canvas = tk.Canvas(self.growth_frame)
        self.growth_canvas.pack(fill=tk.BOTH, expand=True)
    
    def init_chat_interface(self):
        # 聊天设置区域
        setting_frame = ttk.Frame(self.right_frame)
        setting_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(setting_frame, text="AI上下文数量：").pack(side=tk.LEFT, padx=(0, 5))
        
        self.context_var = tk.StringVar(value=str(self.context_limit))
        self.context_entry = ttk.Entry(setting_frame, textvariable=self.context_var, width=5)
        self.context_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.chat_time_label = ttk.Label(setting_frame, text="对话时间范围：无")
        self.chat_time_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 聊天记录区域 - 减少垂直扩展比例
        self.chat_frame = ttk.Frame(self.right_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.chat_text = tk.Text(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED, font=("SimHei", 12))
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.chat_frame, orient=tk.VERTICAL, command=self.chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.config(yscrollcommand=scrollbar.set)
        
        # 输入区域 - 增大高度并允许垂直扩展
        input_frame = ttk.Frame(self.right_frame)
        input_frame.pack(fill=tk.BOTH, expand=False, pady=(5, 0))
        
        self.input_text = tk.Text(input_frame, height=8, wrap=tk.WORD, font=("SimHei", 12))
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        send_button = ttk.Button(input_frame, text="发送", command=self.send_message, width=10)
        send_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定回车键发送消息
        self.input_text.bind("<Return>", lambda e: self.send_message())
        # 保留Ctrl+Enter作为备选
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())
    
    def load_infant_list(self):
        # 加载婴幼儿列表到下拉框
        infants = self.db.get_all_infants()
        if infants:
            self.infant_names = [infant['name'] for infant in infants]
            self.infant_combobox['values'] = self.infant_names
            # 如果当前没有选择婴幼儿，设置默认值为第一个
            if not self.current_infant_name and self.infant_names:
                self.infant_var.set(self.infant_names[0])
                self.current_infant_name = self.infant_names[0]
                # 获取当前婴幼儿的ID
                latest_info = self.db.get_latest_infant(self.infant_names[0])
                if latest_info:
                    self.current_infant_id = latest_info['id']
                self.display_latest_infant_info(self.infant_names[0])
                self.plot_growth_curve(self.infant_names[0])
                self.load_chat_history(self.infant_names[0])
        else:
            self.infant_names = []
            self.infant_combobox['values'] = []
            self.infant_var.set("")
            self.current_infant_name = None
            self.clear_info_display()
            self.clear_chat_display()
    
    def on_infant_selected(self, event):
        # 当选择婴幼儿时，更新当前婴幼儿姓名和显示信息
        selected_name = self.infant_var.get()
        if selected_name:
            self.current_infant_name = selected_name
            # 获取当前婴幼儿的ID
            latest_info = self.db.get_latest_infant(selected_name)
            if latest_info:
                self.current_infant_id = latest_info['id']
            self.display_latest_infant_info(selected_name)
            # 生成生长曲线
            self.plot_growth_curve(selected_name)
            # 加载聊天历史
            self.load_chat_history(selected_name)
    
    def display_latest_infant_info(self, name):
        # 显示婴幼儿最新信息
        infant = self.db.get_latest_infant(name)
        if infant:
            # 计算月龄
            birth_date = datetime.datetime.strptime(str(infant['birth_date']), "%Y-%m-%d")
            today = datetime.datetime.now()
            months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
            
            info = f"姓名：{infant['name']}\n"
            info += f"性别：{infant['gender']}\n"
            info += f"出生日期：{infant['birth_date']}\n"
            info += f"月龄：{months}个月\n"
            info += f"记录日期：{infant['record_date']}\n"
            info += f"是否早产：{'是' if infant['is_preterm'] else '否'}\n"
            if infant['is_preterm']:
                info += f"早产周数：{infant['gestational_age']}周\n"
            info += f"体重：{infant['weight']} kg\n"
            info += f"身高：{infant['height']} cm\n"
            if infant['head_circumference']:
                info += f"头围：{infant['head_circumference']} cm\n"
            info += f"主要喂养方式：{infant['feeding_type']}\n"
            if infant['daily_milk']:
                info += f"每天喝奶量：{infant['daily_milk']} mL\n"
            if infant['辅食_start_age']:
                info += f"辅食添加月龄：{infant['辅食_start_age']}个月\n"
            info += f"食物过敏：{infant['allergies'] if infant['allergies'] else '无'}\n"
            info += f"健康状况：{infant['health_conditions'] if infant['health_conditions'] else '无'}\n"
            info += f"补充剂：{infant['supplements'] if infant['supplements'] else '无'}\n"
            info += f"食物质地：{infant['food_texture']}\n"
            info += f"不爱吃的食物：{infant['disliked_foods'] if infant['disliked_foods'] else '无'}\n"
            info += f"独立进食：{'会' if infant['can_eat_independently'] else '不会'}\n"
            info += f"家庭饮食要求：{infant['family_dietary_restrictions'] if infant['family_dietary_restrictions'] else '无'}\n"
            info += f"所在城市：{infant['city'] if infant['city'] else '未填写'}\n"
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info)
            self.info_text.config(state=tk.DISABLED)
        else:
            self.clear_info_display()
    
    def clear_info_display(self):
        # 清空信息显示
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "请选择一个婴幼儿查看信息")
        self.info_text.config(state=tk.DISABLED)
    
    def add_infant(self):
        # 添加新婴幼儿
        from infant_form import InfantForm
        form = InfantForm(self.root, title="添加婴幼儿档案")
        if form.result:
            # 保存到数据库
            infant_id = self.db.add_infant(form.result)
            if infant_id:
                messagebox.showinfo("成功", "婴幼儿档案添加成功！")
                self.load_infant_list()
                # 选择新添加的婴幼儿
                # 重新加载后，最新添加的婴幼儿会出现在列表中
                # 由于我们使用姓名来管理，不需要特别处理ID
    
    def edit_infant(self):
        # 修改婴幼儿信息
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        # 获取最新的婴幼儿档案
        infant = self.db.get_latest_infant(self.current_infant_name)
        if not infant:
            messagebox.showerror("错误", "婴幼儿信息不存在")
            return
        
        # 转换为字典格式
        infant_data = {
            'name': infant['name'],
            'gender': infant['gender'],
            'birth_date': infant['birth_date'],
            'is_preterm': infant['is_preterm'],
            'gestational_age': infant['gestational_age'],
            'weight': infant['weight'],
            'height': infant['height'],
            'head_circumference': infant['head_circumference'],
            'feeding_type': infant['feeding_type'],
            'daily_milk': infant['daily_milk'],
            '辅食_start_age': infant['辅食_start_age'],
            'allergies': infant['allergies'],
            'health_conditions': infant['health_conditions'],
            'supplements': infant['supplements'],
            'food_texture': infant['food_texture'],
            'disliked_foods': infant['disliked_foods'],
            'can_eat_independently': infant['can_eat_independently'],
            'family_dietary_restrictions': infant['family_dietary_restrictions'],
            'city': infant['city']
        }
        
        from infant_form import InfantForm
        form = InfantForm(self.root, title="修改婴幼儿档案", data=infant_data)
        if form.result:
            # 更新数据库
            # 由于我们是按姓名来管理的，这里需要获取最新的ID
            latest_info = self.db.get_latest_infant(self.current_infant_name)
            if latest_info:
                success = self.db.update_infant(latest_info['id'], form.result)
                if success:
                    messagebox.showinfo("成功", "婴幼儿档案修改成功！")
                    self.display_latest_infant_info(self.current_infant_name)
                    self.load_infant_list()
                    # 重新选择当前婴幼儿
                    if self.infant_names:
                        try:
                            index = self.infant_names.index(self.current_infant_name)
                            self.infant_combobox.current(index)
                        except ValueError:
                            pass
    
    def delete_infant(self):
        # 删除婴幼儿
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        # 获取最新的婴幼儿档案，以获取ID
        latest_info = self.db.get_latest_infant(self.current_infant_name)
        if not latest_info:
            messagebox.showerror("错误", "婴幼儿信息不存在")
            return
        
        if messagebox.askyesno("确认", f"确定要删除{self.current_infant_name}的档案吗？此操作不可恢复！"):
            success = self.db.delete_infant(latest_info['id'])
            if success:
                messagebox.showinfo("成功", "婴幼儿档案删除成功！")
                self.current_infant_name = None
                self.current_infant_id = None
                self.load_infant_list()
                self.clear_info_display()
                self.clear_chat_display()
    
    def delete_history_records(self):
        # 删除婴幼儿的所有历史记录
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        if messagebox.askyesno("确认", f"确定要删除{self.current_infant_name}的所有历史记录吗？此操作不可恢复！"):
            success = self.db.delete_infant_history(self.current_infant_name)
            if success:
                messagebox.showinfo("成功", "历史记录删除成功！")
                # 重新加载婴幼儿列表
                self.load_infant_list()
                # 如果当前婴幼儿仍然存在，重新显示信息
                if self.current_infant_name in self.infant_names:
                    self.display_latest_infant_info(self.current_infant_name)
                    self.plot_growth_curve(self.current_infant_name)
                else:
                    self.current_infant_name = None
                    self.current_infant_id = None
                    self.clear_info_display()
                    self.clear_chat_display()
    
    def load_chat_history(self, infant_name):
        # 加载聊天历史
        history = self.db.get_chat_history(infant_name, limit=self.context_limit)
        self.clear_chat_display()
        
        for message in history:
            self.add_message_to_chat(message['role'], message['content'], message['timestamp'])
        
        # 更新聊天时间范围
        time_range = self.db.get_chat_time_range(infant_name)
        if time_range[0] and time_range[1]:
            self.chat_time_label.config(text=f"对话时间范围：{time_range[0]} 至 {time_range[1]}")
        else:
            self.chat_time_label.config(text="对话时间范围：无")
    
    def clear_chat_display(self):
        # 清空聊天显示
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self.chat_time_label.config(text="对话时间范围：无")
    
    def add_sample_data(self):
        """
        添加示例数据
        """
        # 检查是否已存在示例数据
        existing_infants = self.db.get_all_infants()
        existing_names = [infant['name'] for infant in existing_infants]
        
        if '大头儿子' in existing_names:
            messagebox.showinfo("提示", "示例数据已存在")
            return
        
        # 创建示例数据
        sample_data = [
            {
                'name': '大头儿子',
                'gender': '男',
                'birth_date': '2025-01-01',
                'is_preterm': 0,
                'gestational_age': None,
                'weight': 3.5,
                'height': 50.0,
                'head_circumference': 34.0,
                'feeding_type': '纯母乳',
                'daily_milk': 800.0,
                '辅食_start_age': None,
                'allergies': '无',
                'health_conditions': '无',
                'supplements': '维生素D',
                'food_texture': '果泥/米糊',
                'disliked_foods': '',
                'can_eat_independently': 0,
                'family_dietary_restrictions': '',
                'city': '北京',
                'record_date': '2025-01-01'
            },
            {
                'name': '大头儿子',
                'gender': '男',
                'birth_date': '2025-01-01',
                'is_preterm': 0,
                'gestational_age': None,
                'weight': 5.0,
                'height': 58.0,
                'head_circumference': 38.0,
                'feeding_type': '纯母乳',
                'daily_milk': 900.0,
                '辅食_start_age': None,
                'allergies': '无',
                'health_conditions': '无',
                'supplements': '维生素D',
                'food_texture': '果泥/米糊',
                'disliked_foods': '',
                'can_eat_independently': 0,
                'family_dietary_restrictions': '',
                'city': '北京',
                'record_date': '2025-03-01'
            },
            {
                'name': '大头儿子',
                'gender': '男',
                'birth_date': '2025-01-01',
                'is_preterm': 0,
                'gestational_age': None,
                'weight': 6.5,
                'height': 65.0,
                'head_circumference': 41.0,
                'feeding_type': '母乳+奶粉',
                'daily_milk': 700.0,
                '辅食_start_age': 6.0,
                'allergies': '无',
                'health_conditions': '无',
                'supplements': '维生素D,铁剂',
                'food_texture': '果泥/米糊',
                'disliked_foods': '菠菜',
                'can_eat_independently': 0,
                'family_dietary_restrictions': '',
                'city': '北京',
                'record_date': '2025-07-01'
            },
            {
                'name': '大头儿子',
                'gender': '男',
                'birth_date': '2025-01-01',
                'is_preterm': 0,
                'gestational_age': None,
                'weight': 8.0,
                'height': 72.0,
                'head_circumference': 44.0,
                'feeding_type': '母乳+奶粉',
                'daily_milk': 600.0,
                '辅食_start_age': 6.0,
                'allergies': '无',
                'health_conditions': '无',
                'supplements': '维生素D,铁剂',
                'food_texture': '软烂碎末',
                'disliked_foods': '菠菜',
                'can_eat_independently': 0,
                'family_dietary_restrictions': '',
                'city': '北京',
                'record_date': '2025-10-01'
            },
            {
                'name': '大头儿子',
                'gender': '男',
                'birth_date': '2025-01-01',
                'is_preterm': 0,
                'gestational_age': None,
                'weight': 9.5,
                'height': 78.0,
                'head_circumference': 46.0,
                'feeding_type': '已断奶',
                'daily_milk': 0.0,
                '辅食_start_age': 6.0,
                'allergies': '无',
                'health_conditions': '无',
                'supplements': '维生素D',
                'food_texture': '小块软饭',
                'disliked_foods': '菠菜',
                'can_eat_independently': 1,
                'family_dietary_restrictions': '',
                'city': '北京',
                'record_date': '2026-01-01'
            }
        ]
        
        # 插入示例数据
        for data in sample_data:
            self.db.add_infant(data)
        
        # 重新加载婴幼儿列表
        self.load_infant_list()
        
        # 选择第一个婴幼儿
        if self.infant_names:
            self.infant_var.set(self.infant_names[0])
            self.on_infant_selected(None)
        
        messagebox.showinfo("成功", "示例数据添加成功")
    
    def view_history(self):
        """
        查看历史档案
        """
        selected_name = self.infant_var.get()
        if not selected_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        # 获取历史档案
        history = self.db.get_infant_history(selected_name)
        if not history:
            messagebox.showinfo("提示", "无历史档案")
            return
        
        # 创建历史档案窗口
        window = tk.Toplevel(self.root)
        window.title(f"{selected_name}的历史档案")
        window.geometry("800x600")
        
        # 创建滚动区域
        canvas = tk.Canvas(window)
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示历史档案
        for i, record in enumerate(history):
            frame = ttk.LabelFrame(scrollable_frame, text=f"记录 {i+1} - {record['record_date']}", padding="10")
            frame.pack(fill=tk.X, pady=(0, 10))
            
            # 计算月龄
            birth_date = datetime.datetime.strptime(str(record['birth_date']), "%Y-%m-%d")
            record_date = datetime.datetime.strptime(str(record['record_date']), "%Y-%m-%d")
            months = (record_date.year - birth_date.year) * 12 + (record_date.month - birth_date.month)
            
            info = f"姓名：{record['name']}\n"
            info += f"性别：{record['gender']}\n"
            info += f"出生日期：{record['birth_date']}\n"
            info += f"记录时月龄：{months}个月\n"
            info += f"是否早产：{'是' if record['is_preterm'] else '否'}\n"
            if record['is_preterm']:
                info += f"早产周数：{record['gestational_age']}周\n"
            info += f"体重：{record['weight']} kg\n"
            info += f"身高：{record['height']} cm\n"
            if record['head_circumference']:
                info += f"头围：{record['head_circumference']} cm\n"
            info += f"主要喂养方式：{record['feeding_type']}\n"
            if record['daily_milk']:
                info += f"每天喝奶量：{record['daily_milk']} mL\n"
            if record['辅食_start_age']:
                info += f"辅食添加月龄：{record['辅食_start_age']}个月\n"
            info += f"食物过敏：{record['allergies'] if record['allergies'] else '无'}\n"
            info += f"健康状况：{record['health_conditions'] if record['health_conditions'] else '无'}\n"
            info += f"补充剂：{record['supplements'] if record['supplements'] else '无'}\n"
            info += f"食物质地：{record['food_texture']}\n"
            info += f"不爱吃的食物：{record['disliked_foods'] if record['disliked_foods'] else '无'}\n"
            info += f"独立进食：{'会' if record['can_eat_independently'] else '不会'}\n"
            info += f"家庭饮食要求：{record['family_dietary_restrictions'] if record['family_dietary_restrictions'] else '无'}\n"
            info += f"所在城市：{record['city'] if record['city'] else '未填写'}\n"
            
            text = tk.Text(frame, wrap=tk.WORD, height=15)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, info)
            text.config(state=tk.DISABLED)
    
    def plot_growth_curve(self, name):
        """
        绘制婴幼儿生长曲线
        :param name: 婴幼儿姓名
        """
        # 获取历史档案
        history = self.db.get_infant_history(name)
        if not history:
            # 清空画布
            self.growth_canvas.delete("all")
            self.growth_canvas.create_text(
                150, 100, 
                text="无历史数据，无法绘制生长曲线", 
                font=("SimHei", 12)
            )
            return
        
        # 准备数据
        months = []
        weights = []
        heights = []
        head_circumferences = []
        
        birth_date = datetime.datetime.strptime(str(history[0]['birth_date']), "%Y-%m-%d")
        gender = history[0]['gender']
        
        for record in history:
            record_date = datetime.datetime.strptime(str(record['record_date']), "%Y-%m-%d")
            month = (record_date.year - birth_date.year) * 12 + (record_date.month - birth_date.month)
            months.append(month)
            weights.append(record['weight'])
            heights.append(record['height'])
            if record['head_circumference']:
                head_circumferences.append(record['head_circumference'])
            else:
                head_circumferences.append(None)
        
        # 清除之前的图表
        for widget in self.growth_frame.winfo_children():
            widget.destroy()
        
        # 确保matplotlib不会阻塞主线程
        plt.ioff()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 获取WHO生长标准数据
        who_data = self._get_who_growth_standards()
        gender_key = 'boys' if gender == '男' else 'girls'
        
        # 生成WHO标准曲线的月龄点
        who_months = list(range(36))
        
        # 根据是否有头围数据决定图表布局
        if any(hc is not None for hc in head_circumferences):
            # 如果有头围数据，创建3个子图
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 7), dpi=100)
            fig.subplots_adjust(hspace=0.5)
            
            # 绘制体重曲线
            ax1.plot(months, weights, 'o-', color='blue', label='实际体重 (kg)')
            # 添加WHO参考曲线
            ax1.plot(who_months, who_data['weight'][gender_key]['p50'], '--', color='green', label='WHO P50')
            ax1.plot(who_months, who_data['weight'][gender_key]['p3'], ':', color='orange', label='WHO P3')
            ax1.plot(who_months, who_data['weight'][gender_key]['p97'], ':', color='red', label='WHO P97')
            ax1.fill_between(who_months, who_data['weight'][gender_key]['p3'], who_data['weight'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
            ax1.set_title('体重增长曲线')
            ax1.set_xlabel('月龄')
            ax1.set_ylabel('体重 (kg)')
            ax1.grid(True)
            ax1.legend()
            
            # 绘制身高曲线
            ax2.plot(months, heights, 'o-', color='blue', label='实际身高 (cm)')
            # 添加WHO参考曲线
            ax2.plot(who_months, who_data['height'][gender_key]['p50'], '--', color='green', label='WHO P50')
            ax2.plot(who_months, who_data['height'][gender_key]['p3'], ':', color='orange', label='WHO P3')
            ax2.plot(who_months, who_data['height'][gender_key]['p97'], ':', color='red', label='WHO P97')
            ax2.fill_between(who_months, who_data['height'][gender_key]['p3'], who_data['height'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
            ax2.set_title('身高增长曲线')
            ax2.set_xlabel('月龄')
            ax2.set_ylabel('身高 (cm)')
            ax2.grid(True)
            ax2.legend()
            
            # 绘制头围曲线
            # 过滤出头围数据
            valid_months = []
            valid_hc = []
            for m, hc in zip(months, head_circumferences):
                if hc is not None:
                    valid_months.append(m)
                    valid_hc.append(hc)
            ax3.plot(valid_months, valid_hc, 'o-', color='blue', label='实际头围 (cm)')
            # 添加WHO参考曲线
            ax3.plot(who_months, who_data['head_circumference'][gender_key]['p50'], '--', color='green', label='WHO P50')
            ax3.plot(who_months, who_data['head_circumference'][gender_key]['p3'], ':', color='orange', label='WHO P3')
            ax3.plot(who_months, who_data['head_circumference'][gender_key]['p97'], ':', color='red', label='WHO P97')
            ax3.fill_between(who_months, who_data['head_circumference'][gender_key]['p3'], who_data['head_circumference'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
            ax3.set_title('头围增长曲线')
            ax3.set_xlabel('月龄')
            ax3.set_ylabel('头围 (cm)')
            ax3.grid(True)
            ax3.legend()
        else:
            # 如果没有头围数据，创建2个子图
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), dpi=100)
            fig.subplots_adjust(hspace=0.5)
            
            # 绘制体重曲线
            ax1.plot(months, weights, 'o-', color='blue', label='实际体重 (kg)')
            # 添加WHO参考曲线
            ax1.plot(who_months, who_data['weight'][gender_key]['p50'], '--', color='green', label='WHO P50')
            ax1.plot(who_months, who_data['weight'][gender_key]['p3'], ':', color='orange', label='WHO P3')
            ax1.plot(who_months, who_data['weight'][gender_key]['p97'], ':', color='red', label='WHO P97')
            ax1.fill_between(who_months, who_data['weight'][gender_key]['p3'], who_data['weight'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
            ax1.set_title('体重增长曲线')
            ax1.set_xlabel('月龄')
            ax1.set_ylabel('体重 (kg)')
            ax1.grid(True)
            ax1.legend()
            
            # 绘制身高曲线
            ax2.plot(months, heights, 'o-', color='blue', label='实际身高 (cm)')
            # 添加WHO参考曲线
            ax2.plot(who_months, who_data['height'][gender_key]['p50'], '--', color='green', label='WHO P50')
            ax2.plot(who_months, who_data['height'][gender_key]['p3'], ':', color='orange', label='WHO P3')
            ax2.plot(who_months, who_data['height'][gender_key]['p97'], ':', color='red', label='WHO P97')
            ax2.fill_between(who_months, who_data['height'][gender_key]['p3'], who_data['height'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
            ax2.set_title('身高增长曲线')
            ax2.set_xlabel('月龄')
            ax2.set_ylabel('身高 (cm)')
            ax2.grid(True)
            ax2.legend()
        
        # 将图表添加到界面
        canvas = FigureCanvasTkAgg(fig, master=self.growth_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 手动清理matplotlib资源
        plt.close('all')
    
    def add_message_to_chat(self, role, content, timestamp):
        # 添加消息到聊天界面
        self.chat_text.config(state=tk.NORMAL)
        
        # 增加空行作为分隔
        self.chat_text.insert(tk.END, "\n\n")
        
        if role == "user":
            # 用户消息放在右边
            # 创建右对齐标签，增大时间戳字体
            self.chat_text.tag_config("user", foreground="blue", font=("SimHei", 12, "bold"), justify=tk.RIGHT)
            self.chat_text.tag_config("user_right", justify=tk.RIGHT, background="#E3F2FD")
            # 插入右对齐的用户信息和内容
            # 先插入一个空行，然后使用右对齐标签
            self.chat_text.insert(tk.END, "\n", "user")
            self.chat_text.insert(tk.END, f"【我】 {timestamp}\n", "user")
            # 增加时间戳和内容之间的空行
            self.chat_text.insert(tk.END, "\n")
            self.chat_text.insert(tk.END, content + "\n", "user_right")
        else:
            # AI消息放在左边
            # 创建左对齐标签，增大时间戳字体
            self.chat_text.tag_config("assistant", foreground="green", font=("SimHei", 12, "bold"), justify=tk.LEFT)
            self.chat_text.tag_config("assistant_left", justify=tk.LEFT, background="#F1F8E9")
            # 插入左对齐的AI信息和内容
            self.chat_text.insert(tk.END, f"\n【AI】 {timestamp}\n", "assistant")
            # 增加时间戳和内容之间的空行
            self.chat_text.insert(tk.END, "\n")
            self.chat_text.insert(tk.END, content + "\n", "assistant_left")
        
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
    def send_message(self):
        # 发送消息给AI
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        message = self.input_text.get(1.0, tk.END).strip()
        if not message:
            return
        
        # 获取当前时间
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 添加用户消息到聊天界面
        self.add_message_to_chat("user", message, current_time)
        
        # 保存用户消息到数据库
        self.db.add_chat_message(self.current_infant_name, "user", message)
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
        
        # 显示正在思考
        thinking_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.chat_text.config(state=tk.NORMAL)
        
        # 增加空行作为分隔
        self.chat_text.insert(tk.END, "\n\n")
        
        # AI消息放在左边
        # 创建左对齐标签，增大时间戳字体
        self.chat_text.tag_config("assistant", foreground="green", font=("SimHei", 12, "bold"), justify=tk.LEFT)
        self.chat_text.tag_config("assistant_left", justify=tk.LEFT, background="#F1F8E9")
        # 插入左对齐的AI信息和内容
        self.chat_text.insert(tk.END, f"\n【AI】 {thinking_time}\n", "assistant")
        # 增加时间戳和内容之间的空行
        self.chat_text.insert(tk.END, "\n")
        self.chat_text.insert(tk.END, "AI正在思考...\n", "assistant_left")
        
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
        
        # 刷新界面
        self.root.update()
        
        # 获取婴幼儿信息
        infant = self.db.get_latest_infant(self.current_infant_name)
        if infant:
            infant_info = {
                'name': infant['name'],
                'gender': infant['gender'],
                'birth_date': str(infant['birth_date']),
                'is_preterm': infant['is_preterm'],
                'gestational_age': infant['gestational_age'],
                'weight': infant['weight'],
                'height': infant['height'],
                'head_circumference': infant['head_circumference'],
                'feeding_type': infant['feeding_type'],
                'daily_milk': infant['daily_milk'],
                '辅食_start_age': infant['辅食_start_age'],
                'allergies': infant['allergies'],
                'health_conditions': infant['health_conditions'],
                'supplements': infant['supplements'],
                'food_texture': infant['food_texture'],
                'disliked_foods': infant['disliked_foods'],
                'can_eat_independently': infant['can_eat_independently'],
                'family_dietary_restrictions': infant['family_dietary_restrictions'],
                'city': infant['city']
            }
        else:
            infant_info = None
        
        # 生成系统提示
        system_prompt = self.ai_service.generate_system_prompt(infant_info)
        
        # 构建对话历史
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加最近的对话历史
        history = self.db.get_chat_history(self.current_infant_name, limit=self.context_limit - 1)
        for message_item in history:
            messages.append({"role": message_item['role'], "content": message_item['content']})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        
        # 调用AI获取回复
        response = self.ai_service.get_ai_response(messages)
        
        # 更新AI思考为实际回复
        self.chat_text.config(state=tk.NORMAL)
        # 删除最后几行（包括空行、思考提示和空行）
        # 从倒数第6行开始删除
        self.chat_text.delete('end-6l', tk.END)
        
        # 增加空行作为分隔
        self.chat_text.insert(tk.END, "\n\n")
        
        # 插入AI回复
        # AI消息放在左边
        # 创建左对齐标签，增大时间戳字体
        self.chat_text.tag_config("assistant", foreground="green", font=("SimHei", 12, "bold"), justify=tk.LEFT)
        self.chat_text.tag_config("assistant_left", justify=tk.LEFT, background="#F1F8E9")
        # 插入左对齐的AI信息和内容
        self.chat_text.insert(tk.END, f"\n【AI】 {current_time}\n", "assistant")
        # 增加时间戳和内容之间的空行
        self.chat_text.insert(tk.END, "\n")
        self.chat_text.insert(tk.END, response + "\n", "assistant_left")
        
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
        
        # 保存AI回复到数据库
        self.db.add_chat_message(self.current_infant_name, "assistant", response)
        
        # 更新聊天时间范围
        time_range = self.db.get_chat_time_range(self.current_infant_name)
        if time_range[0] and time_range[1]:
            self.chat_time_label.config(text=f"对话时间范围：{time_range[0]} 至 {time_range[1]}")
    
    def export_growth_curve(self):
        """
        导出生长曲线为PDF文件
        """
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        # 获取保存路径
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*")],
            title="导出生长曲线"
        )
        
        if not filename:
            return
        
        # 获取历史档案
        history = self.db.get_infant_history(self.current_infant_name)
        if not history:
            messagebox.showwarning("警告", "无历史数据，无法导出生长曲线")
            return
        
        # 准备数据
        months = []
        weights = []
        heights = []
        head_circumferences = []
        
        birth_date = datetime.datetime.strptime(str(history[0]['birth_date']), "%Y-%m-%d")
        gender = history[0]['gender']
        
        for record in history:
            record_date = datetime.datetime.strptime(str(record['record_date']), "%Y-%m-%d")
            month = (record_date.year - birth_date.year) * 12 + (record_date.month - birth_date.month)
            months.append(month)
            weights.append(record['weight'])
            heights.append(record['height'])
            if record['head_circumference']:
                head_circumferences.append(record['head_circumference'])
            else:
                head_circumferences.append(None)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 获取WHO生长标准数据
        who_data = self._get_who_growth_standards()
        gender_key = 'boys' if gender == '男' else 'girls'
        
        # 生成WHO标准曲线的月龄点
        who_months = list(range(36))
        
        # 创建PDF文件
        with PdfPages(filename) as pdf:
            # 根据是否有头围数据决定图表布局
            if any(hc is not None for hc in head_circumferences):
                # 如果有头围数据，创建3个子图
                fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8.5, 11), dpi=100)
                fig.subplots_adjust(hspace=0.5)
                
                # 绘制体重曲线
                ax1.plot(months, weights, 'o-', color='blue', label='实际体重 (kg)')
                ax1.plot(who_months, who_data['weight'][gender_key]['p50'], '--', color='green', label='WHO P50')
                ax1.plot(who_months, who_data['weight'][gender_key]['p3'], ':', color='orange', label='WHO P3')
                ax1.plot(who_months, who_data['weight'][gender_key]['p97'], ':', color='red', label='WHO P97')
                ax1.fill_between(who_months, who_data['weight'][gender_key]['p3'], who_data['weight'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
                ax1.set_title(f'{self.current_infant_name}的体重增长曲线')
                ax1.set_xlabel('月龄')
                ax1.set_ylabel('体重 (kg)')
                ax1.grid(True)
                ax1.legend()
                
                # 绘制身高曲线
                ax2.plot(months, heights, 'o-', color='blue', label='实际身高 (cm)')
                ax2.plot(who_months, who_data['height'][gender_key]['p50'], '--', color='green', label='WHO P50')
                ax2.plot(who_months, who_data['height'][gender_key]['p3'], ':', color='orange', label='WHO P3')
                ax2.plot(who_months, who_data['height'][gender_key]['p97'], ':', color='red', label='WHO P97')
                ax2.fill_between(who_months, who_data['height'][gender_key]['p3'], who_data['height'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
                ax2.set_title(f'{self.current_infant_name}的身高增长曲线')
                ax2.set_xlabel('月龄')
                ax2.set_ylabel('身高 (cm)')
                ax2.grid(True)
                ax2.legend()
                
                # 绘制头围曲线
                valid_months = []
                valid_hc = []
                for m, hc in zip(months, head_circumferences):
                    if hc is not None:
                        valid_months.append(m)
                        valid_hc.append(hc)
                ax3.plot(valid_months, valid_hc, 'o-', color='blue', label='实际头围 (cm)')
                ax3.plot(who_months, who_data['head_circumference'][gender_key]['p50'], '--', color='green', label='WHO P50')
                ax3.plot(who_months, who_data['head_circumference'][gender_key]['p3'], ':', color='orange', label='WHO P3')
                ax3.plot(who_months, who_data['head_circumference'][gender_key]['p97'], ':', color='red', label='WHO P97')
                ax3.fill_between(who_months, who_data['head_circumference'][gender_key]['p3'], who_data['head_circumference'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
                ax3.set_title(f'{self.current_infant_name}的头围增长曲线')
                ax3.set_xlabel('月龄')
                ax3.set_ylabel('头围 (cm)')
                ax3.grid(True)
                ax3.legend()
            else:
                # 如果没有头围数据，创建2个子图
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 11), dpi=100)
                fig.subplots_adjust(hspace=0.5)
                
                # 绘制体重曲线
                ax1.plot(months, weights, 'o-', color='blue', label='实际体重 (kg)')
                ax1.plot(who_months, who_data['weight'][gender_key]['p50'], '--', color='green', label='WHO P50')
                ax1.plot(who_months, who_data['weight'][gender_key]['p3'], ':', color='orange', label='WHO P3')
                ax1.plot(who_months, who_data['weight'][gender_key]['p97'], ':', color='red', label='WHO P97')
                ax1.fill_between(who_months, who_data['weight'][gender_key]['p3'], who_data['weight'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
                ax1.set_title(f'{self.current_infant_name}的体重增长曲线')
                ax1.set_xlabel('月龄')
                ax1.set_ylabel('体重 (kg)')
                ax1.grid(True)
                ax1.legend()
                
                # 绘制身高曲线
                ax2.plot(months, heights, 'o-', color='blue', label='实际身高 (cm)')
                ax2.plot(who_months, who_data['height'][gender_key]['p50'], '--', color='green', label='WHO P50')
                ax2.plot(who_months, who_data['height'][gender_key]['p3'], ':', color='orange', label='WHO P3')
                ax2.plot(who_months, who_data['height'][gender_key]['p97'], ':', color='red', label='WHO P97')
                ax2.fill_between(who_months, who_data['height'][gender_key]['p3'], who_data['height'][gender_key]['p97'], color='lightgreen', alpha=0.3, label='WHO 正常范围')
                ax2.set_title(f'{self.current_infant_name}的身高增长曲线')
                ax2.set_xlabel('月龄')
                ax2.set_ylabel('身高 (cm)')
                ax2.grid(True)
                ax2.legend()
            
            # 添加标题和信息
            fig.suptitle(f'{self.current_infant_name}的生长曲线报告', fontsize=16)
            plt.figtext(0.1, 0.01, f'生成日期: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', fontsize=8)
            
            # 保存到PDF
            pdf.savefig()
            plt.close()
        
        messagebox.showinfo("成功", f"生长曲线已成功导出到 {filename}")
    
    def export_infant_info(self):
        """
        导出婴儿信息档案为TXT文件
        """
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        # 获取保存路径
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*")],
            title="导出婴儿信息档案"
        )
        
        if not filename:
            return
        
        # 获取最新档案
        latest_info = self.db.get_latest_infant(self.current_infant_name)
        if not latest_info:
            messagebox.showwarning("警告", "无婴幼儿信息")
            return
        
        # 获取历史档案
        history = self.db.get_infant_history(self.current_infant_name)
        
        # 生成导出内容
        content = f"婴幼儿档案信息\n"
        content += "=" * 80 + "\n"
        content += f"姓名: {latest_info['name']}\n"
        content += f"性别: {latest_info['gender']}\n"
        content += f"出生日期: {latest_info['birth_date']}\n"
        
        # 计算当前月龄
        birth_date = datetime.datetime.strptime(str(latest_info['birth_date']), "%Y-%m-%d")
        today = datetime.datetime.now()
        months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
        content += f"当前月龄: {months}个月\n"
        
        content += f"是否早产: {'是' if latest_info['is_preterm'] else '否'}\n"
        if latest_info['is_preterm']:
            content += f"早产周数: {latest_info['gestational_age']}周\n"
        
        content += f"最新体重: {latest_info['weight']} kg\n"
        content += f"最新身高: {latest_info['height']} cm\n"
        if latest_info['head_circumference']:
            content += f"最新头围: {latest_info['head_circumference']} cm\n"
        
        content += f"主要喂养方式: {latest_info['feeding_type']}\n"
        if latest_info['daily_milk']:
            content += f"每天喝奶量: {latest_info['daily_milk']} mL\n"
        if latest_info['辅食_start_age']:
            content += f"辅食添加月龄: {latest_info['辅食_start_age']}个月\n"
        
        content += f"食物过敏: {latest_info['allergies'] if latest_info['allergies'] else '无'}\n"
        content += f"健康状况: {latest_info['health_conditions'] if latest_info['health_conditions'] else '无'}\n"
        content += f"补充剂: {latest_info['supplements'] if latest_info['supplements'] else '无'}\n"
        content += f"食物质地: {latest_info['food_texture']}\n"
        content += f"不爱吃的食物: {latest_info['disliked_foods'] if latest_info['disliked_foods'] else '无'}\n"
        content += f"独立进食: {'会' if latest_info['can_eat_independently'] else '不会'}\n"
        content += f"家庭饮食要求: {latest_info['family_dietary_restrictions'] if latest_info['family_dietary_restrictions'] else '无'}\n"
        content += f"所在城市: {latest_info['city'] if latest_info['city'] else '未填写'}\n"
        
        if history:
            content += "\n" + "=" * 80 + "\n"
            content += "历史档案记录\n"
            content += "=" * 80 + "\n"
            
            for i, record in enumerate(history):
                content += f"\n记录 {i+1} - {record['record_date']}\n"
                content += "-" * 60 + "\n"
                
                # 计算记录时的月龄
                record_date = datetime.datetime.strptime(str(record['record_date']), "%Y-%m-%d")
                record_months = (record_date.year - birth_date.year) * 12 + (record_date.month - birth_date.month)
                content += f"记录时月龄: {record_months}个月\n"
                content += f"体重: {record['weight']} kg\n"
                content += f"身高: {record['height']} cm\n"
                if record['head_circumference']:
                    content += f"头围: {record['head_circumference']} cm\n"
                content += f"喂养方式: {record['feeding_type']}\n"
        
        content += "\n" + "=" * 80 + "\n"
        content += f"导出日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        messagebox.showinfo("成功", f"婴儿信息档案已成功导出到 {filename}")
    
    def export_chat_history(self):
        """
        导出AI聊天记录为TXT文件
        """
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        # 获取保存路径
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*")],
            title="导出AI聊天记录"
        )
        
        if not filename:
            return
        
        # 获取聊天历史
        history = self.db.get_chat_history(self.current_infant_name)
        if not history:
            messagebox.showwarning("警告", "无聊天记录")
            return
        
        # 生成导出内容
        content = f"AI聊天记录 - {self.current_infant_name}\n"
        content += "=" * 80 + "\n"
        
        for message in history:
            content += f"\n{message['role']} - {message['timestamp']}\n"
            content += "-" * 60 + "\n"
            content += message['content'] + "\n"
        
        content += "\n" + "=" * 80 + "\n"
        content += f"导出日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        messagebox.showinfo("成功", f"AI聊天记录已成功导出到 {filename}")
    
    def display_statistics(self):
        """
        显示数据统计信息
        """
        if not self.current_infant_name:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        # 获取历史档案
        history = self.db.get_infant_history(self.current_infant_name)
        if not history:
            messagebox.showwarning("警告", "无历史数据")
            return
        
        # 准备数据
        weights = []
        heights = []
        head_circumferences = []
        months = []
        
        birth_date = datetime.datetime.strptime(str(history[0]['birth_date']), "%Y-%m-%d")
        
        for record in history:
            record_date = datetime.datetime.strptime(str(record['record_date']), "%Y-%m-%d")
            month = (record_date.year - birth_date.year) * 12 + (record_date.month - birth_date.month)
            months.append(month)
            weights.append(record['weight'])
            heights.append(record['height'])
            if record['head_circumference']:
                head_circumferences.append(record['head_circumference'])
        
        # 计算统计数据
        weight_stats = {
            'mean': np.mean(weights),
            'min': min(weights),
            'max': max(weights),
            'std': np.std(weights)
        }
        
        height_stats = {
            'mean': np.mean(heights),
            'min': min(heights),
            'max': max(heights),
            'std': np.std(heights)
        }
        
        # 计算增长率
        weight_growth_rate = []
        height_growth_rate = []
        
        for i in range(1, len(weights)):
            weight_diff = weights[i] - weights[i-1]
            month_diff = months[i] - months[i-1]
            if month_diff > 0:
                weight_growth_rate.append(weight_diff / month_diff)
            
            height_diff = heights[i] - heights[i-1]
            if month_diff > 0:
                height_growth_rate.append(height_diff / month_diff)
        
        # 创建统计信息窗口
        window = tk.Toplevel(self.root)
        window.title(f"{self.current_infant_name}的健康数据统计")
        window.geometry("600x400")
        
        # 创建滚动区域
        canvas = tk.Canvas(window)
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示统计信息
        stats_frame = ttk.LabelFrame(scrollable_frame, text="统计信息", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_text = tk.Text(stats_frame, wrap=tk.WORD, font=("SimHei", 11))
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        # 生成统计内容
        stats_content = f"婴幼儿: {self.current_infant_name}\n"
        stats_content += f"数据记录数量: {len(history)}\n"
        stats_content += f"记录时间范围: {history[-1]['record_date']} 至 {history[0]['record_date']}\n\n"
        
        stats_content += "体重统计:\n"
        stats_content += f"  平均值: {weight_stats['mean']:.2f} kg\n"
        stats_content += f"  最小值: {weight_stats['min']:.2f} kg\n"
        stats_content += f"  最大值: {weight_stats['max']:.2f} kg\n"
        stats_content += f"  标准差: {weight_stats['std']:.2f} kg\n"
        if weight_growth_rate:
            stats_content += f"  平均月增长率: {np.mean(weight_growth_rate):.2f} kg/月\n"
        stats_content += "\n"
        
        stats_content += "身高统计:\n"
        stats_content += f"  平均值: {height_stats['mean']:.2f} cm\n"
        stats_content += f"  最小值: {height_stats['min']:.2f} cm\n"
        stats_content += f"  最大值: {height_stats['max']:.2f} cm\n"
        stats_content += f"  标准差: {height_stats['std']:.2f} cm\n"
        if height_growth_rate:
            stats_content += f"  平均月增长率: {np.mean(height_growth_rate):.2f} cm/月\n"
        stats_content += "\n"
        
        if head_circumferences:
            head_stats = {
                'mean': np.mean(head_circumferences),
                'min': min(head_circumferences),
                'max': max(head_circumferences),
                'std': np.std(head_circumferences)
            }
            stats_content += "头围统计:\n"
            stats_content += f"  平均值: {head_stats['mean']:.2f} cm\n"
            stats_content += f"  最小值: {head_stats['min']:.2f} cm\n"
            stats_content += f"  最大值: {head_stats['max']:.2f} cm\n"
            stats_content += f"  标准差: {head_stats['std']:.2f} cm\n"
        
        stats_content += "\n"
        stats_content += f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        stats_text.insert(tk.END, stats_content)
        stats_text.config(state=tk.DISABLED)
    
    def __del__(self):
        # 清理matplotlib资源
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass
        
        # 关闭数据库连接 - 只在on_closing未执行时才执行
        # 避免重复关闭导致的错误
        pass

def on_closing(root, app):
    """
    处理窗口关闭事件
    """
    try:
        # 清理matplotlib资源
        import matplotlib.pyplot as plt
        plt.close('all')
    except Exception:
        pass
    
    # 关闭数据库连接
    if hasattr(app, 'db') and app.db:
        try:
            app.db.close()
        except Exception as e:
            # 忽略已经关闭的错误
            if "Already closed" not in str(e):
                pass
    
    # 销毁窗口
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InfantHealthSystem(root)
    
    # 添加窗口关闭事件处理
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, app))
    
    root.mainloop()