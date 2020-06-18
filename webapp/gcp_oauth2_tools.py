
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
        
        self.reset()

    def reset (self): 
        self.loadClientSecret()
        self.makeAuthUrl()
        
    def loadClientSecret (self): 
        assert(self.clientSecretPath is not None), "clientSecretPath missed"
        assert(self.authScopes is not None), "authScopes missed" 
        self.clientSecret = GAuthFlow.from_client_secrets_file(
            self.clientSecretPath, 
            self.authScopes)

    def makeAuthUrl (self): 
        assert(self.callbackUrl is not None), "callbackUrl missed"

        if (self.clientSecret is None): 
            self.loadClientSecret() 
        assert(self.clientSecret is not None), "Failed to load clientSecret"
        
        self.clientSecret.redirect_uri = self.callbackUrl

        self.authUrl, self.authState = self.clientSecret.authorization_url(
            access_type=(self.isOffline and 'offline' or None),
            include_granted_scopes=(self.isIncremental and 'true' or None))

