# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-BroadTech IT Solutions (<http://www.broadtech-innovations.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


import logging
import re

from odoo import api, fields, models
from odoo import exceptions
from odoo import tools
from odoo.tools import pycompat
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    _description = 'Email Thread'

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        context = self._context
        # context:  {'lang': 'es_MX', 'tz': 'America/Mexico_City', 'uid': 2, 'allowed_company_ids': [1], 'default_res_model': 'sale.order', 'default_res_id': 6, 'mail_invite_follower_channel_only': False}
        # context:  {'lang': 'es_MX', 'tz': 'America/Mexico_City', 'uid': 2, 'allowed_company_ids': [1], 'mail_post_autofollow': True}

        if self._context.get('mail_post_autofollow', False):
            return False
        else:
            res = super(MailThread, self).message_subscribe(partner_ids, channel_ids, subtype_ids)
            return res


