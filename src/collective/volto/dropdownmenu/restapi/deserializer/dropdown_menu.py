# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.controlpanels import (
    ControlpanelDeserializeFromJson,
)
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IDeserializeFromJson
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer

import json

KEYS_WITH_URL = ["linkUrl", "navigationRoot", "showMoreLink"]


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
            for tab in root.get("items", []):
                for key in KEYS_WITH_URL:
                    value = tab.get(key, [])
                    if value:
                        tab[key] = [
                            x.get("UID", "") for x in value if x.get("UID", "")
                        ]
                blocks = tab.get("blocks", {})
                if blocks:
                    for id, block_value in blocks.items():
                        block_type = block_value.get("@type", "")
                        handlers = []
                        for h in subscribers(
                            (self.context, self.request),
                            IBlockFieldDeserializationTransformer,
                        ):
                            if (
                                h.block_type == block_type
                                or h.block_type is None  # noqa
                            ):
                                handlers.append(h)
                        for handler in sorted(handlers, key=lambda h: h.order):
                            block_value = handler(block_value)

                        blocks[id] = block_value
        return data
