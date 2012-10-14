import json
from cStringIO import StringIO

import unittest2 as unittest
from zope.component import getUtility
from zope.component import getGlobalSiteManager

from plone.dexterity.utils import createContentInContainer

from collective.dropboxfolder.testing import\
    COLLECTIVE_DROPBOXFOLDER_INTEGRATION

from collective.dropboxfolder.content.config import DROPBOX_FOLDER_TYPE
from collective.dropboxfolder.interfaces import IDropboxSyncProcessor
from collective.dropboxfolder.interfaces import IDropboxSyncMetadata

from collective.dropboxfolder.tests.mocks.mockbox import Mockbox
from collective.dropboxfolder.interfaces import IDropboxClient


class TestDropboxSyncMetadata(unittest.TestCase):

    layer = COLLECTIVE_DROPBOXFOLDER_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        # Override the default sync utility
        gsm = getGlobalSiteManager()
        self.old_client = getUtility(IDropboxClient)
        gsm.unregisterUtility(self.old_client, IDropboxClient)
        # Register our mocked version
        self.client = Mockbox()
        gsm.registerUtility(self.client, IDropboxClient)

    def tearDown(self):
        # remove our mocked utility
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(self.client, IDropboxClient)
        # re-add the original
        gsm.registerUtility(self.old_client, IDropboxClient)

    def test_delta_cursor_stored(self):
        container = self.portal

        metadata = json.loads("""
            {
               "bytes": 77,
               "icon": "page_white_text",
               "is_dir": false,
               "mime_type": "text/plain",
               "modified": "Wed, 20 Jul 2011 22:04:50 +0000",
               "path": "/magnum-opus.txt",
               "rev": "362e2029684fe",
               "revision": 221922,
               "root": "dropbox",
               "size": "77 bytes",
               "thumb_exists": false
           }
        """)

        sync_data = {
                "entries": [
                    ["/magnum-opus.txt", metadata],
                    ],
                "reset": False,
                "cursor": "1",
                "has_more": False,
                }

        self.client.delta_response.append(sync_data)
        self.client.get_file_response.append(StringIO())

        container = self.portal
        container_fti = container.getTypeInfo()

        if container_fti is not None and not container_fti.allowType(DROPBOX_FOLDER_TYPE):
            raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FOLDER_TYPE,))

        folder = createContentInContainer(
            container,
            DROPBOX_FOLDER_TYPE,
            checkConstraints=False,
            id="dropboxfolder",
        )

        processor = IDropboxSyncProcessor(folder)
        md = IDropboxSyncMetadata(folder)

        processor.sync()
        self.assertEqual("1", md.delta_cursor())

        sync_data = {
                "entries": [],
                "reset": False,
                "cursor": "3",
                "has_more": False,
                }
        self.client.delta_response.append(sync_data)
        processor.sync()
        self.assertEqual("3", md.delta_cursor())
