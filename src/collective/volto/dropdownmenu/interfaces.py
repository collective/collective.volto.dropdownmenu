# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu import _
from plone.restapi.controlpanels.interfaces import IControlpanel
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import SourceText
import json


class IDropDownMenu(IControlpanel):
    menu_configuration = SourceText(
        title=_("menu_configuration_label", default="Menu configuration"),
        description="",
        required=True,
        default=json.dumps([{"rootPath": "/", "items": []}]),
    )


class ICollectiveVoltoDropDownMenuLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
