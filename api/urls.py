from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet
from .views import SignUpView

router = DefaultRouter()
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("signup/", SignUpView.as_view(), name="signup"),
]