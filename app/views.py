from django.shortcuts import  render, redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import RoomCreationForm,JoinRoomForm,FileUploadForm,BookUploadForm
from .models import FileUpload,CustomUser,Book 
import random
#import fitz
#from pdf2image import convert_from_path

import tempfile
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings



from .utils import setup_dbqa,set_qa_prompt,build_retrieval_qa
from .llm import load_llm
from .models import Room

#----------------APP LEVEL FUNCTIONS------------------#

@login_required
def home(request):
    user = request.user
    joined_rooms = Room.objects.filter(participants=user)
    return render(request, 'app/home.html', {'joined_rooms': joined_rooms})
    

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomCreationForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.creator = request.user

            # Generate a random 6-digit pass key
            pass_key = str(random.randint(100000, 999999))
            room.pass_key = pass_key

            room.save()
            return redirect('app:home')
    else:
        form = RoomCreationForm()

    return render(request, 'app/create_room.html', {'form': form})

@login_required
def created_rooms(request):
    # Fetch all rooms created by the teacher
    created_rooms = Room.objects.filter(creator=request.user)
    return render(request, 'app/created_rooms.html', {'created_rooms': created_rooms})

@login_required
def join_room(request):
    if request.method == 'POST' and not request.user.is_teacher:
        form = JoinRoomForm(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data['room_name']
            pass_key = form.cleaned_data['pass_key']

            try:
                room = Room.objects.get(name=room_name, pass_key=pass_key)
                # Add the user to the participants of the room
                room.join_requests.add(request.user)
                JsonResponse({'success': True, 'message': 'Sent Join Request. Wait for approval.'})
                return redirect('app:home')  # Redirect to the home page or another appropriate URL
            except Room.DoesNotExist:
                return JsonResponse({'success': True, 'message': 'Room Doesnt Exist. Double Check credentials.'})
    else:
        form = JoinRoomForm()

    return render(request, 'app/join_room.html', {'form': form})

@login_required
def leave_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Check if the user is a participant in the room
    if room.is_participant(request.user):
        # Remove the user from the participants of the room
        room.participants.remove(request.user)

    # Redirect to the home page or another appropriate URL
    return redirect('app:home')

@login_required
def join_requests(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Fetch join requests for the room
    join_requests = room.join_requests.all()

    return render(request, 'app/join_req.html', {'room': room, 'join_requests': join_requests})

@login_required
def accept_join_request(request, room_id, user_id):
    # Get the room and user
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(CustomUser, id=user_id)

    # Add the user to the participants and remove from join requests
    room.participants.add(user)
    room.join_requests.remove(user)

    return redirect('app:room_detail', room_id=room.id)

@login_required
def reject_join_request(request, room_id, user_id):
    # Get the room and user
    room = get_object_or_404(Room, id=room_id)
    user = get_object_or_404(CustomUser, id=user_id)

    # Remove the user from join requests
    room.join_requests.remove(user)

    return JsonResponse({'success': True, 'message': 'Join request rejected successfully.'})

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        if not room.is_participant(request.user):
            # If the user is not a participant, send a leave request
            room.leave_requests.add(request.user)
            return JsonResponse({'success': True, 'message': 'Leave request sent. Wait for approval.'})
        else:
            # If the user is a participant, remove from the participants
            room.participants.remove(request.user)
            room.leave_requests.remove(request.user)
            return JsonResponse({'success': True, 'message': 'Left the room successfully.'})

    return render(request, 'app/room_detail.html', {'room': room})

@login_required
def delete_file(request, file_id):
    file_upload = get_object_or_404(FileUpload, id=file_id)

    # Delete file from the filesystem
    file_upload.file_upload.delete()

    # Delete file from the database
    file_upload.delete()

    return redirect('app:room_detail', room_id=file_upload.room.id)


@login_required
def update_file(request, file_id):
    file_upload = get_object_or_404(FileUpload, id=file_id)

    # Add your update logic here if needed

    return redirect('app:room_detail', room_id=file_upload.room.id)

@login_required
def file_upload_view(request, room_id):
    room = Room.objects.get(pk=room_id)
    file_uploads = FileUpload.objects.filter(room=room).order_by('timestamp')
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            file_upload.user = request.user
            file_upload.room = room
            file_upload.save()
            return redirect('app:file_uploads', room_id=room_id)
    else:
        form = FileUploadForm()

    return render(request, 'app/file_uploads.html', {'form': form, 'file_uploads': file_uploads, 'room': room})


@login_required
def upload_book(request):
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.uploaded_by = request.user
            book.save()
            return redirect('app:book_list')  # Change to the appropriate URL
    else:
        form = BookUploadForm()

    return render(request, 'app/upload_book.html', {'form': form})

@login_required
def book_list(request):
    uploaded_books = Book.objects.filter(uploaded_by_id=request.user)
    return render(request, 'app/book_list.html', {'uploaded_books': uploaded_books})


import os
from django.conf import settings

@login_required
def process_query(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        pages_no = request.POST.get('pages')  # Taking page no. from front end (JS)

        # Directory to store vector stores for each book
        book_vectorstore_dir = os.path.join(settings.MEDIA_ROOT, 'book_vectorstores')
        os.makedirs(book_vectorstore_dir, exist_ok=True)

        # Load PDF file from data path
      
        loader = PyPDFLoader("example_data/layout-parser-paper.pdf")
        pages = loader.load_and_split()

        # Split text from PDF into chunks
        #text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        #texts = text_splitter.split_documents(documents)

        # Load embeddings model
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

        # Build FAISS vector store
        vectorstore = FAISS.from_documents(context, embeddings)

        # Save FAISS vector store
        vectorstore_path = os.path.join(book_vectorstore_dir, 'db_faiss')
        vectorstore.save_local(vectorstore_path)

        # Use the vector store for querying
        dbqa = setup_dbqa(vectorstore_path)
        response = dbqa(query)

        # Once the response is finalized, render the result
        context = {
            'result': response['result'],
            'source_documents': response['source_documents'],
            'time_taken': response['time_taken'],
        }

        return render(request, 'app/query_result.html', context)

    return render(request, 'app/book_detail.html')



def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'app/book_detail.html', {'book': book})



import json
from app.models import Book  # Import your Book model

@login_required
def process_query1(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        text = request.POST.get('text')  # Get the text content
        
        # Directory to store vector stores for each book
        book_vectorstore_dir = os.path.join(settings.MEDIA_ROOT, 'book_vectorstores')
        os.makedirs(book_vectorstore_dir, exist_ok=True)

        # Retrieve the logged-in user's selected book
        user_selected_book = Book.objects.filter(uploaded_by_id=request.user.id).first()

        if user_selected_book:
            # Split text from PDF into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                        chunk_overlap=50)
            texts = text_splitter.split_text(text)
        
            # Load embeddings model
            embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

            # Build FAISS vector store
            vectorstore = FAISS.from_texts(texts, embeddings)

            # Save FAISS vector store
            vectorstore_path = os.path.join(book_vectorstore_dir, 'db_faiss')
            vectorstore.save_local(vectorstore_path)

            # Setup DBQA
            llm = load_llm()
            qa_prompt = set_qa_prompt()
            dbqa = build_retrieval_qa(llm, qa_prompt, vectorstore)

            # Query using DBQA
            response = dbqa(query)


        # Once the response is finalized, render the result
            context = {
                'result': response['result'],
                'source_documents': response['source_documents'],
                'time_taken': response['time_taken'],
            }

            return render(request, 'app/query_result.html', context)      

    return JsonResponse({'error': 'Method not allowed'}, status=405)
