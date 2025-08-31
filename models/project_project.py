from odoo import models, fields


class ProjectProject(models.Model):
    _inherit = 'project.project'

    deadline_date = fields.Datetime(string='Deadline Date')
    budget = fields.Float(string='Budget')
    project_size = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], string='Project Size')
    # The stage_id field already exists in project.project model, 
    # so we don't need to create it again. We'll just use it in the views.
    
    # Case 2, item 6: Add Requirement field
    requirement_id = fields.Many2one(
        'dynamic.requirement.field',
        string='Requirement',
        help='Select a requirement to apply mandatory fields validation based on stages'
    )