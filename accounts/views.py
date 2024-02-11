from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.views.decorators.csrf import csrf_protect

def register_view(request):
    if request.user.is_authenticated:
        return redirect('app:home')  # Redirect if already authenticated

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('app:home')  # Redirect if already authenticated

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('app:home')  # Change 'home' to your desired home page URL
            else:
                form.add_error(None, 'Invalid username or password.')  # Fix the typo here
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')  # Change 'home' to your desired home page URL
