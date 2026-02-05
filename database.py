import pymysql
import os
import datetime

class Database:
    def __init__(self, host='localhost', user='root', password='123456', db='infant_health'):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.conn = None
        self.cursor = None
    
    def connect(self):
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
            print(f"数据库连接失败: {e}")
            return False
    
    def init_db(self):
        """
        初始化数据库表结构
        """
        if not self.conn:
            return
        
        try:
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
            
            # 创建索引，提高查询速度
            # 使用更兼容的方式创建索引
            try:
                self.cursor.execute('CREATE INDEX idx_chat_context_infant_id ON chat_context (infant_id)')
            except Exception:
                pass  # 索引已存在，忽略错误
            
            try:
                self.cursor.execute('CREATE INDEX idx_chat_context_timestamp ON chat_context (timestamp)')
            except Exception:
                pass  # 索引已存在，忽略错误
            
            self.conn.commit()
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            self.conn.rollback()
    
    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"关闭数据库连接失败: {e}")
    
    def set_connection(self, host, user, password, db):
        """
        设置数据库连接参数
        """
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
        
        query = '''
        INSERT INTO infant_profile (
            name, gender, birth_date, is_preterm, gestational_age, 
            weight, height, head_circumference, feeding_type, daily_milk, 
            辅食_start_age, allergies, health_conditions, supplements, 
            food_texture, disliked_foods, can_eat_independently, 
            family_dietary_restrictions, city, record_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        self.cursor.execute('SELECT * FROM infant_profile WHERE id = %s', (infant_id,))
        return self.cursor.fetchone()
    
    def get_latest_infant(self, name):
        """
        获取指定婴幼儿的最新档案
        :param name: 婴幼儿姓名
        :return: 最新档案信息
        """
        self.cursor.execute('''
        SELECT * FROM infant_profile 
        WHERE name = %s 
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
        self.cursor.execute('''
        SELECT * FROM infant_profile 
        WHERE name = %s 
        ORDER BY record_date DESC
        ''', (name,))
        return self.cursor.fetchall()
    
    def update_infant(self, infant_id, data):
        query = '''
        UPDATE infant_profile SET 
            name = %s, gender = %s, birth_date = %s, is_preterm = %s, gestational_age = %s, 
            weight = %s, height = %s, head_circumference = %s, feeding_type = %s, daily_milk = %s, 
            辅食_start_age = %s, allergies = %s, health_conditions = %s, supplements = %s, 
            food_texture = %s, disliked_foods = %s, can_eat_independently = %s, 
            family_dietary_restrictions = %s, city = %s
        WHERE id = %s
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
        # 先删除相关的对话记录
        self.cursor.execute('DELETE FROM chat_context WHERE infant_id = %s', (infant_id,))
        # 再删除婴幼儿档案
        self.cursor.execute('DELETE FROM infant_profile WHERE id = %s', (infant_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # 对话上下文相关方法
    def add_chat_message(self, infant_name, role, content):
        # 检查当前对话消息数量
        self.cursor.execute('SELECT COUNT(*) FROM chat_context WHERE infant_name = %s', (infant_name,))
        count = self.cursor.fetchone()['COUNT(*)']
        
        # 如果超过20条，删除最早的消息
        if count >= 20:
            self.cursor.execute('''
            DELETE FROM chat_context 
            WHERE infant_name = %s AND id IN (
                SELECT id FROM chat_context 
                WHERE infant_name = %s 
                ORDER BY timestamp ASC 
                LIMIT %s
            )
            ''', (infant_name, infant_name, count - 19))
        
        # 添加新消息
        self.cursor.execute('''
        INSERT INTO chat_context (infant_name, role, content) 
        VALUES (%s, %s, %s)
        ''', (infant_name, role, content))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_chat_history(self, infant_name, limit=20):
        self.cursor.execute('''
        SELECT role, content, timestamp 
        FROM chat_context 
        WHERE infant_name = %s 
        ORDER BY timestamp ASC 
        LIMIT %s
        ''', (infant_name, limit))
        return self.cursor.fetchall()
    
    def get_chat_time_range(self, infant_name):
        self.cursor.execute('''
        SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time 
        FROM chat_context 
        WHERE infant_name = %s
        ''', (infant_name,))
        result = self.cursor.fetchone()
        return (result['min_time'], result['max_time']) if result else (None, None)
    
    def clear_chat_history(self, infant_name):
        self.cursor.execute('DELETE FROM chat_context WHERE infant_name = %s', (infant_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0