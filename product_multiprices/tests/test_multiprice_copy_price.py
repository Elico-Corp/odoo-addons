# -*- coding: utf-8 -*-
from openerp.tests import common


class TestMultipriceCopyPrice(common.TransactionCase):
    def setUp(self):
        super(TestMultipriceCopyPrice, self).setUp()

        # create 10 product template records
        self.product_ids = []
        for i in range(0, 10):
            product_id = self.env['product.template'].create(
                {'name': 'testing'})

            self.product_ids.append(product_id.id)

        # open the wizard
        self.multiprice_copy_price = self.env[
            'multiprice.copy.price'].with_context(
                active_ids=self.product_ids).create({
                    'copy_from': 'list_price',
                    'copy_to': 'list_price'
                })

    def test_action_copy_price_with_same_column(self):
        """
            Test action_copy_price for the duplicated column
        """
        with self.assertRaises(Exception):
            self.multiprice_copy_price.action_copy_price()

    def test_action_copy_price(self):
        """
            Test action_copy_price
        """
        list_price = {
            'list_price': 'list_price10',
            'list_price2': 'list_price9',
            'list_price3': 'list_price8',
            'list_price4': 'list_price7',
            'list_price5': 'list_price6',
            'list_price6': 'list_price5',
            'list_price7': 'list_price4',
            'list_price8': 'list_price3',
            'list_price9': 'list_price2',
            'list_price10': 'list_price',
        }

        for source, dest in list_price.items():
            products = self.env['product.template'].browse(self.product_ids)

            for product in products:
                product[source] = 10
                product[dest] = 20

            list_price_source_before_copy = [
                product[source] for product in products]
            list_price_dest_before_copy = [
                product[dest] for product in products]

            self.multiprice_copy_price.copy_from = source
            self.multiprice_copy_price.copy_to = dest
            self.multiprice_copy_price.action_copy_price()

            list_price_source_after_copy = [
                product[source] for product in products]
            list_price_dest_after_copy = [
                product[dest] for product in products]

            self.assertEqual(
                list_price_source_before_copy, list_price_source_after_copy)
            self.assertEqual(
                list_price_source_before_copy, list_price_dest_after_copy)
            self.assertNotEqual(
                list_price_source_before_copy, list_price_dest_before_copy)
            self.assertNotEqual(
                list_price_dest_before_copy, list_price_dest_after_copy)
