import boto3

dynamodb = boto3.resource('dynamodb')

try:
    table = dynamodb.create_table(
        TableName='Test',
        KeySchema=[
            {
                'AttributeName': 'k',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'v',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'k',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'v',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
except Exception:
    table = dynamodb.Table('Test')

response = table.put_item(
    Item={
        'k': '111',
        'v': '1232132',
    }
)

print(response)
