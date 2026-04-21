from django.urls import path
from . import views

app_name = "workers"

urlpatterns = [
    path("", views.WorkerListCreateView.as_view(), name="worker_list_create"),
    path("<int:pk>/", views.WorkerDetailView.as_view(), name="worker_detail"),
    path("<int:pk>/services/", views.WorkerServicesView.as_view(), name="worker_services"),
    path("<int:pk>/reviews/", views.WorkerReviewsView.as_view(), name="worker_reviews"),
]
