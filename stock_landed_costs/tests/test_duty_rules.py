# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from test_base_data import TransactionCaseBaseData


class TestDutyRules(TransactionCaseBaseData):
    '''Tests for duty rules
    Demo data:
    #1.source location is empty and destination location is not.
    #2.both are empty (rule for all)
    #3.destination location is empty and source location is not.'''
    def setUp(self):
        pass
