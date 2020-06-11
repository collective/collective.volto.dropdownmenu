# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PloneRestApiDXLayer
from plone.testing import z2

import collective.volto.dropdownmenu
import plone.restapi


class VoltoDropDownMenuLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.volto.dropdownmenu)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.volto.dropdownmenu:default")


VOLTO_DROPDOWNMENU_FIXTURE = VoltoDropDownMenuLayer()


VOLTO_DROPDOWNMENU_INTEGRATION_TESTING = IntegrationTesting(
    bases=(VOLTO_DROPDOWNMENU_FIXTURE,),
    name="VoltoDropDownMenuLayer:IntegrationTesting",
)


VOLTO_DROPDOWNMENU_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(VOLTO_DROPDOWNMENU_FIXTURE,),
    name="VoltoDropDownMenuLayer:FunctionalTesting",
)


class VoltoDropDownMenuRestApiLayer(PloneRestApiDXLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(VoltoDropDownMenuRestApiLayer, self).setUpZope(
            app, configurationContext
        )

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.volto.dropdownmenu)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.volto.dropdownmenu:default")


VOLTO_DROPDOWNMENU_API_FIXTURE = VoltoDropDownMenuRestApiLayer()
VOLTO_DROPDOWNMENU_API_INTEGRATION_TESTING = IntegrationTesting(
    bases=(VOLTO_DROPDOWNMENU_API_FIXTURE,),
    name="VoltoDropDownMenuRestApiLayer:Integration",
)

VOLTO_DROPDOWNMENU_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(VOLTO_DROPDOWNMENU_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="VoltoDropDownMenuRestApiLayer:Functional",
)
