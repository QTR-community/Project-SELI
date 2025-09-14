"""
URL configuration for Light2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from main.socketsio_docs import socketio_events
from .views import HomePageView
import json

# Build socket.io documentation string manually
schema_view = get_schema_view(
    openapi.Info(
        title="Light Survey API",
        default_version="v1",
        description="REST + Socket.IO documentation for Light2 project",
        contact=openapi.Contact(email="support@light2.local"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # ✅ must be tuple
)

# ✅ Build Socket.IO documentation dynamically
socketio_docs = "\n\n## 🔌 Socket.IO Events\n"
for event in socketio_events:
    payload = json.dumps(event.get("payload", {}), indent=2)
    response = json.dumps(event.get("response", {}), indent=2)
    socketio_docs += f"""
### `{event.get('event', 'unknown-event')}`
**{event.get('description', 'No description available.')}**

- **Payload**:
```json
{payload}"""

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("", HomePageView.as_view(), name="home"),

    # Swagger + Redoc
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
