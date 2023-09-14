from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime


User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="profile")
    id_user = models.IntegerField()
    bio = models.TextField(blank=True) #peut laisser le bio vide 
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.jpg')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name="pprofile")
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    #renvoie le nom de l'utilisateur qui a créé la publication.
    def get_owner_pp(self):
        return self.author.profile.profileimg.url
    def __str__(self):
        return self.author.username


class LikePost(models.Model):
    #champ qui stocke l'identifiant du post aimé
    post_id = models.CharField(max_length=500)
    #champ qui stocke le nom d'utilisateur de l'utilisateur qui a aimé le post
    username = models.CharField(max_length=100)

    #afficher le nom d'utilisateur lors de l'affichage d'une instance de LikePost.
    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    #stocke le nom d'utilisateur de l'utilisateur qui suit l'utilisateur associé
    follower = models.ForeignKey(User, on_delete=models.CASCADE,related_name='follower')
    #stocke le nom d'utilisateur de l'utilisateur suivi
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    def getMyFollowers (username):
        try:
            followers_list = FollowersCount.objects.filter(follower=username)
            return followers_list
        except FollowersCount.DoesNotExist:
            followers_list = None    
        
    def __str__(self):
        return self.user.username