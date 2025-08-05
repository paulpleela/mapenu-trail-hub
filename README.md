# 18M: Measuring Rolling Hills in Trail Running: Towards Olympic-Grade Precision
Data Science, Machine Learning, Scientific Computing, Computer Systems, Software Design, User Experience Design
Geomatics
Surveying
Signal Processing
Spots Analytics
Mentor
UQ Health & Rehabilitation Sciences

Problem Space/Domain
Trail running is gaining momentum worldwide as a competitive sport and is currently under consideration for inclusion in Brisbane 2032 Olympic and Paralympic Games. However, the measurement and classification of trail courses remain inconsistent and imprecise. Traditional GPS-based methods often underestimate total distance and effort, particularly in segments with “rolling hills”. These short, frequent undulations are common in real-world trails, especially on erosion-controlled paths like those found in Mt Coot-tha, Brisbane. These terrain patterns, while subtle, have a significant impact on trail running biomechanics and physiology. Yet, they are often smoothed out or ignored by current geomatic tools, resulting in flawed distance estimates and incomplete trail characterization. This presents a major challenge for any future regulation of the sport, where precise, reproducible trail certification will be essential for fairness and comparability across events. This project sits at the intersection of geomatics, signal processing, and sports science. It aims to explore how to digitally measure natural terrain with enough precision to detect these rolling hill patterns.

Project Brief
This project aims to develop a system capable of measuring, identifying and classifying “rolling hills” (short, frequent undulations in trail segments) using geospatial data from GNSS devices and/or publicly available sources such as Lidar point clouds or digital terrain models. The project focuses on designing a reproducible and scalable method to measure, detect, and characterize micro-oscillations in elevation profiles, particularly in trails that appear to have continuous slope but include hidden fluctuations. These patterns are commonly found on erosion-controlled paths in natural settings like Mt Coot-tha and are highly relevant for accurate course certification in competitive and Olympic-level trail running. The outcome should support trail classification and trail difficulty estimations. Multiple approaches to measuring, analysing, classifying, and visualizing the terrain are encouraged, leaving room for creative and technical exploration.

Success Criteria
Identifies and Classifies Rolling Hill Patterns in Trail Elevation Data
The system detects human-scale undulations (‘rolling hiils’) using geospatial elevation data (e.g. GNSS, LiDAR, DTM) and classifies them in a way that reflections meaningful trail features relevant to difficulty, certification, and course design.

Validates Detection Method on Real Trail Segments
The prototype is tested on real-world trail environments, such as Mt Coot-tha, with results validated through field measurements or expert observations. Identified patterns align with physically noticeable or biomechanically significant terrain variations.

Supports Reproducible and Scalable Terrain Analysis
The method can be applied across different trail segments with minimal adjustment, producing consistent outputs. This demonstrates its potential for use in standardised trail assessment or certification processes.

Communicates Terrain Complexity Through Clear Visual Outputs
The system presents elevation features and rolling hill patterns through intuitive visualisations or summary metrics, supporting interpretations by stakeholders such as certifiers, race organisers, or athletes.

Technologies, Techniques to Consider
RTKLIB (SPP, PPK, RTK, DGNSS)
Wearables GNSS receivers
Professional GNSS receivers (e.g. dual-frequency systems)
RINEX data and ephemeris files
LiDAR datasets
Digital Elevation Models
Satellite imagery
Geographic Information Systems: R, Python or QGIS
Signal processing
Image processing
Data fusion
Geomatics
Recommended Skills/Knowledge to have or develop
Recommended: Algebra and calculus, programming skills, problem solving.
To develop: Geomatics, fast prototyping, field work.
Related References / Documents / Materials
Pagneux, E., Sturludóttir, E., & Ólafsdóttir, R. (2023). Modelling of recreational trails in mountainous areas: An analysis of sensitivity to slope data resolution. Applied Geography, 103112. https://www.sciencedirect.com/science/article/pii/S0143622823002436
World Athletics & AIMS. (2023). The Measurement of Road Race Courses. World Athletics/AIMS. https://media.aws.iaaf.org/competitioninfo/2023%20Course%20Measurement%20Book%20-%20ENG.pdf
Sánchez, R., & Villena, M. (2020). Comparative evaluation of wearable devices for measuring elevation gain in mountain physical activities. Proceedings of the Institution of Mechanical Engineers, Part P: Journal of Sports Engineering and Technology, 234(4), 312–319. https://doi.org/10.1177/1754337120918975
Sánchez, R., Egli, P., Besomi, M., & Truffello, R. (2024). Assessing the impact of Digital Elevation Model resolution on Elevation Gain Estimations in Trail Running. En International Conference on Electrical, Computer and Energy Technologies (ICECET 2024), Sydney, Australia (pp. 1–5). IEEE. https://doi.org/10.1109/ICECET61485.2024.10698606
Sánchez, R., Egli, P. E., Jornet, K., Duggan, M., & Besomi, M. (2025). How fractal complexity distorts distance and elevation gain in trail and mountain running: The case for course measurement standardization. Proceedings of the Institution of Mechanical Engineers, Part P: Journal of Sports Engineering and Technology. https://doi.org/10.1177/17543371251341660
