from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]

class Profile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    follows= models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True) #symetrical= i can follow you but you dont have to follow me, blank=ou dobt have to follow anybody, related_name-opposite of follows

    date_modified = models.DateTimeField(User, auto_now=True)
    def __str__(self):
        return self.user.username

def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        #have a user follow themselves
        user_profile.follows.set([instance.profile.id])
        user_profile.save()


post_save.connect(create_profile, sender=User)    #whenever a new user is posted as saved we wanna connect do the profile


class Post(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='likes') 

    @property
    def total_likes(self):
        return self.likes.count()
    class Meta:
        ordering = ['-updated', '-created'] #od najnowszego

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE) # jak usuwamy post to wszystkie wiado tez
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
        ordering = ['-updated', '-created'] #od najnowszego

    def __str__(self):
        return self.body[0:50]
    