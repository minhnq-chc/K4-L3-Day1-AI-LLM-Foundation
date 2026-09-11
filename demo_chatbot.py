"""Bonus demo: giao diện chatbot và so sánh Nex-N2.5 Pro/Mini."""

import os
import time

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODELS = {
    "Nex-N2.5-Pro": os.getenv("LAB_MODEL", "nex-agi/nex-n2.5-pro:free"),
    "Nex-N2.5-Mini": os.getenv("LAB_MINI_MODEL", "nex-agi/nex-n2.5-mini:free"),
}
DEFAULT_PERSONA = (
    "Bạn là trợ lý học LLM API cho người mới. Trả lời bằng tiếng Việt, "
    "giải thích rõ ràng, ngắn gọn và dùng ví dụ thực tế khi phù hợp."
)

st.set_page_config(
    page_title="NexLab Chat",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {background: radial-gradient(circle at 15% 0%, #172554 0, #07111f 38%, #050912 100%);}
    [data-testid="stHeader"] {background: transparent;}
    [data-testid="stSidebar"] {background: rgba(8, 18, 35, .92); border-right: 1px solid #22395c;}
    .hero {padding: 1.2rem 1.4rem; border: 1px solid #24446d; border-radius: 18px;
      background: linear-gradient(135deg, rgba(22,50,91,.85), rgba(11,25,45,.7)); margin-bottom: 1rem;}
    .hero h1 {margin: 0; font-size: 2rem; color: #f8fafc;}
    .hero p {margin: .35rem 0 0; color: #9fb4ce;}
    .pill {display:inline-block; padding:.2rem .65rem; margin-right:.35rem; border-radius:999px;
      background:#123b5c; color:#7dd3fc; font-size:.78rem; border:1px solid #1e5d82;}
    [data-testid="stChatMessage"] {background: rgba(15, 31, 53, .72); border: 1px solid #203b5d;
      border-radius: 14px; padding: .65rem 1rem; margin-bottom: .55rem;}
    [data-testid="stMetric"] {background:rgba(15,31,53,.78); border:1px solid #203b5d;
      padding:.8rem 1rem; border-radius:14px;}
    .model-card {min-height:84px; padding:.9rem 1rem; border-radius:14px;
      background:rgba(15,31,53,.78); border:1px solid #27496f; margin-bottom:.75rem;}
    .model-card b {color:#7dd3fc;}
    .small-note {color:#8299b5; font-size:.84rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Chưa có OPENAI_API_KEY trong file .env")
    return OpenAI(
        api_key=key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
    )


def extract_text(message) -> str:
    content = message.content or ""
    if content:
        return content
    return getattr(message, "reasoning", None) or "Model chưa tạo phần trả lời cuối. Hãy thử lại."


def stream_answer(client: OpenAI, messages: list[dict], model: str, temperature: float):
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=900,
        stream=True,
    )
    produced = False
    for chunk in stream:
        text = chunk.choices[0].delta.content or ""
        if text:
            produced = True
            yield text
    if not produced:
        yield "Model chưa tạo phần trả lời cuối. Hãy thử lại hoặc giảm temperature."


def complete_once(client: OpenAI, prompt: str, model: str, persona: str, temperature: float) -> dict:
    started = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": persona},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=900,
    )
    latency = time.perf_counter() - started
    usage = response.usage
    return {
        "text": extract_text(response.choices[0].message),
        "latency": latency,
        "tokens": getattr(usage, "total_tokens", 0) if usage else 0,
    }


if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_stats" not in st.session_state:
    st.session_state.last_stats = None

with st.sidebar:
    st.markdown("## ⚡ NexLab Chat")
    page = st.radio("Chế độ", ["💬 Chat", "⚖️ So sánh model"], label_visibility="collapsed")
    st.divider()
    temperature = st.slider("Temperature", 0.0, 1.5, 0.4, 0.1)
    persona = st.text_area("System prompt", DEFAULT_PERSONA, height=145)
    if st.button("Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_stats = None
        st.rerun()
    st.caption("API key chỉ được đọc từ `.env` trên máy và không hiển thị trên giao diện.")

st.markdown(
    """
    <div class="hero">
      <span class="pill">OPENROUTER</span><span class="pill">STREAMING</span><span class="pill">FREE MODELS</span>
      <h1>NexLab Chat</h1>
      <p>Chat trực tiếp và quan sát sự khác biệt giữa Nex-N2.5-Pro với Nex-N2.5-Mini.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    client = get_client()
except RuntimeError as error:
    st.error(str(error))
    st.stop()

if page == "💬 Chat":
    selected_name = st.segmented_control("Model", list(MODELS), default="Nex-N2.5-Mini")
    selected_model = MODELS[selected_name]

    if st.session_state.last_stats:
        col1, col2, col3 = st.columns(3)
        col1.metric("Model", st.session_state.last_stats["model"])
        col2.metric("Latency", f'{st.session_state.last_stats["latency"]:.2f}s')
        col3.metric("Ký tự output", st.session_state.last_stats["chars"])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Nhập câu hỏi cho chatbot…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        api_messages = (
            [{"role": "system", "content": persona}]
            + st.session_state.messages[-7:]
        )
        with st.chat_message("assistant"):
            try:
                started = time.perf_counter()
                answer = st.write_stream(stream_answer(client, api_messages, selected_model, temperature))
                latency = time.perf_counter() - started
            except Exception as error:
                st.error(f"Không gọi được model: {error}")
                st.stop()
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.last_stats = {"model": selected_name, "latency": latency, "chars": len(answer)}
        st.rerun()

else:
    st.markdown("### Một prompt, hai model")
    prompt = st.text_area(
        "Prompt so sánh",
        "Giải thích blockchain cho một người chưa biết công nghệ, dùng một ví dụ đời thường.",
        height=100,
    )
    if st.button("Chạy so sánh", type="primary", use_container_width=True):
        results = {}
        progress = st.progress(0, text="Đang gọi Nex-N2.5-Pro…")
        for index, (name, model) in enumerate(MODELS.items(), start=1):
            try:
                results[name] = complete_once(client, prompt, model, persona, temperature)
            except Exception as error:
                results[name] = {"text": f"Lỗi: {error}", "latency": 0.0, "tokens": 0}
            progress.progress(index / len(MODELS), text=f"Đã hoàn thành {index}/{len(MODELS)} model")
        progress.empty()

        pro_col, mini_col = st.columns(2)
        for column, (name, result) in zip((pro_col, mini_col), results.items()):
            with column:
                st.markdown(f'<div class="model-card"><b>{name}</b><br><span class="small-note">{MODELS[name]}</span></div>', unsafe_allow_html=True)
                metric_a, metric_b = st.columns(2)
                metric_a.metric("Latency", f'{result["latency"]:.2f}s')
                metric_b.metric("Tổng token", result["tokens"] or "N/A")
                st.markdown(result["text"])

        if all(item["latency"] > 0 for item in results.values()):
            fastest = min(results, key=lambda name: results[name]["latency"])
            gap = abs(results["Nex-N2.5-Pro"]["latency"] - results["Nex-N2.5-Mini"]["latency"])
            st.success(f"Lần chạy này {fastest} phản hồi nhanh hơn, chênh lệch {gap:.2f} giây.")
