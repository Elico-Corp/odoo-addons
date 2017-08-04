# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


def is_default_lang(user, partner_lang):
    # TODO not sure if all Odoo's default language is en_US
    '''decide if we print the alt_name of product.
        * first check if we have alt_language defined in user's company.
        * check if the partner's language is default: en_US.
        * check if alt language is the same as user's language '''
    if user.company_id and user.company_id.alt_language:
        return (user.company_id.alt_language in (
            'en_US', None, False, user.lang))
    elif partner_lang:
        return (partner_lang in ('en_US', None, False))
    else:
        return True


def choose_lang(user, o):
    return (user.company_id and user.company_id.alt_language) or\
        o.partner_id.lang
