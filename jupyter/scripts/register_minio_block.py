import os
from prefect.filesystems import RemoteFileSystem


if __name__ == "__main__":
    ARTIFACT_ROOT = os.getenv("ARTIFACT_ROOT")
    MINIO_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    MINIO_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    MLFLOW_S3_ENDPOINT_URL = os.getenv("MLFLOW_S3_ENDPOINT_URL")

    minio_block = RemoteFileSystem(
        basepath=ARTIFACT_ROOT,
        settings={
            "key": MINIO_ACCESS_KEY,
            "secret": MINIO_SECRET_KEY,
            "client_kwargs": {"endpoint_url": MLFLOW_S3_ENDPOINT_URL}
        },
    )
    minio_block.save("minio", overwrite=True)
