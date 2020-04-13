.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Website Captcha No Google
=========================

This module allows you to integrate a python CAPTCHA to your website forms.
You can configure your CAPTCHA in "Settings" -> "Website Settings"

You will need to install and purchase the "website_captcha_nogoogle_crm"
to use it in your "contact us" page

Usage
============

Python external dependencies
-----------------------------

To use this module you need to install the following python libraries:

* `captcha <https://pypi.python.org/pypi/captcha>`_

* `simplecrypt <https://pypi.python.org/pypi/simple-crypt>`_


Integrate the captcha in any of your web pages
----------------------------------------------

.. code-block:: xml

  <t t-call="website_captcha_nogoogle.captcha"/>

Feel free to extend or create a new template to adapt it to your design.

Get captcha in binary format
----------------------------

.. code-block:: python

  print website.captcha

It will simply output the captcha as a binary.

You can display it in HTML as follow:

.. code-block:: html

  <img t-att-src="'data:image/png;base64,%s' % website.captcha" />

Check if the captcha is valid
-----------------------------

Call the website's 'is_captcha_valid' method.

.. code-block:: python

  website.is_captcha_valid(crypt_challenge, response)


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Contributors
------------

* Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
* Ruter Lyu <ruter.lv@elico-corp.com>

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
    :alt: Elico Corp
    :target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corp is an innovative actor in China, Hong-Kong and Singapore servicing
well known international companies and as well as local mid-sized businesses.
Since 2010, our seasoned Sino-European consultants have been providing full
range Odoo services:

* Business consultancy for Gap analysis, BPM, operational work-flows review.
* Ready-to-use ERP packages aimed at starting businesses.
* Odoo implementation for manufacturing, international trading, service industry
  and e-commerce.
* Connectors and integration with 3rd party software (Magento, Taobao, Coswin,
  Joomla, Prestashop, Tradevine etc...).
* Odoo Support services such as developments, training, maintenance and hosting.

Our headquarters are located in Shanghai with branch in Singapore servicing
customers from all over Asia Pacific.

Contact information: `Sales <contact@elico-corp.com>`__
