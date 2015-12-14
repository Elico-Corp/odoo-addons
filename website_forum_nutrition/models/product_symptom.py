# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, tools
from openerp import fields as new_fields
from openerp.osv import fields, orm


class ProductTemplate(orm.Model):
    _inherit = 'product.template'

    symptom_ids = new_fields.Many2many('product.symptom')


class ProductSymptom(orm.Model):
    _name = 'product.symptom'

    @api.multi
    def _get_image(self, name, args):
        return dict(
            (p.id, tools.image_get_resized_images(p.image)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'image': tools.image_resize_image_big(value)})

    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)

    _columns = {
        'name': fields.char('Name', required=True, select=True),
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary(
            "Image",
            help="This field holds the image used as avatar for this contact, \
            limited to 1024x1024px"),
        'image_medium': fields.function(
            _get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'product.symptom': (
                    lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "
                 "resized as a 128x128px image, with aspect ratio preserved. "
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(
            _get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'product.symptom': (
                    lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "
                 "resized as a 64x64px image, with aspect ratio preserved. "
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),
    }
