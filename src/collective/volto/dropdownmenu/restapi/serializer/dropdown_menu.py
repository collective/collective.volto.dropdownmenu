# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.controlpanels import ControlpanelSerializeToJson
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer

import json

KEYS_WITH_URL = ["linkUrl", "navigationRoot", "showMoreLink"]


def serialize_data(json_data, show_children=False):
    if not json_data:
        return ""
    data = json.loads(json_data)
    for root in data:
        for tab in root.get("items", []):
            for key in KEYS_WITH_URL:
                value = tab.get(key, [])
                if value:
                    serialized = []
                    for uid in value:
                        item = api.content.get(UID=uid)
                        if not item:
                            continue
                        summary = getMultiAdapter(
                            (item, getRequest()), ISerializeToJsonSummary
                        )()
                        if summary:
                            # serializer doesn't return uid
                            summary["UID"] = uid
                            if show_children:
                                summary["items"] = get_item_children(item)
                            serialized.append(summary)
                    tab[key] = serialized
    return json_compatible(data)


def get_item_children(item):
    path = "/".join(item.getPhysicalPath())
    query = {
        "path": {"depth": 1, "query": path},
        "sort_on": "getObjPositionInParent",
        "exclude_from_nav": False,
    }
    brains = api.content.find(**query)
    return [
        getMultiAdapter((brain, getRequest()), ISerializeToJsonSummary)()
        for brain in brains
    ]


@implementer(ISerializeToJson)
@adapter(IDropDownMenu)
class DropDownMenuControlpanelSerializeToJson(ControlpanelSerializeToJson):
    def __call__(self):
        json_data = super(
            DropDownMenuControlpanelSerializeToJson, self
        ).__call__()
        conf = json_data["data"].get("menu_configuration", "")
        if conf:
            json_data["data"]["menu_configuration"] = json.dumps(
                serialize_data(json_data=conf)
            )
        return json_data
