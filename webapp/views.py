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

# ====
# Unitities 
# ====
def isRequestAuthorized (request): 
    return ('credentials' in request.session.keys()) 

def makeHostUrl (request): 
    return (request.is_secure() and "https://" or "http://") + request.get_host() 

# ====
# Endpoint 
# ====
# Ping endpoint 
def ping (request): 
    return HttpResponse("Ping!")

# Make a response for enabling CORS
def enableCORS (res, allowedMethod):
    res['Access-Control-Allow-Origin'] = '*'
    res['Access-Control-Allow-Methods'] = str(allowedMethod)
    res['Access-Control-Allow-Headers'] = 'Authorization'

# readSheetData endpoint 
def readSheetData (request): 
    allowedMethod = 'GET'

    if (request.method == 'OPTIONS'):
        preflightRes =  HttpResponse('', status=HTTPStatus.OK)
        enableCORS(preflightRes, allowedMethod)
        return preflightRes

    if (request.method != allowedMethod): 
        return HttpResponse('', status=HTTPStatus.METHOD_NOT_ALLOWED)

    if (ss2json.KEY_AUTHORIZATION not in request.headers): 
        return HttpResponse('OAuth2 token is missed', status=HTTPStatus.BAD_REQUEST)
    token = request.headers[ss2json.KEY_AUTHORIZATION]

    spreadsheetId = request.GET.get('spreadsheetId', None)    
    sheetId = request.GET.get('sheetId', None)
    if (token is None): 
        return HttpResponse('token is missed', status=HTTPStatus.UNAUTHORIZED) 
    if (spreadsheetId is None): 
        return HttpResponse('spreadsheetId missed', status=HTTPStatus.BAD_REQUEST)

    res = ss2json.loadTheTableFromGoogleSpreadsheets(
        spreadsheetId=spreadsheetId, 
        sheetId=sheetId, 
        token=token)

    jsonRes = JsonResponse(res.__dict__)
    enableCORS(jsonRes, allowedMethod)
    return jsonRes

# writeCellData endpoint 
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

# ====
# DEV endpoint 
# ====
def devRead0 (request): 
    sheetData = ss2json.SheetData('spreadsheetId', 'sheetId')
    sheetData.setColumnTitles(['col0', 'col1'])
    rows = [
        ['r0c0', 'r0c1'], 
        ['r1c0', 'r1c1']
    ]
    sheetData.setData(0, rows)

    response = JsonResponse(sheetData.__dict__)

    # this is not a good practice... 
    response['Access-Control-Allow-Origin'] = '*'

    return response