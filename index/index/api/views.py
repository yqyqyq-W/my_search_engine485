"""REST API for index server."""
import pathlib
from math import sqrt
import re
from flask import jsonify, request
import index

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
#       "doc_id_x": [occurrence, normalization],
#       "doc_id_y": [occurrence, normalization], ...,
#       "doc_id_y": [occurrence, normalization], ...,
#       "document_match": [list of doc_ids]}
# }
inverted_index = {}

stop_words = []


@index.app.before_first_request
def before_first_request():
    """Read in data."""
    index_package_dir = pathlib.Path(__file__).parent.parent
    index_dir = pathlib.Path(__file__).parent.parent
    # print(index_package_dir)
    # FIX INPUT DIRECTORIES
    stopwords_filename = index_dir / "stopwords.txt"
    pagerank_filename = index_dir / "pagerank.out"
    inverted_index_filename = index_package_dir / "inverted_index.txt"
    with open(pagerank_filename, mode='r') as page:
        line = page.readline()
        while line:
            line = line.rstrip()
            line_split = line.split(',')
            page_rank[line_split[0]] = line_split[1]
            line = page.readline()

    with open(inverted_index_filename, mode='r') as invert:
        line = invert.readline()
        while line:
            line = line.rstrip()
            line_split = line.split(' ')
            inverted_index[line_split[0]] = {
                "idf": line_split[1]
            }
            document_match = []  # doc_ids that have this word
            for item in range(2, len(line_split), 3):
                # "doc_id": [occurrence, normalization_factor]
                inverted_index[line_split[0]][line_split[item]] \
                    = [line_split[item+1], line_split[item+2]]
                document_match.append(line_split[item])
            inverted_index[line_split[0]]["document_match"] = document_match
            line = invert.readline()

    with open(stopwords_filename, mode='r') as stopwords:
        line = stopwords.readline()
        while line:
            line = line.rstrip()
            stop_words.append(line)
            line = stopwords.readline()


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
    weight = request.args.get('w')
    query = request.args.get('q')
    query = re.sub(r'[^a-zA-Z0-9 ]+', '', query)

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
    print(query_list)

    result = check_empty(query_list[0], inverted_index)
    print(result)
    if result:
        return jsonify(**result)

    document_match = inverted_index[query_list[0]]['document_match']

    for item in range(1, len(query_list)):
        # check if the key exists in the inverted index dictionary
        # if not, return an 'empty' json object
        new_result = check_empty(query_list[item], inverted_index)
        if new_result:
            return new_result

        new_match = inverted_index[query_list[item]]['document_match']
        document_match = list(set(document_match) & set(new_match))

        # handle results if document match is empty
        if not document_match:
            empty_context = {
                "hits": []
            }
            return jsonify(**empty_context)

    # print(document_match)
    # Find related page rank
    page_rank_dict = {}
    for item in document_match:
        page_rank_dict[item] = page_rank[item]

    # Find inverted index idf
    idf = []
    for key in query_dict:
        idf.append(inverted_index[key]["idf"])

    context = calculate_vector(query_dict, weight,
                               page_rank_dict, document_match, idf)

    # Sort the context dictionary by value
    sorted_context = {}
    sorted_keys = sorted(context, key=context.get, reverse=True)
    for weight in sorted_keys:
        sorted_context[weight] = context[weight]

    final_context = {
        "hits": []
    }
    for key in sorted_context:
        instance_dict = {"docid": int(key),
                         "score": float(sorted_context[key])}
        final_context["hits"].append(instance_dict)

    # print(final_context)
    return jsonify(**final_context)


def dot(variable1, variable2):
    """Calculate dot product."""
    return sum(float(x) * float(y) for x, y in zip(variable1, variable2))


def check_empty(key, word_dict):
    """Check empty."""
    if key not in word_dict:
        empty_context = {
            "hits": []
        }
        return empty_context
    else:
        return 0


def calculate_vector(query_dict, weight, page_rank_dict, document_match, idf):
    """Calculate query vector and document vector for each document."""
    context = {}
    # print(inverted_index[key])
    for doc in document_match:
        # q: <term frequency in query> * <idf>
        # d: <term frequency in document> * <idf>
        query_vector = []
        document_vector = []
        # print(query_dict)
        counter = 0
        for key in query_dict:
            idf_instance = idf[counter]
            counter += 1
            q_freq = query_dict[key]
            d_freq = inverted_index[key][doc][0]
            query_vector.append(int(q_freq) * float(idf_instance))
            document_vector.append(int(d_freq) * float(idf_instance))

        # Compute dot product
        dot_product_qd = dot(query_vector, document_vector)
        # Compute normalization factor for query and document
        norm_d = 0
        norm_q = 0

        for item in query_vector:
            norm_q += float(item) * float(item)

        norm_q = sqrt(norm_q)

        for key in query_dict:
            norm_d = float(inverted_index[key][doc][1])
            break

        norm_d = sqrt(norm_d)

        # Compute TF-IDF
        dot_product_norm_qd = norm_q * norm_d
        tfidf = dot_product_qd / dot_product_norm_qd

        # Compute weighted score
        weighted_score = \
            float(weight) * float(page_rank_dict[doc]) + \
            (1 - float(weight)) * float(tfidf)

        # Update context with weighted score and related doc_id
        context[doc] = weighted_score
    return context
