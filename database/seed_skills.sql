-- ================================================================
-- SKILL TAXONOMY - 28 CORE SKILLS
-- Engineering Skills Radar Seed Data
-- ================================================================

INSERT INTO skills (skill_name, skill_category, description, branches, benchmark_score) VALUES

-- ================================================================
-- COMPUTER SCIENCE & IT SKILLS
-- ================================================================
('Data Structures & Algorithms', 'Core Technical', 'Arrays, Trees, Graphs, Sorting, Searching, Dynamic Programming', '["CS", "IT", "All"]', 75),
('Object-Oriented Programming', 'Core Technical', 'Classes, Inheritance, Polymorphism, Encapsulation, Design Patterns', '["CS", "IT", "ECE"]', 70),
('Database Management', 'Core Technical', 'SQL, NoSQL, Schema Design, Queries, Transactions', '["CS", "IT", "All"]', 70),
('Web Development', 'Core Technical', 'HTML, CSS, JavaScript, Frontend/Backend Development', '["CS", "IT"]', 65),
('Operating Systems', 'Core Technical', 'Process Management, Memory, File Systems, Concurrency', '["CS", "IT", "ECE"]', 70),
('Computer Networks', 'Core Technical', 'TCP/IP, Routing, Protocols, Network Security', '["CS", "IT", "ECE"]', 70),

-- ================================================================
-- MECHANICAL ENGINEERING SKILLS
-- ================================================================
('Engineering Mechanics', 'Core Technical', 'Statics, Dynamics, Force Analysis, Free Body Diagrams', '["Mechanical", "Civil"]', 70),
('Thermodynamics', 'Core Technical', 'Heat Transfer, Energy Systems, First/Second Law', '["Mechanical"]', 70),
('Machine Design', 'Core Technical', 'Gears, Bearings, Shafts, Stress Analysis, Failure Theories', '["Mechanical"]', 70),
('Manufacturing Processes', 'Core Technical', 'Casting, Machining, Welding, CNC, Quality Control', '["Mechanical"]', 65),
('CAD/CAM', 'Tools & Software', 'AutoCAD, SolidWorks, CATIA, 3D Modeling', '["Mechanical", "Civil"]', 70),
('Fluid Mechanics', 'Core Technical', 'Flow Analysis, Bernoulli, Pumps, Turbines', '["Mechanical", "Civil"]', 70),

-- ================================================================
-- CIVIL ENGINEERING SKILLS
-- ================================================================
('Structural Analysis', 'Core Technical', 'Beam, Truss, Frame Analysis, Moment Distribution', '["Civil"]', 75),
('Concrete Technology', 'Core Technical', 'Mix Design, Strength Testing, RCC Design', '["Civil"]', 70),
('Geotechnical Engineering', 'Core Technical', 'Soil Mechanics, Foundation Design, Earth Pressure', '["Civil"]', 70),
('Transportation Engineering', 'Core Technical', 'Highway Design, Traffic Engineering, Pavement Design', '["Civil"]', 65),
('Construction Management', 'Applied', 'Project Planning, Cost Estimation, Scheduling, BOQ', '["Civil", "Mechanical"]', 65),
('AutoCAD/STAAD.Pro', 'Tools & Software', 'Drafting, Structural Design Software', '["Civil"]', 70),

-- ================================================================
-- ELECTRICAL & ELECTRONICS SKILLS
-- ================================================================
('Circuit Theory', 'Core Technical', 'KVL, KCL, Network Theorems, AC/DC Analysis', '["Electrical", "ECE"]', 70),
('Digital Electronics', 'Core Technical', 'Logic Gates, Boolean Algebra, Flip-Flops, Microprocessors', '["Electrical", "ECE", "CS"]', 70),
('Power Systems', 'Core Technical', 'Generation, Transmission, Distribution, Load Flow', '["Electrical"]', 70),
('Control Systems', 'Core Technical', 'Feedback, Stability, PID Controllers, Transfer Functions', '["Electrical", "ECE", "Mechanical"]', 70),
('Embedded Systems', 'Core Technical', 'Microcontrollers, Arduino, Raspberry Pi, IoT', '["ECE", "Electrical"]', 70),
('Signal Processing', 'Core Technical', 'Fourier Transform, Filters, Convolution, DSP', '["ECE", "Electrical"]', 70),

-- ================================================================
-- CROSS-FUNCTIONAL SKILLS (ALL BRANCHES)
-- ================================================================
('Engineering Mathematics', 'Foundational', 'Calculus, Linear Algebra, Differential Equations, Probability', '["All"]', 70),
('Technical Communication', 'Applied', 'Report Writing, Presentation, Documentation', '["All"]', 60),
('Problem Solving', 'Applied', 'Analytical Thinking, Debugging, Optimization', '["All"]', 65),
('Project Management', 'Applied', 'Planning, Execution, Team Coordination, Deadlines', '["All"]', 60);
