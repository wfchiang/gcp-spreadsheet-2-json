from http import HTTPStatus
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect 

import json
import urllib.parse
import webapp.ss2json as ss2json
import webapp.gcp_oauth2_tools as gcp_oauth2_tools 

import webapp.settings as django_settings

# ====
# Globals
# ====
AUTH_IS_OFFLINE = False 
AUTH_IS_INCREMENTAL = False
AUTH_CALLBACK_URL = None  
AUTH_CLIENT_SECRET = None 

# ====
# Class(es)
# ====
class AuthResponse: 
    isAuthorized = '' 
    message = ''

    def __init__ (self, isAuthorized, message): 
        self.isAuthorized = ((type(isAuthorized) is str) and isAuthorized or '')
        self.message = ((type(message) is str) and message or '')

# ====
# Unitities 
# ====
def isRequestAuthorized (request): 
    return ('credentials' in request.session.keys()) 

def makeHostUrl (request): 
    return (request.is_secure() and "https://" or "http://") + request.get_host() 

def makeAuthExitUrl (request, isAuthorized, message):
    return makeHostUrl(request) + '/authExit?' + urllib.parse.urlencode({'isAuthorized': str(isAuthorized), 'message': str(message)}, doseq=True)

# ====
# Endpoint 
# ====
# Ping endpoint 
def ping (request): 
    return HttpResponse("Ping!")

# Authorization endpoint
def authEnty (request): 
    global AUTH_CALLBACK_URL
    global AUTH_CLIENT_SECRET

    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    if (isRequestAuthorized(request)): 
        return redirect(makeAuthExitUrl(request, True, ''))

    if (AUTH_CALLBACK_URL is None): 
        AUTH_CALLBACK_URL = makeHostUrl(request) + "/auth"

    if (AUTH_CLIENT_SECRET is None): 
        AUTH_CLIENT_SECRET = gcp_oauth2_tools.loadClientSecret(
            clientSecretPath=ss2json.CLIENT_SECRET_PATH, 
            authScopes=ss2json.AUTH_SCOPES, 
            callbackUrl=AUTH_CALLBACK_URL, 
            authState=None)
    
    if (AUTH_CLIENT_SECRET is None): 
        return redirect(makeAuthExitUrl(request, False, 'Error: fail to load the client secret'))

    authUrl, authState = AUTH_CLIENT_SECRET.authorization_url(
        access_type=(AUTH_IS_OFFLINE and 'offline' or None),
        include_granted_scopes=(AUTH_IS_INCREMENTAL and 'true' or None))

    request.session['authUrl'] = authUrl
    request.session['authState'] = authState

    return redirect(authUrl)

# Authorization Callback endpoint 
def auth (request): 
    if (AUTH_CLIENT_SECRET is None): 
        return redirect(makeAuthExitUrl(request, False, 'AUTH_CLIENT_SECRET is missed'))
    
    gcpCredentials = gcp_oauth2_tools.fetchCredentials(AUTH_CLIENT_SECRET, request.build_absolute_uri())
    dictCredentials = gcp_oauth2_tools.convertCredentialsToDict(gcpCredentials)

    request.session['credentials'] = dictCredentials

    return redirect(makeAuthExitUrl(request, True, ''))

# Authorization Exit -- in order to do something for hiding the auth information 
def authExit (request): 
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    isAuthorized = request.GET.get('isAuthorized', None)
    message = request.GET.get('message', '')

    if (isAuthorized is None): 
        return HttpResponse('isAuthorized missed', status=HTTPStatus.BAD_REQUEST)

    return JsonResponse(AuthResponse(isAuthorized, message).__dict__)

# readSheetData endpoint 
def readSheetData (request): 
    if (request.method != 'GET'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    if (not isRequestAuthorized(request)): 
        return redirect(makeAuthExitUrl(request, False, 'Not Authorized Yet'))
    
    dictCredentials = request.session['credentials']

    spreadsheetsId = request.GET.get('spreadsheetsId', None)
    sheetId = request.GET.get('sheetId', None) 
    if (spreadsheetsId is None): 
        return HttpResponse('spreadsheetsId missed', status=HTTPStatus.BAD_REQUEST)
    
    gssService = ss2json.getGoogleSpreadsheetsService(dictCredentials) 
    sheetData = ss2json.loadTheTableFromGoogleSpreadsheets(
        spreadsheetsService=gssService, 
        spreadsheetsId=spreadsheetsId,
        sheetId=sheetId)
    
    return JsonResponse(sheetData.__dict__)

def writeCellData (request): 
    if (request.method != 'POST'): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    if (not isRequestAuthorized(request)): 
        return redirect(makeAuthExitUrl(request, False, 'Not Authorized Yet'))
    
    dictCredentials = request.session['credentials']

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
    
    gssService = ss2json.getGoogleSpreadsheetsService(dictCredentials) 
    numUpdatedCells = ss2json.writeOneGoogleSpreadsheetsCell(
        spreadsheetsService=gssService, 
        spreadsheetsId=spreadsheetsId,
        sheetId=sheetId, 
        cellIndex=cellIndex, 
        value=value)

    return HttpResponse(str(numUpdatedCells), status=HTTPStatus.OK)
