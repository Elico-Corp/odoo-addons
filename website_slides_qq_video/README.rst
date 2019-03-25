.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Website Slides upload QQ video
==============================
This model  extends the functionality of website_slides and allows to publish the QQ video
in the channel

Installation
============

To install this module, you need to:

 * have basic modules installed (website_slides)


Usage
=====

To use this module, you need to:

Url format is : <address>?vid=<vid>,
The vid is the key for video.

You can get it when you click any qq video most of the time, etc:
http://v.qq.com/cover/k/kg0cy3syh1ovu9z.html?vid=a001986fc2v,

But if you can't find the vid in the url, like:
http://v.qq.com/boke/page/n/0/o/n0163mjor1o.html

Click the share button under the video and find the iframe code for the video like:
<iframe frameborder="0" width="640" height="498" src="http://v.qq.com/iframe/player.html?vid=n0163mjor1o&tiny=0&auto=0" allowfullscreen></iframe>

Just copy and paster the url in the src: http://v.qq.com/iframe/player.html?vid=n0163mjor1o



Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Elico-Corp/odoo/issues/new?body=module:%20website_slides_qq_video%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Siyuan Gu: gu.siyuan@elico-corp.com

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
