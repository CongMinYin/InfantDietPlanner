import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import Database
from ai_service import AIService

class DatabaseConnectDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        # 创建弹窗
        self.window = tk.Toplevel(parent)
        self.window.title("连接数据库")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 主机
        host_frame = ttk.Frame(self.main_frame)
        host_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(host_frame, text="主机：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(host_frame, textvariable=self.host_var, width=30).pack(side=tk.LEFT)
        
        # 用户名
        user_frame = ttk.Frame(self.main_frame)
        user_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(user_frame, text="用户名：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.user_var = tk.StringVar(value="root")
        ttk.Entry(user_frame, textvariable=self.user_var, width=30).pack(side=tk.LEFT)
        
        # 密码
        password_frame = ttk.Frame(self.main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(password_frame, text="密码：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.password_var = tk.StringVar(value="123456")
        ttk.Entry(password_frame, textvariable=self.password_var, show="*", width=30).pack(side=tk.LEFT)
        
        # 数据库
        db_frame = ttk.Frame(self.main_frame)
        db_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(db_frame, text="数据库：", width=10).pack(side=tk.LEFT, anchor=tk.W)
        self.db_var = tk.StringVar(value="infant_health")
        ttk.Entry(db_frame, textvariable=self.db_var, width=30).pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="连接", command=self.connect).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT)
        
        # 显示窗口
        self.window.wait_window()
    
    def connect(self):
        self.result = {
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
    
    def connect_database(self):
        """
        连接数据库
        """
        dialog = DatabaseConnectDialog(self.root)
        if dialog.result:
            self.db = Database(
                host=dialog.result['host'],
                user=dialog.result['user'],
                password=dialog.result['password'],
                db=dialog.result['db']
            )
            if not self.db.connect():
                # 连接失败，重新显示对话框
                retry = messagebox.askretrycancel("连接失败", "数据库连接失败，是否重试？")
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
        ttk.Button(button_frame, text="历史档案", command=self.view_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加示例", command=self.add_sample_data).pack(side=tk.LEFT)
        
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
                for i, (name, id) in enumerate(self.infant_list):
                    if id == infant_id:
                        self.infant_combobox.current(i)
                        self.current_infant_id = infant_id
                        self.display_infant_info(infant_id)
                        break
    
    def edit_infant(self):
        # 修改婴幼儿信息
        if not self.current_infant_id:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        infant = self.db.get_infant(self.current_infant_id)
        if not infant:
            messagebox.showerror("错误", "婴幼儿信息不存在")
            return
        
        # 转换为字典格式
        infant_data = {
            'name': infant[1],
            'gender': infant[2],
            'birth_date': infant[3],
            'is_preterm': infant[4],
            'gestational_age': infant[5],
            'weight': infant[6],
            'height': infant[7],
            'head_circumference': infant[8],
            'feeding_type': infant[9],
            'daily_milk': infant[10],
            '辅食_start_age': infant[11],
            'allergies': infant[12],
            'health_conditions': infant[13],
            'supplements': infant[14],
            'food_texture': infant[15],
            'disliked_foods': infant[16],
            'can_eat_independently': infant[17],
            'family_dietary_restrictions': infant[18],
            'city': infant[19]
        }
        
        from infant_form import InfantForm
        form = InfantForm(self.root, title="修改婴幼儿档案", data=infant_data)
        if form.result:
            # 更新数据库
            success = self.db.update_infant(self.current_infant_id, form.result)
            if success:
                messagebox.showinfo("成功", "婴幼儿档案修改成功！")
                self.display_infant_info(self.current_infant_id)
                self.load_infant_list()
                # 重新选择当前婴幼儿
                for i, (name, id) in enumerate(self.infant_list):
                    if id == self.current_infant_id:
                        self.infant_combobox.current(i)
                        break
    
    def delete_infant(self):
        # 删除婴幼儿
        if not self.current_infant_id:
            messagebox.showwarning("警告", "请先选择一个婴幼儿")
            return
        
        if messagebox.askyesno("确认", "确定要删除该婴幼儿档案吗？此操作不可恢复！"):
            success = self.db.delete_infant(self.current_infant_id)
            if success:
                messagebox.showinfo("成功", "婴幼儿档案删除成功！")
                self.current_infant_id = None
                self.load_infant_list()
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
        
        # 根据是否有头围数据决定图表布局
        if any(hc is not None for hc in head_circumferences):
            # 如果有头围数据，创建3个子图
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 7), dpi=100)
            fig.subplots_adjust(hspace=0.5)
            
            # 绘制体重曲线
            ax1.plot(months, weights, 'o-', color='blue', label='体重 (kg)')
            ax1.set_title('体重增长曲线')
            ax1.set_xlabel('月龄')
            ax1.set_ylabel('体重 (kg)')
            ax1.grid(True)
            ax1.legend()
            
            # 绘制身高曲线
            ax2.plot(months, heights, 'o-', color='green', label='身高 (cm)')
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
            ax3.plot(valid_months, valid_hc, 'o-', color='red', label='头围 (cm)')
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
            ax1.plot(months, weights, 'o-', color='blue', label='体重 (kg)')
            ax1.set_title('体重增长曲线')
            ax1.set_xlabel('月龄')
            ax1.set_ylabel('体重 (kg)')
            ax1.grid(True)
            ax1.legend()
            
            # 绘制身高曲线
            ax2.plot(months, heights, 'o-', color='green', label='身高 (cm)')
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
        
        if role == "user":
            self.chat_text.insert(tk.END, f"\n【我】 {timestamp}\n", "user")
        else:
            self.chat_text.insert(tk.END, f"\n【AI】 {timestamp}\n", "assistant")
        
        self.chat_text.insert(tk.END, content + "\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
        
        # 配置标签样式
        self.chat_text.tag_config("user", foreground="blue", font=("SimHei", 10, "bold"))
        self.chat_text.tag_config("assistant", foreground="green", font=("SimHei", 10, "bold"))
    
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
        self.chat_text.insert(tk.END, f"\n【AI】 {thinking_time}\n", "assistant")
        self.chat_text.insert(tk.END, "AI正在思考...\n")
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
        # 删除最后两行（正在思考的提示）
        # 先获取当前文本内容
        content = self.chat_text.get(1.0, tk.END)
        lines = content.split('\n')
        # 计算需要保留的行数
        if len(lines) >= 3:
            # 删除最后两行（思考提示和空行）
            new_content = '\n'.join(lines[:-3]) + '\n'
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.insert(tk.END, new_content)
        # 插入AI回复
        self.chat_text.insert(tk.END, f"\n【AI】 {current_time}\n", "assistant")
        self.chat_text.insert(tk.END, response + "\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
        
        # 保存AI回复到数据库
        self.db.add_chat_message(self.current_infant_name, "assistant", response)
        
        # 更新聊天时间范围
        time_range = self.db.get_chat_time_range(self.current_infant_name)
        if time_range[0] and time_range[1]:
            self.chat_time_label.config(text=f"对话时间范围：{time_range[0]} 至 {time_range[1]}")
    
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