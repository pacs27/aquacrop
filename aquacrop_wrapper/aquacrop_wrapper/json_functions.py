import json




class JSONFunctions(object):

    def __init__(self, ):
        pass
    
    def read_json_file(self):
        with open(self.json_file) as json_file:
            data = json.load(json_file)
        return data

    def transform_pandas_to_json(self, df):
        return df.to_json(orient='records')
    
    def json_load(self, data):
        return json.loads(data)
    
    def save_json_file(self, data, file_path):
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile)