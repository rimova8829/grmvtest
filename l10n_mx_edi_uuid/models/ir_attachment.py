# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from lxml import etree

from odoo import api, fields, models

FIELDS = ['store_fname', 'res_model', 'res_id', 'name', 'datas']


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    l10n_mx_edi_cfdi_uuid = fields.Char(
        string="Fiscal Folio", index=True,
        prefetch=False, readonly=True)

    def update_uuid(self):
        if not self.ids or not self.exists():
            return
        uuid_attachments = self.search([
            ('id', 'in', self.ids), ('res_id', '!=', False),
            ('res_model', 'in', ['account.move', 'account.payment']),
            '|', ('name', '=ilike', '%.xml'), ('name', 'not like', '.')
        ])
        attachments_skipped = self.browse()
        for attach in uuid_attachments:
            if not attach.datas:
                attachments_skipped |= attach
                continue
            cfdi = base64.decodebytes(attach.datas).replace(
                b'xmlns:schemaLocation', b'xsi:schemaLocation')
            model = self.env[attach.res_model].browse(attach.res_id)
            try:
                tree = (model if model._name == 'account.move' else model.move_id)._l10n_mx_edi_decode_cfdi(cfdi)
            except etree.XMLSyntaxError:
                # it is a invalid xml
                attachments_skipped |= attach
                continue

            if not tree.get('uuid'):
                # It is not a signed xml
                attachments_skipped |= attach
                continue
            attach.with_context(force_l10n_mx_edi_cfdi_uuid=True).write({
                'l10n_mx_edi_cfdi_uuid': tree.get('uuid', '').upper().strip()})
        (self - uuid_attachments + attachments_skipped).with_context(
            force_l10n_mx_edi_cfdi_uuid=True).write({
                'l10n_mx_edi_cfdi_uuid': False})
        invoice_ids = (uuid_attachments - attachments_skipped).filtered(
            lambda r: r.res_model == 'account.move').mapped('res_id')
        invoices = self.env['account.move'].browse(invoice_ids).exists()
        if invoices:
            invoices.sudo()._check_uuid_duplicated()
        return True

    def write(self, vals):
        if self.env.context.get('force_l10n_mx_edi_cfdi_uuid'):
            return super().write(vals)
        vals.pop('l10n_mx_edi_cfdi_uuid', None)
        with self.env.cr.savepoint():
            # Secure way if someone catch the exception to skip a rollback
            res = super(IrAttachment, self).write(vals)
            if set(vals.keys()) & set(FIELDS):
                self.update_uuid()
        return res

    @api.model
    def create(self, vals):
        vals.pop('l10n_mx_edi_cfdi_uuid', None)
        with self.env.cr.savepoint():
            # Secure way if someone catch the exception and skip a rollback
            records = super(IrAttachment, self).create(vals)
            if set(vals.keys()) & set(FIELDS):
                records.update_uuid()
        return records
