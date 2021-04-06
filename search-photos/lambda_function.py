import json
import logging
from elasticsearch import Elasticsearch, RequestsHttpConnection
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    text = event["queryStringParameters"]['q'].strip("\"")
    logger.info(text)
    client = boto3.client('lex-runtime')

    lex_response = client.post_text(
        botName='PhotoBot',
        botAlias='photochatbot',
        userId="3328",
        inputText=text
    )

    logger.info(lex_response["slots"])
    if lex_response["slots"]['slotone'] != None:
        queryValue = lex_response["slots"]["slotone"]
        if lex_response["slots"]['slottwo'] != None:
            queryValue += ' ' + lex_response["slots"]['slottwo']
    else: 
        return {
            'statusCode': 200,
            'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
            'body': json.dumps([])
        }
    body = {
         "query": {
            "match":{
                "labels": {
                    "query": queryValue,
                    "operator": "and"
                }
            }
        }
    }
    eSearch = Elasticsearch(
        hosts = [{"host": 'search-photos-rn3vmvbdfccjc6khiqx33tnnui.us-east-1.es.amazonaws.com', "port": 443}],
        http_auth = ('sw3525', 'CSe6999!'),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    res = eSearch.search(body, index="photos", doc_type="image")
    logger.info(res)
    res = res['hits']['hits']
    photolist = []
    for esResult in res:
        filename = esResult['_source']['objectKey']
        if filename not in photolist:
            photolist.append(filename)
    
        
    # TODO implement
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(photolist)
    }

