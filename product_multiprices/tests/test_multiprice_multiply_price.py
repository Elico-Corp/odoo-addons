# -*- coding: utf-8 -*-
from openerp.tests import common


class TestMultipriceMultiplyPrice(common.TransactionCase):
    def setUp(self):
        super(TestMultipriceMultiplyPrice, self).setUp()

        # create 10 product template records
        self.product_ids = []
        for i in range(0, 10):
            product_id = self.env['product.template'].create(
                {'name': 'testing'})

            self.product_ids.append(product_id.id)

        # open the wizard
        self.multiprice_multiprice_multiply_price = self.env[
            'multiprice.multiply.price'].with_context(
                active_ids=self.product_ids).create({
                    'column': 'list_price',
                    'by_value': 2
                })

    def test_action_multiply_price(self):
        """
            Test action_multiply_price
        """
        list_price = {
            'list_price': 10,
            'list_price2': 20,
            'list_price3': 30,
            'list_price4': 40,
            'list_price5': 50,
            'list_price6': 60,
            'list_price7': 70,
            'list_price8': 80,
            'list_price9': 90,
            'list_price10': 100,
        }

        for list_price, price in list_price.items():
            products = self.env['product.template'].browse(self.product_ids)

            for product in products:
                product[list_price] = price

            list_price_before_copy = [
                product[list_price] for product in products]
            except_list_price_after_copy = [
                product[list_price] *
                self.multiprice_multiprice_multiply_price.by_value
                for product in products
            ]

            self.multiprice_multiprice_multiply_price.column = list_price
            self.multiprice_multiprice_multiply_price.action_multiply_price()

            list_price_after_copy = [
                product[list_price] for product in products]

            self.assertEqual(
                list_price_after_copy, except_list_price_after_copy)
            self.assertNotEqual(
                list_price_before_copy, list_price_after_copy)
