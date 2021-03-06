# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import expression
from openerp.exceptions import ValidationError
import re
from datetime import datetime
from lxml import etree


class dtdream_customer_reception(models.Model):
    _name = 'dtdream.customer.reception'
    _rec_name = 'title'
    _description = u"客户接待"
    _inherit = ['mail.thread']

    @api.depends('name')
    def compute_employee_info(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.iphone = rec.name.mobile_phone
            rec.post = rec.name.duties
            rec.home = rec.name.work_place
            rec.department = rec.name.department_id.complete_name
            rec.code = rec.name.department_id.code

    @api.depends('name')
    def _compute_phone_num(self):
        cr = self.env['dtdream.customer.reception.config'].search([], limit=1)
        self.duty_tel = cr.duty_phone

    def _compute_is_customer_manage(self):
        if self.env.ref("dtdream_customer_reception.customer_reception_manage") in self.env.user.groups_id:
            self.is_manage = True
        else:
            self.is_manage = False

    def _compute_login_is_approve(self):
        if self.current_approve.user_id == self.env.user:
            self.is_current = True
        else:
            self.is_current = False

    def _compute_login_is_shenqinren(self):
        if self.name.user_id == self.env.user:
            self.is_shenqingren = True
        else:
            self.is_shenqingren = False

    def _compute_login_is_receptionist(self):
        if self.receptionist.user_id == self.env.user:
            self.is_receptionist = True
        else:
            self.is_receptionist = False

    def _compute_is_officer(self):
        officer = self.env['dtdream.customer.reception.config'].search([], limit=1).officer
        if officer.user_id == self.env.user:
            self.is_officer = True
        else:
            self.is_officer = False

    @api.onchange('customer_source')
    def update_bill_num(self):
        if self.bill_num:
            letter = 'V' if self.customer_source == '0' else 'N'
            self.bill_num = self.bill_num[:-1] + letter
        if self.customer_source != '0':
            self.has_special = '1'
            self.customer = False
            self.project = False
        else:
            self.has_special = '0'

    @api.onchange('customer')
    def compute_customer_level(self):
        for rec in self:
            if rec.customer:
                rec.customer_level = rec.customer.partner_important
                if rec.customer_level in ["SS", "S"]:
                    rec.camera = "0"
                else:
                    rec.camera = '2'
            else:
                rec.customer_level = False

    @api.onchange('customer_level')
    def compute_camera_value(self):
        for rec in self:
            if rec.customer_level in ["SS", "S"]:
                rec.camera = "0"
            else:
                rec.camera = '2'

    @api.depends('cost')
    def _compute_total_cost(self):
        total = 0
        for rec in self.cost:
            total += rec.money
            self.total_cost = total

    def _compute_is_create(self):
        if self.create_uid == self.env.user:
            self.is_create = True
        else:
            self.is_create = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_customer_reception, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
        if menu == u"所有单据":
            member = self.env.ref("dtdream_customer_reception.customer_reception_member") in self.env.user.groups_id
            manage = self.env.ref("dtdream_customer_reception.customer_reception_manage") in self.env.user.groups_id
            inter = self.env['dtdream.customer.reception.config'].search([], limit=1).inter.user_id == self.env.user
            if member or manage or inter:
                domain = domain if domain else []
            else:
                uid = self._context.get('uid', '')
                if domain:
                    domain = expression.AND([['|', '|', '|', ('approves.user_id', '=', uid), ('name.user_id', '=', uid),
                                              ('current_approve.user_id', '=', uid), ('create_uid', '=', uid)], domain])
                else:
                    domain = ['|', '|', '|',('approves.user_id', '=', uid), ('name.user_id', '=', uid),
                              ('current_approve.user_id', '=', uid), ('create_uid', '=', uid)]
        return super(dtdream_customer_reception, self).search_read(domain=domain, fields=fields, offset=offset,
                                                                   limit=limit, order=order)

    def create_customer_activities(self, result):
        if result.purpose.name == u'公司展厅参观' or result.purpose.name == u"小镇展厅参观":
            activity = '1'
        elif result.purpose.name == u'公司展厅参观+会议交流':
            activity = '0'
        else:
            activity = ''
        company = [p.name for p in result.accompany_leads] + [p.name for p in result.interpreter] +\
                  [p.name for p in result.participants]
        company.append(result.name.name)
        result.env['dtdream.marketing.activities'].create({'activity': activity, 'activity_time': result.visit_date,
                                                           'customer': ';'.join([guest.name_guest for guest in result.guest if guest]),
                                                           'company': ';'.join(set(company)), 'partner_customer': result.customer.id,
                                                           'customer_reception_id': result.id})

    def update_customer_activities(self):
        if self.purpose.name == u'公司展厅参观' or self.purpose.name == u"小镇展厅参观":
            activity = '1'
        elif self.purpose.name == u'会议交流':
            activity = '0'
        else:
            activity = ''
        company = [p.name for p in self.accompany_leads] + [p.name for p in self.interpreter] +\
                  [p.name for p in self.participants]
        company.append(self.name.name)
        if self.receptionist:
            company.append(self.receptionist.name)
        self.env['dtdream.marketing.activities'].search([('customer_reception_id', '=', self.id)]).write(
            {'activity': activity, 'activity_time': self.visit_date,
             'customer': ';'.join([guest.name_guest for guest in self.guest if guest]), 'company': ';'.join(set(company))})

    @api.constrains('cost')
    def constraint_cost_save(self):
        if self.has_special == '1':
            total = 0
            for rec in self.cost:
                total += rec.money
            if total > 5000:
                raise ValidationError('总费用已超5000元,需先申请专项!')

    @api.onchange('has_special', 'special_code')
    def _update_customer_cost(self):
        if self.has_special == '0' and self.special_code:
            cr = self.env['dtdream.approval.fee'].search([('fee', '=', self.special_code.id)])
            target = [(0, 0, {'fee_type': crr.fee_type, 'money': crr.money, 'remark': crr.remark}) for crr in cr]
            self.cost = target
        else:
            self.cost = False
            self.special_code = False

    @api.multi
    def write(self, vals):
        if vals.has_key('special_code') and (vals.get('has_special', None) == '0' or self.has_special == '0')and vals.get('special_code'):
            cr = self.env['dtdream.approval.fee'].search([('fee', '=', vals.get('special_code'))])
            target = [(0, 0, {'fee_type': crr.fee_type, 'money': crr.money, 'remark': crr.remark}) for crr in cr]
            if self.cost and self.cost != target:
                self.cost = [(6, 0, [])]
            vals['cost'] = target

        if self.bill_num:
            letter = 'V' if vals.get('customer_source') == '0' else 'N'
            bill_num = self.bill_num[:-1] + letter
            vals.update({'bill_num': bill_num})
        result = super(dtdream_customer_reception, self).write(vals)
        if result:
            self.update_customer_activities()
        return result

    @api.model
    def create(self, vals):
        if vals.has_key('special_code') and vals.get('has_special') == '0':
            cr = self.env['dtdream.approval.fee'].search([('fee', '=', vals.get('special_code'))])
            target = [(0, 0, {'fee_type': crr.fee_type, 'money': crr.money, 'remark': crr.remark}) for crr in cr]
            vals.update({'cost': target})

        letter = 'V' if vals.get('customer_source') not in ('1', '2') else 'N'
        bill_num = datetime.now().strftime("%Y%m%d")
        cr = self.search([('bill_num', 'like', bill_num)], order='id desc', limit=1)
        if cr:
            bill_num = "%s" % (int(cr.bill_num[:-1]) + 1) + letter
        else:
            bill_num = bill_num + '01' + letter
        vals.update({'bill_num': bill_num})
        result = super(dtdream_customer_reception, self).create(vals)
        result.write({'customer_source': result.customer_source})
        self.create_customer_activities(result)
        return result

    @api.model
    def default_get(self, fields):
        rec = super(dtdream_customer_reception, self).default_get(fields)
        if self._context.get('active_id', None):
            rec.update({"entry_way": True})
        return rec

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_customer_reception_menu(self):
        menu_id = self.env['ir.ui.menu'].search([('name', '=', u'客户接待')], limit=1).id
        menu = self.env['ir.ui.menu'].search([('name', '=', u'所有单据'), ('parent_id', '=', menu_id)], limit=1)
        action = menu.action.id
        return menu_id, action

    def send_mail(self, name, subject, content):
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.name)
        base_url = self.get_base_url()
        menu_id, action = self.get_customer_reception_menu()
        url = '%s/web#id=%s&view_type=form&model=dtdream.customer.reception&action=%s&menu_id=%s' % (base_url, self.id, action, menu_id)
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p><a href="%s">点击进入查看</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    @api.multi
    def _message_poss(self, state, action, approve=''):
        self.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下一处理人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, approve))

    bill_num = fields.Char(string='单据号', store=True)
    title = fields.Char(default='客户接待')
    write_time = fields.Datetime(string='填单时间', default=lambda self: fields.Datetime.now())
    duty_tel = fields.Char(string='客工部值班电话', compute=_compute_phone_num)
    name = fields.Many2one('hr.employee', string='申请人',
                           default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]))
    workid = fields.Char('工号', compute=compute_employee_info, store=True)
    iphone = fields.Char(string='联系电话', compute=compute_employee_info)
    post = fields.Char(string='职务', compute=compute_employee_info)
    home = fields.Char(string='常驻地', compute=compute_employee_info)
    department = fields.Char(string='所属部门', compute=compute_employee_info)
    code = fields.Char(string='部门编码', compute=compute_employee_info)
    customer = fields.Many2one('res.partner', string='客户名称')
    customer_char = fields.Char(string='客户名称')
    customer_level = fields.Selection([('SS', 'SS'), ('S', 'S'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                                      string='客户重要级')
    customer_source = fields.Selection([('0', '营销体系邀请'), ('1', '政府邀请'), ('2', '合作伙伴邀请')], string='客户来源', default='0')
    customer_v = fields.Selection([('0', '是'), ('1', '否')], string='是否价值客户', default='0')
    project = fields.Many2one('crm.lead', string='项目名称')
    visit_count = fields.Integer(string='来访人数')
    guest = fields.One2many('dtdream.guest.honour', 'customer_reception')
    visit_date = fields.Date(string='来访日期')
    inter_tel = fields.Char(string='接口人联系方式')
    background = fields.Text(string='客户背景')
    purpose = fields.Many2one('dtdream.visit.purpose', string='来访目的')
    accompany_leads = fields.Many2many('hr.employee', 'dtdream_customer_accompany_leads', string='公司出席陪同领导')
    interpreter = fields.Many2many('hr.employee', 'dtdream_customer_interpreter', string='汇报讲解人员')
    participants = fields.Many2many('hr.employee', 'dtdream_customer_participants', string='公司参会人员名单')
    room_capacity = fields.Integer(string='会议室大小')
    busy_time_room = fields.Datetime(string='会议室使用时间')
    ppt = fields.Boolean(string='PPT')
    camera = fields.Selection(string='摄影', selection=[('0', '全程摄影'), ('1', '会议室摄影'), ('2', '无需摄影')], default='2')
    water = fields.Boolean(string='瓶装水')
    tea = fields.Boolean(string='茶水')
    meeting_document = fields.Boolean(string='公司资料')
    seat_board = fields.Boolean(string='席位牌')
    banner = fields.Boolean(string='横幅')
    other_more = fields.Boolean(string='其它')
    other_more_text = fields.Text(string='其它准备')
    meeting = fields.Many2one('dtdream.meeting.room', string='会议室预订')
    reserve_time = fields.Datetime(string='会议室预订时间')
    car = fields.Boolean(string='小车')
    car_num = fields.Integer(string='小车')
    commercial_vehicle = fields.Boolean(string='商务车')
    commercial_vehicle_num = fields.Integer(string='商务车')
    bicycle = fields.Boolean(string='自行乘车')
    path = fields.One2many('dtdream.visit.path', 'customer_reception')
    driver = fields.Boolean(string='司机')
    assistance = fields.Boolean(string='接机/接站人员')
    card = fields.Boolean(string='接机牌')
    flower = fields.Boolean(string='鲜花')
    single_room = fields.Boolean(string='标准单人房')
    single_room_num = fields.Integer(string='标准单人房')
    double_room = fields.Boolean(string='标准双人房')
    double_room_num = fields.Integer(string='标准双人房')
    room_self = fields.Boolean(string='自理安排酒店')
    hotel = fields.Selection([('5', '五星级'), ('4', '四星级'), ('3', '三星级或快捷酒店'), ('0', '其它')],
                             string='酒店标准', default='5')
    hotel_position = fields.Selection([('0', '商业区'), ('1', '景区')], string='酒店位置', default='0')
    payment_hotel = fields.Selection([('0', '申请人垫付'), ('1', '客户自理')], string='住宿结算方式', default='0')
    dinner = fields.Selection([('100', '100元以下'), ('300', '101-300元'), ('500', '301-500元'),
                               ('501', '500元以上')], string='用餐标准(人均)', default='100')
    dinner_position = fields.Selection([('0', '商业区'), ('1', '景区')], string='用餐地点', default='0')
    payment_dinner = fields.Selection([('0', '申请人垫付'), ('1', '客户自理')], string='用餐结算方式', default='0')
    memories = fields.Many2one('dtdream.customer.memories', string='纪念品')
    remark = fields.Text(string='备注')
    memories_num = fields.Integer(string='纪念品')
    cost = fields.One2many('dtdream.customer.cost', 'fee', string='费用')
    total_cost = fields.Integer(string='合计(元)', compute=_compute_total_cost)
    has_special = fields.Selection([('0', '是'), ('1', '否')], string='是否有专项')
    special_code = fields.Many2one('dtdream.special.approval', string='专项编码')
    receptionist = fields.Many2one('hr.employee', string='指定客户接待执行人')
    summary = fields.Text(string='接待人员接待小结')
    score = fields.Selection([('%s' % i, '%s分' % i) for i in range(1, 11)], string='评分')
    current_approve = fields.Many2one('hr.employee', string='当前审批人')
    approves = fields.Many2many('hr.employee', string='已审批的人')
    is_current = fields.Boolean(string='是否当前审批人', compute=_compute_login_is_approve)
    is_shenqingren = fields.Boolean(string='是否申请人', compute=_compute_login_is_shenqinren, default=lambda self: True)
    is_receptionist = fields.Boolean(string='是否接待执行人', compute=_compute_login_is_receptionist)
    is_officer = fields.Boolean(string='是否客工部主管', compute=_compute_is_officer)
    is_manage = fields.Boolean(string='是否客户接待管理员', compute=_compute_is_customer_manage)
    is_create = fields.Boolean(string='是否创建人', compute=_compute_is_create, default=lambda self: True)
    entry_way = fields.Boolean(string='创建客户接待方式')
    state = fields.Selection([('0', '草稿'),
                              ('1', '部门审批'),
                              ('2', '客工部审批'),
                              ('3', '接待安排与执行'),
                              ('4', '执行评价'),
                              ('99', '完成'),
                              ], string='状态', default='0')

    @api.multi
    def wkf_draft(self):
        if (self.state == '1' or self.state == '2') and self.name.user_id != self.env.user:
            approve = self.current_approve.id
            self.write({"state": '0', 'current_approve': '', 'approves': [(4, approve)]})
        else:
            if self.state == '3':
                # 通知接待安排执行人
                subject = u'【通知】客户接待申请已被撤回'
                content = u'%s提交的客户接待申请已被撤回,请您知悉!' % self.name.name
                self.send_mail(self.receptionist, subject=subject, content=content)
                # 通知车辆负责人
                cr = self.env['dtdream.customer.reception.config'].search([], limit=1)
                inter = cr.inter
                if (self.car and self.car_num) or (self.commercial_vehicle and self.commercial_vehicle_num):
                    car = cr.car
                    self.send_mail(car, subject=subject, content=content)
                # 通知企划部接口人
                if self.camera == '0' or self.camera == '1':
                    self.send_mail(inter, subject=subject, content=content)
            #if self.state != '0':
                # state = {'1': u'部门审批', '2': u'客工部审批', '3': u'接待安排与执行'}
                # self._message_poss(state=u'%s-->草稿' % state.get(self.state), action=u'撤回', approve=self.name.name)
            self.write({"state": '0', 'current_approve': ''})

    @api.multi
    def wkf_approve1(self):
        current_approve = self.name.department_id.manager_id
        self.write({"state": '1',  'current_approve': current_approve.id})
        subject = u'【通知】请您审批%s提交的客户接待申请!' % self.name.name
        content = u'%s提交了客户接待申请进入部门审批阶段,请您审批!' % self.name.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'草稿-->部门审批', action=u'提交', approve=current_approve.name)

    @api.multi
    def wkf_approve2(self):
        approve = self.current_approve.id
        current_approve = self.env['dtdream.customer.reception.config'].search([], limit=1).officer
        self.write({"state": '2', 'current_approve': current_approve.id, 'approves': [(4, approve)]})
        subject = u'【通知】请您审批%s提交的客户接待申请!' % self.name.name
        content = u'%s提交的客户接待申请进入客工部审批阶段,请您审批!' % self.name.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'部门审批-->客工部审批', action=u'审批同意', approve=current_approve.name)

    @api.multi
    def wkf_apply(self):
        approve = self.current_approve.id
        if not self.receptionist:
            raise ValidationError('请指定客户接待执行人!')
        current_approve = self.receptionist
        self.write({"state": '3', 'current_approve': current_approve.id, 'approves': [(4, approve)]})
        # 通知接待安排执行人
        subject = u'【通知】请您落实安排%s的客户接待申请,待接待完成填写接待小结!' % self.name.name
        content = u'%s提交的客户接待申请进入接待安排与执行阶段,请您与申请人沟通,落实安排,待接待完成填写接待小结!' % self.name.name
        self.send_mail(current_approve, subject=subject, content=content)
        # 通知车辆负责人
        cr = self.env['dtdream.customer.reception.config'].search([], limit=1)
        inter = cr.inter
        if (self.car and self.car_num) or (self.commercial_vehicle and self.commercial_vehicle_num):
            car = cr.car
            subject = u'【通知】请您安排客户接待相关接送车辆!'
            content = u'%s提交的客户接待申请进入接待安排与执行阶段,请您查看及安排相关接送车辆!' % self.name.name
            self.send_mail(car, subject=subject, content=content)
        # 通知企划部接口人
        if self.camera == '0' or self.camera == '1':
            subject = u'【通知】请您安排客户接待摄影相关事宜'
            content = u'%s提交的客户接待申请进入接待安排与执行阶段,请您查看,及安排摄影相关事宜!' % self.name.name
            self.send_mail(inter, subject=subject, content=content)
        self._message_poss(state=u'客工部审批-->接待安排与执行', action=u'审批同意', approve=current_approve.name)

    @api.multi
    def wkf_evaluate(self):
        approve = self.current_approve.id
        current_approve = self.name
        self.write({"state": '4', 'current_approve': current_approve.id, 'approves': [(4, approve)]})
        subject = u'【通知】请您对接待效果做出评价!'
        content = u'您提交的客户接待申请进入执行评价阶段,请您对接待效果做出评价!'
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'接待安排与执行-->执行评价', action=u'提交', approve=current_approve.name)

    @api.multi
    def wkf_done(self):
        self.write({"state": '99', 'current_approve': ''})
        officer = self.env['dtdream.customer.reception.config'].search([], limit=1).officer
        subject = u'【通知】请您查看接待效果评价!'
        content = u'%s对客户接待效果做出了评价,评分:%s分,请您查看!' % (self.name.name, self.score)
        self.send_mail(officer, subject=subject, content=content)
        self._message_poss(state=u'执行评价-->完成', action=u'提交')


class dtdream_customer_cost(models.Model):
    _name = 'dtdream.customer.cost'

    fee_type = fields.Selection([('fee_type1', '餐费(含酒水)'), ('fee_type2', '会务场租'), ('fee_type3', '住宿费'),
                                 ('fee_type4', '交通费用'), ('fee_type5', '礼品费用'), ('fee_type6', '其他')],
                                string='费用类别')
    money = fields.Integer(string="金额(元)")
    remark = fields.Text(string="费用事项说明")
    fee = fields.Many2one("dtdream.customer.reception", ondelete="cascade")


class dtdream_guest_honour(models.Model):
    _name = 'dtdream.guest.honour'

    name_guest = fields.Char(string='主宾姓名', size=20)
    post_guest = fields.Char(string='职务', size=30)
    customer_reception = fields.Many2one('dtdream.customer.reception')


class dtdream_visit_purpose(models.Model):
    _name = 'dtdream.visit.purpose'

    name = fields.Char(string='来访目的')
    config = fields.Many2one('dtdream.customer.reception.config')


class dtdream_meeting_room(models.Model):
    _name = 'dtdream.meeting.room'

    name = fields.Char(string='会议室名称')
    config = fields.Many2one('dtdream.customer.reception.config')


class dtdream_visit_path(models.Model):
    _name = 'dtdream.visit.path'

    start_time = fields.Datetime(string='出发时间')
    starting = fields.Char(string='出发地点', size=25)
    end_time = fields.Datetime(string='到达时间')
    destination = fields.Char(string='到达地点', size=25)
    customer_reception = fields.Many2one('dtdream.customer.reception')


class dtdream_customer_memories(models.Model):
    _name = 'dtdream.customer.memories'

    name = fields.Char(string='纪念品名称')
    config = fields.Many2one('dtdream.customer.reception.config')


class dtdream_customer_reception_config(models.Model):
    _name = 'dtdream.customer.reception.config'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_customer_reception_config, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if res['type'] == "form":
            doc.xpath("//form")[0].set("create", "false")
        if res['type'] == "tree":
            doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('officer')
    def update_officer_approve(self):
        reception = self.env['dtdream.customer.reception'].search([('state', '=', '2')])
        for cr in reception:
            cr.write({'current_approve': self.officer.id})

    duty_phone = fields.Char(string='客工部值班电话')
    officer = fields.Many2one('hr.employee', string='客工部主管')
    car = fields.Many2one('hr.employee', string='车辆负责人')
    inter = fields.Many2one('hr.employee', string='企划部接口人')
    purpose = fields.One2many('dtdream.visit.purpose', 'config')
    memory = fields.One2many('dtdream.customer.memories', 'config')
    metting_room = fields.One2many('dtdream.meeting.room', 'config')
    name = fields.Char(default=lambda self: u'客户接待配置')


class dtdream_marketing_activities(models.Model):
    _name = 'dtdream.marketing.activities'

    activity = fields.Selection([('0', '技术交流'), ('1', '公司参观'), ('2', '高层拜访'), ('3', '现场会'),
                                 ('4', '第三方活动'), ('5', '样板点参观')], string='活动类型')
    activity_time = fields.Date(string='时间')
    activity_place = fields.Char(string='地点', default=lambda self: '公司杭州基地')
    customer = fields.Char(string='客户参与人员')
    company = fields.Char(string='公司参与人员')
    activity_content = fields.Text(string='活动内容')
    activity_result = fields.Text(string='结果')
    customer_reception_id = fields.Integer()
    partner_customer = fields.Many2one('res.partner')


class dtdream_customer_res_partner(models.Model):
    _inherit = 'res.partner'

    def _compute_marketing_activities_log(self):
        for rec in self:
            cr = rec.env["dtdream.customer.reception"].search([("customer.id", "=", rec.id)])
            rec.customer_reception = len(cr)

    marketing_activities = fields.One2many('dtdream.marketing.activities', 'partner_customer')
    customer_reception = fields.Integer(compute=_compute_marketing_activities_log)

    @api.multi
    def act_dtdream_customer_reception(self):
        action = {
            'name': '客户接待',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'dtdream.customer.reception',
            'res_id': '',
            'context': {'default_customer': self.id, 'default_customer_level': self.partner_important,
                        'default_customer_source': '0'},
            }
        return action


class dtdream_hr_department(models.Model):
    _inherit = 'hr.department'

    @api.onchange('manager_id')
    def update_customer_reception(self):
        reception = self.env['dtdream.customer.reception'].search([('state', '=', '1')])
        for cr in reception:
            cr.write({'current_approve': self.manager_id.id})


class dtdream_customer_special(models.Model):
    _inherit = 'dtdream.special.approval'

    @api.multi
    def name_get(self):
        if self._context.get('params', None) and self._context.get('params').\
                get('model', None) != 'dtdream.customer.reception':
            return super(dtdream_customer_special, self).name_get()
        result = []
        for cr in self:
            name = cr.name + ' ' + cr.business_item
            result.append((cr.id, name))
        return result



