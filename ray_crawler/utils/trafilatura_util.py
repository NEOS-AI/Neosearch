import trafilatura
from typing import Union


def extract_url_content(url, output_format: Union[str, None] = "markdown"):
    if output_format not in {"json", "xml", "markdown"}:
        output_format = None

    downloaded = trafilatura.fetch_url(url)

    if output_format is None:
        content =  trafilatura.extract(downloaded)
    else:
        content = trafilatura.extract(downloaded, output_format=output_format)
    return {"url":url, "content":content}
