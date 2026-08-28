''''define the URL modes in with_art'''

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'with_art'

urlpatterns = [
    # frontpage
    path('', views.index, name='home'),
    path('homepage/', views.index, name='home'),
    #path("artist/", views.index, name="index"),  
    
    # show the title of the art projects
    path('projects/', views.artprojects, name='artprojects'),
    #path('image/', views.image_list, name='image_list'),
    #path('image/upload/', views.upload_image, name='upload_image'),
    #path('image/edit/<int:id>/', views.edit_image, name='edit_image'),
    # details of art projects
    path("artprojects/<slug:slug>/", views.artproject, name="artproject"),
    path("current/", views.current_list, name="current_list"),    
    path("current/<slug:slug>/", views.currentproject, name="currentproject"),



    
    path('philo/', views.philo_view, name='philo'),
    path('contact/', views.contact_view, name='contact'),
    path('upload999899/', views.upload_artproject, name='upload_artproject'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)