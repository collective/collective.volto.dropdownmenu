# -*- coding: utf-8 -*-
# from plone import api

DEFAULT_PROFILE = "profile-collective.volto.dropdownmenu:default"


def to_1001(context):
    """
    """
    context.runImportStepFromProfile(DEFAULT_PROFILE, "rolemap")
    context.runImportStepFromProfile(DEFAULT_PROFILE, "controlpanel")
