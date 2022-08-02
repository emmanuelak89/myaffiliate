from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import tweepy
from instagramy import InstagramUser
from googleapiclient.discovery import build
from .models import Bio
from django.http import HttpResponse

@shared_task(bind=True)
def send_email(self,emailto,bid):
    subject = 'Hey! Your bid has been accepted'
    message = f'The bid you sent for' + bid.job.name + 'was approved.\n Contact' + bid.job.uploaded_by + '\n Email : ' + bid.job.uploaded_by.email + '\n Phone number : ' + bid.job.uploaded_by.bio.phone + '\n Have a great day :)'
    email_from = settings.EMAIL_HOST_USER
    recipient = [emailto, ]
    send_mail(subject, message, email_from, recipient)

@shared_task(bind=True)
def user_socials(self):
    authh = tweepy.OAuthHandler('X2yiHbja7B7w4P0rPVLPOr2HP', 'hADbmAdPVSFx3TSwud4VAHk9LqeRJMsn1O7bb7tmVncKFiNJ8o')
    authh.set_access_token('1312752739517108225-PxrLvfK3Ow1gSK1iVulvAgjhwr4Ej1',
                           'jiM128HZpKlqLPrYkavc84NrtQbBJJX5m1yWlZJMqZxfS')
    api = tweepy.API(authh)
    allusers = Bio.objects.all()
    for user in allusers:
        try:
            account = InstagramUser(user.bio.instagram, sessionid='1959093809%3A6apN0Up1cyahtS%3A28')
            user.bio.instagram_following = account.number_of_followers
            user.bio.save()
        except:
            print('error')
        try:
            account = api.get_user(screen_name=user.bio.twitter)
            user.bio.twitter_following = account.followers_count
            user.bio.save()
        except:
            print('error')
        try:
            youtube = build('youtube', 'v3',
                            developerKey='AIzaSyB_TyyyoLhAAzr8313KajUN1L3u-BrmqBY')
            ch_request = youtube.channels().list(
                part='statistics',
                id=str(user.bio.youtube))
            ch_response = ch_request.execute()
            user.bio.youtube_following = int(ch_response['items'][0]['statistics']['subscriberCount'])
            user.bio.save()
        except:
            print('error')