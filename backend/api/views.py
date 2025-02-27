from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Sum

# Rest Framework
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

# other
import json
import random

# Custom Imports
from api import models as api_models
from api import serializer as api_serializers

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializers.MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = api_models.CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializers.RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.ProfileSerializer

    def get_object(self):
        from django.shortcuts import get_object_or_404
        user_id = self.kwargs['user_id']
        user = get_object_or_404(api_models.CustomUser, id=user_id)
        profile = get_object_or_404(api_models.Profile, user=user)
        return profile

# Post APIs Endpoints
class CategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializers.CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return api_models.Category.objects.all()
    
class PostCategoryListAPIView(generics.ListAPIView):
    serializer_class = api_serializers.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = api_models.Category.objects.get(slug=category_slug)
        return api_models.Post.objects.filter(category=category, status='Active')
    
class PostListAPIView(generics.ListAPIView):
    serializer_class = api_serializers.PostSerializer
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        return api_models.Post.objects.filter(status='Active')
    
class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializers.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs['slug']
        post = api_models.Post.objects.get(slug=slug, status='Active')
        post.views += 1
        post.save()
        return post

class LikePostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )
    def post(self, request):
        user_id = request.data['user_id']
        post_id = request.data['post_id']

        user = api_models.CustomUser.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({'message': 'Post Unliked'}, status=status.HTTP_200_OK)
        else:
            post.likes.add(user)
            
            api_models.Notification.objects.create(
                user=post.user,
                post=post,
                type='Like',
            )
            return Response({'message': 'Post Liked'}, status=status.HTTP_200_OK)

class PostCommentAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'comment': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request):
        post_id = request.data['post_id']
        name = request.data['name']
        email = request.data['email']
        comment = request.data['comment']

        post = api_models.Post.objects.get(id=post_id)

        api_models.Comment.objects.create(
            post = post,
            name = name,
            email = email,
            comment = comment,
        )

        api_models.Notification.objects.create(
            user = post.user,
            post = post,
            type = 'Comment',
        )

        return Response({'message': 'Comment Sent'}, status=status.HTTP_200_OK)
    
class BookmarkPostAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )
    def post(self, request):
        user_id = request.data['user_id']
        post_id = request.data['post_id']

        user = api_models.CustomUser.objects.get(id=user_id)
        post = api_models.Post.objects.get(id=post_id)

        bookmark = api_models.Bookmark.objects.filter(user=user, post=post).first()
        if bookmark:
            bookmark.delete()
            return Response({'message': 'Post Unbookmarked'}, status=status.HTTP_200_OK)
        else:
            api_models.Bookmark.objects.create(user=user, post=post)

            api_models.Notification.objects.create(
                user = post.user,
                post = post,
                type = 'Bookmark',
            )
            return Response({'message': 'Post Bookmarked'}, status=status.HTTP_200_OK)

class DashboardStats(generics.ListAPIView):
    serializer_class = api_serializers.AuthorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.CustomUser.objects.filter(id=user_id)
        return user

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        user = queryset.first()
        
        views = api_models.Post.objects.filter(user=user).aggregate(Sum('views'))['views__sum']
        posts = api_models.Post.objects.filter(user=user).count()
        likes = api_models.Post.objects.filter(user=user).aggregate(Sum('likes'))['likes__sum']
        bookmarks = api_models.Bookmark.objects.filter(post__user=user).count()

        data = {
            'views': views,
            'posts': posts,
            'likes': likes,
            'bookmarks': bookmarks,
        }
        
        return Response(data)
    
class DashboardPostLists(generics.ListAPIView):
    serializer_class = api_serializers.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.CustomUser.objects.get(id=user_id)
        return api_models.Post.objects.filter(user=user).order_by('-id')
    
class DashboardCommentLists(generics.ListAPIView):
    serializer_class = api_serializers.CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.CustomUser.objects.get(id=user_id)
        return api_models.Comment.objects.filter(post__user=user).order_by('-id')
    
class DashboardNotificationLists(generics.ListAPIView):
    serializer_class = api_serializers.NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.CustomUser.objects.get(id=user_id)
        return api_models.Comment.objects.all(seen=False, user=user)
    
class DashboardMarkNotificationAsSeen(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'noti_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        )
    )
    def post(self, request):
        noti_id = request.data['noti_id']
        user = api_models.CustomUser.objects.get(id=noti_id)
        notifications = api_models.Notification.objects.filter(user=user, seen=False)
        for notification in notifications:
            notification.seen = True
            notification.save()
        return Response({'message': 'Notifications Marked as Seen'}, status=status.HTTP_200_OK)
    
class DashboardReplyCommentAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'reply': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )

    def post(self, request):
        comment_id = request.data['comment_id']
        reply = request.data['reply']

        comment = api_models.Comment.objects.get(id=comment_id)
        comment.reply = reply
        comment.save()

        return Response({'message': 'Comment Replied'}, status=status.HTTP_200_OK)
    
class DashboardPostCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializers.PostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(request.data)

        user_id = request.data.get('user_id')
        title = request.data.get('title')
        image = request.data.get('image')
        content = request.data.get('content')
        tags = request.data.get('tags')
        category_id = request.data.get('category')
        post_status = request.data.get('post_status', 'Active')

        user = api_models.CustomUser.objects.get(id=user_id)
        category = api_models.Category.objects.get(id=category_id)

        api_models.Post.objects.create(
            user=user,
            category=category,
            title=title,
            image=image,
            content=content,
            tags=tags,
            status=post_status,
        )

        return Response({'message': 'Post Created Successfully'}, status=status.HTTP_200_OK)
    
class DashboardPostUpdateAPIView(generics.UpdateAPIView):
    serializer_class = api_serializers.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        post_id = self.kwargs['post_id']
        user = api_models.CustomUser.objects.get(id=user_id)
        return api_models.Post.objects.get(id=post_id, user=user)
    
    def update(self, request, *args, **kwargs):
        post_instance = self.get_object()

        title = request.data.get('title')
        image = request.data.get('image')
        content = request.data.get('content')
        tags = request.data.get('tags')
        category_id = request.data.get('category')
        post_status = request.data.get('post_status', 'Active')

        category = api_models.Category.objects.get(id=category_id)

        post_instance.title = title
        if image != "undefined":
            post_instance.image = image
        post_instance.content = content
        post_instance.tags = tags
        post_instance.category = category
        post_instance.status = post_status
        post_instance.save()

        return Response({'message': 'Post Updated Successfully'}, status=status.HTTP_200_OK)

