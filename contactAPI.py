
# This lambda function support various methods to support CRUD operation for Contact/AddressBook
# contact detail include phone, firstName, lastName, email, notes
# This function is best used in integration with Rest API via AWS API Gateway
# to use this code, deploy a lambda function and create API end points as below: 
# /contact /allContacts /createContact /updateContact /deleteContact
# version 1.0
# created date 10/8/2023
# created by: Girish Bhatia


import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# setup http method and path vaariables

getMethod = 'GET'
postMethod = 'POST'
putMethod = 'PUT'
deleteMethod = 'DELETE'
createPath = '/createContact'
allContactsPath = '/allContacts'
contactPath = '/contact'
updatePath = '/updateContact'
deletePath = '/deleteContact'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    try:
        contactTable = dynamodb.Table('contacts')
        logger.info("Connected to database")
    except Exception as e:
        logger.error("error in connecting to database" + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error in connecting to database')
        }

# create a new contact
    if httpMethod == postMethod and event['path'] == createPath:
        logger.info("Adding new contact")
        contactItem = json.loads(event['body'])
        logger.info("Contact received: " + str(contactItem))
        # invoke createContact function to create a new contact
        return createContact(contactTable, contactItem)
#  get all contacts
    elif httpMethod == getMethod and event['path'] == allContactsPath:
        logger.info("Getting all contacts")
        # invoke getAllContacts function to get all contacts
        return getAllContacts(contactTable)
#  get a contact
    elif httpMethod == getMethod and event['path'] == contactPath:
        logger.info("Getting contact")
        # invoke getContact function to get a contact
        return getContact(contactTable, event['queryStringParameters']['phone'])
#   update a contact    
    elif httpMethod == putMethod and event['path'] == updatePath:
        logger.info("Updating contact")
        # invoke updateContact function to update a contact
        contactItem = json.loads(event['body'])
        logger.info("Contact received: " + str(contactItem))
        return updateContact(contactTable, event['queryStringParameters']['phone'], contactItem)
#   delete a contact
    elif httpMethod == deleteMethod and event['path'] == deletePath:
        logger.info("Deleting contact")
        # invoke deleteContact function to delete a contact
        return deleteContact(contactTable, event['queryStringParameters']['phone'])

    else:
        return buildResponse(404, 'Not Found')

# function to create a new contact
def createContact(contactTable, contactItem):
    try:
        phone = contactItem['phone']
        contactTable.put_item(
            Item=contactItem,
            ConditionExpression='attribute_not_exists(phone)'
        )
        logger.info("Contact added successfully!")
    except Exception as e:
        logger.error("error in adding new contact" + str(e))
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return buildResponse(409, 'Error: Contact already exists!')
        return buildResponse(500, 'Error in adding new contact')
    return buildResponse(200, 'Contact added successfully!')

# function get all contacts
def getAllContacts(contactTable):
    try:
        response = contactTable.scan()
        logger.info("All contacts retrieved successfully!")
    except Exception as e:
        logger.error("error in retrieving all contacts" + str(e))
        return buildResponse(500, 'Error in retrieving all contacts')
    return buildResponse(200, response['Items'])

# function to get a contact based on phone number
def getContact(contactTable, phone):
    try:
        response = contactTable.get_item(
            Key={
                'phone': phone
            }
        )
        if 'Item' not in response:
            return buildResponse(404, 'Contact not found')
        logger.info("Contact retrieved successfully!")
    except Exception as e:
        logger.error("error in retrieving contact" + str(e))
        return buildResponse(500, 'Error in retrieving contact')
    return buildResponse(200, response['Item'])

# funtion to update a contact based on a phone number
def updateContact(contactTable,phone,contactItem):
    try:
        contactTable.update_item(
            Key={
                'phone': phone
            },
            UpdateExpression="set firstName=:fn, lastName=:ln, email=:em, notes=:no",
            ExpressionAttributeValues={
                ':fn': contactItem['firstName'],
                ':ln': contactItem['lastName'],
                ':em': contactItem['email'],
                ':no': contactItem['notes']
            },
            ConditionExpression="attribute_exists(phone)",
            ReturnValues="UPDATED_NEW"
        )
        logger.info("Contact updated successfully!")
    except Exception as e:
        logger.error("error in updating contact" + str(e))
        if 'ConditionalCheckFailedException' in str(e):
            return buildResponse(409, 'Error:Contact not found')
        return buildResponse(500, 'Error in updating contact')
    return buildResponse(200, 'Contact updated successfully!')

# function to delete a contact based on a phone number
def deleteContact(contactTable,phone):
    response = getContact(contactTable, phone)
    if response['statusCode'] != 200:
        return buildResponse(404, 'Contact not found')
    try:
        contactTable.delete_item(
            Key={
                'phone': phone
            }
        )
        logger.info("Contact deleted successfully!")
    except Exception as e:
        logger.error("error in deleting contact" + str(e))
        return buildResponse(500, 'Error in deleting contact')
    return buildResponse(200, 'Contact deleted successfully!')


# function to build responde based on status code and message
def buildResponse(statusCode, message):
    return {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
        },
        'body': json.dumps(message)
    }
