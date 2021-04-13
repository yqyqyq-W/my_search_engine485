"""REST API for index server."""
import flask
from flask import jsonify, request
import index
import pathlib
import numpy as np

# page rank structure
# {"doc_id1": factor,
#  "doc_id2": factor,
#  ...}
page_rank = {}

# inverted index structure
# {"item1": {"idf": 123,
#       "doc_id_x": [occurrence, normalization],
#       "doc_id_y": [occurrence, normalization], ...,
#       "document_match": [list of doc_ids]}
#  "item2": {"idf": 123,
#       "doc_id_x": [occurrence, normalization], "doc_id_y": [occurrence, normalization], ...,
#       "doc_id_y": [occurrence, normalization], ...,
#       "document_match": [list of doc_ids]}
# }
inverted_index = {}

stop_words = []

@index.app.before_first_request
def before_first_request():
    """Read in data."""
    index_package_dir = pathlib.Path(__file__).parent.parent
    print(index_package_dir)
    # FIX INPUT DIRECTORIES
    stopwords_filename = "stopwords.txt"
    pagerank_filename = "pagerank.out"
    inverted_index_filename = index_package_dir / "hadoop" / "inverted_index" / "inverted_index.txt"
    with open(pagerank_filename, mode='r') as page:
        line = page.readline()
        while line:
            line = line.rstrip()
            line_split = line.split(',')
            inverted_index[line_split[0]] = line_split[1]
            line = page.readline()

    with open(inverted_index_filename, mode='r') as invert:
        line = invert.readline()
        while line:
            line = line.rstrip()
            line_split = line.split(' ')
            inverted_index[line_split[0]] = {
                "idf": line_split[1]
            }
            document_match = [] # doc_ids that have this word
            for item in range(2, len(line_split), 3):
                # "doc_id": [occurrence, normalization_factor]
                inverted_index[line_split[0]][line_split[item]] = [line_split[item+1], line_split[item+2]]
                document_match.append(line_split[item])
            inverted_index[line_split[0]]["document_match"] = document_match
            line = page.readline()

    with open(stopwords_filename, mode='r') as stopwords:
        line = stopwords.readline()
        while line:
            line = line.rstrip()
            stop_words.append(line)
            line = page.readline()

@index.app.route('/api/v1/', methods=['GET'])
def first_route():
    """Handle first route."""
    context = {
        "hits": "/api/v1/hits/",
        "url": "/api/v1/"
    }
    return jsonify(**context)

@index.app.route('/api/v1/hits/', methods=['GET'])
def second_route():
    """Handle second route."""
    w = request.args.get('w')
    query = request.args.get('query')

    # Find common doc_id having all the query words
    query_list = query.split(' ')
    # Remove stopwords
    for item in query_list:
        if item in stop_words:
            query_list.remove(item)

    query_dict = {}
    for item in query_list:
        if item in query_dict:
            query_dict[item] += 1
        else:
            query_dict[item] = 1

    document_match = inverted_index[query_list[0]]
    for item in range(1, len(query_list)):
        new_match = inverted_index[query_list[item]]
        document_match = list(set(document_match) & set(new_match))
        if not len(document_match):
            break

    # Find related page rank
    page_rank_dict = {}
    for item in document_match:
        page_rank_dict[item] = page_rank[item]

    # Find inverted index idf
    idf = []
    for key in query_dict:
        idf.append(inverted_index[key]["idf"])

    # Calculate query vector and document vector for each document
    # for doc in document_match:
    #     # q: <term frequency in query> * <idf>
    #     # d: <term frequency in document> * <idf>
    #     query_vector = []
    #     document_vector = []
    #     for key in query_dict:
    #         idf_instance = idf[key]
    #         q_freq = query_dict[key]
    #         d_freq = inverted_index[key][doc]
    #         query_vector.append(q_freq * idf_instance)
    #         document_vector.append(d_freq * idf_instance)
    #
    #     # Compute dot product
    #     dot_product_qd = np.dot(query_vector, document_vector)
    #     # Compute normalization factor for query and document
    #     norm_q = 0
    #     for item in query_vector:
    #         norm_q += item * item
    #     norm_q = sqrt(norm_q)
    #
    #     norm_d = 0
    #     for item in document_vector:
    #         norm_d += item * item
    #     norm_d = sqrt(norm_d)
    #
    #     # Compute TF-IDF
    #     dot_product_norm_qd = np.dot(norm_q, norm_d)
    #     tfidf =dot_product_qd / dot_product_norm_qd
    #
    #     # Compute weighted score
    #     weighted_score = w * page_rank_dict[doc] + (1 - w) * tfidf
    #
    #     # Update context with weighted score and related doc_id
    #     context[doc] = weighted_score
    context = calculate_vector(query_dict, w, page_rank_dict, document_match, idf)

    # Sort the context dictionary by value
    sorted_context = {}
    sorted_keys = sorted(context, key=context.get)
    for w in sorted_keys:
        sorted_context[w] = context[w]

    return jsonify(**sorted_context)

def calculate_vector(query_dict, w, page_rank_dict, document_match, idf):
    """Calculate query vector and document vector for each document."""
    context = {}
    for doc in document_match:
        # q: <term frequency in query> * <idf>
        # d: <term frequency in document> * <idf>
        query_vector = []
        document_vector = []
        for key in query_dict:
            idf_instance = idf[key]
            q_freq = query_dict[key]
            d_freq = inverted_index[key][doc]
            query_vector.append(q_freq * idf_instance)
            document_vector.append(d_freq * idf_instance)

        # Compute dot product
        dot_product_qd = np.dot(query_vector, document_vector)
        # Compute normalization factor for query and document
        norm_q = 0
        for item in query_vector:
            norm_q += item * item
        norm_q = sqrt(norm_q)

        norm_d = 0
        for item in document_vector:
            norm_d += item * item
        norm_d = sqrt(norm_d)

        # Compute TF-IDF
        dot_product_norm_qd = np.dot(norm_q, norm_d)
        tfidf = dot_product_qd / dot_product_norm_qd

        # Compute weighted score
        weighted_score = w * page_rank_dict[doc] + (1 - w) * tfidf

        # Update context with weighted score and related doc_id
        context[doc] = weighted_score
    return context

