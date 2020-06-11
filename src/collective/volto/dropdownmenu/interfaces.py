# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu import _
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import SourceText


class IDropDownMenu(Interface):
    menu_configuration = SourceText(
        title=_("menu_configuration_label", default="Menu configuration"),
        description="",
        required=True,
    )


class ICollectiveVoltoDropDownMenuLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
