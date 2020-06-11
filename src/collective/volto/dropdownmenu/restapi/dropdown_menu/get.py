# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import json


@implementer(IPublishTraverse)
class DropDownMenuGet(Service):
    def __init__(self, context, request):
        super(DropDownMenuGet, self).__init__(context, request)

    def reply(self):
        record = api.portal.get_registry_record(
            "menu_configuration", interface=IDropDownMenu, default=""
        )
        if not record:
            return {}
        return json.loads(record)
