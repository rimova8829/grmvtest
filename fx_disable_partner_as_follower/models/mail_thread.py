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


import re

from odoo import api, fields, models
from odoo import exceptions
from odoo import tools
from odoo.tools import pycompat
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class Followers(models.Model):
    _inherit = 'mail.followers'

    # def _insert_followers(self, res_model, res_ids, partner_ids, partner_subtypes, channel_ids, channel_subtypes,
    #                       customer_ids=None, check_existing=True, existing_policy='skip'):
    #     """ Main internal method allowing to create or update followers for documents, given a
    #     res_model and the document res_ids. This method does not handle access rights. This is the
    #     role of the caller to ensure there is no security breach.

    #     :param partner_subtypes: optional subtypes for new partner followers. If not given, default
    #      ones are computed;
    #     :param channel_subtypes: optional subtypes for new channel followers. If not given, default
    #      ones are computed;
    #     :param customer_ids: see ``_add_default_followers``
    #     :param check_existing: see ``_add_followers``;
    #     :param existing_policy: see ``_add_followers``;
    #     """
    #     _logger.info("\n############# _insert_followers >>>>>>> ")
    #     context = self._context
    #     _logger.info("\n::::::::: context %s" % context)
        
    #     if self._context.get('mail_post_autofollow', False):
    #         return False

    #     sudo_self = self.sudo().with_context(default_partner_id=False, default_channel_id=False)
    #     if not partner_subtypes and not channel_subtypes:  # no subtypes -> default computation, no force, skip existing
    #         new, upd = self._add_default_followers(
    #             res_model, res_ids,
    #             partner_ids, channel_ids,
    #             customer_ids=customer_ids,
    #             check_existing=check_existing,
    #             existing_policy=existing_policy)
    #     else:
    #         new, upd = self._add_followers(
    #             res_model, res_ids,
    #             partner_ids, partner_subtypes,
    #             channel_ids, channel_subtypes,
    #             check_existing=check_existing,
    #             existing_policy=existing_policy)
    #     if new:
    #         sudo_self.create([
    #             dict(values, res_id=res_id)
    #             for res_id, values_list in new.items()
    #             for values in values_list
    #         ])
    #     if upd:
    #         for fol_id, values in upd.items():
    #             sudo_self.browse(fol_id).write(values)

    # @api.model_create_multi
    # def create(self, values_list):

    #     _logger.info("\n############# Followers create >>>>>>> ")
    #     context = self._context
    #     _logger.info("\n::::::::: context %s" % context)

    #     if self._context.get('mail_post_autofollow', False):
    #         res = super(Followers, self).create(values_list)
    #         res.unlink()
    #         return False
    #     else:
    #         res = super(Followers, self).create(values_list)
    #         return res

    # def _add_default_followers(self, res_model, res_ids, partner_ids, channel_ids=None, customer_ids=None,
    #                            check_existing=True, existing_policy='skip'):

    #     _logger.info("\n############# _add_default_followers >>>>>>> ")
    #     context = self._context
    #     _logger.info("\n::::::::: context %s" % context)

    #     if 'active_model' in context or 'default_res_model' in context or 'mail_invite_follower_channel_only' in context:
    #         if self._context.get('mail_post_autofollow', False):
    #             return False, False
    #         else:
    #             res = super(Followers, self)._add_default_followers(res_model, res_ids, partner_ids, channel_ids=channel_ids, customer_ids=customer_ids,
    #                                check_existing=check_existing, existing_policy=existing_policy)
    #             return res
    #     else:
    #         return False, False

    #     if self._context.get('mail_post_autofollow', False):
    #         return False, False
    #     else:
    #         res = super(Followers, self)._add_default_followers(res_model, res_ids, partner_ids, channel_ids=channel_ids, customer_ids=customer_ids,
    #                            check_existing=check_existing, existing_policy=existing_policy)
    #         return res


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    _description = 'Email Thread'

    # def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
    #     _logger.info("\n############# message_subscribe >>>>>>> ")
    #     context = self._context
    #     _logger.info("\n::::::::: context %s" % context)
    #     # context:  {'lang': 'es_MX', 'tz': 'America/Mexico_City', 'uid': 2, 'allowed_company_ids': [1], 'default_res_model': 'sale.order', 'default_res_id': 6, 'mail_invite_follower_channel_only': False}
    #     # context:  {'lang': 'es_MX', 'tz': 'America/Mexico_City', 'uid': 2, 'allowed_company_ids': [1], 'mail_post_autofollow': True}
    #     if self._context.get('mail_post_autofollow', False):
    #         return False
    #     else:
    #         res = super(MailThread, self).message_subscribe(partner_ids, channel_ids, subtype_ids)
    #         return res

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    # def send_mail(self, auto_commit=False):
    #     _logger.info("\n############# send_mail >>>>>>> ")
    #     context = self._context
    #     _logger.info("\n::::::::: context %s" % context)
    #     res = super(MailComposer, self.with_context(mail_post_autofollow=True)).send_mail(auto_commit=auto_commit)
    #     return res
