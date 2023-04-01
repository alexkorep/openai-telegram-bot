import boto3
import time

TABLE_NAME = "openai_telegram_bot_chat_history"


def create_dynamodb_table_history():
    """ Create a DynamoDB table to store the history 
        Table name: chat_history
        Primary key: chat_dest
        Sort key: timestamp
        It also contains message text and a flag to indicate if it is from the user or the bot
    """
    # If table exists, do nothing
    dynamodb = boto3.resource("dynamodb")
    tables = dynamodb.meta.client.list_tables()["TableNames"]
    if TABLE_NAME in tables:
        print("DynamoDB historr table already exists")
        return

    print("Creating DynamoDB table...")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "chat_dest", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "chat_dest", "AttributeType": "N"},
            {"AttributeName": "timestamp", "AttributeType": "N"},
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    print("Wating until the table is created...")
    table.meta.client.get_waiter("table_exists").wait(TableName=TABLE_NAME)
    print("Table status:", table.table_status)


def save_history(chat_dest: str, message: str, is_user: bool):
    """ Save the message to DynamoDB """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(
        Item={
            "chat_dest": chat_dest,
            "timestamp": int(time.time()),
            "message": message,
            "is_user": is_user,
        }
    )


def get_history(chat_dest: str, nunber_of_messages: int):
    """ Get the history of the chat 
        Return the history records sorted by timestamp in descending order (newest first)
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key(
            "chat_dest").eq(chat_dest),
        ScanIndexForward=False,
        Limit=nunber_of_messages,
    )
    return response["Items"]


def clear_history(chat_dest: str):
    """ Delete all the messages for the chat """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key(
            "chat_dest").eq(chat_dest),
    )
    with table.batch_writer() as batch:
        for each in response["Items"]:
            batch.delete_item(
                Key={
                    "chat_dest": chat_dest,
                    "timestamp": each["timestamp"],
                }
            )
