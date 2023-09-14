from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
#pour afficher les message d'erreurs 
from django.contrib import messages
from django.http import HttpResponse
#obliger l'utilisateur de se connecter s'il n'est pas connecter
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, send_mail
from django.conf import settings

#avant de passer a la page d'accueil il faut que l'utilisateur est connecter
@login_required(login_url='signin')
def index(request):
    #récupère l'utilisateur connecté actuel à partir de l'objet request. 
    user_object = User.objects.get(username=request.user)
    #récupère le profil d'utilisateur associé à l'utilisateur connecté actuel.
    user_profile = Profile.objects.get(user=request.user)

    user_following_list = []
    feed = []

    user_following = FollowersCount.getMyFollowers(user_object)
    for user in user_following:
        user = User.objects.get(username=user)
        feed_lists = Post.objects.filter(author=user)

        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in user_following_all)]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)


    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    #il renvoie l'utilisateur connecté avec le Profile associé à la page d'accueil index.html en utilisant la fonction render.
    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})



@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user_object = User.objects.get(username=request.user)
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(author=user_object, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)
        
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def like_post(request):
    #récupérer le nom de user et l'id de post
    username = request.user.username
    post_id = request.GET.get('post_id')

    #recherche la publication correspondante dans la base de données
    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        # Si l'utilisateur n'a pas aimé la publication auparavant
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        #le nombre total de likes de la publication est incrémenté de 1 
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        #supprimé pour enlever le like
        like_filter.delete()
        #le nombre total de likes de la publication est décrémenté de 1
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(author=user_object)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk
    follower1 = user_object = User.objects.get(username=follower)
    user1 = user_object = User.objects.get(username=user)
    if FollowersCount.objects.filter(follower=follower1, user=user1).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=user1))
    user_following = len(FollowersCount.objects.filter(follower=follower1))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    
    

    return render(request, 'profile.html', context)


#Ce code implémente une vue follow qui permet de suivre ou d'arrêter de suivre
#un utilisateur spécifique.
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        #vérifie si un FollowersCountobjet existe déjà
        #avec les mêmes valeurs followeret user
        follower1 = user_object = User.objects.get(username=follower)
        user1 = user_object = User.objects.get(username=user)
        if FollowersCount.objects.filter(follower=follower1, user=user1).first():
            #uppriment l' FollowersCountobjet existant et
            #redirigent l'utilisateur vers la page de profil du user.
            delete_follower = FollowersCount.objects.get(follower=follower1, user=user1)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            #créent un nouvel FollowersCountobjet avec
            #les valeurs followeret useret l'enregistrent dans la base de données.
            new_follower = FollowersCount.objects.create(follower=follower1, user=user1)
            new_follower.save()
            #L'utilisateur est alors redirigé vers la page de profil du user.
            return redirect('/profile/'+user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def setting(request):

    #récupère le profil d'utilisateur associé à l'utilisateur connecté actuel.
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        
        #pas  d'image a envoyer(l'image par défaut reste)
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('setting')

        #renvoie une réponse HTTP qui affiche le modèle "setting.html" avec le contexte spécifié.
    return render(request, 'setting.html', {'user_profile': user_profile})



def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            #email déjà existe:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            #username déjà existe
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('setting')

        else:
             messages.info(request, 'Password Not Matching')
             return redirect('signup')


    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']


        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')
def forgetpassword(request):
    password_reset_form = PasswordResetForm(request.POST)
    if password_reset_form.is_valid():
        data = password_reset_form.cleaned_data['email']
        associated_users = User.objects.filter(Q(email=data))
        domain = request.headers['Host']

        print(associated_users)
        for user in associated_users:
                    email_template_name = "forgetpassword_template.html"
                    subject = "Password Reset Requested"
                    c = {
                        "email": user.email,
                        'site_name': 'Interface',
                        'domain': domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)

                    try:
                        send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="forgetpassword.html",
                  context={"password_reset_form": password_reset_form})

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')