import requests
from io import BytesIO
from PyPDF2 import PdfReader
import orjson


def extract_pdf_from_url(url):
    response = requests.get(url)
    response.raise_for_status()

    with BytesIO(response.content) as pdf_file:
        reader = PdfReader(pdf_file)
        metadata = reader.metadata

        # 제목(title) 추출
        title = metadata.title if metadata.title else ""
        description = None

        # 본문(content) 추출
        content = ""
        for page in reader.pages:
            content += page.extract_text()

        # 메타데이터(metadata)를 딕셔너리 형태로 변환
        metadata_dict = {key[1:]: value for key, value in metadata.items()}

    metadata_dict_str = orjson.dumps(metadata_dict).decode("utf-8")

    return {
        "title": title,
        "url":url,
        "content":content,
        "description":description,
        "metadata":metadata_dict_str,
    }
