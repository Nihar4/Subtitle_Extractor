from django.urls import path
from . import views

app_name = 'videoapp'

urlpatterns = [
    path('', views.upload_video, name='upload_video'),
    path('search/<int:video_id>/', views.search_subtitles, name='search_subtitles'),
]
