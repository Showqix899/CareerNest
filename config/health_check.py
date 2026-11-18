from django.http import response
def health(request):
    
    return response.JsonResponse({"health":"web server is running","code":200})