# -*- coding:utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError
import base64

class WizardStowageLabelsFile(models.TransientModel):
    _name = 'wizard.stowage.labels.file'

    wizard_id = fields.Many2one('wizard.stowage.labels', 'ID Ref')
    binary_file = fields.Binary('Archivo')
    binary_file_name = fields.Char('Nombre del Archivo')

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

    split_labels = fields.Boolean('Dividir PDF', default=True)
    reports_file_ok = fields.Boolean('Archivos Listos')
    report_file_ids = fields.One2many('wizard.stowage.labels.file', 'wizard_id', 'Archivos')

    def generate_labels_adjunts(self, list_records, report_name, picking_id):
        xbinary_lines = []
        attachment_obj = self.env['ir.attachment'].sudo()
        wizard_binary_obj = self.env['wizard.stowage.labels.file']
        count = 1
        for list_ids in list_records:
            if count < 10:
                count_str = '0'+str(count)
            else:
                count_str = str(count)
            file_name = "Etiqueta %s" % count_str

            report_from_action = self.env.ref(report_name)
            data = {'data': {'lines' : list_ids}}
            result, format = report_from_action._render_qweb_pdf(picking_id, data=data)

            # # TODO in trunk, change return format to binary to match message_post expected format
            result = base64.b64encode(result)
            
            attachment_pdf_name = file_name+'.pdf'

            data_attach_pdf = {
                                    'binary_file'       : result,
                                    'binary_file_name' : attachment_pdf_name,
                               }

            xline = (0,0,data_attach_pdf)
            xbinary_lines.append(xline)
            count += 1

        self.reports_file_ok = True
        self.report_file_ids = xbinary_lines

        # self.onchange_label_type()
        # label = filter(lambda item: item[0] == self.label_type, self._fields['label_type'].selection)
        # label = map(lambda item: item[1], label)
        # msg = f'El usuario {self.env.user.name} ha generado las etiquetas de tipo "{list(label)[0]}"'
        # picking_id.message_post(body=msg)

        # action_return = {
        #                     'name': 'Etiquetas PDF',
        #                     'view_mode': 'form',
        #                     'view_id': self.env.ref('fx_grmv_picking_labels.stowage_labels_form').id,
        #                     'res_model': 'wizard.stowage.labels',
        #                     'context': "{}", # self.env.context
        #                     'type': 'ir.actions.act_window',
        #                     'res_id': self.id,
        #                 }

        action_return =  {
                            'name': 'Etiquetas PDF',
                            'type': 'ir.actions.act_window',
                            'res_model': 'wizard.stowage.labels',
                            'view_mode': 'form',
                            'view_type': 'form',
                            'res_id': self.id,
                            'views': [(False, 'form')],
                            'target': 'new',
                          }
        return action_return
                

    def _process_stowage_labels(self, picking_id):
        if self.platform_qty < 1:
            raise UserError('Indique un número de etiquetas mayor que cero')

        # calcular num de etiquetas = total_piezas / piezas_tarima
        total_qty = sum(picking_id.move_line_ids_without_package.mapped('qty_done'))
        total_qty = int(total_qty)
        if self.platform_qty > total_qty:
            raise UserError(
                'Indique una cantidad menor o igual al total de piezas del traslado'
            )

        pages_qty = int(total_qty / self.platform_qty)
        pages_qty_module = total_qty % self.platform_qty
        if pages_qty_module != 0:
            pages_qty += 1 # agregar una etiqueta para piezas residuales

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

        mrp_prod_id = MrpProd.search([('name', 'ilike', f'{picking_id.origin}%%')])
        if not len(mrp_prod_id):
            raise UserError(f'No se encontró la orden de fabricación {picking_id.origin}')
        
        date_finished = mrp_prod_id[0].date_finished
        mo_date = date_finished.strftime('%d/%m/%Y') if date_finished else ""

        
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
        label_qty = total_qty
        list_records = []
        sublist = []
        count_l = 1
        for idx in range(1, pages_qty + 1):
            label_qty = self.platform_qty
            # cantidad disponible disminuye con cada etiqueta
            if pages_qty_module != 0 and idx == pages_qty:
                # la etiqueta residual contiene menos piezas que las demas
                label_qty = total_qty - (self.platform_qty * (idx - 1))

            xvals = {
                        'pn' : product_name,
                        'mo' : picking_id.origin,
                        'qty' : f'{label_qty} de {total_qty}',
                        'lot' : lot_names,#'LOTE',
                        'qa' : qa_initials,#'INICIALES',
                        'location_dest' : storage_location,#'ALMACENAMIENTO',
                        'mo_date' : mo_date,#'FECHA MO',
                        'pick_date' : pick_date,
                        'count' : f'{idx} de {pages_qty}'
                    }
            lines.append(xvals)
            if count_l <= 800:
                sublist.append(xvals)
                count_l += 1
            else:
                list_records.append(sublist)
                sublist = [xvals]
                count_l = 1
            label_qty = total_qty

        picking_id.stowage_labels_printed = True

        #
        #
        if self.split_labels:
            action_return = self.generate_labels_adjunts(list_records, 'fx_grmv_picking_labels.stowage_stock_label', picking_id)
            return action_return
        else:
            act = self.env.ref(list_records, 'fx_grmv_picking_labels.stowage_stock_label').report_action(self)
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
        list_records = []
        sublist = []
        count_l = 1
        for ln in picking_id.move_line_ids_without_package:
            xvals = {
                        'pn' : ln.product_id.display_name,
                        'mo' : picking_id.origin,
                        'qty' : '%0.2f' % ln.qty_done,
                        'lot' : ln.lot_id.display_name,#'LOTE',
                        'qa' : qa_initials,#'INICIALES',
                        'location_dest' :  location_dest
                    }
            lines.append(xvals)
            if count_l <= 800:
                sublist.append(xvals)
                count_l += 1
            else:
                list_records.append(sublist)
                sublist = [xvals]
                count_l = 1

        picking_id.qa_labels_printed = True
        if self.split_labels:
            action_return = self.generate_labels_adjunts(list_records, 'fx_grmv_picking_labels.qa_stock_label', picking_id)
            return action_return
        else:
            act = self.env.ref(list_records, 'fx_grmv_picking_labels.qa_stock_label').report_action(self)
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

        mrp_prod_id = MrpProd.search([('name', 'ilike', f'{picking_id.origin}%%')])
        if not len(mrp_prod_id):
            raise UserError(f'No se encontró la orden de fabricación {picking_id.origin}')

        date_finished = mrp_prod_id[0].date_finished
        mo_date = date_finished.strftime('%d/%m/%Y') if date_finished else ""
        
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
        list_records = []
        sublist = []
        count_l = 1
        for idx in range(1, total_qty + 1):
            xvals = {
                        'pn' : product_name,
                        'mo' : picking_id.origin,
                        'lot' : lot_names,#'LOTE', 
                        'qa' : qa_initials,#'INICIALES',
                        'storage_location' : storage_location,#'UBICACION ALMACENAJE',
                        'mo_date' : mo_date,#'FECHA FABRICACION',
                        'count' : f'{idx} de {total_qty}'
                    }
            lines.append(xvals)
            if count_l <= 800:
                sublist.append(xvals)
                count_l += 1
            else:
                list_records.append(sublist)
                sublist = [xvals]
                count_l = 1

        picking_id.single_labels_printed = True

        if self.split_labels:
            action_return = self.generate_labels_adjunts(list_records, 'fx_grmv_picking_labels.stock_single_label', picking_id)
            return action_return
        else:
            act = self.env.ref('fx_grmv_picking_labels.stock_single_label').report_action(self)
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
