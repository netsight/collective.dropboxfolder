from five import grok
from zope import schema

from plone.directives import form, dexterity

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from collective.dropboxfolder import _

class IDropboxFolder(form.Schema):
    """A folder which syncs its contents with a given Dropbox account folder.
    """
    
    title = schema.TextLine(
            title=_(u"Name"),
        )
    
    description = schema.Text(
            title=_(u"A short summary"),
        )

    root = schema.TextLine(
            title=_("Root folder"),
        )

