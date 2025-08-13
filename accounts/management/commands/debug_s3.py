from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

class Command(BaseCommand):
    help = 'Debug S3 configuration on Render'

    def handle(self, *args, **options):
        self.stdout.write("=== S3 Debug on Render ===\n")
        
        # Check environment variables
        self.stdout.write("1. Environment Variables:")
        env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME', 'AWS_S3_REGION_NAME']
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                if var in ['AWS_SECRET_ACCESS_KEY']:
                    self.stdout.write(f"   {var}: {'*' * 8}...{value[-4:]}")
                elif var == 'AWS_ACCESS_KEY_ID':
                    self.stdout.write(f"   {var}: {value[:4]}...{value[-4:]}")
                else:
                    self.stdout.write(f"   {var}: {value}")
            else:
                self.stdout.write(f"   {var}: ✗ NOT SET")
        
        # Check Django settings
        self.stdout.write(f"\n2. Django Settings:")
        self.stdout.write(f"   DEBUG: {settings.DEBUG}")
        self.stdout.write(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
        self.stdout.write(f"   MEDIA_URL: {settings.MEDIA_URL}")
        
        # Test storage
        self.stdout.write(f"\n3. Storage Test:")
        try:
            self.stdout.write(f"   Storage class: {default_storage.__class__.__name__}")
            
            if hasattr(default_storage, 'bucket_name'):
                self.stdout.write(f"   S3 Bucket: {default_storage.bucket_name}")
            
            # Test upload
            test_content = ContentFile(b"Render S3 test", name="render_s3_test.txt")
            saved_name = default_storage.save("debug/render_s3_test.txt", test_content)
            url = default_storage.url(saved_name)
            
            self.stdout.write(f"   ✓ Upload successful: {saved_name}")
            self.stdout.write(f"   ✓ URL: {url}")
            
            # Cleanup
            if default_storage.exists(saved_name):
                default_storage.delete(saved_name)
                self.stdout.write(f"   ✓ Cleaned up")
                
        except Exception as e:
            self.stdout.write(f"   ✗ Storage test failed: {e}")
            import traceback
            self.stdout.write(traceback.format_exc())
