from Products.Five.browser import BrowserView

from collective.dropboxfolder.interfaces import IDropboxSyncProcessor


class SyncFolder(BrowserView):

    def sync_now(self):
        syncer = IDropboxSyncProcessor(self.context)
        syncer.sync()
