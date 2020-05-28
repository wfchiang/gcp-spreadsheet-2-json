from django.http import HttpResponse
from django.http import JsonResponse

import json
from . import ss2json

## Ping endpoint 
def ping (request): 
    return HttpResponse("Ping!")

# readSheetData endpoint 
def readSheetData (request): 
    # spreadsheetsId = '1brRpP3_vCuGHAVkA6HkKxLm4DsfnNDNBQVWQCv9prkw'
    spreadsheetsId = '1PnVWC9j-P8lL7EzhMKRKnSuwmf2qDE2avSLIZJYSISg'
    sheetId = 'Character List'
    gssService = ss2json.getGoogleSpreadsheetsService() 
    sheetData = ss2json.loadTheTableFromGoogleSpreadsheets(
        spreadsheetsService=gssService, 
        spreadsheetsId=spreadsheetsId,
        sheetId=sheetId)
    return JsonResponse(sheetData.__dict__)