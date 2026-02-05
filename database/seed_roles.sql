-- ================================================================
-- INDUSTRY ROLES - 15 ROLES ACROSS BRANCHES
-- Engineering Skills Radar Seed Data
-- ================================================================

-- LEGEND for required_skills JSONB format:
-- [{"skill_name": "Skill Name", "min_score": 70, "mandatory": true, "weight": 0.3}]

INSERT INTO industry_roles (role_title, role_category, description, required_skills, eligible_branches, avg_ctc, demand_score, typical_companies) VALUES

-- ================================================================
-- SOFTWARE & DATA ROLES (CS/IT/ECE)
-- ================================================================
(
    'Junior Software Developer',
    'Software',
    'Entry-level software development role focused on coding, testing, and debugging',
    '[
        {"skill_name": "Data Structures & Algorithms", "min_score": 75, "mandatory": true, "weight": 0.35},
        {"skill_name": "Object-Oriented Programming", "min_score": 70, "mandatory": true, "weight": 0.30},
        {"skill_name": "Database Management", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 70, "mandatory": true, "weight": 0.15}
    ]',
    '["CS", "IT", "ECE"]',
    6.50,
    90,
    '["TCS", "Infosys", "Wipro", "Cognizant", "Accenture"]'
),

(
    'Full Stack Developer',
    'Software',
    'Design and develop both frontend and backend components of web applications',
    '[
        {"skill_name": "Web Development", "min_score": 75, "mandatory": true, "weight": 0.35},
        {"skill_name": "Database Management", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "Object-Oriented Programming", "min_score": 70, "mandatory": true, "weight": 0.20},
        {"skill_name": "Data Structures & Algorithms", "min_score": 65, "mandatory": false, "weight": 0.20}
    ]',
    '["CS", "IT"]',
    8.00,
    95,
    '["Amazon", "Flipkart", "Zomato", "Paytm", "Swiggy"]'
),

(
    'Data Analyst',
    'Data',
    'Analyze data, create reports, and derive actionable business insights',
    '[
        {"skill_name": "Database Management", "min_score": 75, "mandatory": true, "weight": 0.40},
        {"skill_name": "Problem Solving", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "Engineering Mathematics", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Technical Communication", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["CS", "IT", "All"]',
    7.00,
    85,
    '["Deloitte", "EY", "KPMG", "Mu Sigma", "ZS Associates"]'
),

(
    'Network Engineer',
    'Infrastructure',
    'Design, implement, and maintain computer networks and systems',
    '[
        {"skill_name": "Computer Networks", "min_score": 75, "mandatory": true, "weight": 0.40},
        {"skill_name": "Operating Systems", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "Digital Electronics", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["CS", "IT", "ECE"]',
    6.00,
    75,
    '["Cisco", "Juniper", "HCL", "Tech Mahindra"]'
),

(
    'Embedded Systems Engineer',
    'Hardware',
    'Develop embedded software and hardware systems for devices',
    '[
        {"skill_name": "Embedded Systems", "min_score": 75, "mandatory": true, "weight": 0.35},
        {"skill_name": "Digital Electronics", "min_score": 70, "mandatory": true, "weight": 0.30},
        {"skill_name": "Object-Oriented Programming", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["ECE", "Electrical", "CS"]',
    7.50,
    80,
    '["Bosch", "Continental", "Samsung", "Qualcomm"]'
),

-- ================================================================
-- MECHANICAL ENGINEERING ROLES
-- ================================================================
(
    'Design Engineer',
    'Design',
    'Create and develop mechanical systems and machine designs',
    '[
        {"skill_name": "Machine Design", "min_score": 75, "mandatory": true, "weight": 0.35},
        {"skill_name": "CAD/CAM", "min_score": 75, "mandatory": true, "weight": 0.30},
        {"skill_name": "Engineering Mechanics", "min_score": 70, "mandatory": true, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["Mechanical"]',
    6.50,
    80,
    '["Tata Motors", "Mahindra", "L&T", "Ashok Leyland"]'
),

(
    'Production Engineer',
    'Manufacturing',
    'Oversee manufacturing processes, quality control, and production planning',
    '[
        {"skill_name": "Manufacturing Processes", "min_score": 75, "mandatory": true, "weight": 0.40},
        {"skill_name": "Machine Design", "min_score": 65, "mandatory": false, "weight": 0.25},
        {"skill_name": "Project Management", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["Mechanical"]',
    5.50,
    75,
    '["Tata Steel", "JSW", "Bharat Forge", "Godrej"]'
),

(
    'Thermal Engineer',
    'Energy',
    'Design heating, cooling, and HVAC systems for buildings and vehicles',
    '[
        {"skill_name": "Thermodynamics", "min_score": 75, "mandatory": true, "weight": 0.40},
        {"skill_name": "Fluid Mechanics", "min_score": 70, "mandatory": true, "weight": 0.30},
        {"skill_name": "Engineering Mechanics", "min_score": 65, "mandatory": false, "weight": 0.15},
        {"skill_name": "CAD/CAM", "min_score": 60, "mandatory": false, "weight": 0.15}
    ]',
    '["Mechanical"]',
    6.00,
    70,
    '["Carrier", "Blue Star", "Voltas", "Daikin"]'
),

-- ================================================================
-- CIVIL ENGINEERING ROLES
-- ================================================================
(
    'Structural Engineer',
    'Infrastructure',
    'Design and analyze structures like buildings, bridges, and dams',
    '[
        {"skill_name": "Structural Analysis", "min_score": 80, "mandatory": true, "weight": 0.40},
        {"skill_name": "Concrete Technology", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "AutoCAD/STAAD.Pro", "min_score": 70, "mandatory": true, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["Civil"]',
    6.00,
    85,
    '["L&T", "Shapoorji Pallonji", "Tata Projects", "Gammon India"]'
),

(
    'Site Engineer',
    'Construction',
    'Supervise construction sites, manage workers, and ensure quality standards',
    '[
        {"skill_name": "Construction Management", "min_score": 75, "mandatory": true, "weight": 0.35},
        {"skill_name": "Concrete Technology", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "Structural Analysis", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Project Management", "min_score": 70, "mandatory": false, "weight": 0.20}
    ]',
    '["Civil"]',
    5.00,
    90,
    '["L&T", "DLF", "Godrej Properties", "Oberoi Realty"]'
),

(
    'Transportation Engineer',
    'Infrastructure',
    'Plan and design transportation systems including highways and traffic management',
    '[
        {"skill_name": "Transportation Engineering", "min_score": 75, "mandatory": true, "weight": 0.40},
        {"skill_name": "AutoCAD/STAAD.Pro", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "Geotechnical Engineering", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Project Management", "min_score": 60, "mandatory": false, "weight": 0.15}
    ]',
    '["Civil"]',
    5.50,
    70,
    '["NHAI", "PWD", "L&T", "IRB Infrastructure"]'
),

-- ================================================================
-- ELECTRICAL ENGINEERING ROLES
-- ================================================================
(
    'Power Systems Engineer',
    'Energy',
    'Work on electrical power generation, transmission, and distribution',
    '[
        {"skill_name": "Power Systems", "min_score": 80, "mandatory": true, "weight": 0.40},
        {"skill_name": "Circuit Theory", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "Control Systems", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["Electrical"]',
    6.50,
    75,
    '["NTPC", "BHEL", "PowerGrid", "Adani Power"]'
),

(
    'Control Systems Engineer',
    'Automation',
    'Design and implement automation and control systems for industrial processes',
    '[
        {"skill_name": "Control Systems", "min_score": 80, "mandatory": true, "weight": 0.40},
        {"skill_name": "Digital Electronics", "min_score": 70, "mandatory": true, "weight": 0.25},
        {"skill_name": "Circuit Theory", "min_score": 65, "mandatory": false, "weight": 0.20},
        {"skill_name": "Problem Solving", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["Electrical", "ECE", "Mechanical"]',
    7.00,
    80,
    '["ABB", "Siemens", "Honeywell", "Schneider Electric"]'
),

-- ================================================================
-- CROSS-FUNCTIONAL ROLES
-- ================================================================
(
    'Technical Consultant',
    'Consulting',
    'Provide technical expertise and solutions to clients across industries',
    '[
        {"skill_name": "Problem Solving", "min_score": 75, "mandatory": true, "weight": 0.30},
        {"skill_name": "Technical Communication", "min_score": 75, "mandatory": true, "weight": 0.30},
        {"skill_name": "Project Management", "min_score": 70, "mandatory": false, "weight": 0.25},
        {"skill_name": "Engineering Mathematics", "min_score": 65, "mandatory": false, "weight": 0.15}
    ]',
    '["All"]',
    8.00,
    85,
    '["Deloitte", "Accenture", "McKinsey", "BCG", "Bain"]'
),

(
    'Quality Assurance Engineer',
    'Quality',
    'Ensure product quality through testing, inspection, and process improvement',
    '[
        {"skill_name": "Problem Solving", "min_score": 70, "mandatory": true, "weight": 0.30},
        {"skill_name": "Technical Communication", "min_score": 65, "mandatory": false, "weight": 0.25},
        {"skill_name": "Project Management", "min_score": 65, "mandatory": false, "weight": 0.25},
        {"skill_name": "Engineering Mathematics", "min_score": 60, "mandatory": false, "weight": 0.20}
    ]',
    '["All"]',
    5.50,
    80,
    '["Tata Motors", "Infosys", "TCS", "L&T", "Mahindra"]'
);
