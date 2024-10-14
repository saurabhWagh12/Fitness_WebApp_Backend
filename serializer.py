from rest_framework import serializers
from rest_framework import response
from app.models import *


class UserSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = '__all__'

class WorkoutTutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutTutorial
        fields = '__all__'

class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrition
        fields = '__all__'

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'