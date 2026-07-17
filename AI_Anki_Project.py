import streamlit as st
import pandas as pd
import io
from PIL import Image

# Sử dụng thư viện chính thức của Google AI
try:
    import google.generativeai as genai
except ImportError:
    st.error("Vui lòng cài đặt thư viện bằng lệnh: pip install google-generativeai")

st.set_page_config(page_title="AI Anki Card Generator", layout="wide")
st.title("🎓 AI Trích Xuất Ảnh Bài Tập & Xuất File Anki")

# Thanh bên cài đặt API và Prompt
st.sidebar.header("⚙️ Cấu hình Hệ thống Anki")
api_key = st.sidebar.text_input("Nhập Google Gemini API Key của bạn:", type="password")

user_prompt = st.sidebar.text_area(
    "Nhập Prompt cá nhân hóa của bạn:",
    value="""Nhiệm vụ của bạn là nhận ảnh bài tập (viết tay hoặc bản in) và tách chúng thành các thẻ Anki.
Hãy tìm tất cả câu hỏi và lời giải/đáp án tương ứng trong ảnh.
Nếu có công thức toán/lý/hóa, hãy chuyển nó sang định dạng LaTeX đặt trong dấu \( ... \).

Yêu cầu xuất kết quả STRICTLY dưới dạng văn bản thô, mỗi dòng là một thẻ, Mặt trước và Mặt sau cách nhau bằng duy nhất một dấu TAB (\t). Không thêm số thứ tự câu, không thêm ký tự giải thích.""",
    height=250
)

# Giao diện tải ảnh
uploaded_file = st.file_uploader("Tải lên ảnh chụp bài tập (Viết tay hoặc bản in)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(image, caption="Ảnh bài tập đầu vào", use_container_width=True)
        
    with col2:
        st.subheader("🔍 Tiến trình xử lý của AI")
        
        if st.button("🚀 Bắt đầu phân tích & Tạo file Anki"):
            if not api_key:
                st.error("⚠️ Vui lòng điền Gemini API Key ở thanh bên để chạy ứng dụng!")
            else:
                try:
                    # Cấu hình AI
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-3.5-flash')
                    
                    with st.spinner("AI đang quét bố cục ảnh và áp dụng Prompt của bạn..."):
                        # Gửi trực tiếp ảnh và Prompt của bạn cho AI xử lý bóc tách
                        response = model.generate_content([user_prompt, image])
                        anki_text_result = response.text
                        
                    st.success("✅ AI đã xử lý và cấu trúc hóa dữ liệu thành công!")
                    st.text_area("Xem trước dữ liệu dạng TAB-Separated:", value=anki_text_result, height=200)
                    
                    # Tạo bộ đệm để tải file xuống
                    txt_buffer = io.BytesIO()
                    txt_buffer.write(anki_text_result.encode('utf-8'))
                    txt_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Tải file .TXT để Import vào Anki",
                        data=txt_buffer,
                        file_name="anki_flashcards.txt",
                        mime="text/plain"
                    )
                    st.info("💡 Mẹo: Khi import file .txt này vào Anki, hãy tích chọn mục 'Fields separated by: Tab' nhé.")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi gọi AI: {e}")