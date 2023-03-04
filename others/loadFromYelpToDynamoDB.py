import boto3
import json
import requests 
import time
from decimal import Decimal

# Set up the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('yelp-restaurants')

# Define the Yelp API endpoint and parameters
url = "https://api.yelp.com/v3/businesses/search?location=manhattan%2C%20new%20york&term=italian%20restaurants&attributes=&sort_by=best_match&limit=50"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer <token>"
}

def lambda_handler(event, context):
    # Make a request to the Yelp API

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    # Extract the relevant data and insert it into DynamoDB
    for business in data['businesses']:
        item = {
            'cuisine': 'italian',
            'Business ID': business['id'],
            'Name': business['name'],
            'Address': ', '.join(business['location']['display_address']),
            'Coordinates': f"{Decimal(str(business['coordinates']['latitude']))}, {Decimal(str(business['coordinates']['longitude']))}",
            'Number of Reviews': business['review_count'],
            'Rating': Decimal(str(business['rating'])),
            'Zip Code': business['location']['zip_code'],
            'insertedAtTimestamp': str(int(time.time()))
        }
        table.put_item(Item=item)
        
        
    response_text='Inserted '+str(len(data['businesses']))+' records.'
    return {'status':200,'response':response_text}



