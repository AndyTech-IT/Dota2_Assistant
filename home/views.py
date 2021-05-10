from django.shortcuts import render

# Create your views here.

def StartPadge(request):
    return render(request, 'home/StartPadge.html')