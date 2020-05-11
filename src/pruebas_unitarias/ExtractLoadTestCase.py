import os
import datetime
import json
import marbles.core

directorio = '/home/alfie-gonzalez/Documentos/Maestría/Segundo Semestre/Métodos de Gran Escala'
os.chdir(directorio)

file = 'afluencia-diaria-del-metro-cdmx.json'
json_file = open(file, 'rb')

class ExtractLoadTestCase(marbles.core.TestCase):
    def setUp(self):
        self.json_file = json_file
    
    def test_extract_load(self):
        #self.assertTrue(type(self.df) == pd.core.frame.DataFrame, 
        #                note = 'Data loaded correctly')
        self.assertTrue(self.json_file.read(2) != '[]', 
                        note = 'json file is empty')
        now = datetime.datetime.now()
        print (now.strftime("%Y-%m-%d %H:%M:%S"))
        
if __name__ == '__main__':
    marbles.core.main()


