import trafilatura
from typing import Union


def extract_url_content(url, output_format: Union[str, None] = "markdown", include_tables: bool = True, deduplicate: bool = False):
    if output_format not in {"json", "xml", "markdown"}:
        output_format = None

    downloaded = trafilatura.fetch_url(url)

    # get metadata and description from the downloaded content
    metadata = trafilatura.extract_metadata(downloaded)
    description = metadata.description
    title = metadata.title

    if output_format is None:
        content =  trafilatura.extract(
            downloaded,
            include_tables=include_tables,
            deduplicate=deduplicate
        )
    else:
        content = trafilatura.extract(
            downloaded,
            deduplicate=deduplicate,
            output_format=output_format,
            include_tables=include_tables
        )

    return {
        "url":url,
        "content":content,
        "description":description,
        "title": title,
    }
