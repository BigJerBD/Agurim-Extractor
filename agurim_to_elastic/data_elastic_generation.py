def elastic_ndjson_generator(jsons, index="agurim", doc_type="datapoint", no_id=False):
    for elastic_id, json_obj in enumerate(jsons):
        yield base_info(index, doc_type, doc_type, no_id)
        yield json_obj


def elastic_json_query_generator(jsons, index="agurim", doc_type="datapoint", no_id=False):
    for elastic_id, json_obj in enumerate(jsons):
        yield {
            **base_info(index, doc_type, elastic_id, no_id),
            "_source": json_obj
        }


def base_info(index, doc_type, elastic_id, no_id=False):
    if no_id:
        return {
            "_index": index,
            "_type": doc_type,
        }
    else:
        return {
            "_index": index,
            "_type": doc_type,
            "_id": elastic_id,
        }
