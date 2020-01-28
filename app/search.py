"""
Search functions.
"""
# flask extensions
from flask import current_app

def add_to_index(index, model):
    """

    Params
        index (str)
            name of index as string where index is the database Model that has an index in elasticsearch
        model (obj)
            the object in the index that represents the row or record in the index to be added.

    """
    if not current_app.elasticsearch:
        return None
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)

def remove_from_index(index, model):
    """
    
    Params
        index (str)
            name of index as string where index is the database Model that has an index in elasticsearch
        model (obj)
            the object in the index that represents the row or record in the index to be added.
    """
    if not current_app.elasticsearch:
        return None
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    """
    Returns search results.

    Params
        index (str)
            name of index to query
        query (str)
            query string. Note: 'from' and 'size' keys in body arg of .search() define the subset of the entire result set to be returned.
        page (int)
            page number to return from the set of search result pages
        per_page (int)
            count of hits per page
    
    Returns
        ids (list) -- list of ids of hits
        hits (int) -- count of hits
    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page,
              'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    hits_count = search['hits']['total']
    return ids, hits_count