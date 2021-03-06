/**
 * @class ExpenseDashboard
 * @classdesc 费用报销Dashboard
 */
odoo.define('dtdream_expense_dingtalk.ui.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');

    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    /**
     * @class ExpenseReportDashboardView
     * @classdesc 费用报销看板
     * @augments KanbanView
     */
    var ExpenseReportDashboardView = KanbanView.extend({
        /**
         * @memberOf ExpenseReportDashboardView
         * @description 标题
         */
        display_name: '费用报销',
        /**
         * @memberOf ExpenseReportDashboardView
         * @description 图标
         */
        icon: 'fa-dashboard',
        /**
         * @memberOf ExpenseReportDashboardView
         * @description 新的视图类型 expense_dashboard
         */
        view_type: "expense_dashboard",
        /**
         * @memberOf ExpenseReportDashboardView
         * @description 是否显示搜索栏
         */
        searchview_hidden: true,
        /**
         *@memberOf ExpenseReportDashboardView
         * @description 事件
         * @property {method} on_dashboard_action_clicked 跳转界面
         */
        events: {
            'click .panel-footer': 'on_dashboard_action_clicked',
        },
        /**
         * @memberOf ExpenseReportDashboardView
         * @description 从服务端获取数据
         * @returns {*|jQuery.Deferred}
         */
        fetch_data: function () {
            // Overwrite this function with useful data
            return new Model('dtdream.expense.report.dashboard')
                .call('retrieve_sales_dashboard', []);
        },
        /**
         * @memberOf ExpenseReportDashboardView
         * @description 显示看板视图内容
         * @returns {*|Promise|Promise.<TResult>}
         */
        render: function () {
            var super_render = this._super;
            var self = this;

            return this.fetch_data().then(function (result) {
                var report_dashboard = QWeb.render('dtdram_expense_dingtalk.ExpenseReportDashboard', {
                    'no_expense_report': result.no_expense_report,
                    'draft_report': result.draft_report,
                    'wait_confirm_report': result.wait_confirm_report,
                    'have_check_report': result.have_check_report,
                    'override_report': result.override_report,
                    'override_report_amount': result.override_report_amount,
                });
                super_render.call(self);

                $(report_dashboard).prependTo(self.$el);
                self.$el.find('.oe_view_nocontent').hide();
            });
        },
        /**
         * @memberOf ExpenseReportDashboardView
         * @description 跳转界面
         * @param ev
         */
        on_dashboard_action_clicked: function (ev) {
            ev.preventDefault();

            var self = this;
            var $action = $(ev.currentTarget);
            var action_name = $action.attr('name');
            var action_extra = $action.data('extra');
            var additional_context = {}

            new Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function (data) {
                    if (data) {
                        self.do_action(data);
                    }
                });
        },
    });

    core.view_registry.add('expense_dashboard', ExpenseReportDashboardView);

    return ExpenseReportDashboardView

});
