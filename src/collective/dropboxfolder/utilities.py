from zope.interface import implements

from collective.dropboxfolder.interfaces import IDropboxAuth


class DropboxAuth(object):
    implements(IDropboxAuth)

    def is_linked(self):
        return False

    def build_authorize_url(self):
        pass

    def obtain_access_token(self):
        pass

    def account_info(self):
        pass
