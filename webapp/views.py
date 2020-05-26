from django.http import HttpResponse

# Ping endpoint 
def ping (request): 
    return HttpResponse("Ping!")