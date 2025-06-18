import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_utils.create_embeddings import create_new_embedding
from langchain_utils.langgraph_react_agent import get_react_agent
from langchain import hub
from agentql_utils.get_application import get_form_files
from agentql_utils.fill_form import fill_the_form
from langchain_core.output_parsers import JsonOutputParser
import json
import tempfile
import subprocess
import time

# 从.env文件加载环境变量
load_dotenv()

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

new_embedding = create_new_embedding(file_path=pdf_path,
                                     embedding_collection_name="my-resume",
                                     retriever_tool_name="my_resume",
                                     retriever_tool_description="my resume have the the information me as a machine learning engineer.")
retriever_tool = new_embedding.create_retriever_tools()

@tool
def get_answers_about_me(query: str):
    llm = ChatOpenAI(
        temperature=0,
        model='deepseek-chat',
        openai_api_key='sk-c19d3ee565094a15b97fc25e6131e6f8',
        openai_api_base='https://api.deepseek.com',
        streaming=False
    )
    prompt = hub.pull("hwchase17/openai-tools-agent")
    prompt.messages[0].prompt.template = "你是一个简历信息提取助手，专门帮助用户从简历文本中提取关键字段，并以标准化的JSON格式返回。"

    agent = create_openai_tools_agent(llm, [retriever_tool], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[retriever_tool])
    response = agent_executor.invoke({"input": query})
    print(response.content)
    return response

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
