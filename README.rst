
===================
Volto Dropdown Menu
===================

Add-on for manage a Dropdown menu in Volto.

Features
--------

- Control panel for plone registry to manage menu configuration.
- Restapi view that exposes these settings for Volto

Volto endpoint
--------------

Anonymous users can't access registry resources by default with plone.restapi (there is a special permission).

To avoid enabling registry access to everyone, this package exposes a dedicated restapi route with the infos to draw the menu: *@dropdown-menu*::

    > curl -i http://localhost:8080/Plone/@dropdown-menu -H 'Accept: application/json'


Control panel
-------------

You can edit settings directly from Volto because the control has been registered on Plone and available with plone.restapi.


Volto integration
-----------------

To use this product in Volto, your Volto project needs to include a new plugin: https://github.com/collective/volto-dropdownmenu


Translations
------------

This product has been translated into

- Italian


Installation
------------

Install collective.volto.dropdownmenu by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.volto.dropdownmenu


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.volto.dropdownmenu/issues
- Source Code: https://github.com/collective/collective.volto.dropdownmenu


License
-------

The project is licensed under the GPLv2.

Authors
-------

This product was developed by **RedTurtle Technology** team.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
