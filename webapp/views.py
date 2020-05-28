from django.http import HttpResponse

from . import ss2json

# Ping endpoint 
def ping (request): 
    spreadsheetsId = '1brRpP3_vCuGHAVkA6HkKxLm4DsfnNDNBQVWQCv9prkw'
    dataRange = 'A2:B3'
    gssService = ss2json.getGoogleSpreadsheetsService() 
    values = ss2json.loadTheTableFromGoogleSpreadsheets(
        spreadsheetsService=gssService, 
        spreadsheetsId=spreadsheetsId,
        sheetId=None)
    return HttpResponse("Ping!")