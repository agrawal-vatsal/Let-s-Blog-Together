from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class BlogUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)


    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def __eq__(self, other):
        return self.user_id == other.user_id


class Post(models.Model):
    author = models.ForeignKey('blog.BlogUser', related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now())
    publish_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    def publish(self):
        self.publish_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={'pk': self.pk})

    def approve_comments(self):
        return self.comments.filter(approved_comment=True)



class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=256)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now())
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse("post_list")
