from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth import authenticate
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from .models import *
from .tasks import *

import requests
from datetime import datetime
from .serializers import BioSerializer,JobSerializer,BidSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from bs4 import BeautifulSoup
from tiktokscraper import scraper
from instagramy import InstagramUser
from googleapiclient.discovery import build

# link = 'https://www.instagram.com/accounts/login/'
# login_url = 'https://www.instagram.com/accounts/login/ajax/'
#
# time = int(datetime.now().timestamp())
#
# payload = {
#     'username': 'emmanuelakerele553',
#     'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:Emerald1996',
#     'queryParams': {},
#     'optIntoOneTap': 'false'
# }
#
# with requests.Session() as s:
#     r = s.get(link)
#     csrf = re.findall(r"csrf_token\":\"(.*?)\"",r.text)[0]
#     r = s.post(login_url,data=payload,headers={
#         "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
#         "X-Requested-With": "XMLHttpRequest",
#         "Referer": "https://www.instagram.com/accounts/login/",
#         "x-csrftoken":csrf
#     })
#     sessionid=s.cookies

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        bio = request.POST['bio']
        tiktok = request.POST['tiktok']
        youtube = request.POST['youtube']
        instagram = request.POST['instagram']
        twitter = request.POST['twitter']
        phone = request.POST['phone']
        image = request.FILES['image']
        fs = FileSystemStorage()
        doc = fs.save(image.name, image)
        if request.POST['password'] == request.POST['password2']:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            u = User.objects.get(username=email)
            influencer = Bio(email=u, name =name,phone=phone,image=doc,instagram=instagram,twitter=twitter,shortbio=bio,tiktok=tiktok,youtube=youtube)
            influencer.save()
            auth.login(request, user)
            return redirect('dashboard')
        else:
            mg = 'passwords must match'
            return render(request, 'signup.html', {'mg': mg})
    else:
        return render(request, 'signup.html')

def clientsignup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        bio = request.POST['bio']
        phone = request.POST['phone']
        image = request.FILES['image']
        fs = FileSystemStorage()
        doc = fs.save(image.name, image)
        if request.POST['password'] == request.POST['password2']:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            u = User.objects.get(username=email)
            client = Bio(email=u, name =name,phone=phone,image=doc,role='client',shortbio=bio)
            client.save()
            auth.login(request, user)
            return redirect('clientdashboard')
        else:
            mg = 'passwords must match'
            return render(request, 'csignup.html', {'mg': mg})
    else:
        return render(request, 'csignup.html')

def signin(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            user_socials.delay(request.user)
            if request.user.bio.role == 'influencer':
                return redirect('dashboard')
            else:
                return redirect('clientdashboard')
        else:
            return render(request, 'signin.html', {'error': 'username or password is incorrect'})
    else:
        return render(request, 'signin.html')

def signout(request):
    auth.logout(request)
    return redirect('home')

def clientdashboard(request):
    bio = Bio.objects.get(email=request.user)
    jobs = Job.objects.filter(uploaded_by=request.user)
    totalbids = []
    pendingbids = []
    acceptedbids = []
    topinfluencers = Bio.objects.all().order_by('-accepted')
    for job in jobs:
        if Bid.objects.filter(job=job,status='pending'):
            pendingbids += Bid.objects.filter(job=job)
        elif Bid.objects.filter(job=job,status='accepted'):
            acceptedbids += Bid.objects.filter(job=job)
    return render(request, 'client-dashboard.html', {'bio': bio, 'jobs': jobs, 'totalbids': len(totalbids), 'pendingbids': pendingbids, 'acceptedbids': acceptedbids, 'pendingbidscount': len(pendingbids), 'acceptedbidscount': len(acceptedbids),'topinfluencers':topinfluencers})

def dashboard(request):
    acceptedbids = Bid.objects.filter(BidSentBy=request.user, status='accepted')
    pendingbids = Bid.objects.filter(BidSentBy=request.user, status='pending')
    allbids = Bid.objects.filter(BidSentBy=request.user)
    jobs = Job.objects.all()
    topinfluencers = Bio.objects.all().order_by('-accepted')
    return render(request, 'dashboard.html', {'jobs': jobs,
                                             'acceptedbids':acceptedbids, 'pendingbids':pendingbids, 'allbids':allbids,'topinfluencers':topinfluencers})

def bidderinfo(request,id):
    bidder = User.objects.get(id=id)
    jobs = Job.objects.filter(uploaded_by=request.user)
    bids=[]
    for job in jobs:
        bids+= Bid.objects.filter(job=job,BidSentBy=bidder)
    return render(request, 'bidder-info.html', {'bidder': bidder,'bids':bids})

def viewjob(request,id):
    job = Job.objects.get(id=id)
    return render(request, 'job-info.html', {'job': job})

def editjob(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        id = request.POST['id']
        Job.objects.get(id=id).update(name=title,description=description)
        return redirect('clientdashboard')

def uploadjob(request):
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        description = request.POST['description']
        image = request.FILES['image']
        fs = FileSystemStorage()
        doc = fs.save(image.name, image)
        uploaded = datetime.datetime.now()
        job = Job(uploaded_by=request.user,name=name,description=description,uploaded=uploaded,price=price,image=doc)
        job.save()
        return redirect('dashboard')
    else:
        return render(request, 'upload-job.html')

def deletejob(request,id):
    job = Job.objects.get(id=id)
    job.delete()
    return redirect('clientdashboard')

def editprofile(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        phone = request.POST['phone']
        image = request.FILES['image']
        fs = FileSystemStorage()
        doc = fs.save(image.name, image)
        u = User.objects.get(username=request.user.get_username())
        u.set_password(password)
        u.email = email
        u.save()
        Bio.objects.get(user=u).update(name =name,phone=phone,image=doc)
        bio = Bio.objects.get(user=u)
        if bio.role == 'influencer':
            return redirect('dashboard')
        else:
            return redirect('clientdashboard')
    else:
        if request.user.bio.role == 'influencer':
            return render(request, 'user-profile.html')
        else:
            return render(request, 'client-profile.html')

def editsocials(request):
    email = request.POST['email']
    instagram = request.POST['instagram']
    youtube = request.POST['youtube']
    twitter = request.POST['twitter']
    tiktok = request.POST['tiktok']
    user = request.user
    user.email = email
    user.save()
    Bio.objects.get(user=user).update(instagram=instagram, youtube=youtube, twitter=twitter, tiktok=tiktok)
    bio = Bio.objects.get(user=user)
    if bio.role == 'influencer':
        return redirect('dashboard')
    else:
        return redirect('clientdashboard')


def submitbid(request,id):
    job = Job.objects.get(id=id)
    bid = Bid(job=job,BidSentBy=request.user)
    bid.save()
    return redirect('dashboard')

def deletebid(request,id):
    bid = Bid.objects.get(id=id)
    bid.delete()
    return redirect('dashboard')

def acceptbid(request,id):
    bid = Bid.objects.get(id=id)
    bid.BidSentBy.bio.rejected += 1
    job = bid.job
    job.influencer = bid.BidSentBy
    job.save()
    bid.status = 'accepted'
    bid.save()
    emailto = bid.BidSentBy.email
    send_email.delay(emailto,bid)
    for b in Bid.objects.filter(job=job):
        b.delete()
    return redirect('clientdashboard')

def rejectbid(request,id):
    bid = Bid.objects.get(id=id)
    bid.BidSentBy.bio.rejected +=1
    bid.delete()
    if request.user.bio.role == 'influencer':
        return redirect('dashboard')
    else:
        return redirect('clientdashboard')


def deleteprofile(request):
    user = request.user
    user.delete()
    return redirect('home')

#API to update a bio object mainly but also performs retrieve ,post and delete actions
class BioAPI(ModelViewSet):
    serializer_class = BioSerializer
    queryset = Bio.objects.all()

    def perform_update(self, serializer):
        try:
            user = User.objects.get(username=self.request.data['email'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save(email=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#API to update a job object mainly but also performs retrieve ,post and delete actions
class JobAPI(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def perform_update(self, serializer):
        try:
            user = User.objects.get(username=self.request.data['uploaded_by'])
            influencer = ''
            try:
                if self.request.data['influencer'] == '':
                    influencer = None
            except User.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save(uploaded_by=user,influencer=influencer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#API to view all bids but also performs retrieve ,post and delete actions
class BidAPI(ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer


