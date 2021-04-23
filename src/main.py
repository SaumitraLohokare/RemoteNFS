import time
import os
from flask import Flask, render_template
from DriveAPI import DriveAPI
from utils import utils

app = Flask(__name__)
api = DriveAPI()

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

def init():
    """
    Initialises RemoteNFS for new Users
    """
    # Check if RemoteNFS exists
    res = api.getFileIds().get('RemoteNFS')
    if res == None:
        print("RemoteNFS folder not found in User's Drive...\nCreating Folder")
        api.createRemoteNFS()
        print("Folder created.")
    
    while res == None:
        res = api.getFileIds().get('RemoteNFS')
        if res == None:
            print("RemoteNFS folder still not found, sleeping for 1s and checking again")
            time.sleep(1)
    
    if not os.path.exists("resources/.env"):
        utils.setupEnv({'PARENT_FOLDER': res})
    

if __name__ == '__main__':
    app.run(debug=True)
    init()