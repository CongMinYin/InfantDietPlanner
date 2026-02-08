#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfantDietPlanner - 数据库模块

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

import pymysql
import sqlite3
import os
import datetime

class Database:
    def __init__(self, db_type='sqlite', host='localhost', user='root', password='123456', db='infant_health'):
        self.db_type = db_type
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """
        连接到数据库
        :return: 是否连接成功
        """
        try:
            if self.db_type == 'mysql':
                return self._connect_mysql()
            else:  # sqlite
                return self._connect_sqlite()
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def _connect_mysql(self):
        """
        连接到MySQL数据库
        :return: 是否连接成功
        """
        try:
            # 先连接到MySQL服务器（不指定数据库）
            temp_conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            temp_cursor = temp_conn.cursor()
            
            # 检查数据库是否存在，不存在则创建
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            temp_cursor.close()
            temp_conn.close()
            
            # 连接到指定数据库
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            self.init_db()
            return True
        except Exception as e:
            print(f"MySQL连接失败: {e}")
            return False
    
    def _connect_sqlite(self):
        """
        连接到SQLite数据库
        :return: 是否连接成功
        """
        try:
            # 连接到SQLite数据库文件
            db_path = f"{self.db}.db"
            self.conn = sqlite3.connect(db_path)
            # 设置为返回字典格式
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.init_db()
            return True
        except Exception as e:
            print(f"SQLite连接失败: {e}")
            return False
    
    def init_db(self):
        """
        初始化数据库表结构
        """
        if not self.conn:
            return
        
        try:
            if self.db_type == 'mysql':
                self._init_mysql_db()
            else:  # sqlite
                self._init_sqlite_db()
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            if self.conn:
                self.conn.rollback()
    
    def _init_mysql_db(self):
        """
        初始化MySQL数据库表结构
        """
        # 创建婴幼儿档案表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS infant_profile (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender VARCHAR(10) NOT NULL,
            birth_date DATE NOT NULL,
            is_preterm TINYINT NOT NULL,
            gestational_age INT,
            weight DECIMAL(5,2),
            height DECIMAL(5,2),
            head_circumference DECIMAL(5,2),
            feeding_type VARCHAR(50),
            daily_milk DECIMAL(6,2),
            辅食_start_age DECIMAL(3,1),
            allergies TEXT,
            health_conditions TEXT,
            supplements TEXT,
            food_texture VARCHAR(50),
            disliked_foods TEXT,
            can_eat_independently TINYINT,
            family_dietary_restrictions TEXT,
            city VARCHAR(100),
            record_date DATE NOT NULL, -- 记录日期，用于区分不同时期的档案
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建索引，提高查询速度
        try:
            self.cursor.execute('CREATE INDEX idx_infant_profile_name ON infant_profile (name)')
        except Exception:
            pass
        try:
            self.cursor.execute('CREATE INDEX idx_infant_profile_record_date ON infant_profile (record_date)')
        except Exception:
            pass
        
        # 创建对话上下文消息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_context (
            id INT AUTO_INCREMENT PRIMARY KEY,
            infant_name VARCHAR(50) NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建索引，提高查询速度
        try:
            self.cursor.execute('CREATE INDEX idx_chat_context_infant_name ON chat_context (infant_name)')
        except Exception:
            pass
        
        try:
            self.cursor.execute('CREATE INDEX idx_chat_context_timestamp ON chat_context (timestamp)')
        except Exception:
            pass  # 索引已存在，忽略错误
        
        self.conn.commit()
    
    def _init_sqlite_db(self):
        """
        初始化SQLite数据库表结构
        """
        # 创建婴幼儿档案表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS infant_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            birth_date DATE NOT NULL,
            is_preterm INTEGER NOT NULL,
            gestational_age INTEGER,
            weight REAL,
            height REAL,
            head_circumference REAL,
            feeding_type TEXT,
            daily_milk REAL,
            辅食_start_age REAL,
            allergies TEXT,
            health_conditions TEXT,
            supplements TEXT,
            food_texture TEXT,
            disliked_foods TEXT,
            can_eat_independently INTEGER,
            family_dietary_restrictions TEXT,
            city TEXT,
            record_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引，提高查询速度
        try:
            self.cursor.execute('CREATE INDEX idx_infant_profile_name ON infant_profile (name)')
        except Exception:
            pass
        try:
            self.cursor.execute('CREATE INDEX idx_infant_profile_record_date ON infant_profile (record_date)')
        except Exception:
            pass
        
        # 创建对话上下文消息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            infant_name TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引，提高查询速度
        try:
            self.cursor.execute('CREATE INDEX idx_chat_context_infant_name ON chat_context (infant_name)')
        except Exception:
            pass
        
        try:
            self.cursor.execute('CREATE INDEX idx_chat_context_timestamp ON chat_context (timestamp)')
        except Exception:
            pass  # 索引已存在，忽略错误
        
        self.conn.commit()
    
    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"关闭数据库连接失败: {e}")
    
    def set_connection(self, host='localhost', user='root', password='123456', db='infant_health', db_type='sqlite'):
        """
        设置数据库连接参数
        """
        self.db_type = db_type
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        # 重新连接
        self.close()
        return self.connect()
    
    # 婴幼儿档案相关方法
    def add_infant(self, data):
        # 如果没有提供record_date，使用当前日期
        record_date = data.get('record_date', datetime.datetime.now().strftime('%Y-%m-%d'))
        
        if self.db_type == 'mysql':
            query = '''
            INSERT INTO infant_profile (
                name, gender, birth_date, is_preterm, gestational_age, 
                weight, height, head_circumference, feeding_type, daily_milk, 
                辅食_start_age, allergies, health_conditions, supplements, 
                food_texture, disliked_foods, can_eat_independently, 
                family_dietary_restrictions, city, record_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        else:  # sqlite
            query = '''
            INSERT INTO infant_profile (
                name, gender, birth_date, is_preterm, gestational_age, 
                weight, height, head_circumference, feeding_type, daily_milk, 
                辅食_start_age, allergies, health_conditions, supplements, 
                food_texture, disliked_foods, can_eat_independently, 
                family_dietary_restrictions, city, record_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        
        self.cursor.execute(query, (
            data['name'], data['gender'], data['birth_date'], data['is_preterm'], 
            data['gestational_age'], data['weight'], data['height'], 
            data['head_circumference'], data['feeding_type'], data['daily_milk'], 
            data['辅食_start_age'], data['allergies'], data['health_conditions'], 
            data['supplements'], data['food_texture'], data['disliked_foods'], 
            data['can_eat_independently'], data['family_dietary_restrictions'], 
            data['city'], record_date
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_infant(self, infant_id):
        if self.db_type == 'mysql':
            self.cursor.execute('SELECT * FROM infant_profile WHERE id = %s', (infant_id,))
        else:  # sqlite
            self.cursor.execute('SELECT * FROM infant_profile WHERE id = ?', (infant_id,))
        return self.cursor.fetchone()
    
    def get_latest_infant(self, name):
        """
        获取指定婴幼儿的最新档案
        :param name: 婴幼儿姓名
        :return: 最新档案信息
        """
        if self.db_type == 'mysql':
            self.cursor.execute('''
            SELECT * FROM infant_profile 
            WHERE name = %s 
            ORDER BY record_date DESC 
            LIMIT 1
            ''', (name,))
        else:  # sqlite
            self.cursor.execute('''
            SELECT * FROM infant_profile 
            WHERE name = ? 
            ORDER BY record_date DESC 
            LIMIT 1
            ''', (name,))
        return self.cursor.fetchone()
    
    def get_all_infants(self):
        '''
        获取所有唯一的婴幼儿姓名
        '''
        self.cursor.execute('SELECT DISTINCT name FROM infant_profile ORDER BY name')
        return self.cursor.fetchall()
    
    def get_infant_history(self, name):
        """
        获取指定婴幼儿的历史档案
        :param name: 婴幼儿姓名
        :return: 历史档案列表
        """
        if self.db_type == 'mysql':
            self.cursor.execute('''
            SELECT * FROM infant_profile 
            WHERE name = %s 
            ORDER BY record_date DESC
            ''', (name,))
        else:  # sqlite
            self.cursor.execute('''
            SELECT * FROM infant_profile 
            WHERE name = ? 
            ORDER BY record_date DESC
            ''', (name,))
        return self.cursor.fetchall()
    
    def update_infant(self, infant_id, data):
        if self.db_type == 'mysql':
            query = '''
            UPDATE infant_profile SET 
                name = %s, gender = %s, birth_date = %s, is_preterm = %s, gestational_age = %s, 
                weight = %s, height = %s, head_circumference = %s, feeding_type = %s, daily_milk = %s, 
                辅食_start_age = %s, allergies = %s, health_conditions = %s, supplements = %s, 
                food_texture = %s, disliked_foods = %s, can_eat_independently = %s, 
                family_dietary_restrictions = %s, city = %s
            WHERE id = %s
            '''
        else:  # sqlite
            query = '''
            UPDATE infant_profile SET 
                name = ?, gender = ?, birth_date = ?, is_preterm = ?, gestational_age = ?, 
                weight = ?, height = ?, head_circumference = ?, feeding_type = ?, daily_milk = ?, 
                辅食_start_age = ?, allergies = ?, health_conditions = ?, supplements = ?, 
                food_texture = ?, disliked_foods = ?, can_eat_independently = ?, 
                family_dietary_restrictions = ?, city = ?
            WHERE id = ?
            '''
        self.cursor.execute(query, (
            data['name'], data['gender'], data['birth_date'], data['is_preterm'], 
            data['gestational_age'], data['weight'], data['height'], 
            data['head_circumference'], data['feeding_type'], data['daily_milk'], 
            data['辅食_start_age'], data['allergies'], data['health_conditions'], 
            data['supplements'], data['food_texture'], data['disliked_foods'], 
            data['can_eat_independently'], data['family_dietary_restrictions'], 
            data['city'], infant_id
        ))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_infant(self, infant_id):
        # 先获取婴幼儿姓名，因为chat_context表使用的是infant_name字段
        if self.db_type == 'mysql':
            self.cursor.execute('SELECT name FROM infant_profile WHERE id = %s', (infant_id,))
        else:  # sqlite
            self.cursor.execute('SELECT name FROM infant_profile WHERE id = ?', (infant_id,))
        infant = self.cursor.fetchone()
        
        if infant:
            infant_name = infant['name'] if self.db_type == 'mysql' else infant[0]
            # 删除相关的对话记录
            if self.db_type == 'mysql':
                self.cursor.execute('DELETE FROM chat_context WHERE infant_name = %s', (infant_name,))
            else:  # sqlite
                self.cursor.execute('DELETE FROM chat_context WHERE infant_name = ?', (infant_name,))
        
        # 再删除婴幼儿档案
        if self.db_type == 'mysql':
            self.cursor.execute('DELETE FROM infant_profile WHERE id = %s', (infant_id,))
        else:  # sqlite
            self.cursor.execute('DELETE FROM infant_profile WHERE id = ?', (infant_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_infant_history(self, infant_name):
        """
        删除指定婴幼儿的所有历史记录
        :param infant_name: 婴幼儿姓名
        :return: 是否删除成功
        """
        try:
            # 删除相关的对话记录
            if self.db_type == 'mysql':
                self.cursor.execute('DELETE FROM chat_context WHERE infant_name = %s', (infant_name,))
            else:  # sqlite
                self.cursor.execute('DELETE FROM chat_context WHERE infant_name = ?', (infant_name,))
            
            # 删除该婴幼儿的所有档案记录
            if self.db_type == 'mysql':
                self.cursor.execute('DELETE FROM infant_profile WHERE name = %s', (infant_name,))
            else:  # sqlite
                self.cursor.execute('DELETE FROM infant_profile WHERE name = ?', (infant_name,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"删除历史记录失败: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    # 对话上下文相关方法
    def add_chat_message(self, infant_name, role, content):
        # 检查当前对话消息数量
        if self.db_type == 'mysql':
            self.cursor.execute('SELECT COUNT(*) FROM chat_context WHERE infant_name = %s', (infant_name,))
        else:  # sqlite
            self.cursor.execute('SELECT COUNT(*) FROM chat_context WHERE infant_name = ?', (infant_name,))
        count = self.cursor.fetchone()[0] if self.db_type == 'sqlite' else self.cursor.fetchone()['COUNT(*)']
        
        # 如果超过20条，删除最早的消息
        if count >= 20:
            if self.db_type == 'mysql':
                self.cursor.execute('''
                DELETE FROM chat_context 
                WHERE infant_name = %s AND id IN (
                    SELECT id FROM chat_context 
                    WHERE infant_name = %s 
                    ORDER BY timestamp ASC 
                    LIMIT %s
                )
                ''', (infant_name, infant_name, count - 19))
            else:  # sqlite
                self.cursor.execute('''
                DELETE FROM chat_context 
                WHERE infant_name = ? AND id IN (
                    SELECT id FROM chat_context 
                    WHERE infant_name = ? 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
                ''', (infant_name, infant_name, count - 19))
        
        # 添加新消息
        if self.db_type == 'mysql':
            self.cursor.execute('''
            INSERT INTO chat_context (infant_name, role, content) 
            VALUES (%s, %s, %s)
            ''', (infant_name, role, content))
        else:  # sqlite
            self.cursor.execute('''
            INSERT INTO chat_context (infant_name, role, content) 
            VALUES (?, ?, ?)
            ''', (infant_name, role, content))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_chat_history(self, infant_name, limit=20):
        if self.db_type == 'mysql':
            self.cursor.execute('''
            SELECT role, content, timestamp 
            FROM chat_context 
            WHERE infant_name = %s 
            ORDER BY timestamp ASC 
            LIMIT %s
            ''', (infant_name, limit))
        else:  # sqlite
            self.cursor.execute('''
            SELECT role, content, timestamp 
            FROM chat_context 
            WHERE infant_name = ? 
            ORDER BY timestamp ASC 
            LIMIT ?
            ''', (infant_name, limit))
        return self.cursor.fetchall()
    
    def get_chat_time_range(self, infant_name):
        if self.db_type == 'mysql':
            self.cursor.execute('''
            SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time 
            FROM chat_context 
            WHERE infant_name = %s
            ''', (infant_name,))
        else:  # sqlite
            self.cursor.execute('''
            SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time 
            FROM chat_context 
            WHERE infant_name = ?
            ''', (infant_name,))
        result = self.cursor.fetchone()
        return (result['min_time'], result['max_time']) if result else (None, None)
    
    def clear_chat_history(self, infant_name):
        if self.db_type == 'mysql':
            self.cursor.execute('DELETE FROM chat_context WHERE infant_name = %s', (infant_name,))
        else:  # sqlite
            self.cursor.execute('DELETE FROM chat_context WHERE infant_name = ?', (infant_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0