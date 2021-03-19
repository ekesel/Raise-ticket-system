from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify

# Create your models here.
class Feedback(models.Model):
    userid = models.IntegerField()
    feed = models.CharField(max_length=200)

    def __str__(self):
        us = User.objects.get(id=self.userid)
        return "Feedback by: "+us.username

    class Meta:
        verbose_name_plural = "Feedback by Users"

class Post(models.Model):
	title = models.CharField(max_length = 50)
	overview = models.TextField()
	slug = models.SlugField(null=True, blank=True)
	body_text = RichTextUploadingField(null=True)
	time_upload = models.DateTimeField(auto_now_add = True)
	auther = models.ForeignKey(User, on_delete=models.CASCADE)
	read = models.IntegerField(default = 0)

	class Meta:
		ordering = ['-pk']

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Post, self).save(*args, **kwargs)

class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now_add=True)
	comm = models.TextField()

class SubComment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now_add=True)
	comm = models.TextField()
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mob = models.CharField(max_length=12)
    mess = models.TextField()
    time = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return "Contact by: "+self.name