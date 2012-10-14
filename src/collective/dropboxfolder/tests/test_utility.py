import unittest2 as unittest
from zope.component import getUtility
from zope.interface.verify import verifyObject

from collective.dropboxfolder.testing import\
    COLLECTIVE_DROPBOXFOLDER_INTEGRATION
from collective.dropboxfolder.interfaces import IDropboxAuth
from collective.dropboxfolder.utilities import DropboxAuthException


class TestDropboxAuth(unittest.TestCase):

    layer = COLLECTIVE_DROPBOXFOLDER_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_interface(self):
        auth = getUtility(IDropboxAuth)
        self.assertTrue(verifyObject(IDropboxAuth, auth))

    def test_app_secret(self):
        """ get and set the app secret """
        test_secret = 'x1c2v3b4'
        auth = getUtility(IDropboxAuth)
        self.assertFalse(auth.get_app_secret())
        auth.set_app_secret(test_secret)
        self.assertEquals(auth.get_app_secret(), test_secret)

    def test_is_linked(self):
        """ not linked by default """
        auth = getUtility(IDropboxAuth)
        self.assertFalse(auth.is_linked())

    def test_build_authorize_url(self):
        """ test that custom exception is raised """
        auth = getUtility(IDropboxAuth)
        self.assertRaises(DropboxAuthException,
                          auth.build_authorize_url)

    def test_obtain_access_token(self):
        """ test that we cant do this without a valid token """
        auth = getUtility(IDropboxAuth)
        self.assertFalse(
            auth.obtain_access_token('token', 'code')
        )
