import pickle
import os
from googleapiclient.discovery import build as GClientBuild
from google_auth_oauthlib.flow import InstalledAppFlow as GAuthInstalledAppFlow
from google.auth.transport.requests import Request as GAuthRequest

# ====
# Parameters 
# ====
AUTH_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_PATH = 'credentials.json'
MAX_COLS = 100
MAX_ROWS = 1000 
DATA_CHUNCK_SIZE = 100 

# ====
# Class Definition(s)
# ====
class SheetData: 
    spreadsheetsId = None 
    sheetId = None 
    columnTitles = None 
    data = None 

    def __init__ (self, spreadsheetsId, sheetId): 
        self.spreadsheetsId = spreadsheetsId
        self.sheetId = sheetId

    def setColumnTitles (self, columnTitles = []): 
        self.columnTitles = columnTitles[:]

    def setData (self, rows = []):
        self.data = [] 
        for r in rows: 
            new_data = {} 
            for i in range(0, len(self.columnTitles)): 
                new_data[self.columnTitles[i]] = r[i]
            self.data.append(new_data)

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

# ====
# GCP IO functions
# ====
# This function loads the credentials -- the code refers to the example provided by GCP tutorial
def getGoogleCredentials (): 
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GAuthRequest())
        else:
            flow = GAuthInstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, AUTH_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

# This function loads the Google service -- the code refers to the example provided by GCP tutorial 
def getGoogleSpreadsheetsService (): 
    gCreds = getGoogleCredentials() 
    gService = GClientBuild.service = GClientBuild('sheets', 'v4', credentials=gCreds)
    return gService.spreadsheets()

# This function read data of a Google spreadsheets from a SpreadsheetsService 
def readGoogleSpreadsheets (spreadsheetsService, spreadsheetsId, dataRange): 
    serviceResult = spreadsheetsService.values().get(spreadsheetId=spreadsheetsId, range=dataRange).execute()
    values = serviceResult.get('values', [])
    return values 

# Try loading "THE" (upper-left) table in a sheet
def loadTheTableFromGoogleSpreadsheets (spreadsheetsService, spreadsheetsId, sheetId): 
    
    sheetData = SheetData(spreadsheetsId=spreadsheetsId, sheetId=sheetId)

    # Try to get the column titles 
    dataRange = makeDataRange(
        sheetId=sheetId, 
        upperLeftCell=(makeColumnIndex(1)+'1'), 
        bottomRightCell=(makeColumnIndex(MAX_COLS)+'1'))
    values = readGoogleSpreadsheets(
        spreadsheetsService=spreadsheetsService, 
        spreadsheetsId=spreadsheetsId,
        dataRange=dataRange)
    columnTitles = values[0]
    for i in range(0, len(columnTitles)): 
        if (isEmptyCell(columnTitles[i])): 
            columnTitles = columnTitles[0:i]

    sheetData.setColumnTitles(columnTitles)
    
    # Try to load the rows 
    rows = [] 
    new_rows = [] 
    starting_row_index = 2
    end_of_data = False 
    while (len(rows) < MAX_ROWS): 
        dataRange = makeDataRange(
            sheetId=sheetId, 
            upperLeftCell=(makeColumnIndex(1)+str(starting_row_index)),
            bottomRightCell=(makeColumnIndex(len(columnTitles))+str(starting_row_index+DATA_CHUNCK_SIZE-1)))
        starting_row_index += DATA_CHUNCK_SIZE
        values = readGoogleSpreadsheets(
            spreadsheetsService=spreadsheetsService, 
            spreadsheetsId=spreadsheetsId, 
            dataRange=dataRange)
        if not values or len(values) == 0: 
            break
        for v in values: 
            if all(map(isEmptyCell, v)): 
                end_of_data = True 
            else: 
                rows.append(v)
        if (end_of_data): 
            break 
    
    sheetData.setData(rows)

    print (str(sheetData.columnTitles))
    print (str(sheetData.data))
        