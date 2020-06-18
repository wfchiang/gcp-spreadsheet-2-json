
from google_auth_oauthlib.flow import Flow as GAuthFlow 

class GCPOAuth2Info: 
    clientSecretPath = None 
    clientSecret = None 
    authScopes = None 
    authUrl = None 
    authState = None 
    callbackUrl = None 
    isOffline = False 
    isIncremental = False 

    authCode = None 

    credentials = None 

    def __init__ (self, clientSecretPath, authScopes, callbackUrl, isOffline, isIncremental):
        assert(type(clientSecretPath) is str), "clientSecretPath is not a string"
        assert(type(authScopes) is list), "authScopes is not a list"
        assert(type(callbackUrl) is str), "callbackUrl is not a string"
        assert(type(isOffline) is bool), "isOffline is not a bool"
        assert(type(isIncremental) is bool), "isIncremental is not a bool"

        self.clientSecretPath = clientSecretPath 
        self.callbackUrl = callbackUrl
        self.authScopes = authScopes[:]
        self.isOffline = isOffline
        self.isIncremental = isIncremental
        
        self.loadClientSecret()
        
    def loadClientSecret (self): 
        assert(self.clientSecretPath is not None), "clientSecretPath missed"
        assert(self.authScopes is not None), "authScopes missed" 
        assert(self.callbackUrl is not None), "callbackUrl missed"

        self.clientSecret = GAuthFlow.from_client_secrets_file(
            self.clientSecretPath, 
            scopes=self.authScopes, 
            state=self.authState)
        assert(self.clientSecret is not None), "Failed to load clientSecret"
        
        self.clientSecret.redirect_uri = self.callbackUrl

        self.authUrl, self.authState = self.clientSecret.authorization_url(
            access_type=(self.isOffline and 'offline' or None),
            include_granted_scopes=(self.isIncremental and 'true' or None))

    def fetchCredentials (self, callbackOperation): 
        assert(type(callbackOperation) is str), "callbackOperation is not a string"

        self.loadClientSecret()
        self.clientSecret.fetch_token(authorization_response=callbackOperation) 
        self.saveCredentials(self.clientSecret.credentials)

        print (str(self.credentials))

    def saveCredentials (self, gcpCredentials): 
        assert(gcpCredentials is not None), "gcpCredentials missed" 

        self.credentials = {'token': gcpCredentials.token,
          'refresh_token': gcpCredentials.refresh_token,
          'token_uri': gcpCredentials.token_uri,
          'client_id': gcpCredentials.client_id,
          'client_secret': gcpCredentials.client_secret,
          'scopes': gcpCredentials.scopes}
