.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
HR TimeSheet Auto Creation
===========================

This module extends the functionality of HR timesheet to automatically
create the Timesheet Activity report via a cron job.

Installation
============

To install this module, you need to:

#. Have basic modules installed (hr_timesheet_sheet)

Configuration
=============

To configure this module, you need to:

#. Set system's timezone correct(Administrator>Preferences>Timezone:
Your location timezone).
#. Set the user access in read the employee and read/write on
time sheet(default the user is Administrator, So you can skip this set).
#. Set the time or frequency as you want in the cron job:
    1). Settings>Users>Administrator>Usability>Technical Features: check;

    2). Settings>Technical>Automation>Scheduled Actions>My current TMS:
        modify the time(`Next Execution Date`) or frequency(`Interval Number` and `Interval Unit`).

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback

Credits
=======

Contributors
------------

* Kevin Dong <kevin.dong@elico-corp.com>
* Eric Caudal <eric.caudal@elico-corp.com>

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
   :alt: Elico Corp
   :target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corporation offers consulting services to implement open source management
software in SMEs, with a strong involvement in quality of service.

Our headquarters are located in Shanghai and Singapore servicing customers from
Greater China and Asia Pacific.

Contact information: `Sales <contact@elico-corp.com>`__
