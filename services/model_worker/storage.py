"""Private encrypted storage. Local development adapter or private S3 bucket."""

from pathlib import Path
import os
from .store import STATE, CIPHER, PRODUCTION


def client():
    import boto3

    return boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL") or None)


def put(aid, data):
    encrypted = CIPHER.encrypt(data)
    bucket = os.getenv("S3_BUCKET")
    if bucket:
        key = "private/" + aid
        client().put_object(
            Bucket=bucket,
            Key=key,
            Body=encrypted,
            ContentType="application/octet-stream",
            ServerSideEncryption="AES256",
        )
        return "s3:" + key
    if PRODUCTION:
        raise RuntimeError("Private S3 bucket is required in production")
    path = STATE / "assets" / aid
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(encrypted)
    path.chmod(0o600)
    return str(path)


def get(path):
    if path.startswith("s3:"):
        encrypted = (
            client()
            .get_object(Bucket=os.environ["S3_BUCKET"], Key=path[3:])["Body"]
            .read()
        )
    else:
        encrypted = Path(path).read_bytes()
    return CIPHER.decrypt(encrypted)


def remove(path):
    if path.startswith("s3:"):
        client().delete_object(Bucket=os.environ["S3_BUCKET"], Key=path[3:])
    else:
        Path(path).unlink(missing_ok=True)
