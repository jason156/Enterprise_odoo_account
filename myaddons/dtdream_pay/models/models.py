# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp
import logging

path_log_file = '/tmp/dtdream_pay.log'
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(path_log_file)
formatter = logging.Formatter('%(asctime)s:%(name)s-->%(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

from openerp.dtdream import openerplib

class view(models.Model):
    _inherit = 'ir.ui.view'

    type= fields.Selection([
        ('tree', 'Tree'),
        ('form', 'Form'),
        ('graph', 'Graph'),
        ('pivot', 'Pivot'),
        ('calendar', 'Calendar'),
        ('diagram', 'Diagram'),
        ('gantt', 'Gantt'),
        ('kanban', 'Kanban'),
        ('sales_team_dashboard', 'Sales Team Dashboard'),
        ('expense_dashboard', 'expense_dashboard'),
        ('rd_dashboard', 'rd_dashboard'),
        ('dtdream_pay_dashboard', 'dtdream_pay_dashboard'),
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')

_logger = logging.getLogger(__name__)
class dtdream_pay(models.Model):
    _name = 'dtdream.pay'

    name = fields.Char()

    @api.model
    def retrieve_pay_dashboard(self):
        em = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        _logger.info("retrieve_pay_dashboard login: " + em.job_number)
        try:
            hostname = openerp.tools.config['hostname']
            database = openerp.tools.config['database']
            wage_login = openerp.tools.config['login']
            password = openerp.tools.config['password']
        except Exception, e:
            return {"code": 20000, "message": u"工资查询系统参数未配置"}
        connection = openerplib.get_connection(hostname=hostname, database=database, login=wage_login, password=password)
        remodel = connection.get_model("dtdream.verification.code")
        result = remodel.get_statistics_time(login=em.account)
        return result

    @api.model
    def get_pay_list_by_user(self,startMonth=None,endMonth=None,vaCode=None,host=None):
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        _logger.info("get_pay_list_by_user login: " + em.job_number)
        _logger.info("get_pay_list_by_user host: " + host)
        try:
            hostname = openerp.tools.config['hostname']
            database = openerp.tools.config['database']
            wage_login = openerp.tools.config['login']
            password = openerp.tools.config['password']
        except Exception, e:
            return {"code": 20000, "message": u"工资查询系统参数未配置"}
        connection = openerplib.get_connection(hostname=hostname, database=database, login=wage_login, password=password)
        remodel = connection.get_model("dtdream.verification.code")
        checkresult = remodel.check_verification_code(em.account,vaCode)
        if checkresult['code']==10000:
            remodel = connection.get_model("dtdream.wage")
            lists = remodel.get_wage_list_by_user(em.job_number,startMonth,endMonth,host)
            return lists
        else:
            return checkresult


    @api.model
    def get_pay_phone_list_by_user(self,startMonth=None,endMonth=None,vaCode=None,host=None):
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        _logger.info("get_pay_phone_list_by_user login: " + em.job_number)
        _logger.info("get_pay_phone_list_by_user host: " + host)
        try:
            hostname = openerp.tools.config['hostname']
            database = openerp.tools.config['database']
            wage_login = openerp.tools.config['login']
            password = openerp.tools.config['password']
        except Exception, e:
            return {"code": 20000, "message": u"工资查询系统参数未配置"}
        connection = openerplib.get_connection(hostname=hostname, database=database, login=wage_login, password=password)
        remodel = connection.get_model("dtdream.verification.code")

        checkresult = remodel.check_verification_code(em.account, vaCode)
        if checkresult['code'] == 10000:
            remodel = connection.get_model("dtdream.wage")
            lists = remodel.get_wage_phone_list_by_user(em.job_number, startMonth, endMonth,host)
            return lists
        else:
            return checkresult

    @api.model
    def get_pay_list_detail_by_month(self,month=None,vaCode=None,host=None):
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        _logger.info("get_pay_list_detail_by_month login: " + em.job_number)
        _logger.info("get_pay_list_detail_by_month host: " + host)
        try:
            hostname = openerp.tools.config['hostname']
            database = openerp.tools.config['database']
            wage_login = openerp.tools.config['login']
            password = openerp.tools.config['password']
        except Exception, e:
            return {"code": 20000, "message": u"工资查询系统参数未配置"}
        connection = openerplib.get_connection(hostname=hostname, database=database, login=wage_login, password=password)
        remodel = connection.get_model("dtdream.verification.code")
        checkresult = remodel.check_verification_code(em.account, vaCode)
        if checkresult['code'] == 10000:
            remodel = connection.get_model("dtdream.wage")
            lists = remodel.get_wage_list_detail_by_month(em.job_number, month,host)
            return lists
        else:
            return checkresult


    @api.model
    def get_pay_phone_list_detail_by_month(self, month=None, vaCode=None,host=None):
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        _logger.info("get_pay_phone_list_detail_by_month login: " + em.job_number)
        _logger.info("get_pay_phone_list_detail_by_month host: " + host)
        try:
            hostname = openerp.tools.config['hostname']
            database = openerp.tools.config['database']
            wage_login = openerp.tools.config['login']
            password = openerp.tools.config['password']
        except Exception, e:
            return {"code": 20000, "message": u"工资查询系统参数未配置"}
        connection = openerplib.get_connection(hostname=hostname, database=database, login=wage_login, password=password)
        remodel = connection.get_model("dtdream.verification.code")
        checkresult = remodel.check_verification_code(em.account, vaCode)
        if checkresult['code'] == 10000:
            remodel = connection.get_model("dtdream.wage")
            lists = remodel.get_pay_phone_list_detail_by_month(em.job_number, month,host)
            return lists
        else:
            return checkresult