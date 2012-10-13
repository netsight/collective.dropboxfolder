from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree
from Products.CMFCore.interfaces import ISiteRoot

ANNOTATION_KEY = "collective.dropboxfolder"


def getStorage(clear=False):
    portal = getUtility(ISiteRoot)
    annotations = IAnnotations(portal)
    if ANNOTATION_KEY not in annotations or clear:
        storage = OOBTree()
        annotations[ANNOTATION_KEY] = storage
    return annotations[ANNOTATION_KEY]
