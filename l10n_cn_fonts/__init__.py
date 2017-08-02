# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2011 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <contact@elico-corp.com>
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

from tools.config import config
import report
import os

def wrap_trml2pdf(method):
    """We have to wrap the original parseString() to modify the rml data
    before it generates the pdf."""
    def convert2TrueType(*args, **argv):
        """This function replaces the type1 font names with their truetype
        substitutes and puts a font registration section at the beginning
        of the rml file. The rml file is acually a string (data)."""
        odata = args[0]
	fontmap = {
            'Times-Roman':                   'verasansyuanti_regular',
            'Times-BoldItalic':              'verasansyuanti_bolditalic',
            'Times-Bold':                    'verasansyuanti_bold',
            'Times-Italic':                  'verasansyuanti_italic',

            'Helvetica':                     'verasansyuanti_regular',
            'Helvetica-BoldItalic':          'verasansyuanti_bolditalic',
            'Helvetica-Bold':                'verasansyuanti_bold',
            'Helvetica-Italic':              'verasansyuanti_italic',
            'Helvetica-Oblique':             'verasansyuanti_italic',
            'Helvetica-BoldOblique':         'verasansyuanti_bolditalic',

            'Courier':                       'verasansyuanti_regular',
            'Courier-Bold':                  'verasansyuanti_bold',
            'Courier-BoldItalic':            'verasansyuanti_bolditalic',
            'Courier-Italic':                'verasansyuanti_italic',
            'Courier-Oblique':               'verasansyuanti_italic',
            'Courier-BoldOblique':           'verasansyuanti_bolditalic',

            'Helvetica-ExtraLight':          'verasansyuanti_regular',

            'TimesCondensed-Roman':          'verasansyuanti_regular',
            'TimesCondensed-BoldItalic':     'verasansyuanti_bolditalic',
            'TimesCondensed-Bold':           'verasansyuanti_bold',
            'TimesCondensed-Italic':         'verasansyuanti_italic',

            'HelveticaCondensed':            'verasansyuanti_regular',
            'HelveticaCondensed-BoldItalic': 'verasansyuanti_bolditalic',
            'HelveticaCondensed-Bold':       'verasansyuanti_bold',
            'HelveticaCondensed-Italic':     'verasansyuanti_italic',
        } 
        i = odata.find('<docinit>')
        if i == -1:
            i = odata.find('<document')
            i = odata.find('>', i)
            i += 1
            starttag = '\n<docinit>\n'
            endtag = '</docinit>'
        else:
            i = i + len('<docinit>')
            starttag = ''
            endtag = ''
        data = odata[:i] + starttag
        adp = os.path.abspath(config['addons_path'])
        for new in fontmap.itervalues():
            fntp = os.path.normcase(os.path.join(adp, 'l10n_cn_fonts', 'fonts', new))
            data += '    <registerFont fontName="' + new + '" fontFile="' + fntp + '.ttf"/>\n'
        data += endtag + odata[i:]
	while len(fontmap)>0:
		ck=max(fontmap)
		data = data.replace(ck,fontmap.pop(ck))
       
        return method(data, args[1:] if len(args) > 2 else args[1], **argv)
    return convert2TrueType

report.render.rml2pdf.parseString = wrap_trml2pdf(report.render.rml2pdf.parseString)

report.render.rml2pdf.parseNode = wrap_trml2pdf(report.render.rml2pdf.parseNode)
