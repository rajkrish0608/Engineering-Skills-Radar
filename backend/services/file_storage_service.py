"""
File Storage Service (MinIO/S3)
Handles document uploads for syllabi, project PDFs, certificates
"""
import os
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import mimetypes
from minio import Minio
from minio.error import S3Error
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class FileStorageService:
    """
    Service for uploading and managing files in MinIO or S3
    """
    
    def __init__(self):
        self.storage_type = os.getenv('STORAGE_TYPE', 'minio')
        self.max_file_size_mb = int(os.getenv('MAX_UPLOAD_SIZE_MB', 10))
        self.allowed_extensions = os.getenv('ALLOWED_FILE_EXTENSIONS', 'pdf,docx,csv,xlsx').split(',')
        
        if self.storage_type == 'minio':
            self._init_minio()
        else:
            self._init_s3()
    
    def _init_minio(self):
        """Initialize MinIO client"""
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=os.getenv('MINIO_SECURE', 'False') == 'True'
        )
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME', 'esr-documents')
        
        # Create bucket if it doesn't exist
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                print(f"Created MinIO bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error creating MinIO bucket: {e}")
    
    def _init_s3(self):
        """Initialize AWS S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'esr-documents')
    
    def validate_file(self, filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """
        Validate file before upload
        
        Returns:
            (is_valid, error_message)
        """
        # Check file extension
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if ext not in self.allowed_extensions:
            return False, f"File type not allowed. Allowed: {', '.join(self.allowed_extensions)}"
        
        # Check file size
        max_size_bytes = self.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"File size exceeds maximum ({self.max_file_size_mb}MB)"
        
        return True, None
    
    def generate_object_name(self, filename: str, category: str, student_roll: Optional[str] = None) -> str:
        """
        Generate unique object name for storage
        
        Args:
            filename: Original filename
            category: File category (syllabi, projects, certificates, etc.)
            student_roll: Optional student roll number
        
        Returns:
            Object name in format: category/YYYYMMDD_rollnumber_timestamp_filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = filename.replace(' ', '_').replace('/', '_')
        
        if student_roll:
            object_name = f"{category}/{datetime.now().strftime('%Y%m')}/{student_roll}_{timestamp}_{safe_filename}"
        else:
            object_name = f"{category}/{datetime.now().strftime('%Y%m')}/{timestamp}_{safe_filename}"
        
        return object_name
    
    def upload_file(
        self,
        file_content: BinaryIO,
        filename: str,
        category: str,
        student_roll: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Upload file to storage
        
        Returns:
            Dictionary with upload result
        """
        # Generate object name
        object_name = self.generate_object_name(filename, category, student_roll)
        
        # Get content type
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'
        
        try:
            if self.storage_type == 'minio':
                # Upload to MinIO
                file_content.seek(0)
                self.minio_client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    data=file_content,
                    length=-1,  # Auto-detect length
                    part_size=10*1024*1024,  # 10MB parts
                    content_type=content_type,
                    metadata=metadata or {}
                )
            else:
                # Upload to S3
                file_content.seek(0)
                extra_args = {
                    'ContentType': content_type,
                    'Metadata': metadata or {}
                }
                self.s3_client.upload_fileobj(
                    Fileobj=file_content,
                    Bucket=self.bucket_name,
                    Key=object_name,
                    ExtraArgs=extra_args
                )
            
            # Generate access URL
            file_url = self.get_file_url(object_name)
            
            return {
                'success': True,
                'object_name': object_name,
                'file_url': file_url,
                'bucket': self.bucket_name,
                'uploaded_at': datetime.now().isoformat()
            }
        
        except (S3Error, ClientError) as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_url(self, object_name: str, expiry_hours: int = 24) -> str:
        """
        Get presigned URL for file access
        
        Args:
            object_name: Object name in storage
            expiry_hours: URL expiry time in hours
        
        Returns:
            Presigned URL
        """
        try:
            if self.storage_type == 'minio':
                url = self.minio_client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    expires=timedelta(hours=expiry_hours)
                )
            else:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': object_name
                    },
                    ExpiresIn=expiry_hours * 3600
                )
            
            return url
        
        except (S3Error, ClientError) as e:
            return f"Error generating URL: {str(e)}"
    
    def delete_file(self, object_name: str) -> bool:
        """
        Delete file from storage
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.storage_type == 'minio':
                self.minio_client.remove_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name
                )
            else:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
            
            return True
        
        except (S3Error, ClientError) as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(self, prefix: str = '') -> list:
        """
        List files in storage with optional prefix filter
        
        Returns:
            List of file objects
        """
        try:
            if self.storage_type == 'minio':
                objects = self.minio_client.list_objects(
                    bucket_name=self.bucket_name,
                    prefix=prefix,
                    recursive=True
                )
                return [
                    {
                        'object_name': obj.object_name,
                        'size': obj.size,
                        'last_modified': obj.last_modified
                    }
                    for obj in objects
                ]
            else:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                return [
                    {
                        'object_name': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    }
                    for obj in response.get('Contents', [])
                ]
        
        except (S3Error, ClientError) as e:
            print(f"Error listing files: {e}")
            return []
