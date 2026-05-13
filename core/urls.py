from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # autenticação JWT
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # apps
    path('api/usuarios/', include('apps.usuarios.urls')),
    path('api/hortas/', include('apps.hortas.urls')),
    path('api/missoes/', include('apps.missoes.urls')),
    path('api/recompensas/', include('apps.recompensas.urls')),
    path('api/loja/', include('apps.loja.urls')),
    path('api/conquistas/', include('apps.conquistas.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
