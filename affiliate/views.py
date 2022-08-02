from django.shortcuts import render,redirect

def home(request):
    return render(request,'index3.html')