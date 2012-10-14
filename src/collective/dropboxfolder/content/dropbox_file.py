from five import grok
from zope import schema

from plone.directives import form, dexterity

from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobFile

from collective.dropboxfolder import _

class IDropboxFile(form.Schema):
    """A folder which syncs its contents with a given Dropbox account folder.
    """

    title = schema.TextLine(
            title=_(u"Name"),
        )

    description = schema.Text(
            title=_(u"A short summary"),
        )

    file_data = NamedBlobFile(
            title=_(u"File"),
        )


