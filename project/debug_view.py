"""
Temporary debug view - Add this to your urls.py for debugging on Render
"""
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

def debug_s3_view(request):
    """
    Debug view to check S3 configuration on Render
    Add this to your urls.py: path('debug-s3/', debug_s3_view, name='debug_s3')
    """
    html = ["<h1>S3 Debug on Render</h1>"]
    
    # Environment variables
    html.append("<h2>1. Environment Variables</h2>")
    env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME', 'AWS_S3_REGION_NAME']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'AWS_SECRET_ACCESS_KEY':
                display_value = f"{'*' * 8}...{value[-4:]}"
            elif var == 'AWS_ACCESS_KEY_ID':
                display_value = f"{value[:4]}...{value[-4:]}"
            else:
                display_value = value
            html.append(f"<p>{var}: {display_value}</p>")
        else:
            html.append(f"<p style='color:red'>{var}: NOT SET</p>")
    
    # Django settings
    html.append("<h2>2. Django Settings</h2>")
    html.append(f"<p>DEBUG: {settings.DEBUG}</p>")
    html.append(f"<p>DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}</p>")
    html.append(f"<p>MEDIA_URL: {settings.MEDIA_URL}</p>")
    
    # Storage test
    html.append("<h2>3. Storage Test</h2>")
    try:
        html.append(f"<p>Storage class: {default_storage.__class__.__name__}</p>")
        
        if hasattr(default_storage, 'bucket_name'):
            html.append(f"<p>S3 Bucket: {default_storage.bucket_name}</p>")
        
        # Test upload
        test_content = ContentFile(b"Render S3 debug test", name="debug_test.txt")
        saved_name = default_storage.save("debug/render_debug_test.txt", test_content)
        url = default_storage.url(saved_name)
        
        html.append(f"<p style='color:green'>✓ Upload successful: {saved_name}</p>")
        html.append(f"<p style='color:green'>✓ URL: <a href='{url}' target='_blank'>{url}</a></p>")
        
        # Cleanup
        if default_storage.exists(saved_name):
            default_storage.delete(saved_name)
            html.append(f"<p style='color:green'>✓ Test file cleaned up</p>")
            
    except Exception as e:
        html.append(f"<p style='color:red'>✗ Storage test failed: {str(e)}</p>")
        import traceback
        html.append(f"<pre style='color:red'>{traceback.format_exc()}</pre>")
    
    return HttpResponse("<br>".join(html))
