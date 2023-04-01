import boto3

TABLE_NAME = "openai_telegram_bot_prompt"

def create_dynamodb_table_prompt():
    """ Create a DynamoDB table to store the prompt for this chat
        Table name: openai_telegram_bot_prompt
        Primary key: chat_dest
    """
    # If table exists, do nothing
    dynamodb = boto3.resource("dynamodb")
    tables = dynamodb.meta.client.list_tables()["TableNames"]
    if TABLE_NAME in tables:
        print("DynamoDB prompt table already exists", TABLE_NAME)
        return
    
    print("Creating DynamoDB table...")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "chat_dest", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            
            {"AttributeName": "chat_dest", "AttributeType": "N"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    print("Wating until the table is created...")
    table.meta.client.get_waiter("table_exists").wait(TableName=TABLE_NAME)
    print("Table status:", table.table_status)


def save_prompt(chat_dest: str, prompt: str):
    """ Save the prompt to DynamoDB """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(
        Item={
            "chat_dest": chat_dest,
            "prompt": prompt,
        }
    )


def get_prompt(chat_dest: str) -> str:
    """ Get the prompt for the chat 
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(
        Key={
            "chat_dest": chat_dest,
        }
    )
    if "Item" in response:
        return response["Item"]["prompt"]
    else:
        return ""
