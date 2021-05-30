from dotenv import dotenv_values
import mimetypes
from Google import Create_Service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io
import crypto

class DriveAPI:
    def __init__(self):
        self.config = dotenv_values("resources/.env")

        self.CLIENT_SECRET_FILE = 'resources/client_secret.json'
        self.API_NAME = 'drive'
        self.API_VERSION = 'v3'
        self.SCOPES = ['https://www.googleapis.com/auth/drive']

        self.service = Create_Service(self.CLIENT_SECRET_FILE, self.API_NAME, self.API_VERSION, self.SCOPES)

    def getUserData(self) -> dict:
        return self.service.about().get(fields="user").execute()

    def createRemoteNFS(self):
        """
        Creates the RemoteNFS folder for new users.
        """
        file_metadata = {
            'name': 'RemoteNFS',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        self.service.files().create(body=file_metadata).execute()

    def createFolder(self, folderName: str, parentFolderId: str = ""):
        if parentFolderId != "":
            parents = [parentFolderId]
        else:
            parents = [self.config['PARENT_FOLDER']]
        file_metadata = {
            'name': folderName,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': parents
        }
        self.service.files().create(body=file_metadata).execute()

    def deleteFolder(self, folderId):
        self.service.files().delete(**{'fileId': folderId}).execute()

    def listFiles(self, count: int = 10) -> [str]:
        """
        Give count as negative to list all files.
        """
        response = self.service.files().list().execute()['files']
        if count > 0:
            result = [file['name'] + ":" + file['id'] for file in response[:count]]
        else:
            result = [file['name'] + ":" + file['id'] for file in response]
            
        return result

    def getFilesData(self) -> {str:str}:
        """
        Will return a dict with filename as key and fileId as value
        """
        response = self.service.files().list().execute()['files']
        
        return response

    def getFileIds(self) -> {str:str}:
        """
        Will return a dict with filename as key and fileId as value
        """
        response = self.service.files().list().execute()['files']
        names = [file['name'] for file in response]
        ids = [file['id'] for file in response]
        result = dict()
        for k, v in zip(names, ids):
            result[k] = v
        
        return result

    def uploadFile(self, path: str, parentFolderId: str = ""):
        """
        Path must be absolute path to the file, and must also include file name and extension
        Path must use / and not \\
        You can use utils.sanitizeFilePath() to convert \\ to /
        """
        if parentFolderId != "":
            parents = [parentFolderId]
        else:
            parents = [self.config['PARENT_FOLDER']]

        if '/' in path:
            fileName = path.split('/')[-1]
        else:
            fileName = path.split('\\')[-1]
        fileMetadata = {
            'name': fileName,
            'parents': parents
        }
        # TODO: Encrypt file here
        crypto.encryptFile(path, self.config['PASSWORD'])

        # logic to find mime types
        _mimeType = mimetypes.guess_type(path)
        mimeType = _mimeType[0]
        if mimeType == None:
            raise Exception(f'Mime type of file: {fileName} could not be guessed.')

        media = MediaFileUpload('encrypted.file', mimetype=mimeType)

        response = self.service.files().create(
            body=fileMetadata,
            media_body=media,
            fields='id'
        ).execute()

        return fileName
        # return response['id']

    def downloadFile(self, fileId: str, fileName: str):
        request = self.service.files().get_media(fileId=fileId)        

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f'Download progress {status.progress() * 100}')
        
        fh.seek(0)
        with open(os.path.join('./downloads/', fileName), 'wb') as f:
            f.write(fh.read())
            f.close()
        
        decrypted = crypto.decryptFile(os.path.join('./files/', fileName), self.config['PASSWORD'])
        with open(os.path.join('./downloads/', fileName), 'wb') as f:
            f.write(decrypted)
            f.close()


    def deleteFile(self, fileId):
        self.service.files().delete(**{'fileId': fileId}).execute()
        
