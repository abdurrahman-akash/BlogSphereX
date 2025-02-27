from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views

urlpatterns = [
    path('user/token/', api_views.MyTokenObtainPairView.as_view()),
    path('user/token/refresh/', TokenRefreshView.as_view()),
    path('user/register/', api_views.RegisterView.as_view()),
    path('user/profile/<int:user_id>/', api_views.ProfileView.as_view()),

    # Post Endpoints
    path('post/category/list/', api_views.CategoryListAPIView.as_view()),
    path('post/category/posts/<category_slug>/', api_views.PostCategoryListAPIView.as_view()),
    path('post/list/', api_views.PostListAPIView.as_view()),
    path('post/detail/<slug>/', api_views.PostDetailAPIView.as_view()),
    path('post/like/', api_views.LikePostAPIView.as_view()),
    path('post/comment/', api_views.PostCommentAPIView.as_view()),
    path('post/bookmark/', api_views.BookmarkPostAPIView.as_view()),

    # Dashboard Endpoints
    path('author/dashboard/stats/<user_id>/', api_views.DashboardStats.as_view()),
    path('author/dashboard/comment-list/<user_id>/', api_views.DashboardCommentLists.as_view()),
    path('author/dashboard/notification-list/<user_id>/', api_views.DashboardNotificationLists.as_view()),
    path('author/dashboard/notification-mark-seen/', api_views.DashboardMarkNotificationAsSeen.as_view()),
    path('author/dashboard/reply-comment/', api_views.DashboardReplyCommentAPIView.as_view()),

    # Dashboard Post Endpoints
    path('author/dashboard/create-post/', api_views.DashboardPostCreateAPIView.as_view()),
    path('author/dashboard/update-post/<user_id>/<post_id>/', api_views.DashboardPostUpdateAPIView.as_view()),
]
