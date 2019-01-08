# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015-TODAY Akretion (http://www.akretion.com)
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

from odoo import fields, api, models


class ProjectProject(models.Model):
    _inherit='project.project'

    customer_project_name = fields.Char(
        help='Name that will appear on customer support menu',
        index=True)
    assign_template_id = fields.Many2one(
        'mail.template',
        string='Assign Template',
        help='If fill a mail will be send when the task is assigned')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    stage_name = fields.Char(
        'Stage', compute='_compute_stage_name', inverse='_inverse_stage_name',
        store=True)
    author_id = fields.Many2one('res.partner', string='Create By')
    assignee_id = fields.Many2one('res.partner', related='user_id.partner_id')
    origin_name = fields.Char()
    origin_url = fields.Char()
    origin_db = fields.Char()
    origin_model = fields.Char()

    @api.depends('stage_id')
    def _compute_stage_name(self):
        for task in self:
            task.stage_name = task.stage_id.name

    def _inverse_stage_name(self):
        for task in self:
            stages = self.env['project.task.type'].search([
                ('project_ids', 'in', [task.project_id.id]),
                ('name', '=', self.stage_name)])
            if stages:
                task.stage_id = stages[0].id

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        if self._context.get('force_message_author_id'):
            kwargs['author_id'] = self._context['force_message_author_id']
        return super(ProjectTask, self).message_post(
            body=body, subject=subject, message_type=message_type,
            subtype=subtype, parent_id=parent_id, attachments=attachments,
            content_subtype=content_subtype, **kwargs)

    def _track_template(self, tracking):
        res = super(ProjectTask, self)._track_template(tracking)
        for task in self:
            changes, tracking_value_ids = tracking[task.id]
            if 'user_id' in changes\
                    and task.project_id.assign_template_id and task.user_id:
                res['user_id'] = (
                    task.project_id.assign_template_id,
                    {'composition_mode': 'mass_mail'})
        return res
