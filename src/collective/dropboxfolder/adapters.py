import logging

from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility

from BTrees.OOBTree import OOBTree

from zope.annotation import IAnnotations
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.i18n.normalizer.interfaces import IFileNameNormalizer

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.utils import createContentInContainer
from plone.namedfile import NamedBlobFile

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
        filename_normalize = getUtility(IFileNameNormalizer).normalize
        container = self.context

        cursor = IDropboxSyncMetadata(container).delta_cursor()
        logger.info("DropboxSyncProcessor: current cursor %s", cursor)
        delta = connector.delta(cursor)

        entries = delta.get('entries', [])
        for lower_case_path, metadata in entries:

            # The API says lower_case_path will always be lowercase:
            # https://www.dropbox.com/developers/reference/api#delta
            # but we assume this below, so make sure this is the case
            # in case the API changes.
            lower_case_path = lower_case_path.lower()

            exploded_path = [x for x in lower_case_path.split('/') if x]
            folders = exploded_path[:-1]
            filename = exploded_path[-1]

            if metadata is not None and metadata['is_dir']: continue  # skip directories for now
            if folders: continue  # support just one level for now

            # Dictionary of Dropbox path to Plone ID - only really efficient for
            # the one level sync currently implemented.
            existing = dict()
            for ob in container.objectValues():
                md = IDropboxFileMetadata(ob).get()
                if md is not None:
                    existing[md['path'].lower()] = ob

            if metadata is not None:  # file has data
                if lower_case_path in existing:
                    logger.info("DropboxSyncProcessor: Updating file for path %s", lower_case_path)
                    db_file = existing[lower_case_path]
                else:
                    logger.info("DropboxSyncProcessor: Creating file for path %s", lower_case_path)
                    container_fti = container.getTypeInfo()
                    if container_fti is not None and not container_fti.allowType(DROPBOX_FILE_TYPE):
                        raise ValueError("Disallowed subobject type: %s" % (DROPBOX_FILE_TYPE,))
                    db_file = createContentInContainer(
                        container,
                        DROPBOX_FILE_TYPE,
                        checkConstraints=False,
                        id=normalize(filename),
                    )

                # Update with latest data
                current_rev = None
                current_metadata = IDropboxFileMetadata(db_file).get()
                if current_metadata is not None:
                    current_rev = current_metadata.get('rev', None)
                if current_rev is None or current_rev != metadata['rev']:
                    logger.info('DropboxSyncProcessor: File has changed - updating data')
                    filedata = connector.get_file(lower_case_path).read()
                    db_file.file_data = NamedBlobFile(
                        filedata,
                        filename=filename,
                    )

                # Update the metadata with the latest
                IDropboxFileMetadata(db_file).set(metadata)


            if metadata is None and lower_case_path in existing: # file deleted
                container.manage_delObjects( [existing[lower_case_path].getId()] )

        IDropboxSyncMetadata(container).set_delta_cursor(delta['cursor'])
        logger.info("DropboxSyncProcessor: complete (new cursor: %s)", delta['cursor'])
