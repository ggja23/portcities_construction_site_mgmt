from odoo import models, fields, api


class DynamicRequirementField(models.Model):
    _name = 'dynamic.requirement.field'
    _description = 'Dynamic Requirement Field'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    type = fields.Selection([
        ('site', 'Site'),
        ('milestone', 'Milestone')
    ], string='Type', required=True)
    name = fields.Char(string='Name', default='Requirement', copy=False, required=True)
    active = fields.Boolean(string='Active', default=True)
    mandatory_project_line = fields.One2many(
        'dynamic.requirement.field.line', 
        'requirement_mandatory_project', 
        string='Mandatory Project Line'
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'Requirement') == 'Requirement':
            sequence = self.env['ir.sequence'].next_by_code('dynamic.requirement.field') or '1'
            vals['name'] = f"Requirement {sequence}"
        return super(DynamicRequirementField, self).create(vals)

    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = self.name + ' (Copy)'
        return super(DynamicRequirementField, self).copy(default)

    @api.model
    def get_requirements_for_stage(self, stage_id, requirement_type):
        """
        Get all mandatory fields for a specific stage and type
        """
        return self.search([
            ('active', '=', True),
            ('type', '=', requirement_type),
            ('mandatory_project_line.stage_id', '=', stage_id)
        ])

    def get_mandatory_fields_for_stage(self, stage_id):
        """
        Get mandatory fields for a specific stage from this requirement
        """
        for line in self.mandatory_project_line:
            if line.stage_id.id == stage_id:
                return line.mandatory_fields
        return self.env['ir.model.fields']
