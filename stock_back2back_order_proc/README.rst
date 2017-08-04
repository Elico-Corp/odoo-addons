.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Stock Back-to-back orders
=============================

This module aims to change the original back-order logic of OpenERP in chained locations introducing true back-to-back orders.

STANDARD OPENERP BACK-TO-BACK ORDER BEHAVIOR:
Original behavior is not fully suitable to handle back-to-back backorders process (check "back-to-back orders comparison.pdf"):
eg: Let's take the following example to understand the implemented difference:
- One PO from a supplier for the full quantity (eg 100 PCE) and your supplier ships immediately only the available quantity which is 70 PCE. 
- 30 PCE are to be shipped later on.
- Setup with following chained location: SUPPLIER => TRANSIT (Chained/Manual) => INPUT locations 

When PO is validated to TRANSIT location,
- DN1 is created for 100 PCE (SUPPLIER to TRANSIT)
- chained move DN2 is automatically created for 100 PCE (from TRANSIT to INPUT)
When only partial quantity is shipped (eg 70 PCE):
- DN1 is processed and shipped for 70 PCE (done state)
- DN2 is kept with 100 PCE (in waiting state "waiting that all replenishments arrive at location before shipping")
- chained move DN3 is automatically created with 30 PCE (from SUPPLIER to TRANSIT) as back order of DN1.

Several drawbacks make current behavior unappropriate:
- Stock in the different locations are not reflecting real stocks.
- This is due to the fact that original delivery note is kept in waiting state in input or output location until all incoming chained DN are processed. 
- For this reason as well, real stock in the warehouse is incorrect in our case and is only correct when all backorders are shipped impacting company stock visibility.
- Documents (DN) are not following actual flow (one document missing)

ENHANCED BACK-TO-BACK ORDER BEHAVIOR
This modules replace standard OpenERP behavior by an enhanced back-to-back order workflow with the following behavior:
- Within a chained location structure, all chained moves will be created for the full quantity (eg: 100 PCE), following standard OE behavior.
(for how many chained location that has been created: if a second location is chained, an additional chained move is created)
- Nevertheless, when a partial quantity is shipped in the original delivery note (eg: 70 PCE), all related chained moves are updated with this new quantity 
(70 PCES) for as many level as necessary (difference with standard behavior).
- Backorders and related chained moves are created with the remaining quantities (eg: 30 PCE)
- Automated and manual chained behavior are respected.

Taking back our previous example (check as well "back-to-back orders comparison.pdf"):

When PO is validated to TRANSIT location,
- DN1 is created for 100 PCE (SUPPLIER to TRANSIT)
- chained move DN2 is automatically created for 100 PCE (from TRANSIT to INPUT)
When only partial quantity is shipped (eg 70 PCE):
- DN1 is shipped to 70 PCE (done state)
- DN2 is kept with 100 PCE (in waiting state "waiting that all replenishments arrive at location before shipping")
- chained move DN3 is automatically created with 30 PCE (from SUPPLIER to TRANSIT)

When DN1 is partially shipped with 70 PCE:
- DN2 quantity is changed to 70 PCE (and depending on stock marked as available since in our example it is set as manual). 
If automatic chained move, it would be automatically shipped according to DN1 shipment.
- a back order DN3 is automatically created with 30 PCE (from SUPPLIER to TRANSIT), 
- chained move DN4 is automatically created with 30 PCE (from TRANSIT to INPUT)

Please note:
- In this case, workflow is closer to reality: all real stocks figures are correct and all relevant documents are created.
- Later on, DN2 and DN4 can be shipped separately (as they are setup as manual in this example)
- As many back order as necessary can be created: all chained moves are automatically updated and created accordingly
- this behavior works as well in case of sales orders.

Bug Tracker
===========

Bugs are tracked on `<https://github.com/Elico-Corp/openerp-7.0/issues>`_. 
In case of trouble, please check there if you issue has been already reported.
if you spotted it first,help us smash it by providing detailed and welcomed 
feedback.

Contributors
------------

* Eric Caudal <eric.caudal@elico-corp.com>
* Yannick Gouin <yannick.gouin@elico-corp.com>

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