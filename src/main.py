import time
import os
from flask import Flask, render_template, request, redirect, url_for
from flask.json import jsonify
from DriveAPI import DriveAPI
from utils import utils

app = Flask(__name__)
api = DriveAPI()

@app.route('/', methods=['GET'])
def home():
    files = api.getFileIds()
    return jsonify(files)

@app.route('/download', methods=['GET', 'POST'])
def download():
    file_id = request.args['id']
    file_name = request.args['name']
    api.downloadFile(file_id, file_name)
    return f"file id: {file_id}"

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file_path = request.args['path']
    name = api.uploadFile(file_path)
    return f'file path: {name}'

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    api.deleteFile(request.args['id'])
    return redirect(url_for('home'))

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

def uploadImg() -> str:
    _id = api.uploadFile(os.path.join(os.path.dirname(os.path.realpath('__file__')), './files/dog.png'))
    return _id

def downloadImg(_id):
    api.downloadFile(_id, 'dog_downloaded.png')

def uploadText() -> str:
    _id = api.uploadFile(os.path.join(os.path.dirname(os.path.realpath('__file__')), './files/test.txt'))
    return _id

def downloadText(_id):
    api.downloadFile(_id, 'test_downloaded.txt')


if __name__ == '__main__':
    app.run(debug=True)
    init()

    # for file in api.listFiles():
    #     print(file)
    # api.deleteFile(fileId='')
    

    # _id = None
    # while True:
    #     choice = input('Enter command: ')
    #     if choice == 'uploadText':
    #         _id = uploadText()
    #         print('Text Id: ', _id)
    #     if choice == 'downloadText':
    #         downloadText(_id)
    #     if choice == 'uploadImg':
    #         _id = uploadImg()
    #         print('Image Id: ', _id)
    #     if choice == 'downloadImg':
    #         downloadImg(_id)
    #     if choice == 'downloadTextById':
    #         downloadText(input('Enter ID: '))
    #     if choice == 'downloadImgById':
    #         downloadImg(input('Enter ID: '))
    #     if choice == 'exit':
    #         break