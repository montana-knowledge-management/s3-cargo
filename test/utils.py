from os import getenv
from pathlib import Path

import boto3
import yaml
from botocore.exceptions import ClientError

TESTROOT = Path(__file__).parent
URL = getenv("S3_URL")
BUCKETNAME = getenv("S3_BUCKET")
PROJECTID = "test_project"
RESULTS = "project_results"

s3 = boto3.resource("s3", endpoint_url=URL)
bucket = s3.Bucket(BUCKETNAME)


def export_config(cfg):
    """
    Export the config dictionary into the cargoconf.yml file.
    """
    f = TESTROOT.joinpath("cargoconf.yml")
    f.write_text(yaml.dump(cfg))
    return f


def is_key_exists(key: str):
    """
    Check if file exists in the bucket.
    """
    try:
        s3.Object(BUCKETNAME, key).get()
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return False
    else:
        return True


def cleanup_bucket_folder(folder: str):
    """
    Delete all keys under folder.
    """
    assert "input" not in folder, "You cannot delete the input folder."
    for item in bucket.objects.filter(Prefix=f"{PROJECTID}/{folder}"):
        item.delete()
