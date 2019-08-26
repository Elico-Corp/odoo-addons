# -*- coding: utf-8 -*-
from . import models


def post_init_hook(cr, registry):
    cr.execute('ALTER TABLE account_move_line '
        'DROP CONSTRAINT account_move_line_credit_debit1;')
    cr.execute('ALTER TABLE account_move_line '
        'DROP CONSTRAINT account_move_line_credit_debit2;')
