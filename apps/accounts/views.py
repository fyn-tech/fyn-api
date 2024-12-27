from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from .models import User, model_to_dict
import json

# -------------------------------------------------------------------------------------------------
# Front End Requests
# -------------------------------------------------------------------------------------------------

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        company = data.get('company')
        country = data.get('country')

        # Validate the data
        if not all([first_name, email, username, password]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)

        # Check if the email is unique
        if User.objects.all().filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists'}, status=400)

        # Create a new user
        user = User.objects.create_user(
            username=username,  
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            company=company,
            country=country,
        )
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Registration successful'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def sign_in(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'status': 'success',
                'userData': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid login'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})
    

def update_user(request, id):
    user = User.objects.get(id=id)
    data = json.loads(request.body)
    user.first_name = data.get('first_name')
    user.last_name = data.get('last_name')
    user.email = data.get('email')
    user.username = data.get('username')
    user.company = data.get('company')
    user.country = data.get('country')
    user.save()
    return JsonResponse({'status': 'success', 'message': 'User updated successfully'}, status=200)

# -------------------------------------------------------------------------------------------------
# Back End Requests
# -------------------------------------------------------------------------------------------------

def home(request):
    template = loader.get_template('master.html')
    context = {}
    return HttpResponse(template.render(context, request))

def admin(request):
    template = loader.get_template('admin.html')
    context = {}
    return HttpResponse(template.render(context, request))

def account_manager(request):
    template = loader.get_template('account_manager.html')
    context = {}
    return HttpResponse(template.render(context, request))

def get_all_users(request):
    order = request.GET.get('order', 'username')  # Default sort order is by 'username'
    attribute = request.GET.get('attribute', 'username')  # Default search attribute is 'username'
    query = request.GET.get('q')  # Search query
    reset = request.GET.get('reset')  # Reset search query

    all_users = User.objects.all()

    if query and not reset:  # If a search query is provided
        kwargs = {
            '{0}__icontains'.format(attribute): query
        }
        all_users = all_users.filter(**kwargs)  # Filter users by selected attribute

    all_users = all_users.order_by(order)
    print(all_users)
    template = loader.get_template('get_all_users.html')
    context = {
        'all_users': all_users,
    }
    return HttpResponse(template.render(context, request))

def get_user(request, id):
    user = User.objects.get(id=id)
    user_dict = model_to_dict(user, fields=None)
    template = loader.get_template('get_user.html')
    context = {
        'user': user,
        'user_dict': user_dict
    }
    return HttpResponse(template.render(context, request))

def delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return JsonResponse({'status': 'success', 'message': 'User deleted successfully'}, status=200)

