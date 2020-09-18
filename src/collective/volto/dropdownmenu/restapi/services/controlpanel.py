# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import (
    ICollectiveVoltoDropDownMenuLayer,
    IDropDownMenu,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, ICollectiveVoltoDropDownMenuLayer)
@implementer(IDropDownMenu)
class DropDownMenuControlpanel(RegistryConfigletPanel):
    schema = IDropDownMenu
    configlet_id = "DropDownMenu"
    configlet_category_id = "Products"
    schema_prefix = None
