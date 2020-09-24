# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from collective.volto.dropdownmenu.restapi.serializer.dropdown_menu import (
    serialize_data,
)
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class DropDownMenuGet(Service):
    def __init__(self, context, request):
        super(DropDownMenuGet, self).__init__(context, request)

    def reply(self):
        record = api.portal.get_registry_record(
            "menu_configuration", interface=IDropDownMenu, default=""
        )
        if not record:
            return []
        return serialize_data(json_data=record, show_children=True)
