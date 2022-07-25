import requests
import os
import json
import time
import io
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from configparser import ConfigParser

SCOPES = ['https://www.googleapis.com/auth/drive.metadata', 'https://www.googleapis.com/auth/drive']

# class InstaDownloader:
#
#     def __init__(self, token: str):
#         self.token = token
#
#     def download_photo(self):
#         url = 'https://graph.instagram.com/me/media'
#         params = {'fields': 'id,media_url,children', 'access_token': self.token}
#         list_of_media = []
#         list_of_media_children = []
#         response = requests.get(url=url, params=params)
#         data = response.json()
#         x = 1
#         while x == True:
#             if 'next' in data['paging']:
#                 for item in data['data']:
#                     if 'children' in item:
#                         list_of_media_children.append(item['id'])
#                     else:
#                         list_of_media.append(item['id'])
#                 url = data['paging']['next']
#                 response = requests.get(url=url)
#                 data = response.json()
#             else:
#                 for item in data['data']:
#                     if 'children' in item:
#                         list_of_media_children.append(item['id'])
#                     else:
#                         list_of_media.append(item['id'])
#                 x = 0
#         list_of_mediafiles = []
#         for mediafile in list_of_media:
#             url1 = 'https://graph.instagram.com/' + mediafile
#             params1 = {'fields': 'id,media_type,media_url', 'access_token': self.token}
#             response2 = requests.get(url=url1, params=params1)
#             data2 = response2.json()
#             list_of_mediafiles.append(data2)
#         for mediafile in list_of_media_children:
#             url3 = 'https://graph.instagram.com/' + mediafile + '/children'
#             params3 = {'fields': 'id,media_type,media_url', 'access_token': self.token}
#             response3 = requests.get(url=url3, params=params3)
#             data3 = response3.json()
#             for item in data3['data']:
#                 list_of_mediafiles.append(item)
#         with open('list_of_mediafiles.json', 'w') as file:
#             file.write(f'{list_of_mediafiles}')
#         return list_of_mediafiles
#         # return data


class GDrive:

    def gdriver(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # create gmail api client
            service = build('drive', 'v3', credentials=creds)
            file_metadata_folder = {
                'name': f'Insta {time.strftime("%d %b %Y %H:%M:%S")}',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = service.files().create(body=file_metadata_folder, fields='id,name'
                                          ).execute()
            print(F'Folder has created with ID: "{file.get("id")}".')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        folder_vot = file.get('id')

        with open("list_of_mediafiles.json", encoding='utf-8') as file:
            alist = json.loads(file.read().replace('\'', '"'))
            for count, name in enumerate(alist):
                try:
                    # create drive api client
                    service = build('drive', 'v3', credentials=creds)
                    if name['media_type'] == 'VIDEO':
                        file_metadata = {'name': f'{name["id"]}.mp4', 'parents': [folder_vot]}
                        file_for = requests.get(url=name["media_url"])
                        file_for_for = file_for.content
                        ttt1 = io.BytesIO(file_for_for)
                        media = MediaIoBaseUpload(ttt1,
                                                mimetype='video/mp4')
                        file = service.files().create(body=file_metadata, media_body=media,
                                                      fields='id,name').execute()
                        print(F'File ID: {file.get("id")}')
                    else:
                        file_metadata = {'name': f'{name["id"]}.jpg', 'parents': [folder_vot]}
                        file_for1 = (requests.get(url=name["media_url"]))
                        file_for_for1 = file_for1.content
                        ttt = io.BytesIO(file_for_for1)
                        media = MediaIoBaseUpload(ttt,
                                                mimetype='image/jpg')
                        file = service.files().create(body=file_metadata, media_body=media,
                                                      fields=f'id,name').execute()
                        print(f'File {count+1} with ID: {file.get("id")} uploaded to {file_metadata_folder["name"]}' )



                except HttpError as error:
                    print(F'An error occurred: {error}')
                    file = None

        return 'All done'



if __name__ == '__main__':
    config = ConfigParser()
    config.read('grabphotosfrominsta.ini')
    token_insta = config.get('section_a', 'token_insta')
    downloadr = InstaDownloader(token_insta)
    downloadr.download_photo()
    uploader = GDrive()
    uploader.gdriver()
