import json
import logging
from elasticsearch import Elasticsearch, RequestsHttpConnection
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # TODO implement
    logger.info(event)
    bucket = event['Records'][0]['s3']['bucket']['name'] #'ccbdha2b2' #
    photo_name = event['Records'][0]['s3']['object']['key'] #'turtle.jpg' #
    S3client = boto3.client('s3')
    headobj = S3client.head_object(Bucket=bucket, Key=photo_name)['Metadata']
    logger.info(headobj)
    # This is not the same as the last modified time. Is this Okay?
    photo_time = event["Records"][0]["eventTime"].split('.')[0]

    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': photo_name,
            }
        },
        MaxLabels= 8
    )
    
    logger.info(response)

    labels = []
    
    for x in response["Labels"]:
        if x["Name"] not in labels and x["Confidence"] > 70:
            labels.append(x["Name"])
            
    if (headobj != {} and headobj['customlabels'] != ''):
        for x in headobj['customlabels'].split(','):
            x = x.strip()
            if x not in labels:
                labels.append(x)

    record = {}
    record["objectKey"] = photo_name
    record["bucket"] = bucket
    record["createdTimestamp"] = photo_time
    record["labels"] = labels
    logger.info(record)
    eSearch = Elasticsearch(
        hosts = [{"host": 'search-photos-rn3vmvbdfccjc6khiqx33tnnui.us-east-1.es.amazonaws.com', "port": 443}],
        http_auth = ('sw3525', 'CSe6999!'),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    res = eSearch.index(index="photos", doc_type="image", body=record)
    logger.info(res)
    
    # return {
    #   'statusCode': 200,
    #   'body': json.dumps('Hello from Lambda!')
    # }

