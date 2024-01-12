from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.messages import constants as messages
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, User, Message, Profile, Hashtag, Location
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from .forms import PostForm, MyUserCreationForm, ProfilePicForm
from django.conf import settings
import googlemaps
import json



def map(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        city = data.get('city')
        zipcode = data.get('zipcode')
        country = data.get('country')
        place_id = data.get('place_id')
        street_name = data.get('street_name')
        street_number = data.get('street_number')

        address = str(street_name)+" "+str(street_number)+", "+str(zipcode) +" "+str(city) + ", " +str(country)

        Location.objects.create(latitude=latitude, longitude=longitude, city=city, zipcode=zipcode, country=country, place_id=place_id, street_name=street_name, street_number=street_number, address=address)

        return JsonResponse({'message': 'Location saved successfully'})
    
    locations = Location.objects.all()
    
    
    key= settings.GOOGLE_API_KEY
    context={'key':key, 'locations':locations}
    return render(request, 'base/map.html', context)

def mapLocations(request):
    locations = Location.objects.all()
    context={'locations':locations}
    return render(request, 'base/map_locations.html', context)

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
            user = form.save(commit=False) #freezing data, example user added username uppercase so we want to make username lowercase
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, ("You have successfully registered!"))
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    posts = Post.objects.filter(
         # to albo to
        Q(name__icontains=q) |
        Q(description__icontains=q)|
        Q(host__name__icontains=q)

    )
    

    
    post_count = posts.count()
    hashtags = Hashtag.objects.all()
    
   
   
    # only activity related to the topic
    post_messages = Message.objects.all()

    context = {'posts': posts, 'post_count': post_count, 'post_messages': post_messages, 'hashtags':hashtags }
    return render(request, 'base/home.html', context)


def post(request, pk):
    post = Post.objects.get(id=pk)
    # model name lowercase, give set of messages related to the specific post
    post_messages = post.message_set.all()
    participants = post.participants.all()

    post_obj = get_object_or_404(Post, pk=pk)
    flag = False
    if post_obj.likes.filter(id=request.user.id).exists():
       flag = True
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            post=post,
            body=request.POST.get('body')
        )
        post.participants.add(request.user)
        return redirect('post', pk=post.id)



    context = {'post': post, 'post_messages': post_messages,
               'participants': participants, 'flag':flag}
    return render(request, 'base/post.html', context)


@login_required
def likePost(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
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
def hashtag(request, hash_pk):
    hashtag = get_object_or_404(Hashtag, pk=hash_pk)
    posts = hashtag.post_set.order_by('-pk')
    context={'hashtag':hashtag, 'posts':posts}
    return render(request, 'base/hashtag.html', context)

@login_required(login_url='login')
def createPost(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # passing all the data into the form
        image= request.FILES.get('image')
        if form.is_valid():
            post = form.save(commit=False)  # saving in the database
            post.host = request.user  # host will be added based on whoever is logged in
            post.save()
            for word in post.description.split():
                if word.startswith('#'):
                    hashtag_text = word[1:]
                    hashtag, created = Hashtag.objects.get_or_create(description=hashtag_text)
                    post.hashtags.add(hashtag)

            messages.success(request, ("Posted a cat!"))
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
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            post.hashtags.clear()
            for word in post.description.split():
                if word.startswith('#'):
                    hashtag_text = word[1:]
                    hashtag, created = Hashtag.objects.get_or_create(description=hashtag_text)
                    post.hashtags.add(hashtag)
            return redirect('home')

    context = {'form': form, 'post':post}
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


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    profile = request.user
    user_form = MyUserCreationForm(instance=user)
    profile_form = ProfilePicForm(instance=user)

    if request.method == 'POST':
        user_form = MyUserCreationForm(request.POST, instance=user)
        profile_form = ProfilePicForm(request.FILES, instance=user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'user_form':user_form, 'profile_form':profile_form})

    # current_user = User.objects.get(id=request.user.id)
    # profile_user = Profile.objects.get(user__id=request.user.id)
    # user_form = MyUserCreationForm(request.POST or None, request.FILES or None, instance=current_user)
    # profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
    # if request.method == 'POST':
        
    #     if user_form.is_valid() and profile_form.is_valid():
    #         user_form.save()
    #         profile_form.save()

    #         login(request, current_user)
    #         messages.success(request, ("Your profile has been updated!"))
    #         return redirect('home')

    # context={'user_form':user_form, 'profile_form':profile_form}
    # return render(request, 'base/update-user.html', context)


