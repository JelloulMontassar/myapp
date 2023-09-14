from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('setting', views.setting, name='setting'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    # URL pour la vue profile qui prend un argument de chemin nommé pk (Primary Key)
    #(exemple:http://localhost:8000/profile/1)
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('forgetpassword', views.forgetpassword, name='forgetpassword'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
template_name="password_reset_confirm.html"), name='password_reset_confirm'),
 
path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
template_name='password_reset_done.html'), name='password_reset_done'),
path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
template_name='password_reset_complete.html'), name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)