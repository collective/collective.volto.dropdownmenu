# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.volto.dropdownmenu.testing import (
    VOLTO_DROPDOWNMENU_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.volto.dropdownmenu is properly installed."""

    layer = VOLTO_DROPDOWNMENU_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.volto.dropdownmenu is installed."""
        self.assertTrue(
            self.installer.isProductInstalled("collective.volto.dropdownmenu")
        )

    def test_browserlayer(self):
        """Test that ICollectiveVoltoDropDownMenuLayer is registered."""
        from collective.volto.dropdownmenu.interfaces import (
            ICollectiveVoltoDropDownMenuLayer,
        )
        from plone.browserlayer import utils

        self.assertIn(
            ICollectiveVoltoDropDownMenuLayer, utils.registered_layers()
        )


class TestUninstall(unittest.TestCase):

    layer = VOLTO_DROPDOWNMENU_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["collective.volto.dropdownmenu"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.volto.dropdownmenu is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled("collective.volto.dropdownmenu")
        )

    def test_browserlayer_removed(self):
        """Test that ICollectiveVoltoDropDownMenuLayer is removed."""
        from collective.volto.dropdownmenu.interfaces import (
            ICollectiveVoltoDropDownMenuLayer,
        )
        from plone.browserlayer import utils

        self.assertNotIn(
            ICollectiveVoltoDropDownMenuLayer, utils.registered_layers()
        )
