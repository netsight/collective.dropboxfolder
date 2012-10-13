from zope.component import Interface


class IDropboxAuth(Interface):

    def is_linked():
        """ are we currently linked to a dropbox account?"""

    def build_authorize_url():
        """ get an authorizing url for linking to dropbox """

    def obtain_access_token():
        """ get and store the access token for linking to dropbox """

    def account_info():
        """ look up the account information we are linked to """
