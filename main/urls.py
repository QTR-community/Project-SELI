from django.urls import path
from .views import CreateProfile, UpdateProfile, get_area_status

urlpatterns = [
    # REST API endpoints
    path("api/profiles/", CreateProfile.as_view(), name="create_profile"),
    path("api/profiles/<str:pk>/", UpdateProfile.as_view(), name="update_profile"),
    path("api/surveys/<str:city>/<str:street>/", get_area_status, name="get_area_status"),
]
