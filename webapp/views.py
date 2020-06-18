from http import HTTPStatus
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect 

import json
import webapp.ss2json as ss2json

# Ping endpoint 
def ping (request): 
    return HttpResponse("Ping!")

# Authorization endpoint
def auth (request): 
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    ss2json.AUTH_INFO.fetchCredentials(request.build_absolute_uri())
    
    # return HttpResponse('Authorized', status=HTTPStatus.OK)
    return JsonResponse(ss2json.AUTH_INFO.credentials)

# readSheetData endpoint 
def readSheetData (request): 
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    spreadsheetsId = request.GET.get('spreadsheetsId', None)
    sheetId = request.GET.get('sheetId', None) 
    if (spreadsheetsId is None): 
        return HttpResponse('spreadsheetsId missed', status=HTTPStatus.BAD_REQUEST)
    
    gssService = ss2json.getGoogleSpreadsheetsService() 
    sheetData = ss2json.loadTheTableFromGoogleSpreadsheets(
        spreadsheetsService=gssService, 
        spreadsheetsId=spreadsheetsId,
        sheetId=sheetId)
    
    return JsonResponse(sheetData.__dict__)

# ====
# Debugging Endpoints 
# ====
def peepClientSecret (request):
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED) 

    isOffline = False
    isIncremental = False 
    callbackUrl = (request.is_secure() and "https://" or "http://") + request.get_host() + "/auth"
    
    ss2json.setAuthInfo(
        callbackUrl=callbackUrl, 
        isOffline=isOffline, 
        isIncremental=isIncremental)
    
    return redirect(ss2json.AUTH_INFO.authUrl)