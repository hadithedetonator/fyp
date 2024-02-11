from django.db import models
from accounts.models import CustomUser
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(max_length=255)
    pass_key = models.CharField(max_length=50)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    participants = models.ManyToManyField(CustomUser, related_name='joined_rooms', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    join_requests = models.ManyToManyField(CustomUser, related_name='pending_requests', blank=True)

    def has_join_request(self, user):
        return user in self.join_requests.all()

    def is_participant(self, user):
        return user in self.participants.all()

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    upload = models.FileField(upload_to='books/')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FileUpload(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    file_upload = models.FileField(upload_to='submissions/')
    timestamp = models.DateTimeField(auto_now_add=True)
