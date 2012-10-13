from dropbox import session, client

from zope.interface import implements

from collective.dropboxfolder.interfaces import IDropboxAuth
from collective.dropboxfolder.storage import getStorage

APP_KEY = 'wgpqxchu9chkfy1'
APP_SECRET = 'dgc7h96vd3v1g6t'
ACCESS_TYPE = 'dropbox'


class DropboxAuth(object):
    implements(IDropboxAuth)

    def _box(self):
        box = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        storage = getStorage()
        if storage.get('access_token'):
            access_token = storage.get('access_token')
            access_token_secret = storage.get('access_token_secret')
            box.set_token(access_token, access_token_secret)
        return box

    def is_linked(self):
        return self._box().is_linked()

    def build_authorize_url(self, callback_url=None):
        box = self._box()
        request_token = box.obtain_request_token()
        getStorage()['request_token'] = request_token
        url = box.build_authorize_url(request_token,
                                      oauth_callback=callback_url)
        return url

    def obtain_access_token(self, token, verification_code):
        box = self._box()
        storage = getStorage()
        request_token = storage['request_token']
        if request_token.key != token:
            return False

        box.set_request_token(request_token.key, request_token.secret)
        access_token = box.obtain_access_token(request_token)
        storage['access_token'] = access_token.key
        storage['access_token_secret'] = access_token.secret
        return True

    def unlink(self):
        if not self.is_linked():
            return

        storage = getStorage()
        if 'access_token' in storage:
            del storage['access_token']
        if 'access_token_secret' in storage:
            del storage['access_token_secret']

    def account_info(self):
        box = self._box()
        boxclient = client.DropboxClient(box)
        return boxclient.account_info()

