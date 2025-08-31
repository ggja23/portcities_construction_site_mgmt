from odoo import models, fields, api


class DynamicRequirementFieldLine(models.Model):
    _name = 'dynamic.requirement.field.line'
    _description = 'Dynamic Requirement Field Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    requirement_mandatory_project = fields.Many2one(
        'dynamic.requirement.field', 
        string='Requirement Mandatory Project'
    )
    stage_id = fields.Many2one(
        'project.project.stage', 
        string='Stage'
    )
    mandatory_fields = fields.Many2many(
        'ir.model.fields', 
        string='Mandatory Fields'
    )
    custom_warning_message = fields.Char(
        string='Custom Warning Message', 
        required=True,
        default="Field %s is mandatory",
        help="Use %s as a placeholder for the mandatory field name(s). Example: 'Field %s is mandatory'"
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )

    @api.constrains('stage_id', 'requirement_mandatory_project')
    def _check_unique_stage_per_requirement(self):
        """
        Ensure that each stage can only be defined once per requirement
        """
        for record in self:
            if record.stage_id and record.requirement_mandatory_project:
                duplicate = self.search([
                    ('id', '!=', record.id),
                    ('stage_id', '=', record.stage_id.id),
                    ('requirement_mandatory_project', '=', record.requirement_mandatory_project.id)
                ])
                if duplicate:
                    raise models.ValidationError(
                        f"Stage '{record.stage_id.name}' is already defined for requirement '{record.requirement_mandatory_project.name}'"
                    )
                    
    @api.constrains('custom_warning_message')
    def _check_warning_message_format(self):
        """
        Ensure that custom_warning_message contains the %s placeholder
        """
        for record in self:
            if record.custom_warning_message and '%s' not in record.custom_warning_message:
                raise models.ValidationError(
                    "Custom Warning Message must contain '%s' as a placeholder for the field name(s)"
                )

    def check_mandatory_fields_completion(self, record):
        """
        Check if all mandatory fields are completed for a given record
        Returns a tuple (is_complete, missing_fields, warning_message)
        """
        missing_fields = []
        
        for field in self.mandatory_fields:
            field_value = getattr(record, field.name, None)
            if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                missing_fields.append(field.field_description or field.name)
        
        is_complete = len(missing_fields) == 0
        warning_message = self.custom_warning_message if not is_complete else ""
        
        return is_complete, missing_fields, warning_message

    @api.model
    def get_requirements_for_record(self, record, stage_id):
        """
        Get all requirement lines for a specific record and stage
        """
        return self.search([
            ('stage_id', '=', stage_id),
            ('requirement_mandatory_project.type', '=', record._name),
            ('requirement_mandatory_project.active', '=', True)
        ])
