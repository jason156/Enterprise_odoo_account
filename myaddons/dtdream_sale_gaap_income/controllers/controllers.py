# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSaleGaapIncome(http.Controller):
#     @http.route('/dtdream_sale_gaap_income/dtdream_sale_gaap_income/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_sale_gaap_income/dtdream_sale_gaap_income/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_sale_gaap_income.listing', {
#             'root': '/dtdream_sale_gaap_income/dtdream_sale_gaap_income',
#             'objects': http.request.env['dtdream_sale_gaap_income.dtdream_sale_gaap_income'].search([]),
#         })

#     @http.route('/dtdream_sale_gaap_income/dtdream_sale_gaap_income/objects/<model("dtdream_sale_gaap_income.dtdream_sale_gaap_income"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_sale_gaap_income.object', {
#             'object': obj
#         })