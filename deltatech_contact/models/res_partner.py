# -*- coding: utf-8 -*-
##############################################################################
#
#     Romanian accounting localization for OpenERP V7
#        @author -  Fekete Mihai, Tatár Attila <atta@nvm.ro>
#     Copyright (C) 2011-2013 TOTAL PC SYSTEMS (http://www.www.erpsystems.ro). 
#     Copyright (C) 2013 Tatár Attila
#                    Dorin Hongu <dhongu(@)gmail(.)com       
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

from odoo import models, fields, api, tools, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import odoo.addons.decimal_precision as dp
from odoo.api import Environment


class res_partner(models.Model):
    _inherit = 'res.partner'


    @api.multi
    def check_cnp(self):
        
        for contact in self:
            if not contact.cnp:
                return True
            cnp = contact.cnp
            if (len(cnp) != 13):
                return False
            key = '279146358279';
            suma = 0
            for i in range(len(key)):
                suma +=  int(cnp[i])*int(key[i])
    
            if (suma % 11 == 10):
                rest = 1
            else:
                rest = suma % 11
                
            if (rest == int(cnp[12])):
                return True
            else:
                return False

    @api.onchange('cnp')
    def cnp_change(self):
        if self.cnp:
            self.birthdate = fields.Date. time.strftime("%Y-%m-%d", time.strptime(self.cnp[1:7],"%y%m%d"))

    @api.onchange('birthdate')
    def birthdate_change(self):
        if self.cnp:
            cnp = self.cnp
            cnp = cnp[0] + time.strftime("%y%m%d", time.strptime(value, "%Y-%m-%d")) + cnp[7:12]
            key = '279146358279';
            suma = 0
            for i in range(len(key)):
                suma +=  int(cnp[i])*int(key[i])
            if (suma % 11 == 10):
                rest = 1
            else:
                rest = suma % 11
            self.cnp = cnp + str(rest)




    @api.one
    @api.depends('type', 'is_company')
    def _compute_is_department(self):
        if self.is_company or self.type == 'contact': 
            self.is_department = False
        else:
            self.is_department = True
                

    cnp = fields.Char(string='CNP', size=13)
    id_nr = fields.Char(string='ID Nr', size=12)
    id_issued_by = fields.Char(string='ID Issued by', size=20)
    mean_transp = fields.Char(string='Mean Transport', size=12)
    is_department = fields.Boolean(string='Is department', compute='_compute_is_department')
    birthdate = fields.Datetime(string="Birthdate")

 
 
    _defaults = {'user_id': lambda self, cr, uid, context: uid} 
    _constraints = [(check_cnp, _("CNP invaid"), ["cnp"]), ]

    @api.multi
    def name_get(self):
        context = self.env.context

        res = []
        for record in self:
            name = record.name
            if record.parent_id and not record.is_company and record.type != 'contact': 
                    name = "%s, %s" % (record.parent_name, name)
            if context.get('show_address_only'):
                name = self._display_address(  without_company=True)
            if context.get('show_address'):
                name = name + "\n" + self._display_address( without_company=True )
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if context.get('show_phone') and record.phone:    
                name = "%s\n<%s>" % (name, record.phone)
            if context.get('show_category') and record.category_id:    
                cat = []               
                for category in record.category_id:  
                    cat.append(category.name)  
                name = name + "\n["+','.join(cat)+"]"
            name = name.replace('\n\n','\n')
            name = name.replace('\n\n','\n')                
            res.append((record.id, name))      
        return res
 
    @api.model
    def name_search(self,  name, args=None, operator='ilike',  limit=100): 
        res_vat = []
        if name and len(name)>2:
            partner_ids =  self.search( [('vat', 'ilike',  name  ),('is_company','=',True)], limit=10 )   
            if partner_ids:
                res_vat =  partner_ids.name_get()
        res =  super(res_partner,self).name_search(name, args, operator=operator, limit=limit) + res_vat
        return res   

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: