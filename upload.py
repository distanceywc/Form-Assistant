import streamlit as st
import tempfile
import os
from PIL import Image
import base64
import json

# 设置页面配置
st.set_page_config(
    page_title="表单自动填写助手",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# 自定义CSS样式
def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# 创建style.css文件内容 - 优化了容器高度
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
    --primary: #4361ee;
    --secondary: #3f37c9;
    --accent: #4895ef;
    --light: #f8f9fa;
    --dark: #212529;
    --success: #4cc9f0;
    --border-radius: 16px;
}

* {
    font-family: 'Poppins', sans-serif;
}

body {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
}

.stApp {
    max-width: 800px;
    margin: 0 auto;
    padding: 1.5rem 1rem; /* 减少整体页面内边距 */
}

.header-container {
    text-align: center;
    padding: 1.5rem 0; /* 减少标题区域内边距 */
    margin-bottom: 1rem; /* 减少标题区域外边距 */
}

.header-title {
    font-size: 2.2rem; /* 稍微减小标题大小 */
    font-weight: 700;
    color: black;
    margin-bottom: 0.3rem; /* 减少标题下方间距 */
    background: linear-gradient(90deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: black;
}

.header-subtitle {
    font-size: 1rem; /* 稍微减小副标题大小 */
    color: #555;
    max-width: 600px;
    margin: 0 auto;
}

.url-container {
    background: #e6f0ff;
    border-radius: var(--border-radius);
    padding: 1.5rem; /* 减少容器内边距 */
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem; /* 减少容器间外边距 */
    border: 1px solid rgba(0,0,0,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.url-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    background: #d9e6ff; 
}

.url-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.2rem; /* 减小标题大小 */
    color: var(--dark);
    margin-bottom: 1rem; /* 减少标题下方间距 */
}

.url-icon {
    font-size: 1.5rem; /* 减小图标大小 */
    color: var(--primary);
}

.url-input-row {
    display: flex;
    gap: 10px;
    margin-bottom: 1rem;
    align-items: center;
}

.url-input {
    flex: 1;
    padding: 0.7rem 1rem; /* 减小输入框内边距 */
    border-radius: 8px;
    border: 1px solid #cbd5e0;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-sizing: border-box;
}

.url-input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
}

.url-hint {
    font-size: 0.85rem; /* 减小提示文字大小 */
    color: #718096;
    margin-top: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: #f8f9fa;
    border-radius: 8px;
    border-left: 3px solid var(--accent);
}

.confirm-btn {
    background: var(--primary);
    color: white;
    border: none;
    padding: 0.7rem 1.3rem; /* 减小按钮内边距 */
    border-radius: 8px;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 6px rgba(67, 97, 238, 0.3);
    min-width: 90px; /* 减小按钮最小宽度 */
    height: 42px; /* 减小按钮高度 */
    white-space: nowrap;
}

.confirm-btn:hover {
    background: var(--secondary);
    transform: translateY(-2px);
    box-shadow: 0 6px 8px rgba(67, 97, 238, 0.4);
}

.upload-container {
    background: #e6ffe6;
    border-radius: var(--border-radius);
    padding: 1.5rem; /* 减少容器内边距 */
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem; /* 减少容器间外边距 */
    border: 1px solid rgba(0,0,0,0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.upload-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    background: #d9e6ff;
}

.upload-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.2rem; /* 减小标题大小 */
    color: var(--dark);
    margin-bottom: 1rem; /* 减少标题下方间距 */
}

.upload-icon {
    font-size: 1.5rem; /* 减小图标大小 */
    color: var(--primary);
}

.file-uploader {
    border: 2px dashed #cbd5e0;
    border-radius: 12px;
    padding: 1.5rem 1rem; /* 减少上传区域内边距 */
    text-align: center;
    margin-bottom: 1rem; /* 减少上传区域下方间距 */
    background-color: #f8fafc;
    transition: all 0.3s ease;
    cursor: pointer;
}

.file-uploader:hover {
    border-color: var(--accent);
    background-color: #f0f7ff;
}

.file-uploader .stFileUploader {
    width: 100%;
}

.success-box {
    background: linear-gradient(135deg, #e3fdfd 0%, #cbf1f5 100%);
    border-radius: 12px;
    padding: 1rem; /* 减少成功框内边距 */
    margin-top: 1rem; /* 减少成功框上方间距 */
    border-left: 4px solid var(--success);
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.file-info {
    display: flex;
    flex-direction: column;
    gap: 6px; /* 减小文件信息间距 */
    margin-top: 0.8rem; /* 减少文件信息上方间距 */
    padding: 0.8rem; /* 减少文件信息内边距 */
    background-color: white;
    border-radius: 8px;
    border: 1px solid #edf2f7;
    font-size: 0.9rem; /* 减小文件信息字体大小 */
}

.file-info-item {
    display: flex;
    justify-content: space-between;
    padding: 0.4rem 0; /* 减小文件信息项内边距 */
    border-bottom: 1px solid #eee;
}

.file-info-item:last-child {
    border-bottom: none;
}

.warning-box {
    background: #fff9db;
    border-radius: 12px;
    padding: 1rem; /* 减少警告框内边距 */
    text-align: center;
    border: 1px solid #ffe066;
    margin-top: 1rem;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(255, 193, 7, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
}

.step-container {
    background: white;
    border-radius: var(--border-radius);
    padding: 1.5rem; /* 减少步骤容器内边距 */
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    margin-top: 1.5rem;
}

.step-title {
    font-size: 1.1rem; /* 减小步骤标题大小 */
    color: var(--dark);
    margin-bottom: 1rem; /* 减少步骤标题下方间距 */
    display: flex;
    align-items: center;
    gap: 10px;
}

.step-icon {
    font-size: 1.3rem; /* 减小步骤图标大小 */
    color: var(--accent);
}

.form-columns {
    display: flex;
    gap: 1.2rem; /* 减小表单列间距 */
    margin-top: 1rem;
}

.form-column {
    flex: 1;
}

.form-group {
    margin-bottom: 1.2rem; /* 减少表单组间距 */
}

.form-label {
    display: block;
    margin-bottom: 0.4rem; /* 减少标签下方间距 */
    font-weight: 500;
    color: #4a5568;
    font-size: 0.95rem; /* 减小标签字体大小 */
}

.form-input {
    width: 100%;
    padding: 0.7rem 1rem; /* 减小表单输入框内边距 */
    border-radius: 8px;
    border: 1px solid #cbd5e0;
    font-size: 0.95rem; /* 减小表单输入框字体大小 */
    transition: all 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
}

.submit-btn {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    border: none;
    padding: 0.9rem 2.3rem; /* 减小提交按钮内边距 */
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem; /* 减小提交按钮字体大小 */
    cursor: pointer;
    transition: all 0.3s ease;
    display: block;
    margin: 1.5rem auto 0; /* 减少提交按钮外边距 */
    box-shadow: 0 6px 12px rgba(67, 97, 238, 0.3);
}

.submit-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 15px rgba(67, 97, 238, 0.4);
}

.footer {
    text-align: center;
    margin-top: 2rem; /* 减少页脚上方间距 */
    color: #718096;
    font-size: 0.85rem; /* 减小页脚字体大小 */
}

.link-icon {
    color: var(--primary);
    font-size: 1rem; /* 减小链接图标大小 */
    margin-right: 6px; /* 减少链接图标右边距 */
    vertical-align: middle;
}

/* 修改后的成功框样式 - 居中占满一行 */
.url-success {
    background: linear-gradient(135deg, #e6f7e6 0%, #d0f0d0 100%);
    border-radius: 12px;
    padding: 1rem; /* 减少成功框内边距 */
    margin-top: 1rem;
    border-left: 4px solid #4CAF50;
    animation: fadeIn 0.5s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    width: 100%;
}

.url-success-content {
    max-width: 100%;
    word-break: break-all;
    font-size: 0.9rem; /* 减小成功内容字体大小 */
}

/* 新增：自动填写提示框样式 */
.auto-fill-box {
    background: linear-gradient(135deg, #e6f2ff 0%, #cce0ff 100%);
    border-radius: 12px;
    padding: 1.2rem; /* 内边距 */
    margin: 1.5rem 0; /* 上下外边距 */
    border-left: 4px solid var(--primary);
    animation: fadeIn 0.5s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    width: 100%;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.auto-fill-box h3 {
    margin: 0;
    font-size: 1.2rem; /* 标题字体大小 */
    color: var(--dark);
    display: flex;
    align-items: center;
    gap: 10px;
}

.auto-fill-icon {
    font-size: 1.5rem; /* 图标大小 */
    color: var(--primary);
    animation: pulse 2s infinite;
}
</style>
"""

# 将CSS保存到文件
with open("style.css", "w") as f:
    f.write(css)

# 加载CSS
load_css()

# 初始化session_state变量
if 'form_url' not in st.session_state:
    st.session_state.form_url = ""
if 'url_confirmed' not in st.session_state:
    st.session_state.url_confirmed = False
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None

# 页面内容
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📝表单自动填写助手</h1>
    <p class="header-subtitle">上传您的简历并填写目标表单链接，我们将帮助您自动填写求职表单，节省时间并提高申请效率</p>
</div>
""", unsafe_allow_html=True)

# 表单链接容器
with st.container():
    st.markdown("""
    <div class="url-container">
        <div class="url-title">
            <span class="url-icon">🔗</span>
            <span>step1: 填写目标表单链接</span>
        </div>
    """, unsafe_allow_html=True)

    # 使用行布局放置输入框和按钮
    st.markdown('<div class="url-input-row">', unsafe_allow_html=True)

    # 创建两列布局：输入框占据大部分空间，按钮占据小部分
    col1, col2 = st.columns([4, 1])

    with col1:
        # 表单链接输入框
        new_url = st.text_input(
            "目标表单链接",
            value=st.session_state.form_url,
            placeholder="请输入目标表单的URL链接",
            label_visibility="collapsed",
            key="url_input"
        )

    with col2:
        # 确认按钮 - 与输入框在同一行
        if st.button("确认", key="confirm_url", type="primary", use_container_width=True):
            if new_url.strip():
                st.session_state.form_url = new_url
                st.session_state.url_confirmed = True
            else:
                st.error("请输入有效的表单链接")

    st.markdown('</div>', unsafe_allow_html=True)

    # 提示信息
    st.markdown("""
    <div class="url-hint">
        <span class="link-icon">💡</span>
        请确保表单链接正确无误，您可以从招聘网站的申请页面复制此链接
    </div>
    """, unsafe_allow_html=True)

    # 显示确认状态 - 居中占满一行
    if st.session_state.url_confirmed:
        st.markdown(f"""
        <div class="url-success">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 1.3rem;">✅</span>
                <h3 style="margin: 0; font-size: 1.1rem;">表单链接已确认</h3>
            </div>
            <div class="url-success-content">
                <p style="margin: 0; word-break: break-all; font-size: 0.9rem;">
                    <strong>目标链接：</strong> {st.session_state.form_url}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# 上传容器
with st.container():
    st.markdown("""
    <div class="upload-container">
        <div class="upload-title">
            <span class="upload-icon">📄</span>
            <span>step2: 上传您的简历(PDF文件)</span>
        </div>
    """, unsafe_allow_html=True)

    # 文件上传组件
    uploaded_file = st.file_uploader("选择PDF文件", type="pdf", label_visibility="collapsed")

    # 处理上传的文件
    if uploaded_file is not None:
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                st.session_state.pdf_path = tmp_file.name

            st.markdown("""
            <div class="success-box">
                <h3 style="font-size: 1.1rem; margin-bottom: 0.5rem;">🎉 文件上传成功！</h3>
                <div class="file-info">
                    <div class="file-info-item">
                        <span>文件名：</span>
                        <strong>{file_name}</strong>
                    </div>
                    <div class="file-info-item">
                        <span>文件大小：</span>
                        <strong>{file_size} 字节</strong>
                    </div>
                    <div class="file-info-item">
                        <span>状态：</span>
                        <strong style="color: #10b981;">已就绪</strong>
                    </div>
                </div>
            </div>
            """.format(file_name=uploaded_file.name, file_size=uploaded_file.size), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"文件处理失败: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# 自动填写提示框（在URL确认和文件上传都成功后显示）
if st.session_state.url_confirmed and st.session_state.pdf_path is not None:
    st.markdown("""
    <div class="auto-fill-box">
        <h3>
            <span class="auto-fill-icon">⚡</span>
            表单开始自动填写
        </h3>
        <p style="margin-top: 10px; font-size: 1rem; color: #4a5568;">
            表单助手正在处理您的简历数据，准备自动填写表单...
        </p>
    </div>
    """, unsafe_allow_html=True)

# 页脚
st.markdown("""
<div class="footer">
    <p>© 2025 表单自动填写助手 | 让求职申请更简单高效</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.url_confirmed and st.session_state.pdf_path is not None:
    data = {
        "form_url": st.session_state.form_url,
        "pdf_path": st.session_state.pdf_path
    }

    # 之前已将用户上传的简历和表单链接下载到本地，并用json临时文件保存其存储路径
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, "tmp_data.json")

    with open(temp_file, "w") as f:
        json.dump(data, f)
