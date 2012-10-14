import logging

from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility

from BTrees.OOBTree import OOBTree

from zope.annotation import IAnnotations
from plone.i18n.normalizer.interfaces import IURLNormalizer

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.utils import createContentInContainer

from collective.dropboxfolder.interfaces import IDropboxSyncProcessor
from collective.dropboxfolder.interfaces import IDropboxClient
from collective.dropboxfolder.interfaces import IDropboxSyncMetadata
from collective.dropboxfolder.interfaces import IDropboxFileMetadata
from collective.dropboxfolder.content.dropbox_folder import IDropboxFolder
from collective.dropboxfolder.content.config import DROPBOX_FOLDER_TYPE
from collective.dropboxfolder.content.config import DROPBOX_FILE_TYPE

FILE_METADATA_KEY = "collective.dropboxfolder.metadata"
SYNC_METADATA_KEY = "collective.dropboxfolder.metadata"

logger = logging.getLogger("collective.dropboxfolder")


class DropboxFileMetadata(object):

    implements(IDropboxFileMetadata)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def get(self):
        annotations = IAnnotations(self.context)
        return annotations.get(FILE_METADATA_KEY, None)

    def set(self, value):
        assert(isinstance(value, dict))
        annotations = IAnnotations(self.context)
        annotations[FILE_METADATA_KEY] = value


class DropboxSyncMetadata(object):

    implements(IDropboxSyncMetadata)
    adapts(IDexterityContainer)

    def __init__(self, context):
        self.context = context

    def _storage(self):
        annotations = IAnnotations(self.context)
        return annotations.setdefault(SYNC_METADATA_KEY, default=OOBTree())

    def delta_cursor(self):
        storage = self._storage()
        return storage.get('delta_cursor', None)

    def set_delta_cursor(self, value):
        storage = self._storage()
        storage['delta_cursor'] = value


class DropboxSyncProcessor(object):

    implements(IDropboxSyncProcessor)
    adapts(IDexterityContainer)

    def __init__(self, context):
        self.context = context

    def sync(self):
        logger.info("DropboxSyncProcessor: starting...")
        connector = getUtility(IDropboxClient)

        normalize = getUtility(IURLNormalizer).normalize
        container = self.context

        cursor = IDropboxSyncMetadata(container).delta_cursor()
        logger.info("DropboxSyncProcessor: current cursor %s", cursor)
        delta = connector.delta(cursor)

        entries = delta.get('entries', [])
        for path, metadata in entries:
            exploded_path = [x for x in path.split('/') if x]
            folders = exploded_path[:-1]
            filename = exploded_path[-1]

            if metadata is not None and metadata['is_dir']: continue # skip directories for now
            if folders: continue # support just one level for now

            # Dictionary of Dropbox path to Plone ID - only really efficient for
            # the one level sync currently implemented.
            existing = dict()
            for ob in container.objectValues():
                md = IDropboxFileMetadata(ob).get()
                if md is not None:
                    existing[md['path']] = ob

            if metadata is not None: # file has data
                if path in existing:
                    logger.info("DropboxSyncProcessor: Updating file for path %s", path)
                    db_file = existing[path]
                else:
                    logger.info("DropboxSyncProcessor: Creating file for path %s", path)
                    plone_id = normalize(filename)
                    container_fti = container.getTypeInfo()
                    if container_fti is not None and not container_fti.allowType(DROPBOX_FILE_TYPE):
                        raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FILE_TYPE,))
                    db_file = createContentInContainer(container,
                                                  DROPBOX_FILE_TYPE,
                                                  checkConstraints=False,
                                                  id=normalize(filename),
                                                  )

                # Update the metadata with the latest
                IDropboxFileMetadata(db_file).set(metadata)

            if metadata is None and path in existing: # file deleted
                container.manage_delObjects( [existing[path].getId()] )

        IDropboxSyncMetadata(container).set_delta_cursor(delta['cursor'])
        logger.info("DropboxSyncProcessor: complete (new cursor: %s)", delta['cursor'])
