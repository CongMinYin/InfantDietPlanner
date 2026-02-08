# InfantDietPlanner(婴幼儿健康分析和智能问答系统)

## 项目介绍

InfantDietPlanner是一个功能强大的婴幼儿健康分析和智能问答系统，专为家长和医护人员设计，用于跟踪婴幼儿的生长发育、健康状况，并提供AI驱动的营养分析和食谱推荐。

## 核心功能

### 1. 双数据库支持
- 支持MySQL数据库（需要本地安装）
- 支持SQLite数据库（嵌入式，无需额外安装）
- 启动时可选择使用哪种数据库

### 2. 婴幼儿档案管理
- 添加新婴幼儿档案
- 编辑现有档案信息
- 删除最新档案
- **删除历史档案**：删除指定婴幼儿的所有历史记录
- 查看历史档案信息

### 3. AI健康顾问
- 基于婴幼儿档案信息生成个性化系统提示
- 体质分析和健康评估
- 营养需求分析
- 个性化食谱推荐
- 聊天式交互界面
- 支持Enter键发送消息

### 4. 生长曲线绘制
- 体重增长曲线
- 身高/身长增长曲线
- 头围增长曲线
- 集成WHO儿童生长标准（P3、P50、P97百分位）
- 支持导出生长曲线为PDF

### 5. 数据导出功能
- 导出生长曲线为PDF文件
- 导出婴幼儿信息为TXT文件
- 导出聊天记录为TXT文件

### 6. 示例数据
- 内置示例数据（大头儿子）
- 包含不同年龄段的生长数据
- 便于快速体验系统功能

## 技术架构

- **前端**：Python Tkinter GUI
- **后端**：Python
- **数据库**：MySQL / SQLite
- **AI集成**：ModelScope大模型
- **数据可视化**：Matplotlib
- **PDF导出**：Matplotlib PDF backend

## 安装说明

### 1. 环境要求
- Python 3.7+
- pip包管理器

### 2. 依赖安装

```bash
# 克隆或下载项目后，进入项目目录
cd InfantDietPlanner

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库准备

#### MySQL（可选）
- 安装MySQL数据库
- 创建数据库：`infant_diet_planner`
- 确保有用户权限（默认：root/123456）

#### SQLite（默认）
- 无需额外安装，系统会自动创建

## 使用方法

### 1. 启动系统

```bash
python main.py
```

### 2. 数据库选择
- 启动后会弹出数据库选择对话框
- 选择SQLite（推荐，无需配置）或MySQL
- 若选择MySQL，需要输入数据库连接信息

### 3. 基本操作

#### 添加婴幼儿
- 点击"添加"按钮
- 填写婴幼儿基本信息、体检数据、喂养情况等
- 点击"保存"按钮

#### 选择婴幼儿
- 在左侧列表中选择已添加的婴幼儿
- 右侧会显示该婴幼儿的最新档案信息
- 下方会生成生长曲线

#### 编辑/删除档案
- 选择婴幼儿后，点击"编辑"按钮修改信息
- 点击"删除"按钮删除最新档案
- 点击"删除历史档案"按钮删除该婴幼儿的所有历史记录

#### 查看历史信息
- 选择婴幼儿后，点击"历史信息"按钮
- 在弹出的窗口中查看该婴幼儿的所有历史档案

#### AI健康顾问
- 在下方聊天输入框中输入问题或需求
- 点击"发送"按钮或按Enter键
- 等待AI回复（会显示"AI正在思考中..."）
- 查看AI的分析和建议

#### 导出数据
- 选择婴幼儿后，点击"导出"按钮
- 选择要导出的内容（生长曲线、基本信息、聊天记录）
- 选择保存位置

## 系统界面

- **左侧**：婴幼儿列表、基本信息、历史信息按钮
- **中部**：生长曲线图表（体重、身高、头围）
- **右侧**：聊天记录、AI回复、输入框
- **底部**：导出按钮、AI上下文数量设置

## 示例数据

系统内置了"大头儿子"的示例数据，包含不同年龄段的生长记录，便于用户快速体验系统功能。点击"添加示例"按钮即可导入。

## 注意事项

1. 使用MySQL时，请确保数据库服务已启动
2. AI功能需要有效的ModelScope API密钥
3. 导出PDF功能需要Matplotlib支持
4. 生长曲线绘制需要足够的历史数据

## 故障排除

- **数据库连接失败**：检查MySQL服务是否启动，连接信息是否正确
- **AI无回复**：检查API密钥是否有效，网络连接是否正常
- **生长曲线不显示**：确保已添加足够的历史数据

## 许可证

本项目采用BSD 3-Clause许可证。

```
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
```

## 联系方式

如有问题或建议，请联系项目维护者。

---

*版本：1.0.0*
*更新日期：2026-02-08*