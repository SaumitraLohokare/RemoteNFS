from dotenv import dotenv_values
import mimetypes
from Google import Create_Service
from googleapiclient.http import MediaFileUpload

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

        fileName = path.split('/')[-1]
        fileMetadata = {
            'name': fileName,
            'parents': parents
        }

        # logic to find mime types
        _mimeType = mimetypes.guess_type(path)
        mimeType = _mimeType[0]
        if mimeType == None:
            raise Exception(f'Mime type of file: {fileName} could not be guessed.')

        media = MediaFileUpload(path, mimetype=mimeType)

        self.service.files().create(
            body=fileMetadata,
            media_body=media,
            fields='id'
        ).execute()

    def deleteFile(self, fileId):
        self.service.files().delete(**{'fileId': fileId}).execute()
        
