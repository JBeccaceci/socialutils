import os
import time
import boto3

dynamodb = boto3.client("dynamodb")

table_name = os.getenv("DYNAMODB_CREDENTIALS_TABLE", "MetaCredentials")


def get_short_lived_access_token():
    """
    Get short-lived access token from DynamoDB table

    Returns:
        str: Short-lived access token
    """
    response = dynamodb.get_item(
        TableName=table_name, Key={"id": {"S": "fb_access_token"}}
    )

    if "Item" in response:
        token = response["Item"]["token"]["S"]
        return token

    return None


def get_or_generate_long_lived_access_token(generate_access_token):
    """
    Get long-lived access token from DynamoDB table.
    If it doesn't exist, retrieve a short-lived access token and storage it in DynamoDB

    Returns:
        str: Long-lived access token
    """
    long_lived_access_token = get_long_lived_access_token()

    if long_lived_access_token is None:
        try:
            token = get_short_lived_access_token()
            long_lived_access_token = generate_access_token(token)
            save_long_lived_acces_token(long_lived_access_token)
        except Exception:
            raise

    return long_lived_access_token


def save_long_lived_acces_token(access_token: str):
    """
    Save meta long-lived access token in DynamoDB credentials table

    Args:
        access_token (str): Meta long-lived access token

    Returns:
        str: Provided access token
    """
    expiration_time = int(time.time()) + (60 * 24 * 60 * 60)

    dynamodb.put_item(
        TableName=table_name,
        Item={
            "id": {"S": "meta_access_token"},
            "token": {"S": access_token},
            "expiration": {"N": str(expiration_time)},
        },
    )

    return access_token


def get_long_lived_access_token():
    """
    Get long-lived access token from DynamoDB table

    Returns:
        str: Long-lived access token
    """
    response = dynamodb.get_item(
        TableName=table_name, Key={"id": {"S": "meta_access_token"}}
    )

    if "Item" in response:
        token = response["Item"]["token"]["S"]
        expiration = int(response["Item"]["expiration"]["N"])
        current_time = int(time.time())

        if current_time < expiration:
            return token

    return None
