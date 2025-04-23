# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UploadFileForm

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')
    else:
        form = UploadFileForm()
    return render(request, 'fileuploader/upload.html', {'form': form})

@login_required
def upload_success(request):
    return render(request, 'fileuploader/success.html')