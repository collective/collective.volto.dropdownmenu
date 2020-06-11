# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.testing import (
    VOLTO_DROPDOWNMENU_API_FUNCTIONAL_TESTING,
)
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from transaction import commit

import json
import unittest


class DropDownMenuServiceTest(unittest.TestCase):

    layer = VOLTO_DROPDOWNMENU_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_route_exists(self):
        response = self.api_session.get("/@dropdown-menu")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

    def test_return_empty_dict_if_not_set(self):
        response = self.api_session.get("/@dropdown-menu")
        results = response.json()
        self.assertEqual(results, {})

    def test_right_data(self):
        test_data = {"foo": "bar"}
        api.portal.set_registry_record(
            "menu_configuration",
            json.dumps(test_data),
            interface=IDropDownMenu,
        )
        commit()
        response = self.api_session.get("/@dropdown-menu")
        result = response.json()
        self.assertEqual(result, test_data)
