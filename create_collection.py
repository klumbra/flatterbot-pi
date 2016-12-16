import boto3

client = boto3.client('rekognition')

res = client.create_collection(CollectionId='flatterees')
