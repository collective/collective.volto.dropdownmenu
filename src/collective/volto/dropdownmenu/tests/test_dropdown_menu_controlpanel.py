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
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import RelativeSession
from transaction import commit
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

import json
import unittest


class DropDownMenuServiceTest(unittest.TestCase):

    layer = VOLTO_DROPDOWNMENU_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        self.controlpanel_url = "/@controlpanels/dropdown-menu-settings"
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_controlpanel_listed(self):
        response = self.api_session.get("/@controlpanels")

        titles = [x.get("title") for x in response.json()]
        self.assertIn("Dropdown Menu settings", titles)

    def test_route_exists(self):
        response = self.api_session.get(
            "/@controlpanels/dropdown-menu-settings"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )


class BaseTestWithFolders(unittest.TestCase):
    layer = VOLTO_DROPDOWNMENU_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        self.controlpanel_url = "/@controlpanels/dropdown-menu-settings"
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder_a = api.content.create(
            container=self.portal, type="Folder", title="Folder a"
        )

        self.folder_b = api.content.create(
            container=self.portal, type="Folder", title="Folder b"
        )

        self.doc = api.content.create(
            container=self.portal, type="Document", title="Document"
        )

        self.doc_a = api.content.create(
            container=self.folder_a, type="Document", title="Document a"
        )

        self.doc_aa = api.content.create(
            container=self.folder_a, type="Document", title="Document aa"
        )
        self.doc_excluded = api.content.create(
            container=self.folder_a,
            type="Document",
            title="Document excluded",
            exclude_from_nav=True,
        )
        self.alternative_root = api.content.create(
            container=self.portal, type="Folder", title="Alternative root"
        )

        self.alternative_folder_a = api.content.create(
            container=self.alternative_root,
            type="Folder",
            title="Alternative folder a",
        )
        self.alternative_folder_b = api.content.create(
            container=self.alternative_root,
            type="Folder",
            title="Alternative folder b",
        )
        self.alternative_document_a = api.content.create(
            container=self.alternative_folder_a,
            type="Document",
            title="Alternative document a",
        )
        commit()

    def tearDown(self):
        self.api_session.close()

    def set_record_value(self, data):
        api.portal.set_registry_record(
            "menu_configuration", json.dumps(data), interface=IDropDownMenu
        )


class DropDownMenuServiceDeserializerTest(BaseTestWithFolders):
    def serialize(self, content):
        # hack to have the right @id attribute for folders
        self.request.form["fullobjects"] = True
        serializer = getMultiAdapter((content, self.request), ISerializeToJson)
        return serializer()

    def get_record_value(self):
        record = api.portal.get_registry_record(
            "menu_configuration", interface=IDropDownMenu, default=""
        )
        if not record:
            return []
        return json.loads(record)

    def test_return_empty_dict_if_not_set(self):
        response = self.api_session.get("/@dropdown-menu")
        results = response.json()
        self.assertEqual(results, [{"rootPath": "/", "items": []}])

    def test_set_wrong_data(self):
        response = self.api_session.patch(
            self.controlpanel_url, json={"foo": "bar"}
        )

        self.assertEqual(response.status_code, 400)

    def test_deserializer_convert_linkUrl_into_uids(self):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "linkUrl": [
                            self.serialize(self.folder_a),
                            self.serialize(self.folder_b),
                        ],
                    }
                ],
            }
        ]
        self.api_session.patch(
            self.controlpanel_url,
            json={"menu_configuration": json.dumps(data)},
        )
        commit()
        record = self.get_record_value()
        self.assertEqual(len(record), 1)
        self.assertEqual(len(record[0]["items"][0]["linkUrl"]), 2)
        self.assertEqual(
            record[0]["items"][0]["linkUrl"],
            [self.folder_a.UID(), self.folder_b.UID()],
        )

    def test_deserializer_convert_linkUrl_into_uids_and_skip_wrong_paths(self):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "linkUrl": [
                            self.serialize(self.folder_a),
                            {"@id": "http://www.plone.org"},
                        ],
                    }
                ],
            }
        ]
        self.api_session.patch(
            self.controlpanel_url,
            json={"menu_configuration": json.dumps(data)},
        )
        commit()
        record = self.get_record_value()

        self.assertEqual(len(record), 1)
        self.assertEqual(len(record[0]["items"][0]["linkUrl"]), 1)
        self.assertEqual(
            record[0]["items"][0]["linkUrl"], [self.folder_a.UID()]
        )

    def test_deserializer_convert_navigationRoot_into_uids(self):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "navigationRoot": [
                            self.serialize(self.folder_a),
                            self.serialize(self.folder_b),
                        ],
                    }
                ],
            }
        ]
        self.api_session.patch(
            self.controlpanel_url,
            json={"menu_configuration": json.dumps(data)},
        )
        commit()
        record = self.get_record_value()
        self.assertEqual(len(record), 1)
        self.assertEqual(len(record[0]["items"][0]["navigationRoot"]), 2)
        self.assertEqual(
            record[0]["items"][0]["navigationRoot"],
            [self.folder_a.UID(), self.folder_b.UID()],
        )

    def test_deserializer_convert_navigationRoot_into_uids_and_skip_wrong_paths(  # noqa
        self,
    ):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "navigationRoot": [
                            self.serialize(self.folder_a),
                            {"@id": "http://www.plone.org"},
                        ],
                    }
                ],
            }
        ]
        self.api_session.patch(
            self.controlpanel_url,
            json={"menu_configuration": json.dumps(data)},
        )
        commit()
        record = self.get_record_value()

        self.assertEqual(len(record), 1)
        self.assertEqual(len(record[0]["items"][0]["navigationRoot"]), 1)
        self.assertEqual(
            record[0]["items"][0]["navigationRoot"], [self.folder_a.UID()]
        )

    def test_deserializer_convert_showMoreLink_into_uids(self):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "showMoreLink": [
                            self.serialize(self.folder_a),
                            self.serialize(self.folder_b),
                        ],
                    }
                ],
            }
        ]
        self.api_session.patch(
            self.controlpanel_url,
            json={"menu_configuration": json.dumps(data)},
        )
        commit()
        record = self.get_record_value()
        self.assertEqual(len(record), 1)
        self.assertEqual(len(record[0]["items"][0]["showMoreLink"]), 2)
        self.assertEqual(
            record[0]["items"][0]["showMoreLink"],
            [self.folder_a.UID(), self.folder_b.UID()],
        )

    def test_deserializer_convert_showMoreLink_into_uids_and_skip_wrong_paths(  # noqa
        self,
    ):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "showMoreLink": [
                            self.serialize(self.folder_a),
                            {"@id": "http://www.plone.org"},
                        ],
                    }
                ],
            }
        ]
        self.api_session.patch(
            self.controlpanel_url,
            json={"menu_configuration": json.dumps(data)},
        )
        commit()
        record = self.get_record_value()

        self.assertEqual(len(record), 1)
        self.assertEqual(len(record[0]["items"][0]["showMoreLink"]), 1)
        self.assertEqual(
            record[0]["items"][0]["showMoreLink"], [self.folder_a.UID()]
        )


class DropDownMenuServiceSerializerTest(BaseTestWithFolders):
    def serialize(self, item):
        return getMultiAdapter((item, getRequest()), ISerializeToJsonSummary)()

    def test_serializer_convert_linkUrl_from_uid_to_summary(self):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "linkUrl": [self.folder_a.UID(), self.folder_b.UID()],
                    }
                ],
            }
        ]
        self.set_record_value(data=data)
        commit()

        response = self.api_session.get(self.controlpanel_url)
        result = json.loads(response.json()["data"]["menu_configuration"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["items"][0]["linkUrl"]), 2)

        linkUrls = result[0]["items"][0]["linkUrl"]
        self.assertEqual(linkUrls[0]["UID"], self.folder_a.UID())
        self.assertEqual(linkUrls[1]["UID"], self.folder_b.UID())
        self.assertEqual(linkUrls[0]["title"], self.folder_a.title)
        self.assertEqual(linkUrls[1]["title"], self.folder_b.title)

    def test_serializer_convert_linkUrl_from_uid_to_summary_and_skip_broken_items(  # noqa
        self,
    ):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "linkUrl": [self.folder_a.UID(), "foo"],
                    }
                ],
            }
        ]
        self.set_record_value(data=data)
        commit()

        response = self.api_session.get(self.controlpanel_url)
        result = json.loads(response.json()["data"]["menu_configuration"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["items"][0]["linkUrl"]), 1)

        linkUrls = result[0]["items"][0]["linkUrl"]
        self.assertEqual(linkUrls[0]["UID"], self.folder_a.UID())
        self.assertEqual(linkUrls[0]["title"], self.folder_a.title)

    def test_serializer_convert_navigationRoot_from_uid_to_summary(self):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "navigationRoot": [
                            self.folder_a.UID(),
                            self.folder_b.UID(),
                        ],
                    }
                ],
            }
        ]
        self.set_record_value(data=data)
        commit()

        response = self.api_session.get(self.controlpanel_url)
        result = json.loads(response.json()["data"]["menu_configuration"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["items"][0]["navigationRoot"]), 2)

        navigationRoots = result[0]["items"][0]["navigationRoot"]
        self.assertEqual(navigationRoots[0]["UID"], self.folder_a.UID())
        self.assertEqual(navigationRoots[1]["UID"], self.folder_b.UID())
        self.assertEqual(navigationRoots[0]["title"], self.folder_a.title)
        self.assertEqual(navigationRoots[1]["title"], self.folder_b.title)

    def test_serializer_convert_navigationRoot_from_uid_to_summary_and_skip_broken_items(  # noqa
        self,
    ):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "navigationRoot": [self.folder_a.UID(), "foo"],
                    }
                ],
            }
        ]
        self.set_record_value(data=data)
        commit()

        response = self.api_session.get(self.controlpanel_url)
        result = json.loads(response.json()["data"]["menu_configuration"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["items"][0]["navigationRoot"]), 1)

        navigationRoots = result[0]["items"][0]["navigationRoot"]
        self.assertEqual(navigationRoots[0]["UID"], self.folder_a.UID())
        self.assertEqual(navigationRoots[0]["title"], self.folder_a.title)

    def test_serializer_convert_showMoreLink_from_uid_to_summary(self):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "showMoreLink": [
                            self.folder_a.UID(),
                            self.folder_b.UID(),
                        ],
                    }
                ],
            }
        ]
        self.set_record_value(data=data)
        commit()

        response = self.api_session.get(self.controlpanel_url)
        result = json.loads(response.json()["data"]["menu_configuration"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["items"][0]["showMoreLink"]), 2)

        showMoreLinks = result[0]["items"][0]["showMoreLink"]
        self.assertEqual(showMoreLinks[0]["UID"], self.folder_a.UID())
        self.assertEqual(showMoreLinks[1]["UID"], self.folder_b.UID())
        self.assertEqual(showMoreLinks[0]["title"], self.folder_a.title)
        self.assertEqual(showMoreLinks[1]["title"], self.folder_b.title)

    def test_serializer_convert_showMoreLink_from_uid_to_summary_and_skip_broken_items(  # noqa
        self,
    ):

        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "showMoreLink": [self.folder_a.UID(), "foo"],
                    }
                ],
            }
        ]
        self.set_record_value(data=data)
        commit()

        response = self.api_session.get(self.controlpanel_url)
        result = json.loads(response.json()["data"]["menu_configuration"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["items"][0]["showMoreLink"]), 1)

        showMoreLinks = result[0]["items"][0]["showMoreLink"]
        self.assertEqual(showMoreLinks[0]["UID"], self.folder_a.UID())
        self.assertEqual(showMoreLinks[0]["title"], self.folder_a.title)
