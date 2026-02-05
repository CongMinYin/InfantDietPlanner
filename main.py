import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
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
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # 显示数据库连接对话框
        self.db = None
        self.connect_database()
        
        if not self.db:
            messagebox.showerror("错误", "数据库连接失败，程序将退出")
            root.destroy()
            return
        
        # 初始化AI服务
        self.ai_service = AIService()
        
        # 当前选择的婴幼儿ID
        self.current_infant_id = None
        
        # AI上下文数量设置
        self.context_limit = 20
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧婴幼儿信息管理区域
        self.left_frame = ttk.LabelFrame(self.main_frame, text="婴幼儿档案管理", padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
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
        ttk.Button(button_frame, text="删除", command=self.delete_infant).pack(side=tk.LEFT)
        
        # 婴幼儿信息显示区域
        self.info_frame = ttk.LabelFrame(self.left_frame, text="基本信息", padding="10")
        self.info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(self.info_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
    
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
        
        # 聊天记录区域
        self.chat_frame = ttk.Frame(self.right_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.chat_text = tk.Text(self.chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.chat_frame, orient=tk.VERTICAL, command=self.chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.config(yscrollcommand=scrollbar.set)
        
        # 输入区域
        input_frame = ttk.Frame(self.right_frame)
        input_frame.pack(fill=tk.X)
        
        self.input_text = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Button(input_frame, text="发送", command=self.send_message, width=10).pack(side=tk.RIGHT)
        
        # 绑定回车键发送消息
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())
    
    def load_infant_list(self):
        # 加载婴幼儿列表到下拉框
        infants = self.db.get_all_infants()
        if infants:
            self.infant_list = [(infant['name'], infant['id']) for infant in infants]  # (name, id)
            self.infant_combobox['values'] = [infant[0] for infant in self.infant_list]
        else:
            self.infant_list = []
            self.infant_combobox['values'] = []
            self.infant_var.set("")
            self.current_infant_id = None
            self.clear_info_display()
            self.clear_chat_display()
    
    def on_infant_selected(self, event):
        # 当选择婴幼儿时，更新当前婴幼儿ID和显示信息
        selected_name = self.infant_var.get()
        for name, infant_id in self.infant_list:
            if name == selected_name:
                self.current_infant_id = infant_id
                self.display_infant_info(infant_id)
                self.load_chat_history(infant_id)
                break
    
    def display_infant_info(self, infant_id):
        # 显示婴幼儿信息
        infant = self.db.get_infant(infant_id)
        if infant:
            # 计算月龄
            birth_date = datetime.datetime.strptime(str(infant['birth_date']), "%Y-%m-%d")
            today = datetime.datetime.now()
            months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
            
            info = f"姓名：{infant['name']}\n"
            info += f"性别：{infant['gender']}\n"
            info += f"出生日期：{infant['birth_date']}\n"
            info += f"月龄：{months}个月\n"
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
    
    def load_chat_history(self, infant_id):
        # 加载聊天历史
        history = self.db.get_chat_history(infant_id, limit=self.context_limit)
        self.clear_chat_display()
        
        for message in history:
            self.add_message_to_chat(message['role'], message['content'], message['timestamp'])
        
        # 更新聊天时间范围
        time_range = self.db.get_chat_time_range(infant_id)
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
        if not self.current_infant_id:
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
        self.db.add_chat_message(self.current_infant_id, "user", message)
        
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
        infant = self.db.get_infant(self.current_infant_id)
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
        history = self.db.get_chat_history(self.current_infant_id, limit=self.context_limit - 1)
        for role, content, _ in history:
            messages.append({"role": role, "content": content})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        
        # 调用AI获取回复
        response = self.ai_service.get_ai_response(messages)
        
        # 更新AI思考为实际回复
        self.chat_text.config(state=tk.NORMAL)
        # 删除最后一行（正在思考）
        self.chat_text.delete("end-2l", "end")
        self.chat_text.insert(tk.END, response + "\n")
        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)
        
        # 保存AI回复到数据库
        self.db.add_chat_message(self.current_infant_id, "assistant", response)
        
        # 更新聊天时间范围
        time_range = self.db.get_chat_time_range(self.current_infant_id)
        if time_range[0] and time_range[1]:
            self.chat_time_label.config(text=f"对话时间范围：{time_range[0]} 至 {time_range[1]}")
    
    def __del__(self):
        # 关闭数据库连接
        if hasattr(self, 'db') and self.db:
            self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = InfantHealthSystem(root)
    root.mainloop()