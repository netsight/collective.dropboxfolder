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

    def unlink():
        """ unlink from a dropbox account """


class IDropboxSync(Interface):

    def delta():
        """ Get the list of changes from the linked dropbox """

    def get_file():
        """ Get a file's data from dropbox """

    def put_file():
        """ Put a files data to dropbox """


class IDropboxSyncProcessor(Interface):

    def sync():
        """ Connect to dropbox and work out what to do to sync the folder """


class IDropboxFileMetadata(Interface):
    """ Store the metadata from dropbox on a file. """

    def get():
        """ Get the dropbox metadata for an object as a dict """

    def set(value):
        """ Set the dropbox metadata for an object """


class IDropboxSyncMetadata(Interface):
    """ Store the metadata for the dropbox sync process (e.g., the
        delta() cursor value).
    """

    def delta_cursor():
        """ Get the last dropbox metadata cursor for container. """

    def set_delta_cursor():
        """ Set the delta cursor for a container. """

