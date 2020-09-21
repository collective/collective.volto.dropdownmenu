# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.controlpanels import (
    ControlpanelDeserializeFromJson,
)
from plone.restapi.interfaces import IDeserializeFromJson
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from zExceptions import BadRequest
from zope.component import adapter
from zope.interface import implementer

import json

KEYS_WITH_URL = ["linkUrl", "navigationRoot", "showMoreLink"]


# def path2uid(context, path):
#     # unrestrictedTraverse requires a string on py3. see:
#     # https://github.com/zopefoundation/Zope/issues/674
#     if not isinstance(path, str):
#         path = path.decode("utf-8")

#     portal_url = api.portal.get().absolute_url()
#     if path and path.startswith(portal_url):
#         path = path[len(portal_url) + 1 :]  # noqa
#     obj = context.unrestrictedTraverse(path, None)
#     if obj is None:
#         return None
#     segments = path.split("/")
#     suffix = ""
#     while not IUUIDAware.providedBy(obj):
#         obj = aq_parent(obj)
#         suffix += "/" + segments.pop()
#     return IUUID(obj)


@implementer(IDeserializeFromJson)
@adapter(IDropDownMenu)
class DropDownMenuControlpanelDeserializeFromJson(
    ControlpanelDeserializeFromJson
):
    def __call__(self):
        req = json_body(self.controlpanel.request)
        proxy = self.registry.forInterface(
            self.schema, prefix=self.schema_prefix
        )
        errors = []

        data = req.get("menu_configuration", {})
        if not data:
            errors.append(
                {"message": "Missing data", "field": "menu_configuration"}
            )
            raise BadRequest(errors)
        try:
            value = self.deserialize_data(json.loads(data))
            setattr(proxy, "menu_configuration", json.dumps(value))
        except ValueError as e:
            errors.append(
                {"message": str(e), "field": "menu_configuration", "error": e}
            )

        if errors:
            raise BadRequest(errors)

    def deserialize_data(self, data):
        for root in data:
            rootpath = root.get("rootPath", "")
            if rootpath != "/":
                uid = rootpath.get("UID", "")
                if not uid:
                    raise ValueError(
                        "Root element not found: {}".format(rootpath)
                    )
                root["rootPath"] = uid
            for tab in root.get("items", []):
                for key in KEYS_WITH_URL:
                    value = tab.get(key, [])
                    if value:
                        tab[key] = [
                            x.get("UID", "") for x in value if x.get("UID", "")
                        ]
        return data
