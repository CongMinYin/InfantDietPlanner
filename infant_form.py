#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfantDietPlanner - 婴幼儿档案表单模块

BSD 3-Clause License

Copyright (c) 2026 InfantDietPlanner
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class InfantForm:
    def __init__(self, parent, title="婴幼儿档案", data=None):
        self.parent = parent
        self.title = title
        self.data = data or {}
        self.result = None
        
        # 创建弹窗
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始化表单
        self.init_form()
        
        # 显示窗口
        self.window.wait_window()
    
    def init_form(self):
        # 1. 基本信息
        basic_frame = ttk.LabelFrame(self.scrollable_frame, text="1. 基本信息", padding="10")
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 姓名
        name_frame = ttk.Frame(basic_frame)
        name_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(name_frame, text="姓名：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.name_var = tk.StringVar(value=self.data.get('name', ''))
        ttk.Entry(name_frame, textvariable=self.name_var, width=40).pack(side=tk.LEFT)
        
        # 性别
        gender_frame = ttk.Frame(basic_frame)
        gender_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(gender_frame, text="性别：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.gender_var = tk.StringVar(value=self.data.get('gender', '男'))
        ttk.Radiobutton(gender_frame, text="男", variable=self.gender_var, value="男").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(gender_frame, text="女", variable=self.gender_var, value="女").pack(side=tk.LEFT)
        
        # 出生日期
        birth_frame = ttk.Frame(basic_frame)
        birth_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(birth_frame, text="出生日期：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.birth_var = tk.StringVar(value=self.data.get('birth_date', datetime.datetime.now().strftime("%Y-%m-%d")))
        ttk.Entry(birth_frame, textvariable=self.birth_var, width=20).pack(side=tk.LEFT)
        ttk.Label(birth_frame, text="（格式：YYYY-MM-DD）").pack(side=tk.LEFT, padx=(5, 0))
        
        # 是否早产
        preterm_frame = ttk.Frame(basic_frame)
        preterm_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(preterm_frame, text="是否早产：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.is_preterm_var = tk.IntVar(value=self.data.get('is_preterm', 0))
        ttk.Radiobutton(preterm_frame, text="否（足月）", variable=self.is_preterm_var, value=0, command=self.toggle_preterm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(preterm_frame, text="是", variable=self.is_preterm_var, value=1, command=self.toggle_preterm).pack(side=tk.LEFT)
        
        # 早产周数
        self.gestational_frame = ttk.Frame(basic_frame)
        self.gestational_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(self.gestational_frame, text="早产周数：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.gestational_var = tk.StringVar(value=str(self.data.get('gestational_age', '')) if self.data.get('gestational_age') else '')
        self.gestational_entry = ttk.Entry(self.gestational_frame, textvariable=self.gestational_var, width=10)
        self.gestational_entry.pack(side=tk.LEFT)
        ttk.Label(self.gestational_frame, text="周").pack(side=tk.LEFT, padx=(5, 0))
        
        # 初始状态
        self.toggle_preterm()
        
        # 2. 体检数据
        exam_frame = ttk.LabelFrame(self.scrollable_frame, text="2. 最近一次体检数据", padding="10")
        exam_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 体重
        weight_frame = ttk.Frame(exam_frame)
        weight_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(weight_frame, text="体重：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.weight_var = tk.StringVar(value=str(self.data.get('weight', '')) if self.data.get('weight') else '')
        ttk.Entry(weight_frame, textvariable=self.weight_var, width=10).pack(side=tk.LEFT)
        ttk.Label(weight_frame, text="kg").pack(side=tk.LEFT, padx=(5, 0))
        
        # 身高
        height_frame = ttk.Frame(exam_frame)
        height_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(height_frame, text="身高/身长：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.height_var = tk.StringVar(value=str(self.data.get('height', '')) if self.data.get('height') else '')
        ttk.Entry(height_frame, textvariable=self.height_var, width=10).pack(side=tk.LEFT)
        ttk.Label(height_frame, text="cm").pack(side=tk.LEFT, padx=(5, 0))
        
        # 头围
        head_frame = ttk.Frame(exam_frame)
        head_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(head_frame, text="头围（如有）：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.head_var = tk.StringVar(value=str(self.data.get('head_circumference', '')) if self.data.get('head_circumference') else '')
        ttk.Entry(head_frame, textvariable=self.head_var, width=10).pack(side=tk.LEFT)
        ttk.Label(head_frame, text="cm").pack(side=tk.LEFT, padx=(5, 0))
        
        # 3. 喂养情况
        feeding_frame = ttk.LabelFrame(self.scrollable_frame, text="3. 喂养情况", padding="10")
        feeding_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 主要喂养方式
        feed_type_frame = ttk.Frame(feeding_frame)
        feed_type_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(feed_type_frame, text="目前主要吃：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.feeding_var = tk.StringVar(value=self.data.get('feeding_type', '纯母乳'))
        ttk.Radiobutton(feed_type_frame, text="纯母乳", variable=self.feeding_var, value="纯母乳").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(feed_type_frame, text="配方奶", variable=self.feeding_var, value="配方奶").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(feed_type_frame, text="母乳+奶粉", variable=self.feeding_var, value="母乳+奶粉").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(feed_type_frame, text="已断奶", variable=self.feeding_var, value="已断奶").pack(side=tk.LEFT)
        
        # 每天喝奶量
        milk_frame = ttk.Frame(feeding_frame)
        milk_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(milk_frame, text="每天喝奶大约：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.milk_var = tk.StringVar(value=str(self.data.get('daily_milk', '')) if self.data.get('daily_milk') else '')
        ttk.Entry(milk_frame, textvariable=self.milk_var, width=10).pack(side=tk.LEFT)
        ttk.Label(milk_frame, text="mL").pack(side=tk.LEFT, padx=(5, 0))
        
        # 辅食添加月龄
        辅食_frame = ttk.Frame(feeding_frame)
        辅食_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(辅食_frame, text="辅食从：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.辅食_var = tk.StringVar(value=str(self.data.get('辅食_start_age', '')) if self.data.get('辅食_start_age') else '')
        ttk.Entry(辅食_frame, textvariable=self.辅食_var, width=10).pack(side=tk.LEFT)
        ttk.Label(辅食_frame, text="月龄开始添加").pack(side=tk.LEFT, padx=(5, 0))
        
        # 4. 健康与过敏
        health_frame = ttk.LabelFrame(self.scrollable_frame, text="4. 健康与过敏", padding="10")
        health_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 食物过敏
        allergy_frame = ttk.Frame(health_frame)
        allergy_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(allergy_frame, text="食物过敏：", width=15).pack(side=tk.LEFT, anchor=tk.N)
        
        allergy_check_frame = ttk.Frame(allergy_frame)
        allergy_check_frame.pack(side=tk.LEFT, anchor=tk.W)
        
        self.allergy_vars = {
            '牛奶/奶粉': tk.IntVar(value=1 if '牛奶/奶粉' in (self.data.get('allergies', '') or '') else 0),
            '鸡蛋': tk.IntVar(value=1 if '鸡蛋' in (self.data.get('allergies', '') or '') else 0),
            '花生/坚果': tk.IntVar(value=1 if '花生/坚果' in (self.data.get('allergies', '') or '') else 0),
            '海鲜': tk.IntVar(value=1 if '海鲜' in (self.data.get('allergies', '') or '') else 0),
            '无过敏': tk.IntVar(value=1 if '无过敏' in (self.data.get('allergies', '') or '') else 0),
        }
        
        ttk.Checkbutton(allergy_check_frame, text="牛奶/奶粉", variable=self.allergy_vars['牛奶/奶粉']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(allergy_check_frame, text="鸡蛋", variable=self.allergy_vars['鸡蛋']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(allergy_check_frame, text="花生/坚果", variable=self.allergy_vars['花生/坚果']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(allergy_check_frame, text="海鲜", variable=self.allergy_vars['海鲜']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(allergy_check_frame, text="无过敏", variable=self.allergy_vars['无过敏']).pack(side=tk.LEFT, padx=(0, 10))
        
        # 其他过敏
        other_allergy_frame = ttk.Frame(health_frame)
        other_allergy_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(other_allergy_frame, text="其他过敏：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.other_allergy_var = tk.StringVar(value=self.data.get('other_allergies', ''))
        ttk.Entry(other_allergy_frame, textvariable=self.other_allergy_var, width=40).pack(side=tk.LEFT)
        
        # 健康状况
        condition_frame = ttk.Frame(health_frame)
        condition_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(condition_frame, text="健康状况：", width=15).pack(side=tk.LEFT, anchor=tk.N)
        
        condition_check_frame = ttk.Frame(condition_frame)
        condition_check_frame.pack(side=tk.LEFT, anchor=tk.W)
        
        self.condition_vars = {
            '湿疹严重': tk.IntVar(value=1 if '湿疹严重' in (self.data.get('health_conditions', '') or '') else 0),
            '经常便秘': tk.IntVar(value=1 if '经常便秘' in (self.data.get('health_conditions', '') or '') else 0),
            '腹泻': tk.IntVar(value=1 if '腹泻' in (self.data.get('health_conditions', '') or '') else 0),
            '乳糖不耐': tk.IntVar(value=1 if '乳糖不耐' in (self.data.get('health_conditions', '') or '') else 0),
            '先天性疾病': tk.IntVar(value=1 if '先天性疾病' in (self.data.get('health_conditions', '') or '') else 0),
            '无': tk.IntVar(value=1 if '无' in (self.data.get('health_conditions', '') or '') else 0),
        }
        
        ttk.Checkbutton(condition_check_frame, text="湿疹严重", variable=self.condition_vars['湿疹严重']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(condition_check_frame, text="经常便秘", variable=self.condition_vars['经常便秘']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(condition_check_frame, text="腹泻", variable=self.condition_vars['腹泻']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(condition_check_frame, text="乳糖不耐", variable=self.condition_vars['乳糖不耐']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(condition_check_frame, text="先天性疾病", variable=self.condition_vars['先天性疾病']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(condition_check_frame, text="无", variable=self.condition_vars['无']).pack(side=tk.LEFT, padx=(0, 10))
        
        # 补充剂
        supplement_frame = ttk.Frame(health_frame)
        supplement_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(supplement_frame, text="补充剂：", width=15).pack(side=tk.LEFT, anchor=tk.N)
        
        supplement_check_frame = ttk.Frame(supplement_frame)
        supplement_check_frame.pack(side=tk.LEFT, anchor=tk.W)
        
        self.supplement_vars = {
            '维生素D': tk.IntVar(value=1 if '维生素D' in (self.data.get('supplements', '') or '') else 0),
            '铁剂': tk.IntVar(value=1 if '铁剂' in (self.data.get('supplements', '') or '') else 0),
            'DHA': tk.IntVar(value=1 if 'DHA' in (self.data.get('supplements', '') or '') else 0),
            '益生菌': tk.IntVar(value=1 if '益生菌' in (self.data.get('supplements', '') or '') else 0),
            '暂无': tk.IntVar(value=1 if '暂无' in (self.data.get('supplements', '') or '') else 0),
        }
        
        ttk.Checkbutton(supplement_check_frame, text="维生素D", variable=self.supplement_vars['维生素D']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(supplement_check_frame, text="铁剂", variable=self.supplement_vars['铁剂']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(supplement_check_frame, text="DHA", variable=self.supplement_vars['DHA']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(supplement_check_frame, text="益生菌", variable=self.supplement_vars['益生菌']).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(supplement_check_frame, text="暂无", variable=self.supplement_vars['暂无']).pack(side=tk.LEFT, padx=(0, 10))
        
        # 5. 饮食习惯
        diet_frame = ttk.LabelFrame(self.scrollable_frame, text="5. 饮食习惯", padding="10")
        diet_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 食物质地
        texture_frame = ttk.Frame(diet_frame)
        texture_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(texture_frame, text="食物质地：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.texture_var = tk.StringVar(value=self.data.get('food_texture', '果泥/米糊'))
        ttk.Radiobutton(texture_frame, text="果泥/米糊", variable=self.texture_var, value="果泥/米糊").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(texture_frame, text="软烂碎末", variable=self.texture_var, value="软烂碎末").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(texture_frame, text="小块软饭", variable=self.texture_var, value="小块软饭").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(texture_frame, text="和大人一样", variable=self.texture_var, value="和大人一样").pack(side=tk.LEFT)
        
        # 不爱吃的食物
        dislike_frame = ttk.Frame(diet_frame)
        dislike_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(dislike_frame, text="不爱吃的食物：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.dislike_var = tk.StringVar(value=self.data.get('disliked_foods', ''))
        ttk.Entry(dislike_frame, textvariable=self.dislike_var, width=40).pack(side=tk.LEFT)
        
        # 独立进食
        independent_frame = ttk.Frame(diet_frame)
        independent_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(independent_frame, text="独立进食：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.independent_var = tk.IntVar(value=self.data.get('can_eat_independently', 0))
        ttk.Radiobutton(independent_frame, text="会", variable=self.independent_var, value=1).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(independent_frame, text="还不会", variable=self.independent_var, value=0).pack(side=tk.LEFT)
        
        # 6. 家庭小贴士
        family_frame = ttk.LabelFrame(self.scrollable_frame, text="6. 家庭小贴士", padding="10")
        family_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 家庭饮食要求
        family_diet_frame = ttk.Frame(family_frame)
        family_diet_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(family_diet_frame, text="家庭饮食要求：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.family_diet_var = tk.StringVar(value=self.data.get('family_dietary_restrictions', ''))
        ttk.Entry(family_diet_frame, textvariable=self.family_diet_var, width=40).pack(side=tk.LEFT)
        
        # 所在城市
        city_frame = ttk.Frame(family_frame)
        city_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(city_frame, text="所在城市：", width=15).pack(side=tk.LEFT, anchor=tk.W)
        self.city_var = tk.StringVar(value=self.data.get('city', ''))
        ttk.Entry(city_frame, textvariable=self.city_var, width=40).pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="保存", command=self.save).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT)
    
    def toggle_preterm(self):
        # 切换早产周数输入框的状态
        if self.is_preterm_var.get():
            self.gestational_entry.config(state=tk.NORMAL)
        else:
            self.gestational_entry.config(state=tk.DISABLED)
            self.gestational_var.set('')
    
    def save(self):
        # 验证数据
        if not self.name_var.get().strip():
            messagebox.showwarning("警告", "请输入姓名")
            return
        
        try:
            # 验证出生日期格式
            datetime.datetime.strptime(self.birth_var.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("警告", "出生日期格式错误，请使用YYYY-MM-DD格式")
            return
        
        # 收集过敏信息
        allergies = []
        for item, var in self.allergy_vars.items():
            if var.get():
                allergies.append(item)
        if self.other_allergy_var.get().strip():
            allergies.append(self.other_allergy_var.get().strip())
        
        # 收集健康状况
        health_conditions = []
        for item, var in self.condition_vars.items():
            if var.get():
                health_conditions.append(item)
        
        # 收集补充剂
        supplements = []
        for item, var in self.supplement_vars.items():
            if var.get():
                supplements.append(item)
        
        # 构建结果字典
        self.result = {
            'name': self.name_var.get().strip(),
            'gender': self.gender_var.get(),
            'birth_date': self.birth_var.get(),
            'is_preterm': self.is_preterm_var.get(),
            'gestational_age': int(self.gestational_var.get()) if self.gestational_var.get().strip() else None,
            'weight': float(self.weight_var.get()) if self.weight_var.get().strip() else None,
            'height': float(self.height_var.get()) if self.height_var.get().strip() else None,
            'head_circumference': float(self.head_var.get()) if self.head_var.get().strip() else None,
            'feeding_type': self.feeding_var.get(),
            'daily_milk': float(self.milk_var.get()) if self.milk_var.get().strip() else None,
            '辅食_start_age': float(self.辅食_var.get()) if self.辅食_var.get().strip() else None,
            'allergies': ','.join(allergies) if allergies else None,
            'health_conditions': ','.join(health_conditions) if health_conditions else None,
            'supplements': ','.join(supplements) if supplements else None,
            'food_texture': self.texture_var.get(),
            'disliked_foods': self.dislike_var.get().strip() or None,
            'can_eat_independently': self.independent_var.get(),
            'family_dietary_restrictions': self.family_diet_var.get().strip() or None,
            'city': self.city_var.get().strip() or None
        }
        
        # 关闭窗口
        self.window.destroy()
    
    def cancel(self):
        # 取消操作
        self.result = None
        self.window.destroy()