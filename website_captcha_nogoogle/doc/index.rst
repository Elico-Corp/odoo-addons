Odoo CAPTCHA (No Google)
========================

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
