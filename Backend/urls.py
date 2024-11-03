from django.contrib import admin
from django.urls import path,include
from rest_framework.response import Response
from django.conf import settings
from django.conf.urls.static import static 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from app.views import *
from rest_framework import status


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='Home'),
    path('register/',UserAPI.as_view(),name='user-related'),
    path('user/',LoginAPI.as_view(),name='login api view'),
    path('logout/',Logout,name="Logging Out"),
    path('myplans/',myPlans,name='My Plans'),
    path('callgpt/',call_gpt_with_prompt,name='Calling openAI'),
    path('tutorials/',getTutorials,name='Extracting workout tutorials'),
    path('searchworkout/',searchWorkout.as_view(),name='Searching specific Workout'),
    path('deleteplan/<str:id>/',deletePlan,name='Delete Specific Plan'),
    path('postnutrition/',nutrition,name='Adding nutrition value to Object'),
    path('getnutrition/',getnutrition,name='Get All nutrition objects of a user'),
    path('getnutritionbyid/<str:id>/',getNutritionById,name='Get nutrition objects by id'),
    path('getfoods/<str:id>/',getFoods,name='Getting all Food related to a nutrition object'),
    path('getworkout/',exerciseDB),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)

urlpatterns+=staticfiles_urlpatterns()
