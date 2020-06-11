# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from collective.volto.dropdownmenu import _


class DropDownMenuForm(controlpanel.RegistryEditForm):

    schema = IDropDownMenu
    label = _(
        "dropdown_menu_settings_label", default=u"Dropdown Menu Settings"
    )
    description = u"Manage Menu tabs and contents."


class DropDownMenu(controlpanel.ControlPanelFormWrapper):
    form = DropDownMenuForm
