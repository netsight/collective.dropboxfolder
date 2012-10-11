from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import collective.dropboxfolder


COLLECTIVE_DROPBOXFOLDER = PloneWithPackageLayer(
    zcml_package=collective.dropboxfolder,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.dropboxfolder:testing',
    name="COLLECTIVE_DROPBOXFOLDER")

COLLECTIVE_DROPBOXFOLDER_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_DROPBOXFOLDER, ),
    name="COLLECTIVE_DROPBOXFOLDER_INTEGRATION")

COLLECTIVE_DROPBOXFOLDER_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_DROPBOXFOLDER, ),
    name="COLLECTIVE_DROPBOXFOLDER_FUNCTIONAL")
