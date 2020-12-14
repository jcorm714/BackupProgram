
from datetime import datetime
import pysftp
import boto3
import tempfile
import os.path
import shutil
from configuration import Configuration

s3 = boto3.client('s3')

def upload_file(obj_name, file):
        s3.upload_fileobj(file, "joshcormierbackups", obj_name)
      
def save_to_bucket(file, config=Configuration().load()):
        obj_name = config.aws_folder + '/'
        obj_name += datetime.now().strftime("%Y_%m_%d") + "_"
        obj_name += str(file)
        upload_file(obj_name, file)

def get_date_from_key(key):
        file_part = key.split("/")[1]
        split_parts = file_part.split("_")
        date = "_".join([date for date in split_parts if "." not in date])
        return date

def backup_files():
        config = Configuration()
        if not config.has_config():
                print("Please fill out configuration.json")
                return
        config.load()
        opts = pysftp.CnOpts()
        opts.hostkeys = None
        
        if not os.path.exists("TempDownload"):
                os.mkdir("TempDownload")
        else:
                shutil.rmtree("TempDownload")
                os.mkdir("TempDownload")
        current_request_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        with pysftp.Connection(config.host, username=config.user, password=config.password,port=config.port, cnopts=opts) as sftp:
                for fpath in config.paths:
                        file_name = fpath.split("/")[-1]    
                        local_path = os.path.join("TempDownload", file_name) 
                        print("downloading file to: " + local_path)     
                        file =  sftp.get(fpath, localpath=local_path)
                        obj_name = config.aws_folder + '/'
                        obj_name += current_request_time + "/"
                        obj_name += file_name
                        fp = open(local_path, "rb")
                        s3.upload_fileobj(fp, "joshcormierbackups", obj_name)
        res = boto3.resource("s3")
        items =  res.Bucket("joshcormierbackups").objects.all()
        keys =  [obj.key for obj in list(items) if config.aws_folder in obj.key]
        keys.sort()
        keys.reverse()
        times = [get_date_from_key(key) for key in keys]
        times = set(times)

        numberOfBackups = len(times)
        numberOfBackupsToDelete = numberOfBackups - config.numberOfBackups
        times = list(times)
        
        if(numberOfBackupsToDelete <= 0):
                print("Backup Successful")
                return

        timesToBeDeleted = times[:config.numberOfBackups-1:-1]
        for time in timesToBeDeleted:
                itemsToBeDeleted = [key for key in keys if time in key]
                bucket = res.Bucket("joshcormierbackups")
                keysToDelete = [item for item in itemsToBeDeleted]
                objectsToDelete = [{"Key": key} for key in keysToDelete]
                objects = {"Objects": objectsToDelete}
                response = bucket.delete_objects(Delete=objects)
                print(response)


if __name__ == "__main__":
        backup_files()