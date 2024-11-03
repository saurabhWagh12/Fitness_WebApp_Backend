from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from serializer import *
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
import requests
import datetime
from django.db.models import Q
from .models import *
from rest_framework import generics,status

import os
import google.generativeai as genai

genai.configure(api_key='')

@api_view(['POST'])
def call_gpt_with_prompt(request):
    print('hi')
    try:
        prompt = request.data['data']
        nameOfPlan = request.data['name']
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        token = request.data.get('token')  # Use get to avoid KeyError
        if not token:
            return Response({'status': 400, 'message': 'Authentication failed'})
        try:
            # Verify the JWT token and decode the payload
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

            # Retrieve the user based on the user ID in the payload
            user = User.objects.filter(id=payload['id']).first()

        except jwt.ExpiredSignatureError:
            return Response({'status': 400, 'message': 'Token has expired'})

        except jwt.DecodeError:
            return Response({'status': 400, 'message': 'Token is invalid'})

        except Exception as e:
            return Response({'status': 400, 'message': 'Token Error: ' + str(e)})

        plan = Plans.objects.create(user=user,plan_name=nameOfPlan,plan=response.text)
        plan.save()
        # Return the generated text in a serializable format (JSON)
        return Response({'status': 200, 'data': response.text})

    except Exception as e:
        return Response({'status': 400, 'message': str(e)})
    
    
@api_view(['GET'])
def getTutorials(request):
    try:
        tutorials = WorkoutTutorial.objects.all()
        serializer = WorkoutTutorialSerializer(tutorials, many=True)

        return Response({'status':200,'data':serializer.data})

    except Exception as e:
        return Response({'status':400,'message':'Error in Tutorial extraction'})


def searchedResult(queryset):
    try:
        serializer = WorkoutTutorialSerializer(queryset, many=True)
        return {'status': 200, 'data': serializer.data}
    except:
        return {'status': 404, 'message': 'Not Found'}

class searchWorkout(generics.ListAPIView):
    serializer_class = WorkoutTutorialSerializer
    def get_queryset(self):
        queryset = WorkoutTutorial.objects.all()
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
        Q(name__icontains=search_query) | Q(link__icontains=search_query)
    )
    
        result = searchedResult(queryset)  # Serialize and store the result
        return result  # Return the result

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_code = queryset.get('status', 200)
        data = queryset.get('data', [])

        return Response({ 'status':status_code,'data':data})

@api_view(['POST'])
def exerciseDB(request):
    name = request.data['name']
    print(name)
    try:
        url = f"https://exercisedb.p.rapidapi.com/exercises/name/{name}"
        url = url.replace(' ', '%20')
        querystring = {"limit": "10", "offset": "0"}

        headers = {
            "x-rapidapi-key": "6411f1b1a5mshc8b65c411355acfp1d0b9cjsn63007d842c38",
            "x-rapidapi-host": "exercisedb.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad status codes

        return Response({'status': 200, 'data': response.json()})
    except requests.exceptions.RequestException as e:
        return Response({'status': 400, 'message': 'Request Error: ' + str(e)})
    except Exception as e:
        return Response({'status': 400, 'message': 'Token Error: ' + str(e)})
    

@api_view(['POST'])
def myPlans(request):
    token = request.data.get('token')  # Use get to avoid KeyError
    if not token:
        return Response({'status': 400, 'message': 'Authentication failed'})

    try:
        # Verify the JWT token and decode the payload
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        # Retrieve the user based on the user ID in the payload
        user = User.objects.filter(id=payload['id']).first()

    except jwt.ExpiredSignatureError:
        return Response({'status': 400, 'message': 'Token has expired'})

    except jwt.DecodeError:
        return Response({'status': 400, 'message': 'Token is invalid'})

    except Exception as e:
        return Response({'status': 400, 'message': 'Token Error: ' + str(e)})

    # Filter plans based on the user
    plans = Plans.objects.filter(user=user).order_by('-id')
    # Serialize the plans, many=True to handle multiple plans
    serializer = PlanSerializer(plans, many=True)
    
    # Return the serialized plan data in the response
    return Response({'status': 200, 'data': serializer.data})




@api_view(['GET'])
def home(request):
    # Get the token from the request's cookies
    token = request.COOKIES.get('token')
    print('token: '+token)
    if not token:
        return Response({'status': 400, 'message': 'Authentication failed'})

    try:
        # Verify the JWT token and decode the payload
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        # Retrieve the user based on the user ID in the payload
        user = User.objects.filter(id=payload['id']).first()

        if user:
            return Response({'status': 200, 'message': 'home page', 'user': user.username})
        else:
            return Response({'status': 400, 'message': 'User not found'})

    except jwt.ExpiredSignatureError:
        return Response({'status': 400, 'message': 'Token has expired'})

    except jwt.DecodeError:
        return Response({'status': 400, 'message': 'Token is invalid'})

    except Exception as e:
        return Response({'status': 400, 'message': 'Token Error: ' + str(e)})


class UserAPI(APIView):
    def post(self, request):
        data = request.data
        try:
            serializer = RegisterSerializer(data=data)
            if serializer.is_valid():
                user = User.objects.create_user(username=serializer.data['username'], email=serializer.data['email'])
                user.set_password(serializer.data['password'])
                user.save()
                return Response({'status': 200, 'message': 'Registration Successful'})
            return Response({'status': 400, 'message': 'Error in Registration'})
        except Exception as e:
            return Response({'status': 400, 'message': 'Error: ' + str(e)})


class LoginAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:

                # Create a JWT token
                payload = {
                    'id': user.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440),
                    'iat': datetime.datetime.utcnow()
                }

                token = jwt.encode(payload, 'secret', algorithm='HS256')
                response = Response({'status': 200, 'token': token})

                # Set the token as a cookie in the response
                response.set_cookie(key='token', value=token)
                return response
            else:
                return Response({'status': 400, 'message': 'Invalid Credentials'})

        except Exception as e:
            return Response({'status': 400, 'message': 'Error: ' + str(e)})

@api_view(['GET'])
def Logout(request):
    try:
        response = Response({'status': 200, 'message': 'Logging-Out'})
        response.delete_cookie('token')
        return response
    except:
        return Response({'status':400,'message':'Error in Logging-Out'})
    

@api_view(['GET'])
def deletePlan(request,id):
    try:
        plan = Plans.objects.get(pk=id)
        plan.delete()
        return Response({'status':200,'data':'Successful Delete'})
    except Exception as e:
        return Response({'status':400,'message':'Error in Deleting plan'})


@api_view(['POST'])
def nutrition(request):
    try:
        key = 'WfQlyJ5CRE9zrkVYz4qo1w==U9FklGEjrJAPesks'
        date = datetime.date.today()
        token = request.data.get('token')
        food = request.data.get('food')

        if not token:
            return Response({'status': 400, 'message': 'Authentication failed'})

        try:
            # Verify the JWT token and decode the payload
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user = User.objects.filter(id=payload['id']).first()

        except jwt.ExpiredSignatureError:
            return Response({'status': 400, 'message': 'Token has expired'})
        except jwt.DecodeError:
            return Response({'status': 400, 'message': 'Token is invalid'})
        except Exception as e:
            return Response({'status': 400, 'message': 'Token Error: ' + str(e)})

        nutri = Nutrition.objects.filter(user=user, date=date).first()

        api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
        query = food
        response = requests.get(api_url + query, headers={'X-Api-Key': key})

        if response.status_code == requests.codes.ok:
            data = response.json()  # Parse the response as JSON
            print(data)
            food_data = data['items'][0]  # Access the first item in the 'items' list

            if nutri is None:
                nutri = Nutrition.objects.create(user=user)
            
            # Update the nutrition values
            nutri.sugar_g += food_data['sugar_g']
            nutri.calories += food_data['calories']
            nutri.serving_size_g += food_data['serving_size_g']
            nutri.fat_total_g += food_data['fat_total_g']
            nutri.fat_saturated_g += food_data['fat_saturated_g']
            nutri.protein_g += food_data['protein_g']
            nutri.sodium_mg += food_data['sodium_mg']
            nutri.potassium_mg += food_data['potassium_mg']
            nutri.cholesterol_mg += food_data['cholesterol_mg']
            nutri.carbohydrates_total_g += food_data['carbohydrates_total_g']
            nutri.fiber_g += food_data['fiber_g']
            nutri.save()

            f = Food.objects.create(nutrition = nutri,food=query)
            f.save()

        else:
            return Response({'status': 400, 'message': 'Error in Food API'})

        return Response({'status': 200, 'data': 'success'})

    except Exception as e:
        return Response({'status': 400, 'message': str(e)})

@api_view(['POST'])
def getnutrition(request):
    try:
        token = request.data.get('token')

        if not token:
            return Response({'status': 400, 'message': 'Authentication failed'})

        try:
            # Verify the JWT token and decode the payload
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            user = User.objects.filter(id=payload['id']).first()

        except jwt.ExpiredSignatureError:
            return Response({'status': 400, 'message': 'Token has expired'})
        except jwt.DecodeError:
            return Response({'status': 400, 'message': 'Token is invalid'})
        except Exception as e:
            return Response({'status': 400, 'message': 'Token Error: ' + str(e)})
        
        nutri = Nutrition.objects.filter(user=user).order_by('-id')
        nutri2 = []
        if len(nutri)<=7:
            nutri2 = nutri
        else:
            for i in range(0,7):
                nutri2.append(nutri[i])
        serializer = NutritionSerializer(nutri,many=True)
        serial = NutritionSerializer(nutri2,many=True)

        return Response({'status':200,'data':serializer.data,'graph':serial.data})
    except Exception as e:
        return Response({'status': 400, 'message': str(e)})

@api_view(['GET'])
def getNutritionById(request,id):
    try:
        nutri = Nutrition.objects.get(pk=id)
        serializer = NutritionSerializer(nutri)
        return Response({'status':200,'data':serializer.data})
    except Exception as e:
        return Response({'status': 400, 'message': str(e)})

@api_view(['GET'])
def getFoods(request,id):
    try:
        nutrition = Nutrition.objects.get(pk=id)
        foods = Food.objects.filter(nutrition=nutrition)
        serializer = FoodSerializer(foods,many=True)
        return Response({'status':200,'data':serializer.data})
    except Exception as e:
        return Response({'status': 400, 'message': str(e)})
        
    

