from http import HTTPStatus
from django.http import HttpResponse
from django.http import JsonResponse

import json
from . import ss2json

# Ping endpoint 
def ping (request): 
    return HttpResponse("Ping!")

# Authorization endpoint
def auth (request): 
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    authCode = request.GET.get('code', None)
    authScopes = ss2json.splitStringBySpace(request.GET.get('scope', None))

    if (authCode is None): 
        return HttpResponse('Authorization code is missed', status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    if (authScopes is None): 
        return HttpResponse('Authorization scope is missed', status=HTTPStatus.METHOD_NOT_ALLOWED)

    if any(map(lambda x:(x not in ss2json.AUTH_SCOPES), authScopes)): 
        return HttpResponse('Unauthorized scope(s): ' + str(authScopes), status=HTTPStatus.Unauthorized)

    ss2json.AUTH_CODE = authCode
    
    return HttpResponse('Authorized', status=HTTPStatus.OK)

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
def peepAuthCode (request): 
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    return HttpResponse(str(ss2json.AUTH_CODE), status=HTTPStatus.OK)

def peepAuthUrl (request):
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED) 

    isOffline = False
    isIncremental = False 
    callbackUrl = (request.is_secure() and "https://" or "http://") + request.get_host() + "/auth"
    
    ss2json.setAuthInfo(
        callbackUrl=callbackUrl, 
        isOffline=isOffline, 
        isIncremental=isIncremental)
    
    return HttpResponse(ss2json.AUTH_INFO.authUrl, status=HTTPStatus.OK)