from zope.interface import implements
from zope.component import getUtility

from Products.Five.browser import BrowserView
from plone.app.controlpanel.interfaces import IPloneControlPanelView
from Products.statusmessages.interfaces import IStatusMessage

from collective.dropboxfolder.interfaces import IDropboxAuth


class ControlPanel(BrowserView):

    implements(IPloneControlPanelView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.auth = getUtility(IDropboxAuth)

    def __call__(self):

        if 'unlink' in self.request.form:
            self.auth.unlink()
            IStatusMessage(self.request).addStatusMessage("Unlinked from Dropbox.")
            return self.request.response.redirect(self.my_url())

        if 'oauth_token' in self.request.form:
            request_token = self.request.form.get('oauth_token')
            print request_token
            verification_code = self.request.form.get('uid')
            success = self.auth.obtain_access_token(request_token,
                                                    verification_code)
            if success:
                IStatusMessage(self.request).addStatusMessage("Linked to Dropbox.")
            else:
                IStatusMessage(self.request).addStatusMessage("Could not link to Drobox.", 'error')
            return self.request.response.redirect(self.my_url())

        return self.index()

    def my_url(self):
        url = '%s/%s' % (
            self.context.absolute_url(),
            self.__name__,
        )
        return url

    def auth_url(self):
        callback_url = self.my_url()
        return self.auth.build_authorize_url(callback_url=callback_url)

    def is_linked(self):
        return self.auth.is_linked()

    def account_info(self):
        info = self.auth.account_info()
        return info
