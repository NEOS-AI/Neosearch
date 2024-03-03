from neosearch.app.engine.index import get_index


def get_query_engine():
    return get_index().as_query_engine(
        similarity_top_k=3
    )
