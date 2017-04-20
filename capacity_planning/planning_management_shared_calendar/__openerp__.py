# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Shared Calendar",
    "version" : "1.0",
    "author" : "BHC",
    "website" : "http://www.bhc.be/en/application/capacity-planning",
    "category" : "Generic Modules/Others",
    "depends" : ["base"],
    "description" : """The shared calendar module allows you to synchronize different objects in one calendar such as tasks, phone calls, meetings, vacation... 
    Of course, you may also add custom objects in relation with your business.
    You will also be able to manage in one place all your employees calendar so it will be easy to check in one view all your staff agenda.
    The added value of this module is that you may modify elements in the shared calendar with a direct impact on the individual’s calendar by clicking on the element but also via the drag and drop option.""",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["security/planning_management_security.xml","security/ir.model.access.csv","shared_calendar.xml"],
    'images': ['images/Calendar.png','images/Confguration.png','images/Edition.png'],
    "active": False,
    "installable": True,
}
