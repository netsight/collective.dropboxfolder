from collections import deque

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

    def delta(self, cursor):
        return self.delta_response.popleft()

    def get_file(self):
        return self.get_file_response.popleft()

    def put_file(self):
        return self.put_file_response.popleft()
