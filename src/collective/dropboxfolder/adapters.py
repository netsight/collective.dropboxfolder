
from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility

from zope.annotation import IAnnotations
from plone.i18n.normalizer.interfaces import IURLNormalizer 

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.utils import createContentInContainer

from collective.dropboxfolder.interfaces import IDropboxSyncProcessor
from collective.dropboxfolder.interfaces import IDropboxSync
from collective.dropboxfolder.interfaces import IDropboxSyncMetadata
from collective.dropboxfolder.interfaces import IDropboxFileMetadata
from collective.dropboxfolder.content.dropbox_folder import IDropboxFolder
from collective.dropboxfolder.content.config import DROPBOX_FOLDER_TYPE
from collective.dropboxfolder.content.config import DROPBOX_FILE_TYPE

FILE_METADATA_KEY = "collective.dropboxfolder.metadata"
SYNC_METADATA_KEY = "collective.dropboxfolder.metadata"


class DropboxFileMetadata(object):
    
    implements(IDropboxFileMetadata)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def get(self):
        annotations = IAnnotations(self.context)
        return annotations.get(FILE_METADATA_KEY, None)

    def set(self, value):
        assert(isinstance(value,dict))
        annotations = IAnnotations(self.context)
        annotations[FILE_METADATA_KEY] = value


class DropboxSyncMetadata(object):
    
    implements(IDropboxSyncMetadata)
    adapts(IDexterityContainer)

    def __init__(self, context):
        self.context = context

    def _storage(self):
        annotations = IAnnotations(self.context)
        return annotations.get(SYNC_METADATA_KEY, 

    def delta_cursor(self):
        pass

    def set_delta_cursor(self):
        pass


class DropboxSyncProcessor(object):
    
    implements(IDropboxSyncProcessor)
    adapts(IDexterityContainer)

    def __init__(self, context):
        self.context = context

    def sync(self):
        connector = getUtility(IDropboxSync)

        normalize = getUtility(IURLNormalizer).normalize
        container = self.context

        delta = connector.delta()

        entries = delta.get('entries', [])
        for path,metadata in entries:
            exploded_path = [x for x in path.split('/') if x]
            folders = exploded_path[:-1]
            filename = exploded_path[-1]

            if metadata['is_dir']: continue # skip directories for now
            if folders: continue # support just one level for now

            # Dictionary of Dropbox path to Plone ID - only really efficient for
            # the one level sync currently implemented.
            existing = dict()
            for ob in container.objectValues():
                md = IDropboxFileMetadata(ob).get()
                if md is not None:
                    existing[md['path']] = ob

            if path in existing:
                ob = existing[path]
            else:
                plone_id = normalize(filename)
                container_fti = container.getTypeInfo()
                if container_fti is not None and not container_fti.allowType(DROPBOX_FILE_TYPE):
                    raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FILE_TYPE,))
                ob = createContentInContainer(container,
                                              DROPBOX_FILE_TYPE,
                                              checkConstraints=False,
                                              id=normalize(filename),
                                              )

            # Update the metadata with the latest
            IDropboxFileMetadata(ob).set(metadata)



