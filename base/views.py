from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.messages import constants as messages
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, Topic, User, Message, Profile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404

from .forms import PostForm, MyUserCreationForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist.")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):

    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    posts = Post.objects.filter(
        Q(topic__name__icontains=q) |  # to albo to
        Q(name__icontains=q) |
        Q(description__icontains=q)

    )

    topics = Topic.objects.all()
    post_count = posts.count()

    # only activity related to the topic
    post_messages = Message.objects.filter(Q(post__topic__name__icontains=q))

    context = {'posts': posts, 'topics': topics,
               'post_count': post_count, 'post_messages': post_messages}
    return render(request, 'base/home.html', context)


def post(request, pk):
    post = Post.objects.get(id=pk)
    # model name lowercase, give set of messages related to the specific post
    post_messages = post.message_set.all()
    participants = post.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            post=post,
            body=request.POST.get('body')
        )
        post.participants.add(request.user)
        return redirect('post', pk=post.id)



    context = {'post': post, 'post_messages': post_messages,
               'participants': participants}
    return render(request, 'base/post.html', context)


@login_required
def likePost(request):
    if request.method == 'POST' and request.is_ajax():
        if request.POST.get('action') == 'post':
            flag = None
            postid = int(request.POST.get('post_id'))
            post_obj = get_object_or_404(Post, id=postid)

            if post_obj.likes.filter(id=request.user.id).exists():
                post_obj.likes.remove(request.user)
                post_obj.save()
                flag = False
            else:
                post_obj.likes.add(request.user)
                post_obj.save()
                flag = True

            return JsonResponse({'total_likes': post_obj.total_likes, 'flag': flag, })
        return HttpResponse("Error access denied")


def userProfile(request,pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        user = User.objects.get(id=pk)
        posts = user.post_set.all()
        post_messages = user.message_set.all()

        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST['follow']
            #follow or unfollow
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            elif action == 'follow':
                current_user_profile.follows.add(profile)
            current_user_profile.save()


        context={'profile':profile, 'posts':posts, 'post_messages':post_messages}
        return render(request, 'base/profile.html', context)
    else: 
        messages.success(request, ("you must be logged in"))
        return redirect('home')


def listProfile(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user) #dont show logged user profile
        context={'profiles':profiles}
        return render(request, 'base/profile_list.html', context)
    else:
        messages.success(request, ("you must be logged in"))
        return redirect('home')


@login_required(login_url='login')
def createPost(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)  # passing all the data into the form
        if form.is_valid():
            post = form.save(commit=False)  # saving in the database
            post.host = request.user  # host will be added based on whoever is logged in
            post.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/post_form.html', context)


@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)  # form bedzie wypełniony poprzednimi info

    if request.user != post.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        # zeby zupdateowało właściwy post a nie dodawalo nowy
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/post_form.html', context)


@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)

    if request.user != post.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': post})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})
