from . import views
from django.urls import path
from . import webauthn_views
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('<int:tweet_id>/edit/', views.tweet_edit, name='tweet_edit'),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html', authentication_form=CustomLoginForm), name='login'),
    # 🔐 Image decryption and display route
    path('image/<int:tweet_id>/', views.view_tweet_image, name='view_tweet_image'),
    # path('start-registration/', webauthn_views.start_registration, name='start_registration'),
    # path('finish-registration/', webauthn_views.finish_registration, name='finish_registration'),
    # path('start-authentication/', webauthn_views.start_authentication, name='start_authentication'),
    # path('finish-authentication/', webauthn_views.finish_authentication, name='finish_authentication'),
    # path('fingerprint-register/', webauthn_views.fingerprint_register_view, name='fingerprint_register'),

]
