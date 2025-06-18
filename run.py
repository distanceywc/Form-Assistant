import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_utils.langgraph_react_agent import get_react_agent
from agentql_utils.get_application import get_form_files
from agentql_utils.fill_form import fill_the_form
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, Any
import spacy
from pypdf import PdfReader
import re
import json
import tempfile
import subprocess
import time

# 从.env文件加载环境变量
load_dotenv()

# 设置环境变量
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv('LANGCHAIN_TRACING_V2')
os.environ["LANGCHAIN_PROJECT"] = os.getenv('LANGCHAIN_PROJECT')
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

proc = subprocess.Popen(["streamlit", "run", "upload.py"])
time.sleep(20)
# 尝试读取临时文件
temp_dir = tempfile.gettempdir()
temp_file = os.path.join(temp_dir, "tmp_data.json")

if os.path.exists(temp_file):
    with open(temp_file) as f:
        data = json.load(f)
    form_url = data["form_url"]
    pdf_path = data["pdf_path"]
    # 删除临时文件
    os.remove(temp_file)
else:
    print("未能获取表单数据")

@tool
def get_answers_about_me(query: str) -> Dict[str, Any]:
    """从PDF简历中智能提取信息并返回JSON数据"""

    # 定义提取字段
    extracted_data = {
        "姓名": "",
        "性别": "",
        "年龄": "",
        "政治面貌": "",
        "电子邮件": "",
        "地址": "",
        "电话号码": "",
        "教育背景": "",
        "备注": ""
    }

    file_path = pdf_path
    nlp = spacy.load("zh_core_web_sm")

    # 读取PDF文件
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    # 优化姓名提取 - 优先使用正则匹配标签
    name_match = re.search(r'(姓名|名字)[:：]?\s*([^\n]+)', text)
    if name_match:
        extracted_data["姓名"] = name_match.group(2).strip()
    else:
        # 其次使用spaCy实体识别
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and not extracted_data["姓名"]:
                extracted_data["姓名"] = ent.text
                break

    # 性别提取
    gender_match = re.search(r'(性别)[:：]?\s*([男女])', text)
    if gender_match:
        extracted_data["性别"] = gender_match.group(2).strip()
    else:
        # 尝试从文本中识别性别
        if "男" in text:
            extracted_data["性别"] = "男"
        elif "女" in text:
            extracted_data["性别"] = "女"

    # 年龄提取
    age_match = re.search(r'(年龄|岁数)[:：]?\s*(\d{1,2})岁?', text)
    if age_match:
        extracted_data["年龄"] = age_match.group(2).strip()
    else:
        # 尝试从出生日期推算年龄
        birth_match = re.search(r'(出生日期|生日)[:：]?\s*(\d{4})[年/-]', text)
        if birth_match:
            birth_year = int(birth_match.group(2))
            current_year = 2024  # 假设当前年份
            age = current_year - birth_year
            if 18 <= age <= 60:  # 合理的年龄范围
                extracted_data["年龄"] = str(age)

    # 政治面貌提取
    political_match = re.search(r'(政治面貌|党派)[:：]?\s*([^\n]+)', text)
    if political_match:
        extracted_data["政治面貌"] = political_match.group(2).strip()
    else:
        # 尝试匹配常见政治面貌
        political_keywords = ["中共党员", "预备党员", "共青团员", "群众", "民主党派"]
        for keyword in political_keywords:
            if keyword in text:
                extracted_data["政治面貌"] = keyword
                break

    # 优化地址提取 - 优先使用正则匹配标签
    address_match = re.search(r'(地址|所在地)[:：]?\s*([^\n]+)', text)
    if address_match:
        extracted_data["地址"] = address_match.group(2).strip()
    else:
        # 其次使用spaCy实体识别
        doc = nlp(text)
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        if locations:
            extracted_data["地址"] = "，".join(locations[:3])

    # 提取联系方式（正则更可靠）
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        extracted_data["电子邮件"] = email_match.group(0)

    phone_match = re.search(r'1[3-9]\d{9}', text)
    if phone_match:
        extracted_data["电话号码"] = phone_match.group(0)
    else:
        print("手机号格式有误❗❗❗")

    # 备注提取功能
    remark_match = re.search(r'(备注|个人总结|自我介绍)[:：]?\s*([^\n]+)', text)
    if remark_match:
        extracted_data["备注"] = remark_match.group(2).strip()
    else:
        # 如果没有找到备注标签，尝试从内容中提取个人总结
        summary_keywords = ["擅长", "精通", "熟悉", "掌握", "经验", "技能"]
        summary_sentences = []
        for sentence in text.split('\n'):
            if any(kw in sentence for kw in summary_keywords):
                summary_sentences.append(sentence)
        if summary_sentences:
            extracted_data["备注"] = " ".join(summary_sentences[:3])

    # 返回与AgentExecutor兼容的格式
    return {
        "input": query,
        "output": extracted_data,
        "intermediate_steps": []
    }

tools = [get_answers_about_me]
prompt = """
你必须严格模仿以下 JSON 格式回答问题：
{
    "name": "答案",
    "email": "答案",
    "address": "答案",
    "phone": "答案",
    "notes": "答案"
}
问题列表：
{questions}
只返回 JSON，不要包含任何额外数字、符号和文字！
"""
graph_agent = get_react_agent(tools=tools, prompt=prompt)

# 用AgentQL格式定义查询
QUERY = """
{
    details[]
    {
        job_role
        description
        all_questions[]
        {
            question
            type
            options
        }
    }
}
"""

# 定义目标表单URL
url = form_url

# 使用查询从URL获取输入表单
input_forms = get_form_files(url=url, query=QUERY)

# 过滤输入表单中的问题
filtered_data = [
    {**item, 'all_questions': [q for q in item['all_questions'] if
                               'upload your resume' not in q['question'] and q.get('input_filed_type') != 'file']}
    for item in input_forms
]

# 定义ReAct代理的输入
inputs = {"messages": [("user", str(filtered_data))]}

# 调用ReAct代理
result = graph_agent.invoke(inputs)

# 将ReAct代理的输出解析为JSON
parser = JsonOutputParser()
json_data = parser.parse(result["messages"][-1].content)

# 使用解析的JSON数据和简历位置路径填写表单
fill_the_form(url=url, form_data=json_data, resume_location_path=pdf_path)
