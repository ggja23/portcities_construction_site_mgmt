from odoo import fields, models, api, _
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta, MO, SU
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    def create_invoice_line(self, invoice):
        """
        Creates invoice lines based on billable timesheet entries from a project.
        
        This function retrieves all billable timesheet entries for a project within
        the invoicing period, groups them by employee, and creates corresponding
        invoice lines with appropriate products and prices.
        
        Args:
            invoice: The invoice record to add lines to
            
        Returns:
            None - modifies invoice in place by adding lines
        """
        # Find related sale order through analytic account
        sale_order = self.env['sale.order'].search(
            [('analytic_account_id', '=', self.analytic_account_id.id)], 
            limit=1
        )
        
        if not sale_order:
            raise UserError(_("No sale order found for this project."))
            
        # Calculate date range for invoicing
        invoice_period = self._get_invoice_period()
        start_date = invoice_period['start_date']
        end_date = invoice_period['end_date']
        
        # Get tasks and timesheets based on whether project uses sections
        if sale_order.analytic_account_id.section_ids:
            self._create_sectioned_invoice_lines(invoice, sale_order, start_date, end_date)
        else:
            self._create_standard_invoice_lines(invoice, sale_order, start_date, end_date)
            
        # Mark processed timesheets as invoiced
        self._mark_timesheets_as_invoiced(invoice)
        
    def _get_invoice_period(self):
        """Calculate the invoice period (from company setting to current Sunday)"""
        today = date.today()
        # Get the most recent Sunday (0 = Monday, 6 = Sunday in Python's weekday)
        idx = (today.weekday() + 1) % 7
        this_sunday = today - timedelta(days=idx)
        
        return {
            'start_date': self.env.user.company_id.inv_start_date,
            'end_date': this_sunday
        }
    
    def _create_sectioned_invoice_lines(self, invoice, sale_order, start_date, end_date):
        """Create invoice lines grouped by sections"""
        project_task_obj = self.env['project.task']
        
        for section in sale_order.analytic_account_id.section_ids:
            # Get all tasks under this section's main task
            parent_task = section.task_id
            task_ids = project_task_obj.search([
                ('parent_task_id', 'child_of', parent_task.id),
                ('active', '=', True)
            ], order='id asc')
            
            # Get timesheets for these tasks
            timesheet_data = self._fetch_timesheet_data(
                sale_order.analytic_account_id.id, 
                start_date, 
                end_date, 
                task_ids
            )
            
            # Create invoice lines for each user's time
            for user_data in timesheet_data:
                self._create_employee_invoice_line(
                    invoice, 
                    sale_order, 
                    user_data[0],  # user_id
                    user_data[1],  # unit_amount
                    section_id=section.id
                )
    
    def _create_standard_invoice_lines(self, invoice, sale_order, start_date, end_date):
        """Create invoice lines without sections"""
        # Get timesheets for this project without specific tasks
        timesheet_data = self._fetch_timesheet_data(
            sale_order.analytic_account_id.id,
            start_date,
            end_date
        )
        
        # Create invoice lines for each user's time
        for user_data in timesheet_data:
            self._create_employee_invoice_line(
                invoice, 
                sale_order, 
                user_data[0],  # user_id
                user_data[1],  # unit_amount
            )
    
    def _fetch_timesheet_data(self, analytic_account_id, start_date, end_date, task_ids=None):
        """
        Fetch billable timesheet data from the database
        
        Returns: List of tuples (user_id, total_hours, timesheet_id)
        """
        query = '''
            SELECT
                distinct(user_id),
                sum(unit_amount), id
            FROM
                account_analytic_line
            WHERE
                account_id = %s
                AND invoiceable_analytic_line = 't'
                AND date >= %s
                AND date <= %s
                AND project_id is not null
                AND project_invoice_line_id is null
        '''
        
        params = [analytic_account_id, start_date, end_date]
        
        # Add task filter if specified
        if task_ids:
            query += ' AND task_id in %s'
            params.append(tuple(task_ids.ids))
        
        query += ' GROUP BY user_id, id ORDER BY user_id asc'
        
        self._cr.execute(query, tuple(params))
        return self._cr.fetchall()
    
    def _create_employee_invoice_line(self, invoice, sale_order, user_id, hours, section_id=False):
        """
        Create an invoice line for an employee's time
        
        Args:
            invoice: Invoice record
            sale_order: Related sale order
            user_id: User ID of the employee
            hours: Number of hours worked
            section_id: Optional section ID
        """
        # Find employee record
        employee = self.env['hr.employee'].search([('user_id', '=', user_id)])
        
        if employee:
            # Create invoice line using employee record
            self._create_invoice_line_from_employee(
                invoice, sale_order, employee, hours, section_id
            )
        else:
            # No employee record found, try to get data from custom method
            employee_data = self.action_search_employee(user_id)
            self._create_invoice_line_from_employee_data(
                invoice, sale_order, employee_data, hours, section_id
            )
    
    def _create_invoice_line_from_employee(self, invoice, sale_order, employee, hours, section_id=False):
        """Create invoice line using employee record"""
        # Validate required products exist
        if not employee.job_id.product_inhouse_id:
            raise UserError(_('Please fill field Inhouse Product {} in Job Position').format(employee.job_id.name))
            
        if not employee.job_id.product_outsource_id:
            raise UserError(_('Please fill field Outsource Product {} in Job Position').format(employee.job_id.name))
            
        # Select product based on company
        if employee.company_id.id == self.env.user.company_id.id:
            product = employee.job_id.product_inhouse_id
        else:
            product = employee.job_id.product_outsource_id
            
        # Calculate price
        price = self._calculate_product_price(sale_order, product, employee.job_id.product_id)
        
        # Create the invoice line
        values = {
            'employee_id': employee.id,
            'product_id': product.id,
            'name': f"{product.name}: {employee.name}",
            'quantity': hours,
            'price_unit': price,
            'invoice_id': invoice.id,
            'account_id': product.property_account_income_id.id,
            'uom_id': employee.job_id.product_id.uom_id.id,
            'l10n_mx_edi_sat_status': 'none',
            'account_analytic_id': sale_order.analytic_account_id.id,
        }
        
        # Add section if provided
        if section_id:
            values['layout_category_id'] = section_id
            
        self.env['account.invoice.line'].create(values)
    
    def _create_invoice_line_from_employee_data(self, invoice, sale_order, employee_data, hours, section_id=False):
        """Create invoice line using employee data from action_search_employee"""
        # Validate employee data has required products
        if not employee_data.get('inhouse'):
            raise UserError(_('Please fill field Inhouse Product {} in Job Position').format(employee_data['position']))
            
        if not employee_data.get('outsource'):
            raise UserError(_('Please fill field Outsource Product {} in Job Position').format(employee_data['position']))
            
        # Select product based on company
        if employee_data['company_id'] == self.env.user.company_id.id:
            product = employee_data['inhouse']
        else:
            product = employee_data['outsource']
            
        # Get product price
        if sale_order.pricelist_id and sale_order.partner_id:
            product_record = self.env['product.product'].search([('id', '=', employee_data['product_id'])])
            price = self.env['account.tax']._fix_tax_included_price(
                product_record.price, product_record.taxes_id, []
            )
        else:
            price = employee_data['list_price']
            
        # Create invoice line
        values = {
            'employee_id': employee_data['employee_id'],
            'product_id': product.id,
            'name': f"{employee_data['product_name']}: {employee_data['employee']}",
            'quantity': hours,
            'price_unit': price,
            'invoice_id': invoice.id,
            'account_id': product.property_account_income_id.id,
            'uom_id': employee_data['uom_id'],
            'l10n_mx_edi_sat_status': 'none',
            'account_analytic_id': sale_order.analytic_account_id.id,
        }
        
        # Add section if provided
        if section_id:
            values['layout_category_id'] = section_id
            
        self.env['account.invoice.line'].create(values)
    
    def _calculate_product_price(self, sale_order, product, job_product):
        """Calculate product price based on sale order and pricelist"""
        so_line_obj = self.env['sale.order.line']
        
        if sale_order.pricelist_id and sale_order.partner_id:
            product_with_context = job_product.with_context(
                lang=sale_order.partner_id.lang,
                partner=sale_order.partner_id.id,
                quantity=1,
                date=sale_order.date_order,
                pricelist=sale_order.pricelist_id.id,
                uom=job_product.uom_id.id
            )
            return self.env['account.tax']._fix_tax_included_price(
                product_with_context.price, product_with_context.taxes_id, so_line_obj.tax_id
            )
        else:
            return job_product.list_price
    
    def _mark_timesheets_as_invoiced(self, invoice):
        """Mark all processed timesheets as invoiced"""
        timesheets = self.check_timesheet_on_project()
        for timesheet in timesheets:
            self.env['account.analytic.line'].search([('id', '=', timesheet[2])]).write({
                'project_invoice_line_id': invoice.id,
            })
