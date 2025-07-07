from django.shortcuts import render


def storage(request):
    return render(request, 'storage/storage.html') 