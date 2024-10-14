from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Plans(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=False)
    plan_name = models.CharField(max_length=200)
    plan= models.TextField(null=True)
    def __str__(self) -> str:
        return self.user.username

class WorkoutTutorial(models.Model):
    name = models.CharField(max_length=300)
    link = models.URLField()
    def __str__(self) -> str:
        return self.name

class Nutrition(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=False)
    date = models.DateField(auto_now_add=True)
    sugar_g = models.IntegerField(default=0)
    fiber_g = models.IntegerField(default=0)
    serving_size_g = models.IntegerField(default=0)
    sodium_mg = models.IntegerField(default=0)
    potassium_mg = models.IntegerField(default=0)
    fat_saturated_g = models.IntegerField(default=0)
    fat_total_g = models.IntegerField(default=0)
    calories = models.IntegerField(default=0)
    cholesterol_mg = models.IntegerField(default=0)
    protein_g = models.IntegerField(default=0)
    carbohydrates_total_g = models.IntegerField(default=0)

class Food(models.Model):
    nutrition = models.ForeignKey(Nutrition,on_delete=models.CASCADE,null=False,blank=False)
    food = models.TextField(null=False,blank=False)



