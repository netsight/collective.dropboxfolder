from dropbox import client, rest, session
from Products.Five import BrowserView
from oauth.oauth import OAuthToken
from Products.CMFPlone.utils import normalizeString

APP_KEY = 'wgpqxchu9chkfy1'
APP_SECRET = 'dgc7h96vd3v1g6t'
ACCESS_TYPE = 'dropbox'


class Dropbox(BrowserView):

    def generate_access_token(self):
        box = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        request_token = box.obtain_request_token()
        url = box.build_authorize_url(request_token)
        print url
        raw_input()

        access_token = box.obtain_access_token(request_token)
        assert(access_token is not None)
        return access_token.to_string()

    def _get_box_client(self):
        box = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        # TODO: store in ZODB
        access_key = ''
        access_secret = ''
        box.set_token(access_key, access_secret)
        box_client = client.DropboxClient(box)
        return box_client

    def client_info(self):
        box_client = self._get_box_client()
        return box_client.account_info()

    def sync_files(self):
        box_client = self._get_box_client()
        root = box_client.metadata('/plone')
        count = 0

        for f in root['contents']:
            if not f['is_dir']:
                print f['path']
                filename = f['path'].split('/')[-1]
                file_id = normalizeString(filename)
                if file_id not in self.context.objectIds():
                    self.context.invokeFactory(type_name='File', id=file_id)
                ob = getattr(self.context, file_id)
                remote_file, remote_file_metadata = \
                             box_client.get_file_and_metadata(f['path'])
                ob.setFile(remote_file.read(), filename=filename)
                ob.reindexObject()
                count += 1

        return "Synced %i files." % count
