from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to='uploads/%Y/%m')


class Category(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return self.name


class ModelBase(models.Model):
    subject = models.CharField(max_length=255, null=False)
    image = models.ImageField(upload_to='courses/%Y/%m', default=None)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.subject

    class Meta:
        abstract = True


class Article(ModelBase):
    class Meta:
        unique_together = ('subject', 'category')
        ordering = ["-id"]

    content = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True)
    tags = models.ManyToManyField('Tags', related_name="tags", blank=True, null=True)


class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Comment(models.Model):
    content = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class ActionBase(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        unique_together = ("article", "creator")


class Action(ActionBase):
    LIKE, HAHA, HEART = range(3)
    ACTIONS = [
        (LIKE, 'like'),
        (HAHA, 'haha'),
        (HEART, 'heart')
    ]
    type = models.PositiveSmallIntegerField(choices=ACTIONS, default=LIKE)


class Rating(ActionBase):
    rate = models.PositiveSmallIntegerField(default=0)


class ArticleView(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    article = models.OneToOneField(Article, on_delete=models.CASCADE)