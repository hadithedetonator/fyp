from django import forms
from .models import Room,FileUpload,Book

# forms.py
from django import forms
from .models import Room

class RoomCreationForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name']
        labels = {
            'name': 'Room Name',
        }

class JoinRoomForm(forms.Form):
    room_name = forms.CharField(max_length=100, label='Room Name')
    pass_key = forms.CharField(max_length=100, label='Pass Key')



class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['file_upload']



class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'upload']