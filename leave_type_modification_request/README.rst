.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/agpl.html
   :alt: License: AGPL-3

===============================
Leave Type Modification Request
===============================

This module adds functionality to allow the employee(s) to request to add the days
in leave allocation for overtime.
A special type of Leave is been created and the employees can modify via requests 
the allocation requests linked to that leave type.
The Allocation request modifications requests are linked to a workflow that the 
manager or HR officer can approve.

Usage
=====

#. HR Manager needs first to create a leave type and click on the checkbox "Allow Modification via Request"

   .. figure:: static/img/step1.png
      :width: 600 px
      :alt: Leave type
   
#. The employee or HR officer can create a new Allocation Request

   .. figure:: static/img/step2.png
      :width: 600 px
      :alt: New allocation request

   NB:
   
   * the number of days is now read only as it depends on the validated modifications
     requests
   * A new smart button (top right of the form) allows to see and modify the modification
     requests
   * note in the screenshot above the number of days is 0.
   
#. Clicking on the smart button the employee or HR officer can view the list of modification requests and their status, per employee

   .. figure:: static/img/step3.png
      :width: 600 px
      :alt: Allocation Modification request list
  
#. Employee can create a new modification request, specifying the date of creation, related swap days or notes.
   
   .. figure:: static/img/step4.png
      :width: 600 px
      :alt: Creating Allocation Modification request

#. Once prepared it can be confirmed by the employee (it becomes read only)

   .. figure:: static/img/step5.png
      :width: 600 px
      :alt: Confirming Allocation Modification request

#. The HR officer can now approve the Allocation Modification request

   .. figure:: static/img/step6.png
      :width: 600 px
      :alt: Confirming Allocation Modification request

#. The employee can now use the allocation request (number of days is now 2 in the example)

   .. figure:: static/img/step7.png
      :width: 600 px
      :alt: Allocation request with approved modification request


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Elico Corp: `Icon <https://elico-corp.com/logo.png>`_.

Contributors
------------

* Eric Caudal <eric.caudal@elico-corp.com>
* Victor Martin <victor.martin@elico-corp.com>

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
