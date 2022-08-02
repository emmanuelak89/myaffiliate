from django.db import models
from django.contrib.auth.models import User

class Bio(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=35)
    shortbio = models.CharField(max_length=90, default='null', null=True)
    image = models.ImageField(upload_to='images/', default='images/home-profile.jpg', null=True)
    instagram = models.CharField(max_length=90, default='null', null=True)
    instagram_following = models.IntegerField(null=True, default=100)
    twitter = models.CharField(max_length=90, default='null', null=True)
    twitter_following = models.IntegerField(null=True, default=100)
    tiktok = models.CharField(max_length=90, default='null', null=True)
    tiktok_following = models.IntegerField(null=True, default=100)
    youtube = models.CharField(max_length=90, default='null', null=True)
    youtube_following = models.IntegerField(null=True, default=100)
    phone = models.IntegerField(null=True)
    role = models.CharField(max_length=15,default='influencer')
    accepted = models.IntegerField(null=True,default=0)
    rejected = models.IntegerField(null=True, default=0)
    def __str__(self):
        return self.name

class Job(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100,default='no description')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='client')
    influencer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='influencer')
    uploaded = models.DateTimeField(null=True)
    image = models.ImageField(upload_to='images/', default='images/home-profile.jpg', null=True)
    price = models.IntegerField(null=False,default=1000)
    def __str__(self):
        return self.name

class Bid(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=False)
    BidSentBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=15, default='pending')
    def __str__(self):
        return self.job.name
