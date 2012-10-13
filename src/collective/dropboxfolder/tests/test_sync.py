
import json

import unittest2 as unittest
from zope.component import getUtility
from zope.component import getGlobalSiteManager

from plone.dexterity.utils import createContentInContainer

from collective.dropboxfolder.testing import\
    COLLECTIVE_DROPBOXFOLDER_INTEGRATION

from collective.dropboxfolder.tests.mocks.mockbox import Mockbox
from collective.dropboxfolder.interfaces import IDropboxSync
from collective.dropboxfolder.interfaces import IDropboxMetadata
from collective.dropboxfolder.interfaces import IDropboxSyncProcessor

DROPBOX_FOLDER_TYPE = "collective.dropboxfolder.dropbox_folder"
DROPBOX_FILE_TYPE = "collective.dropboxfolder.dropbox_file"

class TestDropboxSync(unittest.TestCase):

    layer = COLLECTIVE_DROPBOXFOLDER_INTEGRATION

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        # Override the default sync utility
        gsm = getGlobalSiteManager()
        self.sync = Mockbox()
        gsm.registerUtility(self.sync, IDropboxSync)


    def test_new_file(self):
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

        self.sync.delta_response.append(sync_data)

        container = self.portal
        container_fti = container.getTypeInfo()
    
        if container_fti is not None and not container_fti.allowType(DROPBOX_FOLDER_TYPE):
            raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FOLDER_TYPE,))
        
        ob = createContentInContainer(container,
                                      DROPBOX_FOLDER_TYPE,
                                      checkConstraints=False,
                                      id="dropboxfolder",
                                      )

        processor = IDropboxSyncProcessor(ob)
        processor.sync()

        self.assertEqual(1, len(ob))
        self.assertIsNotNone(ob.get("magnum-opus.txt", None))

        metadata = IDropboxMetadata(ob['magnum-opus.txt']).get()
        self.assertIsNotNone(metadata)
        self.assertEqual(77, metadata['bytes'])
        self.assertEqual('362e2029684fe', metadata['rev'])

    def test_odd_filename(self):
        container = self.portal

        metadata = json.loads("""
            {
               "bytes": 77,
               "icon": "page_white_text",
               "is_dir": false,
               "mime_type": "text/plain",
               "modified": "Wed, 20 Jul 2011 22:04:50 +0000",
               "path": "/A long and mysterious filename",
               "rev": "362e2029684fe",
               "revision": 221922,
               "root": "dropbox",
               "size": "77 bytes",
               "thumb_exists": false
           }
        """)

        sync_data = {
                "entries": [
                    ["/a-long-and-mysterious-filename", metadata],
                    ],
                "reset": False,
                "cursor": "1",
                "has_more": False,
                }

        self.sync.delta_response.append(sync_data)

        container = self.portal
        container_fti = container.getTypeInfo()
    
        if container_fti is not None and not container_fti.allowType(DROPBOX_FOLDER_TYPE):
            raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FOLDER_TYPE,))
        
        ob = createContentInContainer(container,
                                      DROPBOX_FOLDER_TYPE,
                                      checkConstraints=False,
                                      id="dropboxfolder",
                                      )

        processor = IDropboxSyncProcessor(ob)
        processor.sync()

        self.assertEqual(1, len(ob))
        self.assertIsNotNone(ob.get("a-long-and-mysterious-filename", None))

        metadata = IDropboxMetadata(ob['a-long-and-mysterious-filename']).get()
        self.assertIsNotNone(metadata)
        self.assertEqual(77, metadata['bytes'])
        self.assertEqual('362e2029684fe', metadata['rev'])

    
    def test_multiple_files(self):
        container = self.portal

        metadata1 = json.loads("""
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

        metadata2 = json.loads("""
            {
               "bytes": 1230,
               "icon": "page_white_text",
               "is_dir": false,
               "mime_type": "text/plain",
               "modified": "Wed, 20 Jul 2011 22:04:50 +0000",
               "path": "/Somewhere_over_the_rainbow.txt",
               "rev": "362e",
               "revision": 221922,
               "root": "dropbox",
               "size": "77 bytes",
               "thumb_exists": false
           }
        """)

        sync_data = {
                "entries": [
                    [metadata1['path'], metadata1],
                    [metadata2['path'], metadata2],
                    ],
                "reset": False,
                "cursor": "1",
                "has_more": False,
                }

        self.sync.delta_response.append(sync_data)

        container = self.portal
        container_fti = container.getTypeInfo()
    
        if container_fti is not None and not container_fti.allowType(DROPBOX_FOLDER_TYPE):
            raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FOLDER_TYPE,))
        
        ob = createContentInContainer(container,
                                      DROPBOX_FOLDER_TYPE,
                                      checkConstraints=False,
                                      id="dropboxfolder",
                                      )

        processor = IDropboxSyncProcessor(ob)
        processor.sync()

        self.assertEqual(2, len(ob))

        self.assertIsNotNone(ob.get("magnum-opus.txt", None))
        metadata = IDropboxMetadata(ob['magnum-opus.txt']).get()
        self.assertIsNotNone(metadata)
        self.assertEqual(77, metadata['bytes'])
        self.assertEqual('362e2029684fe', metadata['rev'])

        self.assertIsNotNone(ob.get("somewhere_over_the_rainbow.txt", None))
        metadata = IDropboxMetadata(ob['somewhere_over_the_rainbow.txt']).get()
        self.assertIsNotNone(metadata)
        self.assertEqual(1230, metadata['bytes'])
        self.assertEqual('362e', metadata['rev'])

    
    def test_single_file_update(self):
        container = self.portal

        metadata1 = json.loads("""
            {
               "bytes": 1230,
               "icon": "page_white_text",
               "is_dir": false,
               "mime_type": "text/plain",
               "modified": "Wed, 20 Jul 2011 22:04:50 +0000",
               "path": "/Somewhere_over_the_rainbow.txt",
               "rev": "362e",
               "revision": 221922,
               "root": "dropbox",
               "size": "1230 bytes",
               "thumb_exists": false
           }
        """)

        metadata2 = json.loads("""
            {
               "bytes": 1235,
               "icon": "page_white_text",
               "is_dir": false,
               "mime_type": "text/plain",
               "modified": "Wed, 20 Jul 2011 22:04:50 +0000",
               "path": "/Somewhere_over_the_rainbow.txt",
               "rev": "362f",
               "revision": 221962,
               "root": "dropbox",
               "size": "1235 bytes",
               "thumb_exists": false
           }
        """)

        sync_data = {
                "entries": [
                    [metadata1['path'], metadata1],
                    [metadata2['path'], metadata2],
                    ],
                "reset": False,
                "cursor": "1",
                "has_more": False,
                }

        self.sync.delta_response.append(sync_data)

        container = self.portal
        container_fti = container.getTypeInfo()
    
        if container_fti is not None and not container_fti.allowType(DROPBOX_FOLDER_TYPE):
            raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FOLDER_TYPE,))
        
        ob = createContentInContainer(container,
                                      DROPBOX_FOLDER_TYPE,
                                      checkConstraints=False,
                                      id="dropboxfolder",
                                      )

        processor = IDropboxSyncProcessor(ob)
        processor.sync()

        self.assertEqual(1, len(ob))

        self.assertIsNotNone(ob.get("somewhere_over_the_rainbow.txt", None))
        metadata = IDropboxMetadata(ob['somewhere_over_the_rainbow.txt']).get()
        self.assertIsNotNone(metadata)
        self.assertEqual(1235, metadata['bytes'])
        self.assertEqual('362f', metadata['rev'])





