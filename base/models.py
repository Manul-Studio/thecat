from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save



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

    profile_image = models.ImageField(null=True, blank=True, upload_to="images/")

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

class Hashtag(models.Model):
    description = models.TextField(unique=True)
    def __str__(self):
        return self.description
class Location(models.Model):
    address = models.CharField(max_length=200,blank=True, null=True)
    latitude = models.CharField(max_length=200,blank=True, null=True)
    longitude = models.CharField(max_length=200,blank=True, null=True)
    city = models.CharField(max_length=200,blank=True, null=True)
    zipcode = models.CharField(max_length=200,blank=True, null=True)
    country = models.CharField(max_length=200,blank=True, null=True)
    place_id = models.CharField(max_length=200,blank=True, null=True)
    street_name = models.CharField(max_length=200,blank=True, null=True)
    street_number = models.CharField(max_length=200,blank=True, null=True)

    def __str__(self):
        return f"{self.city}, {self.country}"
    
class Post(models.Model):
    hashtags = models.ManyToManyField(Hashtag, blank=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='likes') 
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    liked = True
    @property
    def total_likes(self):
        return self.likes.count()
    class Meta:
        ordering = ['-created','-updated' ] #od najnowszego

    def __str__(self):
        name_str = self.name if self.name else "No Name"
        location_str = str(self.location) if self.location is not None else "No Location"
        return f"{name_str} - {location_str}"
    
    def isLikedByUser(self, user_id) ->bool:
        return self.likes.filter(id=user_id).exists()

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
    
