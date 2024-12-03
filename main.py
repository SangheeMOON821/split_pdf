import fitz  # PyMuPDF 사용
import streamlit as st
import os
import base64

def split_pdf(input_pdf_path, output_folder_path, page_ranges):
    """
    PDF 파일을 원하는 페이지 범위대로 나눕니다 (PyMuPDF 사용).

    Args:
        input_pdf_path (str): 분할할 PDF 파일 경로
        output_folder_path (str): 분할된 PDF를 저장할 폴더 경로
        page_ranges (list of tuples): 분할할 페이지 범위 (예: [(1, 3), (4, 5)])
    """
    pdf_document = fitz.open(input_pdf_path)
    for idx, (start, end) in enumerate(page_ranges):
        pdf_writer = fitz.open()
        # PDF 페이지는 0부터 시작합니다.
        for page_num in range(start - 1, end):
            pdf_writer.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
        base_filename = os.path.splitext(os.path.basename(input_pdf_path))[0]
        output_filename = f"{base_filename}_{start}-{end}페이지.pdf"
        output_path = os.path.join(output_folder_path, output_filename)
        pdf_writer.save(output_path)
        pdf_writer.close()
        st.success(f"페이지 {start}에서 {end}까지 분할 완료: {output_path}")
        with open(output_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{output_filename}" style="display:inline-block; padding:10px 20px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px;">다운로드</a>'
            st.markdown(href, unsafe_allow_html=True)
    pdf_document.close()

# Streamlit UI
st.title("PDF 페이지 분할기 by 🌟석리송🌟")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])
output_folder_path = "output"
os.makedirs(output_folder_path, exist_ok=True)

if uploaded_file is not None:
    input_pdf_path = os.path.join(output_folder_path, uploaded_file.name)
    with open(input_pdf_path, 'wb') as f:
        f.write(uploaded_file.read())
    
    # PDF 열어서 전체 페이지 수 확인
    pdf_document = fitz.open(input_pdf_path)
    total_pages = pdf_document.page_count
    pdf_document.close()
    
    st.write(f"전체 페이지 수: {total_pages}")
    
    # 페이지 범위 입력 방식과 슬라이더 방식 모두 지원
    default_page_range = "1-1"  # 기본 페이지 범위 설정
    page_range_input = st.text_input("페이지 범위를 입력하세요 (예: 1-3, 4-5)", value=default_page_range)
    page_range_slider = st.slider("페이지 범위 선택", 1, total_pages, (1, total_pages))
    
    if st.button("PDF 분할하기"):
        try:
            # 입력된 페이지 범위와 슬라이더로 선택된 범위 병합
            page_ranges = []
            if page_range_input:
                for part in page_range_input.split(','):
                    start, end = map(int, part.split('-'))
                    page_ranges.append((start, end))
            page_ranges.append((page_range_slider[0], page_range_slider[1]))
            
            # PDF 분할 함수 호출
            split_pdf(input_pdf_path, output_folder_path, page_ranges)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# requirements.txt 파일 생성
requirements = """
streamlit
pymupdf
"""
with open('requirements.txt', 'w') as f:
    f.write(requirements)
