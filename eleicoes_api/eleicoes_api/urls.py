from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from urna.views import (EleitorViewSet, EleicaoViewSet, CandidatoViewSet, AptidaoEleitorViewSet, RegistroVotacaoViewSet, VotoViewSet)

router = DefaultRouter()

router.register(r'eleitores', EleitorViewSet)
router.register(r'eleicoes', EleicaoViewSet)
router.register(r'candidatos', CandidatoViewSet)
router.register(r'aptidoes', AptidaoEleitorViewSet)
router.register(r'registros-votacao', RegistroVotacaoViewSet)
router.register(r'votos', VotoViewSet)

schema_view = get_schema_view(
    openapi.Info(title="API de Eleições", 
        default_version='v1', 
        description="Documentação da API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('swagger/',schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
