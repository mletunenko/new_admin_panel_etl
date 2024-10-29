from django.urls import path
from movies.api.v1.views import MoviesDetailApi, MoviesListApi

urlpatterns = [
    path('movies/<str:pk>/', MoviesDetailApi.as_view()),
    path('movies/', MoviesListApi.as_view()),
]
