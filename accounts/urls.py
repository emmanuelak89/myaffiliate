from . import views
from django.urls import path,include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'bio', views.BioAPI,basename='bio')
router.register(r'job', views.JobAPI,basename='job')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/',views.signup,name='signup'),
    path('clientsignup/', views.clientsignup, name='clientsignup'),
    path('userdashboard/',views.dashboard,name='dashboard'),
    path('clientdashboard/', views.clientdashboard, name='clientdashboard'),
    path('settings/', views.editprofile, name='editprofile'),
    path('editsocials/', views.editsocials, name='editsocials'),
    path('deleteprofile/', views.deleteprofile, name='deleteprofile'),
    path('editjob/', views.editjob, name='editjob'),
    path('uploadjob/', views.uploadjob, name='uploadjob'),
    path('viewjob/<str:id>', views.viewjob, name='viewjob'),
    path('delete/<str:id>', views.deletejob, name='delete'),
    path('submitbid/<str:id>', views.submitbid, name='submitbid'),
    path('acceptbid/<str:id>', views.acceptbid, name='acceptbid'),
    path('deletebid/<str:id>', views.deletebid, name='deletebid'),
    path('rejectbid/<str:id>', views.rejectbid, name='rejectbid'),
    path('bidderinfo/<str:id>', views.bidderinfo, name='bidderinfo'),
    path('acceptbid/<str:id>', views.acceptbid, name='acceptbid'),
    path('rejectbid/<str:id>', views.rejectbid, name='rejectbid'),
    path('clientdashboard/', views.clientdashboard, name='clientdashboard'),
    path('signin/',views.signin,name='signin'),
    path('signout/', views.signout, name='signout'),
]