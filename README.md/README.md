
# SmartPark AI
### AI-Based Smart Parking Violation Assistant

## Project Overview
SmartPark AI is an AI-powered parking compliance assistant that detects parking violations, retrieves relevant parking rules and provides explainable resolution guidance.

## Features
- AI-based parking violation detection
- Semantic search using MiniLM
- Parking rules knowledge base
- Multi-agent system
- Violation explanation engine
- Interactive dashboard
- Parking layout visualization
- Case history management
- SQLite database integration
- Analytics and charts
- CSV and case report export
- System testing module

## Technology Stack
- Python
- Streamlit
- Sentence Transformers
- SQLite
- Plotly
- Pandas
- JSON

## Project Structure
- app_redesigned.py
- src/
- data/
- database/
- requirements.txt
- README.md

## How to Run

Install dependencies:

pip install -r requirements.txt

Run application:

python -m streamlit run app_redesigned.py

## Database
SQLite stores analyzed violation cases and maintains persistent case history.

## Objective
To provide an explainable AI-based solution for identifying parking violations and assisting users with parking compliance.
# 🚗 SmartPark AI – AI-Based Smart Parking Violation Assistant

An intelligent AI-powered parking compliance platform that detects potential parking violations, retrieves relevant parking rules using semantic search, and provides explainable resolution guidance.

🌐 **Live Demo:** https://smartpark-ai-sys.streamlit.app/

💻 **GitHub Repository:** https://github.com/kaurkiran9987/SmartPark-AI

---

## 📌 1. Project Overview

SmartPark AI is an AI-based Smart Parking Violation Assistant designed to simplify parking compliance and help users understand parking regulations.

The system uses Natural Language Processing (NLP), Retrieval-Augmented Generation (RAG)-style semantic retrieval, and a multi-agent approach to analyze user-described parking situations.

It identifies the most relevant parking rule from a structured knowledge base and provides violation details, severity information, and resolution guidance.

The application also maintains case records and presents analytical insights through an interactive dashboard.

---

## 🎯 2. Problem Statement

Parking violations are common in urban areas due to a lack of awareness about parking regulations and difficulty understanding applicable rules.

Traditional parking management systems often provide limited explanations about violations and their possible resolutions.

SmartPark AI addresses this problem by providing an intelligent platform that helps users understand parking violations through semantic rule retrieval and explainable AI-based guidance.

---

## 🎯 3. Project Objectives

- Develop an AI-powered parking violation detection assistant.
- Identify relevant parking regulations using semantic similarity.
- Implement a structured parking rules knowledge base.
- Provide understandable violation explanations.
- Implement a multi-agent system for user and enforcement guidance.
- Store and manage parking violation case records.
- Provide interactive analytics and visualization.
- Develop an accessible web-based dashboard.

---

## ✨ 4. Key Features

### 🤖 AI-Based Violation Detection
- Accepts parking situations in natural language.
- Uses Sentence Transformers for semantic understanding.
- Retrieves the most relevant parking rule.
- Displays similarity scores and detected violation details.

### 📚 Parking Rules Knowledge Base
Includes seven structured parking rules:

1. No-Parking Zone
2. Emergency Access Obstruction
3. Accessible Parking Violation
4. Parking Time Limit Violation
5. Wrong Direction Parking
6. Double Parking
7. Blocked Driveway

### 🧠 RAG-Based Semantic Retrieval
- Uses the all-MiniLM-L6-v2 sentence-transformer model.
- Converts parking rules and user queries into embeddings.
- Compares semantic similarity.
- Retrieves the best-matching rule.

### 🤝 Multi-Agent System
The application includes:

- **User Agent:** Provides guidance from the user's perspective.
- **Enforcement Agent:** Provides enforcement-related guidance.

### 💡 Explainable AI
Provides understandable explanations of detected violations and their corresponding parking rules.

### 📊 Interactive Dashboard
- Total parking rules
- Cases analyzed
- High-severity cases
- Average similarity score
- Interactive charts and analytics

### 🗂️ Case History Management
- Stores analyzed cases using SQLite.
- Displays saved violation records.
- Supports searching and filtering.
- Provides individual case reports.
- Supports CSV export.

### 🧪 System Testing
Includes functional checks for:
- Knowledge base loading
- Semantic retrieval
- AI agent functionality
- Explanation engine
- SQLite database connection
- Case history loading

---

## 🏗️ 5. System Architecture

The application follows this workflow:

1. **User Input:** User describes a parking situation.
2. **Semantic Processing:** Sentence Transformer converts the query into an embedding.
3. **Rule Retrieval:** Semantic similarity identifies the most relevant parking rule.
4. **Violation Detection:** The system selects the best-matching rule.
5. **Multi-Agent Processing:** User Agent and Enforcement Agent provide guidance.
6. **Explanation Engine:** Generates an understandable explanation.
7. **Database Storage:** Analyzed cases are stored using SQLite.
8. **Dashboard Analytics:** Results are displayed through interactive visualizations.

---

## 🛠️ 6. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application and dashboard |
| Sentence Transformers | Semantic text embeddings |
| all-MiniLM-L6-v2 | NLP embedding model |
| PyTorch | Machine learning framework |
| SQLite | Case record storage |
| JSON | Parking rules knowledge base |
| Plotly | Interactive charts |
| Pandas | Data handling and CSV export |
| NumPy | Numerical operations |
| Git & GitHub | Version control and project hosting |
| Streamlit Community Cloud | Application deployment |

---

## 📂 7. Project Structure

```text
SmartPark-AI/
│
├── app_redesigned.py
├── app_odd.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── parking_rules.json
│
├── src/
│   ├── __init__.py
│   ├── rag_engine.py
│   ├── agent_engine.py
│   └── explanation_engine.py
│
├── database/
│   └── smartpark.db
│
└── venv/
```

Note: The virtual environment and local database file should not be committed to GitHub. The database is created by the application when required.

---

## ⚙️ 8. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/kaurkiran9987/SmartPark-AI.git
```

### Step 2: Navigate to the Project Folder

```bash
cd SmartPark-AI
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

For Windows:

```powershell
venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python -m streamlit run app_redesigned.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

---

## 🧪 9. Testing

The project includes a dedicated System Testing module to verify important application components.

The testing module checks:

- Parking rules loading.
- Semantic retrieval functionality.
- Violation detection.
- User and Enforcement Agent functionality.
- Explanation generation.
- SQLite database connectivity.
- Case history loading.

All currently implemented system test cases have passed in the local project testing environment.

---

## 📈 10. Expected Outcomes

SmartPark AI provides:

- Automated identification of potentially relevant parking violations.
- Relevant parking rule retrieval.
- Explainable parking compliance guidance.
- Multi-agent responses.
- Organized case management.
- Interactive analytical insights.

---

## 🔮 11. Future Scope

The project can be extended through:

- Real-time parking monitoring.
- Computer vision-based vehicle and parking detection.
- Integration with smart parking sensors.
- GPS-based parking zone identification.
- Integration with official parking regulation databases.
- Persistent cloud database integration.
- Multilingual user interaction.
- Mobile application development.

---

## ⚠️ 12. Limitations

- The current system primarily relies on user-provided text descriptions.
- Rule detection depends on semantic similarity and the available knowledge base.
- Similarity scores do not represent guaranteed detection accuracy.
- The system provides informational guidance, not official legal decisions.
- Database persistence on cloud hosting depends on the configured storage environment.

---

## 👩‍💻 13. Developer

**Kiranjeet Kaur**

B.Tech – Computer Science and Engineering  
Specialization: Artificial Intelligence and Machine Learning

GitHub: https://github.com/kaurkiran9987

LinkedIn: www.linkedin.com/in/kiran-kaur09

---

## 📜 14. Conclusion

SmartPark AI demonstrates how Artificial Intelligence, Natural Language Processing, semantic retrieval, and multi-agent systems can be combined to develop an intelligent parking compliance assistant.

The platform aims to improve parking rule awareness, simplify violation understanding, and provide explainable resolution guidance through an interactive web application.

**SmartPark AI – Smarter Parking Decisions. Clearer Rule Guidance.** 🚗