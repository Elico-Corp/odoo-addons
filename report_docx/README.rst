.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========
Report Docx
===========

This module adds docx template to the standard odoo reporting engine.


Installation
============
To install this module, you need to:

* install the python lib: docxtpl (http://docxtpl.readthedocs.org/en/latest/)

* install the libreoffice (https://wiki.ubuntu.com/LibreOffice)


Configuration
=============

To configure this module, you need to:

* Inherit the function generate_docx_data in the report/report_docx.py

* Pass the list of the dictionary to the engine. (etc [{data1}, {data2, .....}])

* Each dictionary will generate a report base on the docx template.


Usage
=====

This module adds a new reporting engine to the current standard QWEB allowing the user to directly upload docx files containing scripts (in jinja2) into Odoo.

The reporting engine will interpret the script and create a pdf/docx based on the docx template.

To use this module, you need to:

* Go to System/Technical/Reports/Report, create a new report, change the report type to docx and upload the template file.


Known issues / Roadmap
======================

* To be implemented: export from docx to html.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/odoo/issues>`.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.


Contributors
------------

* Siyuan Gu: gu.siyuan@elico-corp.com

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
   :alt: Elico Corp
   :target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corporation offers consulting services to implement open source management software in SMEs, with a strong involvement in quality of service.

Our headquarters are located in Shanghai with branches in ShenZhen and Singapore servicing customers from China, Hong Kong, Japan, Australia, Europe, Middle East, etc...
