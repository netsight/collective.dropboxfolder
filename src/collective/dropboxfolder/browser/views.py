from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from collective.dropboxfolder.interfaces import IDropboxSyncProcessor


class SyncFolder(BrowserView):

    def sync_now(self):
        syncer = IDropboxSyncProcessor(self.context)
        syncer.sync()

        IStatusMessage(self.request).addStatusMessage("Dropbox sync complete.")
        return self.request.response.redirect(self.context.absolute_url())
