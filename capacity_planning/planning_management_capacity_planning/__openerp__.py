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
    "name" : "Capacity Planning",
    "version" : "1.0",
    "author" : "BHC",
    "website" : "http://www.bhc.be/en/application/capacity-planning",
    "category" : "Generic Modules/Others",
    "depends" : ["base","project","hr","hr_contract","hr_holidays","crm_helpdesk","planning_management_shared_calendar"],
    "description" : """Manage your ressources based on their real load.
    With this module you can create one or several planning and see the overall capacity versus load of your company or team. You can also see the detailed load of each employee and reassign tasks when needed.
    This module will ease you to:
    - Assign tasks based on real load
    - Easily accept/reject holiday requests based on availability of ressources and ongoing projects/orders
    - Give a delivery date to your customer based on your global capacity and planning
    - Better manage ressources need on mid and long term
    - Optimise planning, tasks allocations, and team rentability
""",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["security/planning_management_security.xml","security/ir.model.access.csv","capacity_planning.xml"],
    'images':['images/Planning.png','images/Generator.png','Planning_Employee.png','Planning_Details.png'],
    "active": False,
    "installable": True,
}
