# StatSkill AI — AI-Enabled Learning & Competency Development Platform

**Prototype for India's Official Statistical System (MoSPI)**  
*Smart India Hackathon 2026 Project Prototype*

---

## 🌟 Project Overview

**StatSkill AI** is an AI-powered learning and competency management dashboard built for officers and analysts within India's Official Statistical System (Ministry of Statistics and Programme Implementation - MoSPI). 

The platform enables officers to:
- Track weekly continuous learning progress against cadre targets (e.g. 8.0 hrs/week)
- Identify competency gaps across Statistical, Technical, Digital Governance, and Managerial domains
- Receive personalized, AI-curated learning paths and course recommendations
- Complete interactive lessons, simulations, and assessments
- Observe real-time competency score improvement reflecting back in weekly analytics
- Oversee cadre-wide competency distribution via an executive Administrator portal

---

## 🚀 Live Demo Flow (Hackathon Demonstration)

The prototype includes an interactive step-by-step walkthrough bar at the top of the interface:

1. **Login Page (`/login`)**  
   - Official MoSPI / iGOT portal login with quick one-click "Rahul (Officer)" and "Admin" buttons.
2. **Employee Dashboard (`/dashboard`)**  
   - Header with notifications and officer credentials (Rahul Sharma, Statistical Officer, STAT1024).  
   - 4 KPI cards: Overall Competency (72%), Weekly Learning (6.5 hrs / 8 hrs), Courses Completed (8/12), Current Skill Gaps (4, 2 high priority).  
   - Weekly Learning Activity Chart (Mon–Sun daily breakdown against 1.0 hr/day target).  
   - Skill Progress bars with 4-level color coding (Strong, Developing, Needs Improvement, Critical Gap).  
   - Weekly Achievements & top 3 AI recommendations.
3. **Weekly Progress Page (`/weekly-progress`)** *(Core Evaluation Page)*  
   - Reporting week selector (October 1 – October 7, 2026).  
   - 4 summary metrics: 6.5 / 8 hrs, 4/5 modules, 82% quiz score, +6% improvement.  
   - Daily progress bar chart with hover tooltips and interactive day inspector.  
   - Subject-wise Weekly Learning Breakdown table.  
   - Chronological Weekly Activity Timeline.  
   - "AI Learning Insight" card.
4. **Competency Assessment Page (`/competency-assessment`)**  
   - Four official categories: Statistical Competencies, Technical Competencies, Digital Governance, Behavioural & Managerial.  
   - Granular skill cards with Current score, Required benchmark, and identified Gap.
5. **Skill Gap Analysis Page (`/skill-gap`)**  
   - Multi-axis Radar Chart comparing Current Competency vs. Required Benchmark.  
   - Priority Skill Gaps (High: SQL 61% vs 80%, AI/ML 48% vs 75%; Medium: GIS 55% vs 70%).
6. **Learning Recommendations Page (`/recommendations`)**  
   - AI-Generated sequential roadmap: Step 1 (SQL) → Step 2 (SQL Data) → Step 3 (Python) → Step 4 (Machine Learning).  
   - Course cards with difficulty, duration, progress, and AI recommendation rationale.  
   - Mock integrations for iGOT Karmayogi Bharat and NSSTA Training Academy.
7. **Course Details Page (`/course-details`)**  
   - Interactive module checklist (Modules 1–5). Toggling modules updates course progress in real-time.  
   - "Continue Learning" and "Complete Quiz" buttons.
8. **Quiz / MCQ Page (`/quiz`)**  
   - Interactive MCQ interface for *"Python for Statistical Analysis – Assessment"*.  
   - Question 3: *"Which Python library is commonly used for data manipulation?"* (A. NumPy, B. Pandas, C. Matplotlib, D. TensorFlow).  
   - Real-time scoring (8/10, 80%), detailed explanations, and **live Competency Score Update banner**: Python 68% → 72%, updating the global application state!
9. **Learning History Page (`/history`)**  
   - Searchable, filterable audit trail by Date, Course, Skill Category, and Status.
10. **Officer Profile (`/profile`)**  
    - Educational qualifications (ISI Kolkata), cadre experience, learning preferences, goals, and an in-place profile editor.
11. **Administrator Dashboard (`/admin`)**  
    - Macro KPIs: 1,248 Employees, 934 Active Learners, 68% Average Competency, 74% Training Completion.  
    - 4 Recharts visual analytics: Competency Distribution, Skill Gap Distribution, Weekly Division Hours, Course Completion Rate.  
    - Filterable employee table (by Department, Role, Competency Tier, Training Status) and AI Organizational Insight card.

---

## 🛠️ Technology Stack

- **Frontend**: React 18 with TypeScript
- **Styling**: Tailwind CSS with enterprise government color palette
- **Icons**: Lucide React
- **Data Visualization**: Recharts (Bar Charts, Reference Lines, Radar Charts, Horizontal Bars)
- **Effects**: Canvas Confetti (celebrating assessment milestone completion)
- **Build Tool**: Vite 6

---

## 💻 Running the Application Locally

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The application is accessible at **`http://localhost:3000/`**.
