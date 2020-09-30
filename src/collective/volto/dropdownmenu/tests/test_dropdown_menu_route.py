# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.tests.test_dropdown_menu_controlpanel import (  # noqa
    BaseTestWithFolders,
)
from transaction import commit


class DropDownMenuEndpointTest(BaseTestWithFolders):
    def test_route_exists(self):
        response = self.api_session.get("/@dropdown-menu")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

    def test_route_return_linkUrl_structure(self):
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

        response = self.api_session.get("/@dropdown-menu")
        result = response.json()
        self.assertEqual(len(result), 1)

        linkUrl = result[0]["items"][0]["linkUrl"]
        self.assertEqual(len(linkUrl), 2)
        self.assertEqual(linkUrl[0]["@id"], self.folder_a.absolute_url())
        self.assertEqual(linkUrl[1]["@id"], self.folder_b.absolute_url())

        self.assertEqual(len(linkUrl[0]["items"]), 2)
        self.assertEqual(len(linkUrl[1]["items"]), 0)

    def test_route_return_navigationRoot_structure(self):
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

        response = self.api_session.get("/@dropdown-menu")
        result = response.json()
        self.assertEqual(len(result), 1)

        navigationRoot = result[0]["items"][0]["navigationRoot"]
        self.assertEqual(len(navigationRoot), 2)
        self.assertEqual(
            navigationRoot[0]["@id"], self.folder_a.absolute_url()
        )
        self.assertEqual(
            navigationRoot[1]["@id"], self.folder_b.absolute_url()
        )

        self.assertEqual(len(navigationRoot[0]["items"]), 2)
        self.assertEqual(len(navigationRoot[1]["items"]), 0)

    def test_route_return_showMoreLink_structure(self):
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

        response = self.api_session.get("/@dropdown-menu")
        result = response.json()
        self.assertEqual(len(result), 1)

        showMoreLink = result[0]["items"][0]["showMoreLink"]
        self.assertEqual(len(showMoreLink), 2)
        self.assertEqual(showMoreLink[0]["@id"], self.folder_a.absolute_url())
        self.assertEqual(showMoreLink[1]["@id"], self.folder_b.absolute_url())

        self.assertEqual(len(showMoreLink[0]["items"]), 2)
        self.assertEqual(len(showMoreLink[1]["items"]), 0)

    def test_route_return_navigationRoot_children_honor_exclude_from_nav(self):
        data = [
            {
                "rootPath": "/",
                "items": [
                    {
                        "title": "First tab",
                        "foo": "bar",
                        "navigationRoot": [self.folder_a.UID()],
                    }
                ],
            }
        ]
        self.set_record_value(data=data)
        commit()

        response = self.api_session.get("/@dropdown-menu")
        result = response.json()

        items = result[0]["items"][0]["navigationRoot"][0]["items"]
        self.assertEqual(len(items), 2)
        self.assertNotIn("Document excluded", [x["title"] for x in items])
