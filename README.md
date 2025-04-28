# AI 智能助手

这是一个基于 OpenAI API 的智能助手项目，提供了两个版本的实现：完整版（agent.py）和轻量版（agent_lite.py）。该项目能够通过自然语言交互，帮助用户完成各种任务，包括代码执行、网络搜索、网页内容抓取和 PDF 解析等功能。

## 功能特性

### 完整版 (agent.py)
- 执行 Python 代码
- Google 搜索功能
- 网页内容抓取
- PDF 文件解析
- 智能任务分解和规划
- 多工具组合使用
- 失败重试和替代方案

### 轻量版 (agent_lite.py)
- 执行 Python 代码
- 专注于使用 Python 标准库解决问题
- 更轻量级的系统提示
- 适合简单任务和代码执行

## 技术栈
- Python 3.x
- OpenAI API (通过阿里云 DashScope 兼容接口)
- 依赖库：
  - openai
  - googlesearch-python
  - newspaper3k
  - PyPDF2
  - beautifulsoup4
  - requests
  - 其他相关依赖

## 安装说明

1. 克隆项目到本地：
```bash
git clone https://github.com/casey-cindex/ai-assistant-agent.git
cd ai-assistant-agent
```

2. 创建并激活虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
export OPENAI_API_KEY="your_api_key"  # Linux/Mac
# 或
set OPENAI_API_KEY="your_api_key"  # Windows
```

## 使用方法

### 运行完整版：
```bash
python agent.py
```

### 运行轻量版：
```bash
python agent_lite.py
```

运行后，你可以直接输入自然语言指令，AI 助手会：
1. 分析并拆解你的任务
2. 制定执行计划
3. 调用相应工具完成任务
4. 返回执行结果

## 示例功能

1. 执行 Python 代码：
```
$ 计算斐波那契数列的前10个数
```

2. 搜索信息（仅完整版）：
```
$ 搜索关于人工智能的最新新闻
```

3. 网页内容抓取（仅完整版）：
```
$ 获取指定网页的主要内容
```

4. PDF 解析（仅完整版）：
```
$ 解析本地的report.pdf文件
```

## 注意事项

- 确保已正确设置 OPENAI_API_KEY 环境变量
- 完整版需要网络连接以使用搜索和网页抓取功能
- 建议在虚拟环境中运行项目
- 使用轻量版时，优先使用 Python 标准库解决问题

## 系统要求

- Python 3.x
- 操作系统：Windows/Linux/MacOS
- 网络连接（完整版必需）
- 足够的系统内存（建议 4GB 以上）