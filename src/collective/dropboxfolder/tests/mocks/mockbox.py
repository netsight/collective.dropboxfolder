from collections import deque
import simplejson as json

from zope import interface

from collective.dropboxfolder.interfaces import IDropboxClient


class Mockbox(object):
    """ This is a mocked implementation of the IDropboxClient interface
        for use in tests.
        It works by users queuing up responses. There is no bounds
        checking because the test harness should fill up enough
        responses!
    """

    interface.implements(IDropboxClient)

    delta_response = deque()
    get_file_response = deque()
    put_file_response = deque()

    def delta(self, cursor=None):
        # This makes sure we get something most similar to the json
        # decoding produced by dropbox client
        return json.loads(json.dumps(self.delta_response.popleft()))

    def get_file(self, from_path, rev=None):
        return self.get_file_response.popleft()

    def put_file(self, full_path, file_obj, overwrite=False, parent_rev=None):
        return self.put_file_response.popleft()
