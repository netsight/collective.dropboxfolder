import unittest2 as unittest
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from collective.dropboxfolder.testing import\
    COLLECTIVE_DROPBOXFOLDER_INTEGRATION
from collective.dropboxfolder.interfaces import IDropboxAuth


class TestDropboxAuth(unittest.TestCase):

    layer = COLLECTIVE_DROPBOXFOLDER_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_utility_registered(self):
        auth = getUtility(IDropboxAuth)
        linked = auth.is_linked()
        self.assertTrue(isinstance(linked, bool),
                        'Expected boolean value')
        self.assertFalse(linked,
                         'Auth should not be linked by default')
