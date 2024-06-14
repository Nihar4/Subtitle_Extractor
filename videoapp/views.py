from django.shortcuts import render, redirect
from .forms import VideoForm
from .models import Video
from .tasks import process_video
import boto3
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            process_video(video.id)
            return redirect(f'/search/{video.id}')
    else:
        form = VideoForm()
    return render(request, 'upload.html', {'form': form})

def search_subtitles(request, video_id):
    query = request.GET.get('q')

    if request.method == 'POST':
        query = request.POST.get('search_query')
        return HttpResponseRedirect(reverse('videoapp:search_subtitles', args=[video_id]) + f'?q={query}')  # Redirect to search page with query
    
    if query and video_id:
        dynamodb = boto3.resource('dynamodb',
                                  region_name=settings.AWS_S3_REGION_NAME,
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        
        table = dynamodb.Table('Video_Subtitles')
        
        response = table.scan(
            FilterExpression='video_id = :video_id',
            ExpressionAttributeValues={
                ':video_id': str(video_id),
            }
        )
        
        items = response['Items']
        # print(items)
        subtitles = []
        
        for item in items:
            for subtitle in item['subtitles']:
                if query.lower() in subtitle['content'].lower():
                    start_time = subtitle['start_time'].split(',')[0]
                    end_time = subtitle['end_time'].split(',')[0]
                    subtitles.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'content': subtitle['content']
                    })
        print(subtitles)
    else:
        subtitles = []
    
    return render(request, 'search.html', {'subtitles': subtitles, 'query': query, 'video_id': video_id})