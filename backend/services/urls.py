from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("", views.ServiceCategoryListView.as_view(), name="category_list"),
    path("<int:pk>/", views.ServiceCategoryDetailView.as_view(), name="category_detail"),
    path("<int:pk>/workers/", views.ServiceWorkersView.as_view(), name="service_workers"),
]
