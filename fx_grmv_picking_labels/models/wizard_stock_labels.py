# -*- coding:utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError


class WizardStowageLabels(models.TransientModel):
    _name = 'wizard.stowage.labels'

    platform_qty = fields.Integer('Cantidad en tarima')
    labels_printed = fields.Boolean('Etiquetas impresas')
    state = fields.Selection(
        [('init', 'Init'), ('done', 'Done')], string='State', default='init'
    )
    label_type = fields.Selection(
        [('single', 'Individual'), ('stowage', 'Estiba'), ('qa', 'Calidad')],
        string='Etiqueta a imprimir', default='single'
    )

    def _process_stowage_labels(self, picking_id):
        if self.platform_qty < 1:
            raise UserError('Indique un número de etiquetas mayor que cero')

        # calcular num de etiquetas = total_piezas / piezas_tarima
        total_qty = sum(picking_id.move_line_ids_without_package.mapped('qty_done'))
        label_qty = int(total_qty / self.platform_qty)
        if total_qty % self.platform_qty != 0:
            label_qty += 1 # agregar una etiqueta para piezas residuales

        # valores para las etiquetas
        MrpProd = self.env['mrp.production']
        lot_names = ','.join(
            picking_id.move_line_ids_without_package.mapped('lot_id.display_name')
        )

        qa_initials = picking_id.check_ids.mapped('user_id.name')
        if not len(qa_initials):
            qa_initials = ''
        else:
            qa_initials = map(lambda p: p[0], qa_initials[0].split(' '))
            qa_initials = '.'.join(qa_initials)

        mrp_prod_id = MrpProd.search([('name', '=', picking_id.origin)])
        if not len(mrp_prod_id):
            raise UserError(f'No se encontró la orden de fabricación {picking_id.origin}')
        mo_date = mrp_prod_id[0].date_finished.strftime('%d/%m/%Y')
        
        storage_location = picking_id.move_line_ids_without_package\
            .mapped('product_id.putaway_rule_ids')
        if not len(storage_location):
            storage_location = picking_id.location_dest_id.display_name
        else:
            storage_location = storage_location[0].location_out_id.display_name
        
        pick_date = picking_id.date_done.strftime('%d/%m/%Y')
        
        product_name = picking_id.move_line_ids_without_package\
            .mapped('product_id.display_name')[0]
        
        lines = []
        for idx in range(1, label_qty + 1):
            lines.append({
                'pn' : product_name,
                'mo' : picking_id.origin,
                'qty' : self.platform_qty,
                'lot' : lot_names,#'LOTE',
                'qa' : qa_initials,#'INICIALES',
                'location_dest' : storage_location,#'ALMACENAMIENTO',
                'mo_date' : mo_date,#'FECHA MO',
                'pick_date' : pick_date,
                'count' : f'{idx} de {label_qty}'
            })

        picking_id.stowage_labels_printed = True

        act = self.env.ref('fx_qa_picking_labels.stowage_stock_label').report_action(self)
        act['data'] = {'lines' : lines}
        return act

    def _process_qa_labels(self, picking_id):
        qa_initials = picking_id.check_ids.mapped('user_id.name')
        if not len(qa_initials):
            qa_initials = ''
        else:
            qa_initials = map(lambda p: p[0], qa_initials[0].split(' '))
            qa_initials = '.'.join(qa_initials)

        location_dest = picking_id.location_id.display_name

        lines = []
        for ln in picking_id.move_line_ids_without_package:
            lines.append({
                'pn' : ln.product_id.display_name,
                'mo' : picking_id.origin,
                'qty' : '%0.2f' % ln.qty_done,
                'lot' : ln.lot_id.display_name,#'LOTE',
                'qa' : qa_initials,#'INICIALES',
                'location_dest' :  location_dest
            })

        picking_id.qa_labels_printed = True

        act = self.env.ref('fx_qa_picking_labels.qa_stock_label').report_action(self)
        act['data'] = {'lines' : lines}
        return act
    
    def _process_single_labels(self, picking_id):
        MrpProd = self.env['mrp.production']
        lot_names = ','.join(
            picking_id.move_line_ids_without_package.mapped('lot_id.display_name')
        )

        qa_initials = picking_id.check_ids.mapped('user_id.name')
        if not len(qa_initials):
            qa_initials = ''
        else:
            qa_initials = map(lambda p: p[0], qa_initials[0].split(' '))
            qa_initials = '.'.join(qa_initials)

        mrp_prod_id = MrpProd.search([('name', '=', picking_id.origin)])
        if not len(mrp_prod_id):
            raise UserError(f'No se encontró la orden de fabricación {picking_id.origin}')
        mo_date = mrp_prod_id[0].date_finished.strftime('%d/%m/%Y')
        
        storage_location = picking_id.move_line_ids_without_package\
            .mapped('product_id.putaway_rule_ids')
        if not len(storage_location):
            storage_location = picking_id.location_dest_id.display_name
        else:
            storage_location = storage_location[0].location_out_id.display_name
        
        product_name = picking_id.move_line_ids_without_package\
            .mapped('product_id.display_name')[0]
        
        total_qty = int(sum(picking_id.move_line_ids_without_package.mapped('qty_done')))
        lines = []
        for idx in range(1, total_qty + 1):
            lines.append({
                'pn' : product_name,
                'mo' : picking_id.origin,
                'lot' : lot_names,#'LOTE', 
                'qa' : qa_initials,#'INICIALES',
                'storage_location' : storage_location,#'UBICACION ALMACENAJE',
                'mo_date' : mo_date,#'FECHA FABRICACION',
                'count' : f'{idx} de {total_qty}'
            })

        picking_id.single_labels_printed = True

        act = self.env.ref('fx_qa_picking_labels.stock_single_label').report_action(self)
        act['data'] = {'lines' : lines}
        return act

    def print_labels(self):
        self.ensure_one()

        picking_id = self.env.context['active_id']
        picking_id = self.env['stock.picking'].browse(picking_id)

        if self.label_type == 'stowage':
            act = self._process_stowage_labels(picking_id)
        elif self.label_type == 'qa':
            act = self._process_qa_labels(picking_id)
        else:
            act = self._process_single_labels(picking_id)
        
        self.onchange_label_type()
        label = filter(lambda item: item[0] == self.label_type, self._fields['label_type'].selection)
        label = map(lambda item: item[1], label)
        msg = f'El usuario {self.env.user.name} ha generado las etiquetas de tipo "{list(label)[0]}"'
        picking_id.message_post(body=msg)
        return act
    
    @api.onchange('label_type')
    def onchange_label_type(self):
        picking_id = self.env.context['active_id']
        picking_id = self.env['stock.picking'].browse(picking_id)

        if self.label_type == 'stowage' and picking_id.stowage_labels_printed:
            self.labels_printed = True
        elif self.label_type == 'qa' and picking_id.qa_labels_printed:
            self.labels_printed = True
        elif self.label_type == 'single' and picking_id.single_labels_printed:
            self.labels_printed = True
        else:
            self.labels_printed = False
