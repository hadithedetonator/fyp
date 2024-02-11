from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from app import views

app_name = 'app'  # Add this line to specify the app namespace


urlpatterns = [
    path("",views.home, name='home'),
    path('create-room/', views.create_room, name='create_room'),
    path('join-room/', views.join_room, name='join_room'),
    path('leave-room/<int:room_id>/', views.leave_room, name='leave_room'),
    path('created-rooms/', views.created_rooms, name='created_rooms'),
    path('file-uploads/<int:room_id>/', views.file_upload_view, name='file_uploads'),
    path('room_detail/<int:room_id>/', views.room_detail, name='room_detail'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('update_file/<int:file_id>/', views.update_file, name='update_file'),
    path('room/<int:room_id>/join-requests/', views.join_requests, name='join_requests'),
    path('accept-join-request/<int:room_id>/<int:user_id>/', views.accept_join_request, name='accept_join_request'),
    path('reject-join-request/<int:room_id>/<int:user_id>/', views.reject_join_request, name='reject_join_request'),
    path('upload-book/', views.upload_book, name='upload_book'),
    path('book-list/', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('query-form/', views.process_query1, name='query_form'),


]   

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
