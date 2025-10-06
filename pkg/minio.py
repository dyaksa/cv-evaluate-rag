from core.config import settings
from minio import Minio
from minio.error import S3Error

class MinioClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_URL.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_URL.startswith("https://")
        )

    def upload_file(self, file_path: str, object_name: str) -> str:
        """Upload a file to the specified MinIO bucket."""
        try:
            self.client.fput_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=object_name,
                file_path=file_path
            )
            return f"{settings.MINIO_URL}/{settings.MINIO_BUCKET_NAME}/{object_name}"
        except S3Error as e:
            print(f"Error occurred while uploading file: {e}")
            return ""
            
    def download_file(self, object_name: str, file_path: str) -> bool:
        """Download a file from the specified MinIO bucket."""
        try:
            self.client.fget_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=object_name,
                file_path=file_path
            )
            return True
        except S3Error as e:
            print(f"Error occurred while downloading file: {e}")
            return False
        
    def download_to_bytes(self, object_name: str) -> bytes | None:
        """Download an object from MinIO and return its content as bytes."""
        try:
            response = self.client.get_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=object_name
            )
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error occurred while downloading object: {e}")
            return None