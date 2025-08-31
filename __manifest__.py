{
    'name': 'Port Cities Case 1 & 2 - Site & Milestone Customization with Dynamic Requirements',
    'version': '16.0.1.0.0',
    'category': 'Project',
    'summary': 'Port Cities Case 1 & 2: Customize Project module and add Dynamic Requirement Fields',
    'description': """
        Port Cities Case Study 1 & 2 - Construction Site Management
        
        Case 1: Customize Project module for construction companies:
        - Change 'Project' labels to 'Site' (construction sites)
        - Change 'Task' labels to 'Milestone' (project milestones)
        
        Case 2: Dynamic Requirement Fields
        - Create dynamic.requirement.field and dynamic.requirement.field.line models
        - Define mandatory fields for different stages
        - Support for both Site and Milestone types
        - Custom warning messages for each requirement

        
        Developed as part of Port Cities software engineer assessment.
    """,
    'author': 'Jhon Garcia',
    'maintainer': 'Jhon Garcia',
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/project_views.xml',
        'views/dynamic_requirement_field_views.xml',
        'views/dynamic_requirement_field_line_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
