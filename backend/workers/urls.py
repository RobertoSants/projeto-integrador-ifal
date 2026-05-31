from django.urls import path
from . import views

app_name = "workers"

urlpatterns = [
    path("", views.WorkerListCreateView.as_view(), name="worker_list_create"), # ROTA CRUCIAL ADICIONADA
    path("me/", views.MyProfileView.as_view(), name="worker_my_profile"), # ROTA CRUCIAL ADICIONADA
    path("<int:pk>/", views.WorkerDetailView.as_view(), name="worker_detail"),
    path("<int:pk>/services/", views.WorkerServicesView.as_view(), name="worker_services"),
    path("<int:pk>/reviews/", views.WorkerReviewsView.as_view(), name="worker_reviews"),
    path("optimize-bio/", views.OptimizeBioView.as_view(), name="optimize_bio"), 
]