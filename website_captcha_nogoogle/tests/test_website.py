# -*- coding: utf-8 -*-
import openerp.tests.common as common
import string
import re
from binascii import unhexlify
from simplecrypt import decrypt


class TestWebsite(common.TransactionCase):
    def setUp(self):
        super(TestWebsite, self).setUp()
        # at least 1 website exists
        self.website = self.env['website'].search([])[0]

    def test_captcha_length(self):
        values = [
            ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
            ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
        ]
        self.assertEqual(values, self.website._captcha_length())

    def test_captcha_chars(self):
        values = [
            ('digits', 'Digits only'),
            ('hexadecimal', 'Hexadecimal'),
            ('all', 'Letters and Digits')]
        self.assertEqual(values, self.website._captcha_chars())

    def test_is_captcha_valid(self):
        response = decrypt(
            self.website.captcha_crypt_password,
            unhexlify(self.website.captcha_crypt_challenge))
        self.assertTrue(
            self.website.is_captcha_valid(
                self.website.captcha_crypt_challenge, response))
        self.assertFalse(
            self.website.is_captcha_valid(
                self.website.captcha_crypt_challenge, '__wrongcaptcha__'))

    def test_captcha_is_unicode(self):
        self.assertIsInstance(self.website.captcha, unicode)

    def test_generate_random_str(self):
        value = self.website._generate_random_str('A1', 10)
        self.assertRegexpMatches(value, r'^[A1]{10}$')

    def test_default_salt(self):
        regexp = '^[%s%s%s]{100}$' % (
            string.digits, string.letters,
            re.escape(string.punctuation))
        value = self.website._default_salt()
        self.assertRegexpMatches(value, regexp)
        # generate a random salt

    def test_get_captcha_chars(self):
        default = self.website.captcha_chars
        self.website.captcha_chars = 'digits'
        value = self.website._get_captcha_chars()
        self.assertEqual(value, string.digits)

        self.website.captcha_chars = 'hexadecimal'
        value = self.website._get_captcha_chars()
        self.assertEqual(value, string.digits + 'ABCDEF')

        self.website.captcha_chars = 'all'
        value = self.website._get_captcha_chars()
        self.assertEqual(value, string.digits + string.uppercase)

        # back to default
        self.website.captcha_chars = default
