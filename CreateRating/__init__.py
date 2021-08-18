import os
import logging
import requests
import uuid
import json
import pymongo
from datetime import datetime

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    id = str(uuid.uuid4())
    time_stamp = datetime.utcnow().strftime('%Y-%m-%d %XZ')

    try:
        req_body = req.get_json()
    except:
        return func.HttpResponse(
             "No BODY was passed to this function.",
             status_code=400
        )

    user_id = req_body.get('userId')
    query_params = { "userId": user_id }
    valid_user_id = requests.get('https://serverlessohapi.azurewebsites.net/api/GetUser', params = query_params)

    if valid_user_id.status_code != 200:
        return func.HttpResponse(
             "The field userId is missing or invalid.",
             status_code=404
        )

    product_id = req_body.get('productId')
    query_params = { "productId": product_id }
    valid_product_id = requests.get('https://serverlessohapi.azurewebsites.net/api/GetProduct', params = query_params)

    if valid_product_id.status_code != 200:
        return func.HttpResponse(
             "The field productId is missing or invalid.",
             status_code=404
        )

    location_name = req_body.get('locationName')

    if location_name == None or len(location_name) <= 0:
        return func.HttpResponse(
             "The field locationName is missing or invalid or empty.",
             status_code=404
        )

    rating = req_body.get('rating')

    if rating == None:
        return func.HttpResponse(
             "The field rating is missing or invalid.",
             status_code=404
        )
    
    if(rating > 5 or rating < 0):
        return func.HttpResponse(
             "The field rating must be between 0 and 5.",
             status_code=404
        )

    user_notes = req_body.get('userNotes')

    if user_notes == None or len(user_notes) <= 0:
        return func.HttpResponse(
             "The field userNotes is missing or invalid or empty.",
             status_code=404
        )

    response_body = {
        "id": id,
        "userId": user_id,
        "productId": product_id,
        "timestamp": time_stamp,
        "locationName": location_name,
        "rating": rating,
        "userNotes": user_notes
    }

    mongo_client = pymongo.MongoClient(os.environ["MONGO_DB_CONN_STR"])
    mydb = mongo_client["openhack"]
    mycol = mydb["ratings"]
    mycol.insert_one(response_body)

    del response_body["_id"]

    if (not user_id or not product_id):
        return func.HttpResponse(f"Request body missing userId or productId")
    else:
        return func.HttpResponse(
            #  "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            json.dumps(response_body),
             status_code=200,
             mimetype="application/json"
        )
