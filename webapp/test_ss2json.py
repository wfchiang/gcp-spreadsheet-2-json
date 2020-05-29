import unittest
import ss2json

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
        self.assertTrue('a' in sList)
        self.assertTrue('b' in sList)
        self.assertTrue('c' in sList)

if __name__ == '__main__': 
    unittest.main() 