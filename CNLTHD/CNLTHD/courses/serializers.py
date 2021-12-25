from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Category, User, Article, Tags, Comment, Action, Rating, ArticleView


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TagsSerializer(ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"


class ArticleSerializer(ModelSerializer):
    image = SerializerMethodField()

    def get_image(self, course):
        request = self.context.get("request")
        name = course.image.name
        if name.startswith("static/"):
            path = '/%s' % name
        else:
            path = '/static/%s' % name

        return request.build_absolute_uri(path)

    class Meta:
        model = Article
        fields = ["id", "subject", "image", "created_date", "updated_date", "creator", "category"]


class ArticleDetailSerializer(ArticleSerializer):
    tags = TagsSerializer(many=True)
    rate = SerializerMethodField()

    def get_rate(self, lesson):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            r = lesson.rating_set.filter(creator=request.user).first()
            if r:
                return r.rate

        return -1

    class Meta:
        model = ArticleSerializer.Meta.model
        fields = ArticleSerializer.Meta.fields + ['content', 'tags', "rate"]


class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField()

    def get_avatar(self, user):
        request = self.context['request']
        if user.avatar:
            name = user.avatar.name
            if name.startswith("static/"):
                path = '/%s' % name
            else:
                path = '/static/%s' % name

            return request.build_absolute_uri(path)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "avatar",
                  "username", "password", "email", "date_joined"]
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }


class CommentSerializer(ModelSerializer):
    creator = SerializerMethodField()

    def get_creator(self, comment):
        return UserSerializer(comment.creator, context={"request": self.context.get('request')}).data

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'updated_date', 'creator']


class ActionSerializer(ModelSerializer):
    class Meta:
        model = Action
        fields = ["id", "type", "created_date"]


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "rate", "created_date"]


class ArticleViewSerializer(ModelSerializer):
    class Meta:
        model = ArticleView
        fields = ["id", "views", "lesson"]