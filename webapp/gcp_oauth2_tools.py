from google_auth_oauthlib.flow import Flow as GAuthFlow 

# ====
# Utils 
# ====
def loadClientSecret (clientSecretPath, authScopes, callbackUrl, authState): 
    assert(clientSecretPath is not None), "clientSecretPath missed"
    assert(authScopes is not None), "authScopes missed" 
    assert(callbackUrl is not None), "callbackUrl missed"

    clientSecret = GAuthFlow.from_client_secrets_file(
        clientSecretPath, 
        scopes=authScopes, 
        state=authState)

    clientSecret.redirect_uri = callbackUrl

    return clientSecret

def fetchCredentials (clientSecret, callbackOperation): 
    assert(clientSecret is not None), "clientSecret missed"
    assert(type(callbackOperation) is str), "callbackOperation is not a string"

    clientSecret.fetch_token(authorization_response=callbackOperation) 
    
    return clientSecret.credentials

def convertCredentialsToDict (gcpCredentials): 
    assert(gcpCredentials is not None), 'gcpCredentials missed'
    
    return {'token': gcpCredentials.token,
    'refresh_token': gcpCredentials.refresh_token,
    'token_uri': gcpCredentials.token_uri,
    'client_id': gcpCredentials.client_id,
    'client_secret': gcpCredentials.client_secret,
    'scopes': gcpCredentials.scopes}