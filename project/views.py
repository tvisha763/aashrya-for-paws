from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Shelter, Donation, Dog, Adoption, Euthanization
import bcrypt
import requests
import urllib
import os
from datetime import datetime

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from datetime import datetime



# Create your views here.

def home(request):
        week = timezone.now() - timedelta(days=7)
        adoptions = Adoption.objects.filter(date__gte=week).count()
        numEuth = Euthanization.objects.filter(date__gte=week).count()
        euth = Euthanization.objects.all()
        Context = {
            "adoptions" : adoptions,
            "numEuth" : numEuth,
            "euth" : euth
        }
        return render(request, 'home.html', Context)

def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password').encode("utf8")
        confirmPass = request.POST.get('confirmPass').encode("utf8")
        inputs = [email, username, password, confirmPass, phone]

        # checking if confirm password matches password   
        if (password != confirmPass):
            messages.error(request, "The passwords do not match.")
            return redirect('signup')

        for inp in inputs:
            if inp == '':
                messages.error(request, "Please fill all the boxes.")
                return redirect('signup')

        if password != '' and len(password) < 6:
            messages.error(request, "Your password must be at least 6 charecters.")
            return redirect('signup')
        

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. If this is you, please log in.")
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "An account with this username already exists. Please pick another one.")
            return redirect('signup')

        else:
            salt = bcrypt.gensalt()
            user = User()
            user.email = email
            user.username = username
            user.phone = phone
            user.password = bcrypt.hashpw(password, salt)
            user.salt = salt
            user.save()
            return redirect('login')
    else:
        if request.session.get('logged_in'):
            return redirect('dashboard')

    return render(request, 'auth/signup.html')

def login(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password').encode("utf8")
            inputs = [username, password]

            for inp in inputs:
                if inp == '':
                    messages.error(request, "Please input all the information.")
                    return redirect('login')

            

            if User.objects.filter(username=username).exists():
                saved_hashed_pass = User.objects.filter(username=username).get().password.encode("utf8")[2:-1]
                saved_salt = User.objects.filter(username=username).get().salt.encode("utf8")[2:-1]
                user  = User.objects.filter(username=username).get()
                request.session["username"] = user.username
                request.session['logged_in'] = True
            
                salted_password = bcrypt.hashpw(password, saved_salt)
                if salted_password == saved_hashed_pass:
                    return redirect('dashboard')
                else:
                    messages.error(request, "Your password is incorrect.")
                    return redirect('login')

            else:
                messages.error(request, "An account with this username does not exist. Please sign up.")
                return redirect('login')

    else:
        if request.session.get('logged_in'):
            return redirect('dashboard')

    return render(request, 'auth/login.html')

def logout(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        return redirect('/login')
    else:
        request.session["username"] = None
        request.session['logged_in'] = False
        return redirect('/login')

def dashboard(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        user = User.objects.get(username=request.session["username"])
        shelters = Shelter.objects.filter(user=user)
        donations = Donation.objects.filter(user=user)
        dogs = Dog.objects.filter(user=user)
        context = {
            'shelters' : shelters,
            'donations' : donations,
            'dogs' : dogs,
        }
        return render(request, 'dashboard.html', context)

def addShelter(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":
        user = User.objects.get(username=request.session["username"])
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city").lower()
        info = request.POST.get("info")

        shelter = Shelter(user=user, name=name, email=email, phone=phone, address=address, city=city, additional_info=info)
        shelter.save()

        return render(request, 'addShelter.html')
    else:
        return render(request, 'addShelter.html')

def donate(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":
        user = User.objects.get(username=request.session["username"])
        item = request.POST.get("item")
        address = request.POST.get("address")
        city = request.POST.get("city").lower()
        timeR = request.POST.get("time")
        cond = request.POST.get("cond")
        donation = Donation(user=user, item=item, time_range=timeR, address=address, city=city, condition=cond)
        donation.save()
        return render(request, 'donate.html')
    else:
        return render(request, 'donate.html')

def findShelter(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":
        city = request.POST.get("city").lower()
        shelters = Shelter.objects.filter(city=city)
        donations = Donation.objects.filter(city=city)
        context = {
            'shelters' : shelters,
            'donations' : donations,
        }
        return render(request, 'findShelter.html', context)
    else:
        return render(request, 'findShelter.html')





def donated(request):   
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        donation = Donation.objects.get(id=request.GET.get('id'))
        donation.delete()
        return redirect('dashboard')
    

def addDog(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":
        user = User.objects.get(username=request.session["username"])
        shelter = Shelter.objects.get(name=request.POST.get("shelter"), user=user)
        name = request.POST.get("name")
        image = request.FILES.get('image')
        urgency = request.POST.get('urgency')
        description = request.POST.get('description')

        dog = Dog(user=user, shelter=shelter, name=name, image=image, urgency=urgency, description=description, status='1')
        dog.save()

        
        shelters = Shelter.objects.filter(user=user)

        Context = {
            "shelters" : shelters,
        }
        return render(request, 'addDog.html', Context)
    else:
        user = User.objects.get(username=request.session["username"])
        shelters = Shelter.objects.filter(user=user)

        Context = {
            "shelters" : shelters,
        }
        return render(request, 'addDog.html', Context)
    
def shelterDogs(request, shelter_id):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        shelter = Shelter.objects.get(id=shelter_id)
        dogs = Dog.objects.filter(shelter=shelter)
        Context = {
            "dogs" : dogs,
            "shelter" : shelter,
        }
        return render(request, 'showDogs.html', Context)
    

def dogDetails(request, dog_id):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        dog = Dog.objects.get(id=dog_id)
        shelter = Shelter.objects.get(id = dog.shelter.id)
        Context = {
            "dog" : dog,
            "shelter" : shelter,
        }
        return render(request, 'dogDetails.html', Context)
    
def deleteShelter(request):   
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        shelter = Shelter.objects.get(id=request.GET.get('shelter_id'))
        shelter.delete()
        return redirect('dashboard')
    

def adopted(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        dog = Dog.objects.get(id=request.GET.get('dog_id'))
        adoption = Adoption(dog=dog)
        adoption.save()
        dog.status='2'
        dog.save()
        return redirect('dashboard')

def euthanized(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        dog = Dog.objects.get(id=request.GET.get('dog_id'))
        euthanization = Euthanization(dog=dog)
        euthanization.save()
        dog.status='3'
        dog.save()
        return redirect('dashboard')