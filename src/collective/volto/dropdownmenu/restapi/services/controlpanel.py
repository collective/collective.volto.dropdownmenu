# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface


@adapter(Interface, Interface)
class DropDownMenuControlpanel(RegistryConfigletPanel):
    schema = IDropDownMenu
    configlet_id = "DropDownMenu"
    configlet_category_id = "Products"
    schema_prefix = None
