import fitz  # PyMuPDF 사용
import streamlit as st
import os
import base64
import zipfile

def split_pdf_into_n_parts(input_pdf_path, output_folder_path, page_ranges):
    """
    PDF 파일을 지정된 범위대로 나눕니다 (PyMuPDF 사용).

    Args:
        input_pdf_path (str): 분할할 PDF 파일 경로
        output_folder_path (str): 분할된 PDF를 저장할 폴더 경로
        page_ranges (list of tuples): 분할할 페이지 범위 목록

    Returns:
        list: 생성된 PDF 파일 경로 목록
    """
    pdf_document = fitz.open(input_pdf_path)
    output_files = []
    
    for idx, (start, end) in enumerate(page_ranges):
        if start <= end:  # 유효한 페이지 범위인지 확인
            pdf_writer = fitz.open()
            for page_num in range(start - 1, end):
                pdf_writer.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            base_filename = os.path.splitext(os.path.basename(input_pdf_path))[0]
            output_filename = f"{base_filename}_{start}-{end}페이지.pdf"
            output_path = os.path.join(output_folder_path, output_filename)
            pdf_writer.save(output_path)
            pdf_writer.close()
            output_files.append(output_path)
    pdf_document.close()
    
    return output_files

def create_zip_file(file_paths, output_zip_path):
    """
    여러 파일을 ZIP으로 묶습니다.

    Args:
        file_paths (list): ZIP에 포함할 파일 경로 목록
        output_zip_path (str): 생성할 ZIP 파일 경로
    """
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.basename(file_path))

# Streamlit 앱
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=["pdf"])
output_folder_path = "output"
os.makedirs(output_folder_path, exist_ok=True)

if uploaded_file is not None:
    input_pdf_path = os.path.join(output_folder_path, uploaded_file.name)
    with open(input_pdf_path, 'wb') as f:
        f.write(uploaded_file.read())
    
    pdf_document = fitz.open(input_pdf_path)
    total_pages = pdf_document.page_count
    pdf_document.close()
    
    st.write(f"전체 페이지 수: {total_pages}")
    
    # 기본 페이지 분할 범위 계산
    n_parts = st.number_input("몇 개로 분할하시겠습니까?", min_value=1, max_value=total_pages, value=2, step=1)
    base_pages = total_pages // n_parts
    remainder = total_pages % n_parts
    page_ranges = []
    start_page = 1
    for i in range(n_parts):
        end_page = start_page + base_pages - 1
        if remainder > 0:
            end_page += 1
            remainder -= 1
        page_ranges.append((start_page, end_page))
        start_page = end_page + 1
    
    user_input = st.text_input(
        "페이지 범위를 입력하세요 (예: 1-5, 6-10). 입력하지 않으면 기본값이 사용됩니다.",
        value=", ".join([f"{start}-{end}" for start, end in page_ranges])
    )
    
    if user_input:
        try:
            page_ranges = [
                tuple(map(int, item.split('-')))
                for item in user_input.replace(' ', '').split(',')
                if '-' in item
            ]
            valid = all(1 <= start <= end <= total_pages for start, end in page_ranges)
            if not valid:
                st.error("입력된 범위가 유효하지 않습니다. 다시 확인해주세요.")
                page_ranges = []
        except Exception:
            st.error("입력 형식이 잘못되었습니다. 예: 1-5, 6-10")
            page_ranges = []
    
    if st.button("PDF 분할하기"):
        try:
            with st.spinner("PDF를 분할하고 있습니다. 잠시만 기다려주세요..."):
                output_files = split_pdf_into_n_parts(input_pdf_path, output_folder_path, page_ranges)
                st.success("PDF 분할 완료!")
                
                # 개별 다운로드 링크 생성
                for output_file in output_files:
                    with open(output_file, 'rb') as f:
                        b64 = base64.b64encode(f.read()).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(output_file)}" style="display:inline-block; padding:10px 20px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px;">{os.path.basename(output_file)} 다운로드</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                # ZIP 파일 생성 및 다운로드 링크 제공
                zip_file_path = os.path.join(output_folder_path, "분할된_PDF_파일.zip")
                create_zip_file(output_files, zip_file_path)
                
                with open(zip_file_path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="분할된_PDF_파일.zip" style="display:inline-block; padding:10px 20px; background-color:#2196F3; color:white; text-decoration:none; border-radius:5px;">전체 파일 ZIP 다운로드</a>'
                    st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
