from http import HTTPStatus
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect 

import json
import webapp.ss2json as ss2json
import webapp.gcp_oauth2_tools as gcp_oauth2_tools 

import webapp.settings as django_settings

AUTH_INFO = None 

# ====
# Unitities 
# ====
def checkAuthorization (): 
    return (AUTH_INFO is not None) 

# ====
# Endpoint 
# ====
# Ping endpoint 
def ping (request): 
    return HttpResponse("Ping!")

# Authorization endpoint
def authEnty (request): 
    global AUTH_INFO

    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    request.session['hi'] = 'hello'
    return HttpResponse('[' + str(request.session._session_key) + ', ' + str(request.session._session) + ']')

    isOffline = False
    isIncremental = False 
    callbackUrl = (request.is_secure() and "https://" or "http://") + request.get_host() + "/auth"

    AUTH_INFO = gcp_oauth2_tools.GCPOAuth2Info(
        clientSecretPath=ss2json.CLIENT_SECRET_PATH, 
        authScopes=ss2json.AUTH_SCOPES, 
        callbackUrl=callbackUrl, 
        isOffline=isOffline, 
        isIncremental=isIncremental)

    return redirect(AUTH_INFO.authUrl)

# Authorization Callback endpoint 
def auth (request): 
    if (AUTH_INFO is None): 
        return HttpResponse('AUTH_INFO not ready', status=HTTPStatus.UNAUTHORIZED)
    
    AUTH_INFO.fetchCredentials(request.build_absolute_uri())
    
    request.session['credentials'] = 'True'

    return HttpResponse('Authorized', status=HTTPStatus.OK)
    # return JsonResponse(AUTH_INFO.dictCredentials)

# readSheetData endpoint 
def readSheetData (request): 
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    if (not checkAuthorization()): 
        return HttpResponse('Not authorized yet', status=HTTPStatus.UNAUTHORIZED)
    
    spreadsheetsId = request.GET.get('spreadsheetsId', None)
    sheetId = request.GET.get('sheetId', None) 
    if (spreadsheetsId is None): 
        return HttpResponse('spreadsheetsId missed', status=HTTPStatus.BAD_REQUEST)
    
    gssService = ss2json.getGoogleSpreadsheetsService(AUTH_INFO.dictCredentials) 
    sheetData = ss2json.loadTheTableFromGoogleSpreadsheets(
        spreadsheetsService=gssService, 
        spreadsheetsId=spreadsheetsId,
        sheetId=sheetId)
    
    return JsonResponse(sheetData.__dict__)

def writeCellData (request): 
    if (request.method != 'POST'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    if (not checkAuthorization()): 
        return HttpResponse('Not authorized yet', status=HTTPStatus.UNAUTHORIZED)

    request_data = json.loads(request.body) 
    
    spreadsheetsId = ('spreadsheetsId' in request_data.keys()) and request_data['spreadsheetsId'] or None
    sheetId = ('sheetId' in request_data.keys()) and request_data['sheetId'] or None 
    cellIndex = ('cellIndex' in request_data.keys()) and request_data['cellIndex'] or None 
    value = ('value' in request_data.keys()) and request_data['value'] or None 
    if (spreadsheetsId is None): 
        return HttpResponse('spreadsheetsId missed', status=HTTPStatus.BAD_REQUEST)
    if (cellIndex is None): 
        return HttpResponse('cellIndex missed', status=HTTPStatus.BAD_REQUEST)
    if (value is None): 
        value = ''
    
    gssService = ss2json.getGoogleSpreadsheetsService(AUTH_INFO.dictCredentials) 
    numUpdatedCells = ss2json.writeOneGoogleSpreadsheetsCell(
        spreadsheetsService=gssService, 
        spreadsheetsId=spreadsheetsId,
        sheetId=sheetId, 
        cellIndex=cellIndex, 
        value=value)

    return HttpResponse(str(numUpdatedCells), status=HTTPStatus.OK)

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