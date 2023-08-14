# -*- coding:utf-8 -*- 
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stowage_labels_printed = fields.Boolean('Etiquetas estiba', default=False)
    qa_labels_printed = fields.Boolean('Etiquetas calidad', default=False)
    single_labels_printed = fields.Boolean('Etiquetas individuales', default=False)

    def launch_label_wizard(self):
        self.ensure_one()

        wizard_id = self.env['wizard.stowage.labels']\
            .create({
                'labels_printed' : self.single_labels_printed
            })

        return {
            'type' : 'ir.actions.act_window',
            'name' : 'Etiquetas estibo',
            'res_model' : 'wizard.stowage.labels',
            'view_mode' : 'form',
            'target' : 'new',
            'res_id' : wizard_id.id
        }