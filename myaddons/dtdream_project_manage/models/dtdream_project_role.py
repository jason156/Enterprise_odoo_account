# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import AccessError


class dtdream_project_role(models.Model):
    _name = 'dtdream.project.role'

    @api.depends('name')
    def compute_project_state(self):
        for rec in self:
            rec.state = rec.project_manage_id.state_y

    @api.multi
    def unlink(self):
        for rec in self:
            if not rec.project_manage_id.compute_is_admin and (rec.state != '11' or not rec.required):
                raise AccessError('无法删除此项!')
        return super(dtdream_project_role, self).unlink()

    def update_leader_history(self, vals):
        if self.project_manage_id.is_project_manage and self.state != '11':
            new_leader = vals.get('leader', '')
            old_leader = self.search([('id', '=', self.id)]).leader.id
            if new_leader and new_leader != old_leader:
                leader_history = [rec.id for rec in self.leader_history]
                if old_leader not in leader_history:
                    leader_history += [old_leader]
                super(dtdream_project_role, self).write({'approved': False, 'result': False, 'leader_history': [(
                    6, 0,  leader_history)]})
            if self.project_manage_id.state_y == '12':
                self.project_manage_id.update_current_approve()

    @api.multi
    def write(self, vals):
        self.update_leader_history(vals)
        return super(dtdream_project_role, self).write(vals)

    name = fields.Char(string='角色名称', size=16)
    leader = fields.Many2one('hr.employee', string='负责人')
    required = fields.Boolean(string='可否删除')
    leader_history = fields.Many2many('hr.employee', string='历史负责人列表')
    approved = fields.Boolean(string='已审批')
    result = fields.Boolean(string='审批不通过')
    suggestion = fields.Char(string='审批意见', size=30)
    state = fields.Selection([('0', '草稿'),
                              ('10', '指派项目经理'),
                              ('11', '同步项目订单信息'),
                              ('12', '交付服务经理确认'),
                              ('1', '立项'),
                              ('20', '发起策划'),
                              ('21', 'PMO审核策划'),
                              ('2', '策划'),
                              ('3', '交付'),
                              ('4', '运维'),
                              ('99', '结项')], string='状态', compute=compute_project_state)
    project_manage_id = fields.Many2one('dtdream.project.manage')


class dtdream_project_role_setting(models.Model):
    _name = 'dtdream.project.role.setting'

    name = fields.Char(string='角色名称', size=16)
    required = fields.Boolean(string='可否删除')
