import unittest
import ss2json
import gcp_oauth2_tools as GCPAuthTools

class TestGCPOauth2Tools (unittest.TestCase): 

    def test_class_GCPOAuth2Info_0 (self): 
        fakeCallbackUrl = 'abcdef'

        gcpOauth2Info = GCPAuthTools.GCPOAuth2Info(
            clientSecretPath=ss2json.CLIENT_SECRET_PATH, 
            authScopes=[], 
            callbackUrl=fakeCallbackUrl, 
            isOffline=True, 
            isIncremental=False) 
        
        self.assertEqual(ss2json.CLIENT_SECRET_PATH, gcpOauth2Info.clientSecretPath)
        self.assertEqual(fakeCallbackUrl, gcpOauth2Info.callbackUrl)

        authUrl = gcpOauth2Info.authUrl 
        self.assertIsNotNone(authUrl)
        self.assertGreater(authUrl.find(fakeCallbackUrl), 0)


class TestSS2Json (unittest.TestCase): 
    
    def test_makeDataRange_0 (self):
        dataRange = ss2json.makeDataRange(None, 'A1', 'Z2')
        self.assertEqual('A1:Z2', dataRange)

        dataRange = ss2json.makeDataRange('Sheet 0', 'A2', 'AB3')
        self.assertEqual('Sheet 0!A2:AB3', dataRange)

    def test_makeColumnIndex_0 (self): 
        colIndex = ss2json.makeColumnIndex(-1)
        self.assertIsNone(colIndex)

        colIndex = ss2json.makeColumnIndex(0)
        self.assertIsNone(colIndex)

        colIndex = ss2json.makeColumnIndex(1)
        self.assertEqual('A', colIndex)
        
        colIndex = ss2json.makeColumnIndex(26)
        self.assertEqual('Z', colIndex)

        colIndex = ss2json.makeColumnIndex(27)
        self.assertEqual('AA', colIndex)

        colIndex = ss2json.makeColumnIndex(52)
        self.assertEqual('AZ', colIndex)

        colIndex = ss2json.makeColumnIndex(53)
        self.assertEqual('BA', colIndex)

        colIndex = ss2json.makeColumnIndex(676)
        self.assertEqual('YZ', colIndex)

        colIndex = ss2json.makeColumnIndex(677)
        self.assertEqual('ZA', colIndex)

        colIndex = ss2json.makeColumnIndex(702)
        self.assertEqual('ZZ', colIndex)

        colIndex = ss2json.makeColumnIndex(703)
        self.assertEqual('AAA', colIndex)

    def test_splitStringBySpace_0 (self): 
        sList = ss2json.splitStringBySpace(None)
        self.assertIsNone(sList)
        
        sList = ss2json.splitStringBySpace('  a  b c ')
        self.assertEqual(3, len(sList))
        self.assertIn('a', sList)
        self.assertIn('b', sList)
        self.assertIn('c', sList)

    def test_isEmptyCell_0 (self): 
        self.assertTrue(ss2json.isEmptyCell(None))
        self.assertTrue(ss2json.isEmptyCell(''))
        self.assertTrue(ss2json.isEmptyCell('   '))
        self.assertFalse(ss2json.isEmptyCell('abc'))

    def test_setAuthInfo_0 (self): 
        ss2json.setAuthInfo(callbackUrl='', isOffline=False, isIncremental=False)

        self.assertIsNotNone(ss2json.AUTH_INFO)

if __name__ == '__main__': 
    unittest.main() 