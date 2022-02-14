# -*- coding: utf-8 -*-
from collective.volto.dropdownmenu import logger
from collective.volto.dropdownmenu.interfaces import IDropDownMenu
from collective.volto.dropdownmenu.restapi.serializer.dropdown_menu import serialize_data
import os
from plone import api
from plone.memoize import ram
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


EXPERIMENTAL_CACHE = os.environ.get('DROPDOWNMENU_EXPERIMENTAL_CACHE', False)
if EXPERIMENTAL_CACHE:
    logger.info("Using dropdownmenu experimental cache")


def cache_key(fun, *args, **kwargs):
    return (
        api.portal.get().absolute_url(),
        args,
        frozenset(kwargs.items()),  # WARN: json_data could be too big as cache key
        ["Anonymous"] if api.user.is_anonymous() else api.user.get_roles(user=api.user.get_current()),
        api.portal.get_tool("portal_catalog").getCounter(),
    )


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
        if EXPERIMENTAL_CACHE:
            return ram.cache(cache_key)(serialize_data)(json_data=record, show_children=True)
        else:
            return serialize_data(json_data=record, show_children=True)
