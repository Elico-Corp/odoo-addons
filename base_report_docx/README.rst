.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Docx template report
====================

This module adds a new reporting engine to the current standard QWEB allowing the user to directly upload docx files containing scripts (in jinja2) into Odoo.

The reporting engine will interpret the script and create a pdf/docx based on the docx template.


Installation
============
To install this module, you need to:

* install the docxtpl : Terminal order ("pip install docxtpl")
* install the reportlab : Terminal order ("pip install reportlab")
* install the pypdf : Terminal order ("pip install pypdf")
* install the python lib: docxtpl (http://docxtpl.readthedocs.org/en/latest/)
* install the libreoffice (https://wiki.ubuntu.com/LibreOffice)

Configuration
=============

To configure this module, you need to:

* Inherit the function generate_docx_data in the report/report_docx.py
* Pass the list of the dictionary to the engine. (etc [{data1}, {data2}, .....])
* Each dictionary will generate a report base on the docx template.


Usage
=====

To use this module, you need to:

* Go to System/Technical/Reports/Report
* Create a new report
* Change the report type to docx
* upload the template file.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Elico-Corp/yopark_odoo/issues>`.


Known issues / Roadmap
======================

* To be implemented: export from docx to html.
* load the watermark from html (qweb) 


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.


Contributors
------------
* Eric Caudal <eric.caudal@elico-corp.com>
* Victor M. Martin <victor.martin@elico-corp.com>
* Hulk Liu: <hulk.liu@elico-corp.com>
* Kevin Wei: <kevin.wei@elico-corp.com>

Maintainer
----------

.. image:: https://www.elico-corp.com/logo.png
   :alt: Elico Corp
   :target: https://www.elico-corp.com

This module is maintained by Elico Corporation.

Elico Corporation offers consulting services to implement open source management software in SMEs, with a strong involvement in quality of service.

Our headquarters are located in Shanghai with branches in ShenZhen and Singapore servicing customers from China, Hong Kong, Japan, Australia, Europe, Middle East, etc...
