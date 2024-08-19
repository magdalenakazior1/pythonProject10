# from_gamers_4_gamers/urls.py
from django.contrib import admin
from django.urls import path, include
from store.views import CustomLoginView, register
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView  # Import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),  # Corrected line
    path('accounts/register/', register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),  # Include built-in auth-related URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
