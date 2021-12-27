from rest_framework import viewsets, generics, status, permissions
from rest_framework.views import APIView
from .models import Category, User, Article, Tags, Comment, Action, Rating, ArticleView
from .serializers import CategorySerializer, UserSerializer, ArticleSerializer, ArticleDetailSerializer, CommentSerializer, ActionSerializer, RatingSerializer, ArticleViewSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .paginator import BasePagination
from django.conf import settings
from django.http import Http404
from django.db.models import F


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ArticlePostViewSet(viewsets.ViewSet):
    queryset = Article.objects.filter(active=True)
    serializer_class = ArticleSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    def list(self, request):
        articles = Article.objects.filter(active=True)
        serializer = ArticleSerializer(articles, many=True)

        return Response(data=serializer.data)

    def create(self, request):
        d = request.data
        file = request.data['file']
        if d:
            l = Article.objects.create(subject=d['subject'],
                                        content=d['content'],
                                        creator=request.user)

            serializer = ArticleSerializer(l)
            return Response(serializer.data,
                        status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ArticleViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer
    queryset = Article.objects.filter(active=True)
    pagination_class = BasePagination

    def get_permissions(self):
        if self.action in ['add_comment', 'take_action', 'rate']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path="tags")
    def add_tag(self, request, pk):
        try:
            article = self.get_object()
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            tags = request.data.get("tags")
            if tags is not None:
                for tag in tags:
                    t, _ = Tags.objects.get_or_create(name=tag)
                    article.tags.add(t)

                article.save()

                return Response(self.serializer_class(article).data,
                                status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True, url_path="add-comment")
    def add_comment(self, request, pk):
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content,
                                       article=self.get_object(),
                                       creator=request.user)

            return Response(CommentSerializer(c, context={"request": request}).data,
                            status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='like')
    def take_action(self, request, pk):
        try:
            action_type = int(request.data['type'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            action = Action.objects.create(type=action_type,
                                           creator=request.user,
                                           article=self.get_object())

            return Response(ActionSerializer(action).data,
                            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='rating')
    def rate(self, request, pk):
        try:
            rating = int(request.data['rating'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            r = Rating.objects.update_or_create(creator=request.user,
                                                article=self.get_object(),
                                                defaults={"rate": rating})

            return Response(RatingSerializer(r).data,
                            status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='views')
    def inc_view(self, request, pk):
        v, created = ArticleView.objects.get_or_create(article=self.get_object())
        v.views = F('views') + 1
        v.save()

        # v.views = int(v.views)
        v.refresh_from_db()

        return Response(ArticleViewSerializer(v).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path="comments")
    def get_comments(self, request, pk):
        l = self.get_object()
        return Response(
            CommentSerializer(l.comment_set.order_by("-id").all(), many=True, context={"request": self.request}).data,
            status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path="current-user")
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user, context={"request": request}).data,
                        status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView,
                     generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().creator:
            return super().destroy(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().creator:
            return super().partial_update(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)