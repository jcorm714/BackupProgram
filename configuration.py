import json
import os

class Configuration:
        def __init__ (self):
                self.user = None
                self.password = None
                self.host = None
                self.numberOfBackups = 0
                self.paths = []
                self.port = 0
                self.aws_folder = None
       

        def save(self):
                with open("configuration.json", "w") as fil:
                         data = json.dumps(self.__dict__, indent=4)
                         fil.write(data)
                
        
        def load (self):
                with open("configuration.json", "r") as fil:
                        data = json.load(fil)
                        self.user = data["user"]
                        self.password = data["password"]
                        self.host = data["host"]
                        self.aws_folder = data["aws_folder"]
                        self.paths = data["paths"]
                        self.port = data["port"]
                        self.numberOfBackups = data["numberOfBackups"]
                        
                        
        def has_config(self):
                if os.path.exists("configuration.json"):
                       return  True
                with open("configuration.json", "w") as fil:
                       data = json.dumps(self.__dict__, indent=4)
                       fil.write(data)
                return False



if __name__ == "__main__":
        c = Configuration()
        c.has_config()
        c.load()
        