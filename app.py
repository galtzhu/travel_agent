import streamlit as st
import uuid # 🟢 导入 uuid 生成唯一ID
from agent_engine import get_travel_agent

st.set_page_config(
    page_title="智能旅行助手",
    page_icon="🎒",
    layout="centered"
)

st.title("🎒 智能旅行助手 (Agno + Gemini 2.5)")
st.caption("🚀 由 高德地图 & Tomorrow.io 提供实时数据支持")

# 🟢 1. 为每个用户生成唯一的 Session ID (只在第一次运行时生成)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 🟢 2. 初始化 Agent (传入 session_id)
# 注意：这里去掉了 @st.cache_resource，因为我们要动态传入 session_id
# 且 Agno 有了 Storage 后，创建开销很小，可以直接创建
def get_agent():
    return get_travel_agent(session_id=st.session_state.session_id)

try:
    agent = get_agent()
except Exception as e:
    st.error(f"Agent 初始化失败: {e}")
    st.stop()
    
# 3. 管理聊天记录 (Session State)
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "你好！我是你的旅行搭子。想去哪里玩？或者想查查天气？"}]

# 4. 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. 处理用户输入
if prompt := st.chat_input("输入你的旅行计划..."):
    # 5.1 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5.2 生成助手回复
    with st.chat_message("assistant"):
        # 创建一个空的容器，用来产生“打字机”效果
        response_placeholder = st.empty()
        full_response = ""

        # 调用 Agent (stream=True 获取流式响应)
        try:
            # 这是一个转接器：把 Agno 的流式对象转换成 Streamlit 能显示的文本
            response_generator = agent.run(prompt, stream=True)

            for chunk in response_generator:
                # 根据 Agno 版本不同，chunk 可能是对象也可能是字符串
                # 这里做一个兼容处理
                content = getattr(chunk, "content", str(chunk))
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")

            # 显示最终完整回复
            response_placeholder.markdown(full_response)

            # 5.3 保存助手回复到历史记录
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"发生错误: {e}")
