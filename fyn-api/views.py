from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import loader

def home(request):
    template = loader.get_template('master.html')
    context = {}
    return HttpResponse(template.render(context, request))

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})