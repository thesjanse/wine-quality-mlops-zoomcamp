import io
import os
import pickle
from zipfile import ZipFile

import boto3
import pandas as pd
import requests


URL = "https://archive.ics.uci.edu/static/public/186/wine+quality.zip"
FILENAME = "winequality-red.csv"
S3_ENDPOINT = os.getenv("MLFLOW_S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def read_data(url, filename: str) -> pd.DataFrame:
    """Download zip file with wine data, extract file to DataFrame.
    Keyword Arguments:
        url: url of the zip file.
        filename: name of the file within zip file.

    Returns:
        A dataframe object with wine data."""
    response = requests.get(url, timeout=5)
    if response.ok is True:
        zip_file = ZipFile(io.BytesIO(response.content))
        data = pd.read_csv(zip_file.open(name=filename), header=0, delimiter=";")
    else:
        raise ValueError("Response was not successful!")
    return data


def save_to_s3(bucket_name, filename: str, dataframe: pd.DataFrame) -> None:
    """Save dataframe as pickle to s3 minio bucket.
    Keyword Arguments:
        bucket_name: name of the s3 bucket.
        filename: name of the file in s3 bucket.
        dataframe: a dataframe to save.

    Returns:
        None"""
    s3_resource = boto3.resource("s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=None,
        config=boto3.session.Config(signature_version="s3v4"),
        verify=False
    )
    s3_resource.Object(
        bucket_name=bucket_name,
        key=filename
    ).put(Body=pickle.dumps(dataframe))


if __name__ == "__main__":
    df = read_data(url=URL, filename=FILENAME)
    save_to_s3(
        bucket_name=S3_BUCKET_NAME,
        filename=FILENAME[:-4],
        dataframe=df)
