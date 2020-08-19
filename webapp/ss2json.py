import os
import json
import urllib.parse
import requests
from http import HTTPStatus
from googleapiclient.discovery import build as GClientBuild
from google_auth_oauthlib.flow import InstalledAppFlow as GAuthInstalledAppFlow
from google.auth.transport.requests import Request as GAuthRequest
from google.oauth2.credentials import Credentials as GAuthCredentials

# ====
# Parameters 
# ====
AUTH_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRET_PATH = 'client_secret.json'

MAX_COLS = 10
MAX_ROWS = 1000
DATA_CHUNCK_SIZE = 100

KEY_AUTHORIZATION = 'Authorization'

URL_SPREADSHEETS = 'https://sheets.googleapis.com/v4/spreadsheets'

# ====
# Class Definition(s)
# ====
class GoogleServiceException (Exception): 
    message = None 

    def __init__ (self, message=''): 
        self.message = message  

class SS2JsonException (Exception): 
    message = None 

    def __init__ (self, message=''): 
        self.message = message

class SheetDataId: 
    spreadsheetId = None 
    sheetId = None 

    def __init__ (self, spreadsheetId, sheetId): 
        self.spreadsheetId = spreadsheetId
        self.sheetId = sheetId

class SheetRow: 
    rowIndex = None 
    data = None 

    def __init__ (self, rowIndex, data = {}): 
        self.rowIndex = str(rowIndex) 
        self.data = data 

class SheetData: 
    id = None 
    columnTitles = None 
    rows = None 

    def __init__ (self, spreadsheetId, sheetId): 
        self.id = SheetDataId(spreadsheetId, sheetId).__dict__

    def setColumnTitles (self, columnTitles = []): 
        self.columnTitles = columnTitles[:]

    def setData (self, first_row_index, rows = []):
        self.rows = [] 
        for i in range(0, len(rows)): 
            r = rows[i]
            row_index = str(i + int(first_row_index))
            new_data = {} 
            for j in range(0, len(self.columnTitles)): 
                new_data[self.columnTitles[j]] = (j < len(r) and r[j] or '')
            self.rows.append(SheetRow(row_index, new_data).__dict__)

# ====
# Utilities 
# ====
# A utility for making the data-range string 
def makeDataRange (sheetId, upperLeftCell, bottomRightCell): 
    dataRange = upperLeftCell + ':' + bottomRightCell
    if (sheetId != None): 
        return sheetId + '!' + dataRange
    else: 
        return dataRange

# colId = 1 -> 'A'
# colId = 26 -> 'Z'
# colId = 27 -> 'AA'
def makeColumnIndex (colId): 
    colId = int(colId) - 1
    cIndex = None
    if (colId >= 0): 
        cIndex = chr((colId%26) + ord('A'))
        colId = int(colId / 26)
        while (colId > 0): 
            cIndex = chr(((colId-1)%26) + ord('A')) + cIndex
            colId = int((colId - 1) / 26)
    return cIndex

def isEmptyCell (d): 
    if not d: 
        return True 
    if (d is None): 
        return True 
    if d.strip() == '': 
        return True 
    return False 

def splitStringBySpace (s): 
    if (s is None): 
        return None 
    tempList = s.split(' ')
    sList = []
    for t in tempList: 
        if (t.strip() == ''):
            continue
        sList.append(t)
    return sList

# This function read data of a Google spreadsheets from a SpreadsheetsService 
def readGoogleSpreadsheet (spreadsheetId, dataRange, token): 
    reqUrl = URL_SPREADSHEETS + '/' + urllib.parse.quote(str(spreadsheetId)) + '/values/' + urllib.parse.quote(str(dataRange))
    reqHeaders = {
        KEY_AUTHORIZATION: str(token)
    }
    res = requests.get(reqUrl, headers=reqHeaders)

    if (res.status_code != HTTPStatus.OK): 
        raise GoogleServiceException('readGoogleSpreadsheet call failed -- http status ' + str(res.status_code))

    return res.json() 

# This function write/update to a Google spreadsheet cells 
def writeOneGoogleSpreadsheetsCell (spreadsheetsService, spreadsheetsId, sheetId, cellIndex, value):
    body = {
        'values': [
            [value]
        ]
    }
    serviceResult = spreadsheetsService.values().update(
        spreadsheetId=spreadsheetsId, 
        range=makeDataRange(
            sheetId=sheetId, 
            upperLeftCell=cellIndex, 
            bottomRightCell=cellIndex),
        valueInputOption='RAW', 
        body=body).execute()
    numUpdatedCells = int(serviceResult.get('updatedCells'))
    assert(numUpdatedCells == 1), "Invalid number of updated cell: " + str(numUpdatedCells)
    return numUpdatedCells

# Try loading "THE" (upper-left) table in a sheet
def loadTheTableFromGoogleSpreadsheets (spreadsheetId, sheetId, token): 
    
    sheetData = SheetData(spreadsheetId=spreadsheetId, sheetId=sheetId)

    # Try to get the column titles 
    dataRange = makeDataRange(
        sheetId=sheetId, 
        upperLeftCell=(makeColumnIndex(1)+'1'), 
        bottomRightCell=(makeColumnIndex(MAX_COLS + 1)+str(MAX_ROWS+1)))
    spreadsheetData = readGoogleSpreadsheet(
        spreadsheetId=spreadsheetId, 
        dataRange=dataRange, 
        token=token)

    values = spreadsheetData['values']
    if (len(values) > MAX_ROWS): 
        raise SS2JsonException('The number of rows exceeds ss2json limit (' + str(MAX_ROWS) + ')')
    if (max(map(lambda r : len(r), values)) > MAX_COLS): 
        raise SS2JsonException('The number of columns exceeds ss2json limit (' + str(MAX_COLS) + ')')

    # return if no values 
    if (len(values) == 0): 
        return sheetData
    
    # set column titles 
    sheetData.setColumnTitles(values[0])

    # set rows  
    sheetData.setData(0, values[1:])  

    return sheetData