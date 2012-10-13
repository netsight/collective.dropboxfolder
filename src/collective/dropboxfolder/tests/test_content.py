import unittest2 as unittest
from zope.component import getUtility

from plone.dexterity.utils import createContentInContainer

from collective.dropboxfolder.testing import\
    COLLECTIVE_DROPBOXFOLDER_INTEGRATION

from collective.dropboxfolder.content.config import DROPBOX_FOLDER_TYPE
from collective.dropboxfolder.content.config import DROPBOX_FILE_TYPE

class TestDropboxContent(unittest.TestCase):

    layer = COLLECTIVE_DROPBOXFOLDER_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_folder_addable(self):
        container = self.portal
        container_fti = container.getTypeInfo()
    
        if container_fti is not None and not container_fti.allowType(DROPBOX_FOLDER_TYPE):
            raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FOLDER_TYPE,))
        
        ob = createContentInContainer(container,
                                      DROPBOX_FOLDER_TYPE,
                                      checkConstraints=False,
                                      id='dropboxfolder',
                                      )


    def test_file_addable(self):
        container = self.portal
        container_fti = container.getTypeInfo()
    
        if container_fti is not None and not container_fti.allowType(DROPBOX_FOLDER_TYPE):
            raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FOLDER_TYPE,))
        
        ob = createContentInContainer(container,
                                      DROPBOX_FOLDER_TYPE,
                                      checkConstraints=False,
                                      id='dropboxfolder',
                                      )
        
        ob = createContentInContainer(ob,
                                      DROPBOX_FILE_TYPE,
                                      checkConstraints=False,
                                      id='dropboxfile',
                                      )



