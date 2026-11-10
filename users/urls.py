from django.urls import path
from .views import RegisterView,UserDetail,UpdateProfile,changePassword

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('profile/',UserDetail.as_view(),name='user-profile'),
    path('update-profile/',UpdateProfile.as_view(),name='update-profile'),
    path('change-pass/',changePassword.as_view(),name='change-password')
]