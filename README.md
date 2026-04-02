AI-STUDY-ASSISTANT
AI-powered study assistant that helps students learn, summarize, and interact with educational content.

An AI-powered web application designed to enhance student productivity by providing smart learning tools like notes generation, doubt solving, quiz creation, and study planning — all in one platform.

Features:
->AI-Powered Tools
* Generate notes from any topic using AI
* Convert PDF documents into structured notes
* Ask doubts and get instant AI responses
* Generate quizzes based on topics

->Productivity Tools
* Study Planner (Add, complete, delete tasks)
* Study Hours Tracker (auto tracking)
* Recent Activity tracking system

->User Features
* User Authentication (Login/Register popup)
* Personalized Dashboard
* Save and manage notes
* Quiz performance tracking

->UI/UX
* Modern responsive design (Mobile + Tablet + Desktop)
* Smooth animations & transitions
* Smart loading system with dynamic messages
* Flash notifications (top-centered)
* Chat-like UI for doubt solving

Tech Stack: 
->Frontend
* HTML5
* CSS3 (Custom + Responsive Design)
* JavaScript (Vanilla JS)

->Backend
* Python (Flask)

->Database
* SQLite
* SQLAlchemy ORM

->AI Integration
* Google Gemini API

Project Structure:
->AI-Study-Assistant/
  │
  ├── static/
  │   ├── css/
  │   ├── js/
  │   └── images/
  │
  ├── templates/
  │   ├── base.html
  │   ├── dashboard.html
  │   ├── generate_notes.html
  │   ├── saved_notes.html
  │   ├── ask_doubt.html
  │   ├── quiz.html
  │   ├── planner.html
  │   └── ...
  │
  ├── models.py
  ├── app.py
  |__ config.py
  ├── services/
  │   └── gemini_services.py
  |   |___ pdf_service.py
  │
  ├── .env
  ├── .gitignore
  └── README.md

Environment Variables:
*GEMINI_API_KEY => API key of Google Gemini AI
*SECRET_KEY => Flask secret key

Developed by sayyamnegi19
