🚦 Project Report: AI-Based Adaptive Traffic Signal Control System
1. Project Overview
The AI-Based Adaptive Traffic Signal Control System (ATSC) is an intelligent solution designed to optimize traffic flow in real time using computer vision and machine learning. The system detects vehicle density at intersections using the YOLO (You Only Look Once) object detection model and dynamically adjusts the signal timings to reduce congestion and waiting time.
2. Objectives
• Build an AI-powered traffic management system that adapts signal timings automatically.
• Reduce traffic congestion and fuel wastage by minimizing idle time.
• Integrate real-time traffic simulation (SUMO) and video-based detection for validation.
• Visualize data through a FastAPI dashboard connected with MongoDB Atlas.
3. Tools & Technologies Used
Programming: Python
Machine Learning: YOLOv8 (Ultralytics)
Web Framework: FastAPI
Database: MongoDB Atlas
Simulation: SUMO
Frontend: HTML, CSS, JavaScript
Version Control: GitHub
Environment: Anaconda
4. System Architecture
1. Input Layer – YOLO model detects vehicles from live/recorded video.
2. Processing Layer – YOLO sends vehicle count to FastAPI backend.
3. Decision Layer – Backend adjusts signal timing based on density.
4. Simulation Layer – SUMO simulates intersection & visualizes signals.
5. Storage Layer – MongoDB Atlas stores data for analysis.
6. Frontend – Dashboard displays real-time updates via WebSocket.
5. Implementation Steps
1. Setup YOLOv8 model for vehicle detection.
2. Developed backend using FastAPI integrated with MongoDB Atlas.
3. Configured SUMO for real-time simulation.
4. Built WebSocket for live updates to dashboard.
5. Displayed traffic data on dashboard with real-time visual feedback.
6. Results & Output
• Adaptive control reduced waiting time and congestion.
• SUMO simulation verified dynamic signal timing efficiency.
• MongoDB Atlas stored live traffic logs successfully.
• FastAPI dashboard displayed vehicle count and signal status.
7. Key Learnings
• Implemented AI integration in real-world systems.
• Learned SUMO simulation and WebSocket communication.
• Gained experience with MongoDB Atlas and FastAPI.
• Strengthened backend and cloud integration knowledge.
8. Future Enhancements
• Deploy system with live IoT camera feeds.
• Implement multi-intersection coordination.
9. Acknowledgment
I sincerely thank Infotact Solutions' team for providing me the valuable internship opportunity. This project enhanced my technical knowledge and practical understanding of AI-based systems.
10. Conclusion
The AI-Based Adaptive Traffic Signal Control System demonstrates how AI, computer vision, and simulation tools can create a smart and sustainable urban traffic management system — a significant step toward smart city innovation.
For any query, mail me at aleezafatima1021@gmail.com
