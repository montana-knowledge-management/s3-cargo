from os import getenv

import boto3

s3 = boto3.resource("s3", endpoint_url=getenv("S3_URL"))
bucket = s3.Bucket(getenv("S3_BUCKET"))


for item in bucket.objects.all():
    print(item.key)
