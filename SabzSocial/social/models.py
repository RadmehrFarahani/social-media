from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from taggit.managers import TaggableManager
from django.urls import reverse
# Create your models here.


class User(AbstractUser):
    date_of_birth=models.DateField(verbose_name="تاریخ تولد",blank=True,null=True)
    bio=models.TextField(blank=True,null=True,verbose_name="بایو")
    photo=models.ImageField(verbose_name="تصویر",upload_to="account_images/" ,blank=True,null=True)
    job=models.CharField(blank=True,null=True,verbose_name="شغل")
    phone=models.CharField(max_length=11,blank=True,null=True)
    following=models.ManyToManyField('self',through='Contact',related_name='followers',symmetrical=False)
    def get_absolute_url(self):
        return reverse('social:user_detail',args=[self.username])

class Post (models.Model):

    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_posts",verbose_name="نویسنده")
    description=models.TextField(verbose_name="توضیخات")
    created=models.DateField(auto_now_add=True)
    updated=models.DateField(auto_now=True)
    likes=models.ManyToManyField(User,related_name="liked_posts",blank=True)
    total_likes=models.PositiveIntegerField(default=0)
    active=models.BooleanField(default=True)
    tags = TaggableManager()

    class Meta:
        ordering=['-created']
        indexes=[
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes'])
        ]
        verbose_name="پست"
        verbose_name_plural="پست ها"


    def __str__(self):
        return self.author.first_name

    def get_absolute_url(self):
        return reverse('social:post_detail',args=[self.id])


class Contact(models.Model):
    user_from = models.ForeignKey(User,related_name='rel_from_set',on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes=[
            models.Index(fields=['-created'])
        ]
        ordering=['-created']

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"
