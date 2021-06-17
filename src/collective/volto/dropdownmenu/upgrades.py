# -*- coding: utf-8 -*-
from plone import api
from collective.volto.dropdownmenu.interfaces import IDropDownMenu

import logging
import json

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-collective.volto.dropdownmenu:default"


def to_1001(context):
    """
    """
    context.runImportStepFromProfile(DEFAULT_PROFILE, "rolemap")
    context.runImportStepFromProfile(DEFAULT_PROFILE, "controlpanel")


def to_volto13(context):  # noqa: C901
    # convert listing blocks with new standard

    logger.info("### START CONVERSION TO VOLTO 13 ###")

    def fix_listing(blocks):
        for block in blocks.values():
            if block.get("@type", "") != "listing":
                continue
            if block.get("template", False) and not block.get(
                "variation", False
            ):
                block["variation"] = block["template"]
                del block["template"]
            if block.get("template", False) and block.get("variation", False):
                del block["template"]

            # Migrate to internal structure
            if not block.get("querystring", False):
                # Creates if it is not created
                block["querystring"] = {}
            if block.get("query", False) or block.get("query") == []:
                block["querystring"]["query"] = block["query"]
                del block["query"]
            if block.get("sort_on", False):
                block["querystring"]["sort_on"] = block["sort_on"]
                del block["sort_on"]
            if block.get("sort_order", False):
                block["querystring"]["sort_order"] = block["sort_order"]
                if isinstance(block["sort_order"], bool):
                    block["querystring"]["sort_order"] = (
                        "descending" if block["sort_order"] else "ascending"
                    )
                else:
                    block["querystring"]["sort_order"] = block["sort_order"]
                block["querystring"]["sort_order_boolean"] = (
                    True
                    if block["sort_order"] == "descending"
                    or block["sort_order"]  # noqa
                    else False
                )
                del block["sort_order"]
            if block.get("limit", False):
                block["querystring"]["limit"] = block["limit"]
                del block["limit"]
            if block.get("batch_size", False):
                block["querystring"]["batch_size"] = block["batch_size"]
                del block["batch_size"]
            if block.get("depth", False):
                block["querystring"]["depth"] = block["depth"]
                del block["depth"]

            # batch_size to b_size, idempotent
            if block["querystring"].get("batch_size", False):
                block["querystring"]["b_size"] = block["querystring"][
                    "batch_size"
                ]
                del block["querystring"]["batch_size"]

    menu_configuration = api.portal.get_registry_record(
        "menu_configuration", interface=IDropDownMenu
    )

    if not menu_configuration:
        return
    data = json.loads(menu_configuration)
    for entry in data:
        for item in entry.get("items", []):
            fix_listing(item.get("blocks", {}))
        api.portal.set_registry_record(
            "menu_configuration", json.dumps(data), interface=IDropDownMenu
        )
