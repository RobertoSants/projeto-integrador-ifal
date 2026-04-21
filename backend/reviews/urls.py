from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.ReviewCreateView.as_view(), name="review_create"),
    path("<int:pk>/", views.ReviewDetailView.as_view(), name="review_detail"),
]
