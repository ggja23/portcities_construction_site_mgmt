from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        domain=[('active', '=', True), ('type', '=', 'site')],
        help='Select a requirement to apply mandatory fields validation based on stages'
    )
    
    # Case 2, item 7: Add function to check mandatory fields when changing stage
    @api.constrains('stage_id')
    def _check_mandatory_fields_on_stage_change(self):
        """
        Check if all mandatory fields are filled when moving to a new stage
        """
        for project in self:
            
            validation = (not project.requirement_id or 
                not project.requirement_id.active or 
                project.requirement_id.type != 'site')
            
            # Skip validation if no requirement is set, if it's not active, or if type is not 'site'
            if validation:
                continue
                
                
            # Check if the current stage has mandatory fields defined
            requirement_lines = self.env['dynamic.requirement.field.line'].search([
                ('requirement_mandatory_project', '=', project.requirement_id.id),
                ('stage_id', '=', project.stage_id.id),
            ])
            
            if not requirement_lines:
                continue
                
            # Check if all mandatory fields are filled
            for line in requirement_lines:
                missing_fields = []
                
                for field in line.mandatory_fields:
                    field_value = getattr(project, field.name, None)
                    if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                        field_label = field.field_description or field.name
                        missing_fields.append(field_label)
                
                if missing_fields:
                    # Get the custom warning message from the line
                    warning_msg = line.custom_warning_message
                    
                    # Join field names with formatting
                    field_list = '"' + '", "'.join(missing_fields) + '"'
                    
                    # Format the message using the field list
                    if '%s' in warning_msg:
                        formatted_msg = warning_msg % field_list
                    else:
                        formatted_msg = warning_msg + ': ' + field_list
                    
                    raise ValidationError(formatted_msg)
                    
    def write(self, vals):
        """
        Override write method to check mandatory fields before saving
        """
        if 'stage_id' in vals:
            # Store old stage to check if it changed
            old_stages = {rec.id: rec.stage_id.id for rec in self}
            
            # Call super to apply changes
            result = super(ProjectProject, self).write(vals)
            
            # Check mandatory fields for records whose stage changed
            for rec in self:
                if old_stages.get(rec.id) != rec.stage_id.id:
                    rec._check_mandatory_fields_on_stage_change()
            
            return result
        else:
            return super(ProjectProject, self).write(vals)