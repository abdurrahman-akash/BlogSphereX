from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
import shortuuid

class CustomUser(AbstractUser):
    username = models.CharField(unique=True, max_length=255)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        email_username, mobile = self.email.split('@')
        if self.full_name == "" or self.full_name == None:
            self.full_name = email_username
        if self.username == "" or self.username == None:
            self.username = email_username

        super(CustomUser, self).save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profiles/', default='profiles/default.jpg', null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    about = models.CharField(max_length=255, null=True, blank=True)
    author = models.BooleanField(default=False)
    country = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    github = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = ShortUUIDField()


    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.full_name

        super(Profile, self).save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=CustomUser)
post_save.connect(save_user_profile, sender=CustomUser)


class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="image", null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.title
    
    # class Meta:
    #     verbose_name_plural = 'Categories'
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def post_count(self):
        return Post.objects.filter(category=self).count()

class Post(models.Model):

    STATUS = (
        ('Active', 'Active'),
        ('Draft', 'Draft'),
        ('Disabled', 'Disabled'),
    )


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to="image", null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=255, default='Active')
    view = models.IntegerField(default=0)
    likes = models.ManyToManyField(CustomUser, blank=True, related_name="likes_user")
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Posts'
    
    def save(self, *args, **kwatgs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + shortuuid.uuid()[:2]
        super(Post, self).save(*args, **kwatgs)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    comment = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Comments'


class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Bookmark'

class Notification(models.Model):
    NOTI_TYPE = (
        ('Like', 'Like'),
        ('Comment', 'Comment'),
        ('Bookmark', 'Bookmark'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    type = models.CharField(choices=NOTI_TYPE, max_length=255)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.post:
            return f"{self.post.title} - {self.type}"
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Notification'
    