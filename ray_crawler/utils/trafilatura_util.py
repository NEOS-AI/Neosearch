import trafilatura


def extract_url_content(url):
    downloaded = trafilatura.fetch_url(url)
    content =  trafilatura.extract(downloaded)
    
    return {"url":url, "content":content}
