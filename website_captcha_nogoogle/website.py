# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from captcha.image import ImageCaptcha
import base64
import string
import random
from simplecrypt import encrypt, decrypt
from binascii import hexlify, unhexlify


class website(models.Model):
    _inherit = 'website'

    captcha = fields.Text('Captcha', compute="_captcha", store=False)
    captcha_crypt_challenge = fields.Char(
        'Crypt', compute="_captcha", store=False)
    captcha_crypt_password = fields.Char(
        default=lambda self: self._default_salt(),
        required=True, help='''
        The secret value used as the basis for a key.
        This should be as long as varied as possible.
        Try to avoid common words.''')
    captcha_length = fields.Selection(
        '_captcha_length', default='4', required=True)
    captcha_chars = fields.Selection(
        '_captcha_chars', default='digits', required=True)

    def is_captcha_valid(self, crypt_challenge, response):
        challenge = decrypt(
            self.captcha_crypt_password, unhexlify(crypt_challenge))
        if response.upper() == challenge:
            return True
        return False

    @api.depends('captcha_length', 'captcha_chars')
    @api.one
    def _captcha(self):
        captcha = ImageCaptcha()
        captcha_challenge = self._generate_random_str(
            self._get_captcha_chars(), int(self.captcha_length))
        self.captcha_crypt_challenge = hexlify(
            encrypt(self.captcha_crypt_password, captcha_challenge))
        out = captcha.generate(captcha_challenge).getvalue()
        self.captcha = base64.b64encode(out)

    def _generate_random_str(self, chars, size):
        return ''.join(random.choice(chars) for _ in range(size))

    def _default_salt(self):
        return self._generate_random_str(
            string.digits + string.letters + string.punctuation, 100)
        # generate a random salt

    def _captcha_length(self):
        return [(str(i), str(i)) for i in range(1, 11)]

    def _captcha_chars(self):
        return [
            ('digits', 'Digits only'),
            ('hexadecimal', 'Hexadecimal'),
            ('all', 'Letters and Digits')]

    def _get_captcha_chars(self):
        chars = string.digits
        if self.captcha_chars == 'hexadecimal':
            # do not use the default string.hexdigits because it contains
            # lowercase
            chars += 'ABCDEF'
        elif self.captcha_chars == 'all':
            chars += string.uppercase
        return chars
