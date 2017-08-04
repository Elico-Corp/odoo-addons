# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from test_base_data import TransactionCaseBaseData


class TestLandedCosts(TransactionCaseBaseData):
    '''Tests for landed costs
    Demo data:
        1 stock picking with landed costs:
            * distributed by volume
            * distributed by value
            * distributed by quantity
            
        2 stock moves with landed costs:
            * distributed by volume
            * distributed by value
            * distributed by quantity
    '''
    def setUp(self):
        # prepare the stock moves for testing.
        self.move_id1 = self.move_obj.create({
            'name': 'Move1',
            'product_id': self.product_id
        })

    def StockMove_LandingCostField(self):
        # Environment:
        #   A stock move of a stock picking with landed costs
        # Action:
        #   compute the landing cost
        # Output:
        #   the right landing cost
        pass
