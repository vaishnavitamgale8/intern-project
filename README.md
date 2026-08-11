# ImpactBridge AI

> *Connecting People. Creating Impact.*

ImpactBridge AI is a community-focused web platform built with Flask that connects volunteers, organizations, and meaningful projects. It features an integrated local AI assistant (powered by Ollama) to guide users, with a seamless fallback to a rule-based engine if the AI is offline.

![ImpactBridge AI Home Screenshot](screenshots/home-screenshot.png)
*(Note: Create a `screenshots` folder and replace `home-screenshot.png` with an actual screenshot of the application.)*

## 🚀 Features

- **Project & Campaign Management:** Easily discover and manage community events and campaigns.
- **Local AI Integration:** Built-in **ImpactBot** powered by Ollama (Llama 3.2) that works entirely offline, providing privacy-friendly assistance.
- **Graceful Fallback:** If Ollama is disabled or offline, ImpactBot automatically switches to a built-in rule-based engine. No crashes.
- **Admin Dashboard:** Manage users, projects, and platform analytics with Chart.js integration.
- **Modern UI:** Built on a custom design system with accessible components, responsive layouts, and a clean, consistent color palette.

## 🛠️ Tech Stack

- **Backend:** Flask, Python 3
- **Database:** SQLite (via SQLAlchemy)
- **Frontend:** Jinja2 Templates, Vanilla HTML/CSS (Custom Design System), Chart.js
- **AI:** Ollama (Llama 3.2 local model)
- **Forms & Auth:** Flask-WTF, Flask-Login

## 📸 Screenshots

### Projects & Campaigns
![Our Projects](screenshots/projects.png)
<img width="1269" height="679" alt="Screenshot 2026-08-11 111502" src="https://github.com/user-attachments/assets/9de1f621-5161-4c77-8131-ecd095f21c50" />

### Become a Volunteer
<img width="1269" height="677" alt="Screenshot 2026-08-11 111451" src="https://github.com/user-attachments/assets/ecac970a-e697-4bc2-a168-61a95d2c1f98" />


### Admin Dashboard
![Admin Dashboard](screenshots/dashboard.png)
<img width="1280" height="676" alt="Screenshot 2026-08-11 111343" src="https://github.com/user-attachments/assets/3b9696aa-c7d9-469e-be66-174df8bf4e3c" />


### Donations Management
![Donations](screenshots/donations.png)
<img width="1280" height="678" alt="Screenshot 2026-08-11 111411 - Copy" src="https://github.com/user-attachments/assets/eef46741-395e-401d-a936-47770a97dda8" />


### User Login
![Login Page](screenshots/login.png)
<img width="1280" height="676" alt="Screenshot 2026-08-11 111428 - Copy" src="https://github.com/user-attachments/assets/4995ae3b-56d5-4336-8096-42379c1167f8" />


## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/impactbridge-ai.git
cd impactbridge-ai
```

### 2. Set up the virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and update variables if needed:
```bash
cp .env.example .env
```
Ensure `OLLAMA_ENABLED=true` in `.env` if you plan to use local AI.

### 5. Initialize the Database
Run the seed script to create tables and populate initial dummy data:
```bash
python seed.py
```

### 6. Start the App
```bash
python run.py
```
Visit `http://localhost:5000` in your browser!

## 🤖 Running Ollama (Optional)
To use the AI features, make sure Ollama is installed and running on your machine:
```bash
ollama run llama3.2
```
If you skip this step, ImpactBridge AI will smoothly fall back to a rule-based mode.

## 🎨 Design System
The visual aesthetics, components, colors, and typography follow our strict design guidelines. See `DESIGN.md` for a complete breakdown of the UI system.

## 📄 License
This project is licensed under the MIT License.
