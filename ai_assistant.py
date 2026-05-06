import streamlit as st
from openai import OpenAI
from datetime import datetime
import os
import json

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    st.error("❌ 环境变量 DEEPSEEK_API_KEY 未设置")
    st.stop()

# 测试API连通性
try:
    test_client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    test_client.models.list()  # 轻量级调用，验证key有效性
except Exception as e:
    st.error(f"🔌 API 连接测试失败：{e}\n请检查网络和 API Key")
    st.stop()

# 创建OpenAI客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")

# 页面的配置项
st.set_page_config(
    page_title="AI智能助手",
    page_icon="🤖",
    # 布局
    layout="wide",
    # 控制的是侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={}
)

# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载sessions目录下的文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True) # 降序排列
    return session_list

# 加载会话数据函数
def load_session(session_name):
    try:
        with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
            session_data = json.load(f)
            st.session_state.messages = session_data["messages"]
            st.session_state.nick_name = session_data["nick_name"]
            st.session_state.nature = session_data["nature"]
            st.session_state.current_session = session_name
            st.success(f"✅ 加载会话成功：{session_name}")
    except FileNotFoundError:
        st.warning(f"会话文件不存在：{session_name}")
    except json.JSONDecodeError:
        st.error(f"会话文件损坏，无法解析：{session_name}")
    except Exception as e:
        st.error(f"加载会话时发生未知错误：{e}")

# 删除会话数据函数
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            st.success(f"删除会话数据成功：{session_name}")
            # 如果删除的是当前会话，则重新生成会话名称
            if st.session_state.current_session == session_name:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception as e:
        st.error(f"删除会话数据失败：{e}")

# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存当前会话信息函数
def save_session():
    if not st.session_state.current_session:
        return
    try:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存会话失败：{e}")

# logo
st.logo("./resources/logo.jpg",size = "large")

# 大标题
st.title("AI智能助手")

# 初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小助手"

if "nature" not in st.session_state:
    st.session_state.nature = "专业严谨、乐于助人"

if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 展示聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 左侧边栏 - with:streamlit中上下文管理器
with st.sidebar:
    # 会话信息
    st.title("控制面板")
    if st.button("新建会话",width="stretch",icon="✏️"):
        # 保存当前会话信息
        if st.session_state.messages:
            save_session()

        # 重置为新会话
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()
        st.session_state.nick_name = "小助手"
        st.session_state.nature = "专业严谨、乐于助人"
        st.rerun() # 重新运行页面
    # 历史会话
    st.subheader("历史会话")
    # 1、展示历史会话列表
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1],width="stretch")
        with col1:
            # 加载会话信息
            # 三元运算符：条件 ? 真 : 假-->语法：条件 ? 值1 : 值2
            if st.button(session,width="stretch",icon="📄",key=f"load_{session}",type="primary" if session ==st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            # 删除会话信息
            if st.button("",width="stretch",icon="🗑️",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()
    # 伴侣信息
    st.subheader("助手设定")
    # 昵称输入
    nick_name_input = st.text_input("助手名称：",value=st.session_state.nick_name, placeholder="例如：小智、阿助..")
    if nick_name_input:
        st.session_state.nick_name = nick_name_input

    # 性格输入
    nature_input = st.text_area("助手风格：",value=st.session_state.nature, placeholder="例如：专业严谨、幽默风趣、温柔耐心...")
    if nature_input:
        st.session_state.nature = nature_input

    # 导出对话
    st.subheader("导出对话")
    # 生成聊天记录文本
    chat_content = f"# AI助手对话记录\n\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    chat_content += f"助手名称：{st.session_state.nick_name}\n"
    chat_content += f"助手风格：{st.session_state.nature}\n"
    chat_content += f"会话名称：{st.session_state.current_session}\n\n"
    chat_content += "## 对话内容\n\n"
    for msg in st.session_state.messages:
        role = "👤 我" if msg["role"] == "user" else f"❤️ {st.session_state.nick_name}"
        chat_content += f"**{role}**：{msg['content']}\n\n"

        # 提供下载
    st.download_button(
        label="📥 导出当前对话",
        data=chat_content.encode("utf-8"),
        file_name=f"chat_{st.session_state.current_session}.md",
        mime="text/markdown",
        key="export_chat",
        use_container_width=True
    )

# 系统提示词
system_prompt = f"""
你是{st.session_state.nick_name}，一个智能AI助手，助人为乐。请完全带入助手角色。
规则：
1. 每次只回复一条消息
2. 禁止任何场景或状态描述性文字（如“*思考中*”）
3. 匹配用户的交流语言
4. 回复简短清晰，像聊天一样自然
5. 可以适当使用emoji表情
6. 用符合“{st.session_state.nature}”的风格回复
7. 内容要体现你的性格特征

你必须遵守上述规则来回答用户。
"""

# 聊天框
prompt = st.chat_input("给AI智能助手发送消息...")
if prompt:
    st.chat_message("user").write(prompt)
    print(f"----->调用AI大模型，提示词：{prompt}")
    # 保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 组装系统提示词
    messages_with_system = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # 调用大模型，带异常处理
    try:
        response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages_with_system,
        stream=True,
        timeout=30, # 设置超时时间为30秒
        )
    except Exception as e:
    # 根据不同错误类型给出更精确的提示
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            st.error("⏰ 网络超时，请检查网络连接后重试。")
        elif "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            st.error("🔑 API Key 无效或已过期，请检查环境变量 DEEPSEEK_API_KEY。")
        elif "rate_limit" in error_msg.lower():
            st.error("🚦 请求过于频繁，请稍后再试。")
        else:
            st.error(f"🤖 AI 服务出错：{error_msg}\n请稍后重试。")
        st.stop()
    # assistant_response = response.choices[0].message.content

# 输出大模型返回的结果（非流式输出的解析方式）
#     st.chat_message("assistant").write(assistant_response)
#     print(f"<-----AI大模型返回结果：{response.choices[0].message.content}")

# 输出大模型返回的结果（流失输出的解析方式）
    response_message = st.empty() # 创建一个空的组件，用于展示大模型返回的结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    #  保存会话信息
    save_session()

    # 刷新页面更新历史会话列表
    st.rerun()


