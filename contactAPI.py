
# This lambda function support various methods to support CRUD operation for Contact/AddressBook
# contact detail include phone, firstName, lastName, email, notes
# This function is best used in integration with Rest API via AWS API Gateway
# to use this code, deploy a lambda function and create API end points as below: 
# /contact /allContacts /createContact /updateContact /deleteContact
# version 1.1
# created date 10/8/2023
# created by: Girish Bhatia


import boto3
import json
import logging


# create a logger

logger = logging.getLogger()
logger.setLevel(logging.INFO)


dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
contactTable = dynamodb.Table('contacts')
logger.info("Connected to database")


# setup http method and path vaariables
# setup http method and path variables to support GET, POST, PUT, DELETE Method
# path variables to support createContact, getAllContacts, getContact, updateContact, deleteContact API endpoints

GET_METHOD = 'GET'
POST_METHOD = 'POST'
PUT_METHOD = 'PUT'
DELETE_METHOD = 'DELETE'

CREATE_PATH = '/createContact'
ALL_CONTACTS_PATH = '/allContacts'
CONTACT_PATH = '/contact'
UPDATE_PATH = '/updateContact'
DELETE_PATH = '/deleteContact'

# this is the main lambda function
# this function will invoke various sub function depending on the http method and path variable
# this function can also be break into multiple independent lambda functions.

def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']

# create a new contact
# this function will invoke createContact function to create a new contact
    if httpMethod == POST_METHOD and path == CREATE_PATH:
        logger.info("Adding new contact")
        contactItem = json.loads(event['body'])
        logger.info(f"Contact received:{contactItem}")
        # invoke createContact function to create a new contact
        return createContact(contactTable, contactItem)
#  get all contacts
# this function will invoke getAllContacts function to get all contacts
    elif httpMethod == GET_METHOD and path == ALL_CONTACTS_PATH:
        logger.info("Getting all contacts")
        # invoke getAllContacts function to get all contacts
        return getAllContacts(contactTable)
#  get a contact
# this function will invoke getContact function to get a contact
    elif httpMethod == GET_METHOD and path == CONTACT_PATH:
        logger.info("Getting contact")
        # invoke getContact function to get a contact
        return getContact(contactTable, event['queryStringParameters']['phone'])
#   update a contact 
# this function will invoke updateContact function to update a contact   
    elif httpMethod == PUT_METHOD and path == UPDATE_PATH:
        logger.info("Updating contact")
        # invoke updateContact function to update a contact
        contactItem = json.loads(event['body'])
        logger.info(f"Contact received:{contactItem}")
        return updateContact(contactTable, event['queryStringParameters']['phone'], contactItem)
#   delete a contact
# this function will invoke deleteContact function to delete a contact
    elif httpMethod == DELETE_METHOD and path == DELETE_PATH:
        logger.info("Deleting contact")
        # invoke deleteContact function to delete a contact
        return deleteContact(contactTable, event['queryStringParameters']['phone'])

    else:
        return buildResponse(404, 'Not Found')

# function to create a new contact
# this function will add a new contact to the database
def createContact(contactTable, contactItem):
    try:
        phone = contactItem['phone']
        contactTable.put_item(
            Item=contactItem,
            ConditionExpression='attribute_not_exists(phone)'
        )
        logger.info("Contact added successfully!")
    except Exception as e:
        logger.error(f"error in adding new contact{e}")
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return buildResponse(409, 'Error: Contact already exists!')
        return buildResponse(500, 'Error in adding new contact')
    return buildResponse(200, 'Contact added successfully!')

# function get all contacts
# this function will get all contacts from the database
def getAllContacts(contactTable):
    try:
        response = contactTable.scan()
        logger.info("All contacts retrieved successfully!")
    except Exception as e:
        logger.error(f"error in retrieving all contacts{e}")
        return buildResponse(500, 'Error in retrieving all contacts')
    return buildResponse(200, response['Items'])

# function to get a contact based on phone number
# this function will get a contact from the database based on phone number
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
        logger.error(f"error in retrieving contact{e}")
        return buildResponse(500, 'Error in retrieving contact')
    return buildResponse(200, response['Item'])

# funtion to update a contact based on a phone number
# this function will update a contact in the database based on phone number
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
        logger.error(f"error in updating contact{e}")
        if 'ConditionalCheckFailedException' in str(e):
            return buildResponse(409, 'Error:Contact not found')
        return buildResponse(500, 'Error in updating contact')
    return buildResponse(200, 'Contact updated successfully!')

# function to delete a contact based on a phone number
# this function will delete a contact from the database based on phone number
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
        logger.error(f"error in deleting contact{e}")
        return buildResponse(500, 'Error in deleting contact')
    return buildResponse(200, 'Contact deleted successfully!')


# function to build responde based on status code and message
# this function will build a response based on status code and message
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
