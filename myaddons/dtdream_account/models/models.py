# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_account(models.Model):
    _inherit = 'account.account.type'

    type = fields.Selection([
        ('other', 'Regular'),
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
        ('liquidity', 'Liquidity'),
        ('account_type_0', '非流动负债'),
        ('account_type_1', '非流动资产'),
        ('account_type_2', '流动负债'),
        ('account_type_3', '流动资产'),
        ('account_type_4', '所有者权益'),
        ('account_type_5', '财务费用'),
        ('account_type_6', '期间费用'),
        ('account_type_7', '所得税费用'),
        ('account_type_8', '投资收益'),
        ('account_type_9', '营业外收入'),
        ('account_type_10', '营业外支出'),
        ('account_type_11', '营业务成本'),
        ('account_type_12', '营业务收入'),
        ('account_type_13', '营业务税金及附加'),
        ('account_type_14', '资本公积'),
    ], required=True,
        help="The 'Internal Type' is used for features available on "\
        "different types of accounts: liquidity type is for cash or bank accounts"\
        ", payable/receivable is for vendor/customer accounts.")

class dtdream_account_move_line(models.Model):
    _inherit = "account.move.line"

    @api.onchange('dept_id')
    def _compute_dept(self):
        for rec in self:
            rec.dept_code = rec.dept_id.code

    dept_id = fields.Many2one('hr.department',string="部门")
    dept_code = fields.Char(default="000000", string="部门编码")
    company = fields.Many2one('dtdream.company',string="公司")
    product = fields.Char(string="产品",default="0000000")
    region = fields.Char(string="区域",default="0000")
    bussiness_mode = fields.Char(string="商业模式",default="00")
    sale_mode = fields.Char(string="销售模式", default="0000")
    rel_company = fields.Char(string="关联公司", default="000")
    other = fields.Char(string="备用", default="0000")



class dtdream_company(models.Model):
    _name = "dtdream.company"

    name = fields.Char("名称")
