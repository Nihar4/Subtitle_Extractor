import subprocess
import boto3
from .models import Video
from django.conf import settings
import os
import tempfile

def process_video(video_id):
    video = Video.objects.get(id=video_id)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        video.file.seek(0)  # Ensure you're at the start of the file
        temp_file.write(video.file.read())
        temp_file_path = temp_file.name
            
    output_srt = f'{temp_file_path}.srt'

    subprocess.run(['CCExtractor_win_portable\\ccextractorwinfull.exe', temp_file_path, '-o', output_srt])
            
    s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME , aws_access_key_id=settings.AWS_ACCESS_KEY_ID , aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3_client.upload_file(output_srt, settings.AWS_STORAGE_BUCKET_NAME, f'{video.file.name}.srt')
    
    subtitles = []

    with open(output_srt, 'r') as file:
        start_time, end_time = "", ""
        for line in file:
            if '-->' in line:
                start_time, end_time = line.strip().split(' --> ')
            else:
                content = line.strip()
                if content and not content.isdigit():
                    subtitle = {
                        'start_time': start_time,
                        'end_time': end_time,
                        'content': content
                    }
                    subtitles.append(subtitle)
    
    dynamodb = boto3.resource('dynamodb',
                              region_name=settings.AWS_S3_REGION_NAME,
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    
    table = dynamodb.Table('Video_Subtitles')
    table.put_item(Item={'video_id': str(video_id), 'subtitles': subtitles})
        
    os.remove(temp_file_path)
    os.remove(output_srt)