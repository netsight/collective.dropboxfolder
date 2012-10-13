from dropbox import session, client, rest

from zope.interface import implements

from collective.dropboxfolder.interfaces import IDropboxAuth
from collective.dropboxfolder.storage import getStorage

APP_KEY = 'i1sjpaxv3brl0oa'
ACCESS_TYPE = 'dropbox'


class DropboxAuthException(Exception):
    pass


class DropboxAuth(object):
    implements(IDropboxAuth)

    def _box(self):
        storage = getStorage()
        app_secret = self.get_app_secret() or ''

        box = session.DropboxSession(APP_KEY, app_secret, ACCESS_TYPE)
        if storage.get('access_token'):
            access_token = storage.get('access_token')
            access_token_secret = storage.get('access_token_secret')
            box.set_token(access_token, access_token_secret)
        return box

    def set_app_secret(self, value):
        storage = getStorage()
        storage['app_secret'] = value

    def get_app_secret(self):
        storage = getStorage()
        app_secret = storage.get('app_secret')
        return app_secret

    def can_link(self):
        return self.get_app_secret() is not None

    def is_linked(self):
        box = self._box()
        return box.is_linked()

    def build_authorize_url(self, callback_url=None):
        box = self._box()
        try:
            request_token = box.obtain_request_token()
        except rest.ErrorResponse as e:
            raise DropboxAuthException(e)

        getStorage()['request_token'] = request_token
        try:
            url = box.build_authorize_url(request_token,
                                          oauth_callback=callback_url)
        except rest.ErrorResponse as e:
            raise DropboxAuthException(e)
        return url

    def obtain_access_token(self, token, verification_code):
        box = self._box()
        storage = getStorage()
        request_token = storage.get('request_token')
        if not request_token or request_token.key != token:
            return False

        box.set_request_token(request_token.key, request_token.secret)
        try:
            access_token = box.obtain_access_token(request_token)
        except rest.ErrorResponse as e:
            raise DropboxAuthException(e)
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
