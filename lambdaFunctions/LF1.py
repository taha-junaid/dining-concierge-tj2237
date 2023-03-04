import json
import random
import decimal 
import boto3

sqs = boto3.client('sqs')
queue_url = '<qs_endpoint'

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']
    
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None    

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }  

def DiningSuggestion(intent_request):
    session_attributes = get_session_attributes(intent_request)
    location = get_slot(intent_request, 'location')
    cuisine = get_slot(intent_request, 'cuisine')
    diningTime = get_slot(intent_request, 'diningTime')
    peopleCount =get_slot(intent_request, 'noOfpeople')
    phone = get_slot(intent_request, 'phone')

    # Create a dictionary object from the slot values
    data = {
        'location': location,
        'cuisine': cuisine,
        'diningTime': diningTime,
        'peopleCount': peopleCount,
        'phone': phone
    }

    # Convert the dictionary object to a JSON string
    message_body = json.dumps(data)
    
    # log request in dynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('user-last-request')
    item={'phone':phone, 'requestDetails': message_body}
    table.put_item(Item=item)
    
    # Send the message to the SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )

    text = "Your Response has been recorded. ConfirmationId: "+response['MessageId']+", you will recieve an SMS on "+phone+" with the suggestion."
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(intent_request, session_attributes, fulfillment_state, message)

def UserHistory(intent_request):
    session_attributes = get_session_attributes(intent_request)
    phone = get_slot(intent_request, 'phone')  
    
    # get request details by phone
    dynamodb = boto3.client('dynamodb')
    userlastRequest = dynamodb.get_item(
        TableName='user-last-request',
        Key={
            'phone': {'S': phone}
        }
    )
    if 'Item' in userlastRequest:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=userlastRequest['Item']['requestDetails']['S']
        )
        
        text = "Thanks for confirming!, you will recieve an SMS on "+phone+" with the suggestion based on our last conversation. ConfirmationId: "+response['MessageId']
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "Fulfilled"
        return close(intent_request, session_attributes, fulfillment_state, message)
    else:
        text = "No previous conversation found for "+phone
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "Failed" 
        return close(intent_request, session_attributes, fulfillment_state, message)
    
def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return DiningSuggestion(intent_request)
    elif intent_name == 'userHistory':
        return UserHistory(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')
    
def lambda_handler(event, context):
    response = dispatch(event)
    return response
