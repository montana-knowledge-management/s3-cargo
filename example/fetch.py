from os import getenv
from botocore.exceptions import ClientError

import boto3

BUCKETNAME = getenv("S3_BUCKET")

s3 = boto3.resource("s3", endpoint_url=getenv("S3_URL"))
bucket = s3.Bucket(BUCKETNAME)

def is_key_exists(key):
    try:
        s3.Object(BUCKETNAME, key).get()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
    else:
        return True

def cleanup_bucket_folder(folder):
    for item in bucket.objects.filter(Prefix=folder):
        item.delete()
        print(item.key)

# for item in bucket.objects.all():
#     print(item.key)
obj0 = s3.Object(BUCKETNAME, "almA")
obj1 = s3.Object(BUCKETNAME, "test_project/input/f-84f5.txt")
print(is_key_exists("test_project/input/f-84f5.txt"))

cleanup_bucket_folder('test_project/project_results')
