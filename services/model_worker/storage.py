"""Private encrypted storage. Local development adapter or private S3 bucket."""

from pathlib import Path
import os
from .store import STATE, CIPHER, PRODUCTION


def client():
    import boto3
    from botocore.config import Config

    endpoint = os.getenv("S3_ENDPOINT_URL") or None
    if PRODUCTION and endpoint and not endpoint.startswith("https://"):
        raise RuntimeError("Production S3 endpoints require HTTPS")
    style = os.getenv("S3_ADDRESSING_STYLE") or ("path" if endpoint else "auto")
    if style not in ["auto", "path", "virtual"]:
        raise RuntimeError("Invalid S3 addressing configuration")
    return boto3.client("s3", endpoint_url=endpoint, config=Config(
        s3={"addressing_style": style}, connect_timeout=3, read_timeout=15,
        retries={"mode": "standard", "total_max_attempts": 1},
    ))


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
