#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfantDietPlanner - AI服务模块

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

from openai import OpenAI

class AIService:
    def __init__(self, api_key="*******************"):
        self.api_key = api_key
        self.base_url = "https://api-inference.modelscope.cn/v1/"
        self.client = None
        self.init_client()
    
    def init_client(self):
        """
        初始化OpenAI客户端
        """
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def set_api_key(self, api_key):
        """
        设置API密钥并重新初始化客户端
        """
        self.api_key = api_key
        self.init_client()
    
    def get_ai_response(self, messages, model="Qwen/Qwen2.5-Coder-32B-Instruct", temperature=0.7, max_tokens=2000):
        """
        调用ModelScope大模型获取AI回复
        :param messages: 对话历史，格式为[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        :param model: 使用的模型，默认为Qwen/Qwen2.5-Coder-32B-Instruct
        :param temperature: 生成文本的随机性，默认为0.7
        :param max_tokens: 最大生成token数，默认为2000
        :return: AI的回复内容
        """
        try:
            # 确保客户端已初始化
            if not self.client:
                self.init_client()
            
            # 调用API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False  # 非流式响应
            )
            
            # 处理响应
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                return "AI暂时无法回复，请稍后再试"
        
        except Exception as e:
            print(f"AI请求失败: {e}")
            return f"AI请求失败: {str(e)}"
    
    def generate_system_prompt(self, infant_info):
        """
        根据婴幼儿信息生成系统提示
        :param infant_info: 婴幼儿信息字典
        :return: 系统提示内容
        """
        if not infant_info:
            return "你是一个专业的婴幼儿营养健康顾问，专注于为0-3岁婴幼儿提供科学的饮食建议和健康指导。"
        
        name = infant_info.get('name', '宝宝')
        gender = infant_info.get('gender', '未知')
        birth_date = infant_info.get('birth_date', '未知')
        is_preterm = "是" if infant_info.get('is_preterm', 0) else "否"
        gestational_age = infant_info.get('gestational_age', '未知')
        weight = infant_info.get('weight', '未知')
        height = infant_info.get('height', '未知')
        feeding_type = infant_info.get('feeding_type', '未知')
        daily_milk = infant_info.get('daily_milk', '未知')
        辅食_start_age = infant_info.get('辅食_start_age', '未知')
        allergies = infant_info.get('allergies', '无')
        health_conditions = infant_info.get('health_conditions', '无')
        supplements = infant_info.get('supplements', '无')
        food_texture = infant_info.get('food_texture', '未知')
        disliked_foods = infant_info.get('disliked_foods', '无')
        can_eat_independently = "会" if infant_info.get('can_eat_independently', 0) else "不会"
        family_dietary_restrictions = infant_info.get('family_dietary_restrictions', '无')
        city = infant_info.get('city', '未知')
        
        prompt = f"""
你是一个专业的婴幼儿营养健康顾问，专注于为0-3岁婴幼儿提供科学的饮食建议和健康指导。

请根据以下婴幼儿的详细信息，为其提供个性化的体质分析、营养分析和食谱推荐：

【基本信息】
姓名：{name}
性别：{gender}
出生日期：{birth_date}
是否早产：{is_preterm}
早产周数：{gestational_age}周

【体检数据】
体重：{weight} kg
身高/身长：{height} cm

【喂养情况】
主要喂养方式：{feeding_type}
每天喝奶量：{daily_milk} mL
辅食添加月龄：{辅食_start_age} 月龄

【健康与过敏】
食物过敏：{allergies}
健康状况：{health_conditions}
正在服用的补充剂：{supplements}

【饮食习惯】
食物质地接受度：{food_texture}
不爱吃的食物：{disliked_foods}
是否能独立进食：{can_eat_independently}

【家庭情况】
家庭饮食特殊要求：{family_dietary_restrictions}
所在城市：{city}

请在回答中包含以下内容：
1. 体质分析：根据提供的信息，分析宝宝的体质状况
2. 营养分析：评估宝宝的营养需求和当前饮食是否合理
3. 食谱推荐：根据宝宝的年龄、饮食情况和健康状况，推荐适合的食谱
4. 健康建议：针对宝宝的具体情况，提供相应的健康建议

请注意：
- 所有建议必须基于科学依据，符合婴幼儿营养指南
- 要特别注意宝宝的过敏情况，避免推荐可能引起过敏的食物
- 建议要具体、实用，易于家长操作
- 语言要通俗易懂，避免使用专业术语
        """
        
        return prompt