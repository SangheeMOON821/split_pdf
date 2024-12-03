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
        output_path = f"{output_folder_path}/split_{idx + 1}.pdf"
        pdf_writer.save(output_path)
        pdf_writer.close()
        st.success(f"페이지 {start}에서 {end}까지 분할 완료: {output_path}")
        with open(output_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="split_{idx + 1}.pdf">여기에서 다운로드</a>'
            st.markdown(href, unsafe_allow_html=True)
    pdf_document.close()

# Streamlit UI
st.title("PDF 페이지 분할기 (PyMuPDF 사용)")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])
output_folder_path = "output"
os.makedirs(output_folder_path, exist_ok=True)

if uploaded_file is not None:
    page_range_input = st.text_input("페이지 범위를 입력하세요 (예: 1-3, 4-5)")
    if st.button("PDF 분할하기"):
        try:
            # 페이지 범위 파싱
            page_ranges = []
            for part in page_range_input.split(','):
                start, end = map(int, part.split('-'))
                page_ranges.append((start, end))
            
            # 업로드된 파일을 임시 파일로 저장
            input_pdf_path = os.path.join(output_folder_path, uploaded_file.name)
            with open(input_pdf_path, 'wb') as f:
                f.write(uploaded_file.read())
            
            # PDF 분할 함수 호출
            split_pdf(input_pdf_path, output_folder_path, page_ranges)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
