import {
  UserProfile,
  CompetencyScore,
  DayProgress,
  WeeklyBreakdownItem,
  ActivityTimelineItem,
  Course,
  Quiz,
  LearningHistoryRecord,
  AdminEmployee
} from '../types';

export const initialUserProfile: UserProfile = {
  name: 'Rahul Sharma',
  employeeId: 'STAT1024',
  department: 'Data Analytics Division',
  designation: 'Statistical Officer',
  jobRole: 'Official Statistics Analyst & Data Modeler',
  experience: '4 years',
  education: 'M.Sc. Statistics (Indian Statistical Institute, Kolkata)',
  email: 'rahul.sharma@mospi.gov.in',
  phone: '+91 98765 43210',
  location: 'MoSPI Headquarters, Sardar Patel Bhawan, New Delhi',
  learningPreferences: [
    'Self-paced interactive modules',
    'Hands-on statistical coding labs (Python/R)',
    'Practical case studies from National Sample Surveys',
    'Weekend micro-assessments'
  ],
  currentGoals: [
    'Achieve 80%+ proficiency in SQL data pipelines for Census & Survey records',
    'Upskill in AI/ML predictive modeling for agricultural price index forecasting',
    'Complete National Statistical Systems Training Academy (NSSTA) Certification',
    'Consistently maintain 8+ learning hours per week'
  ]
};

export const initialSkills: CompetencyScore[] = [
  {
    name: 'Statistical Analysis',
    current: 82,
    required: 85,
    gap: 3,
    category: 'Statistical',
    level: 'strong',
    trend: '+4% this month'
  },
  {
    name: 'Python',
    current: 68,
    required: 80,
    gap: 12,
    category: 'Technical',
    level: 'developing',
    trend: '+7% this week'
  },
  {
    name: 'Data Visualization',
    current: 74,
    required: 80,
    gap: 6,
    category: 'Technical',
    level: 'developing',
    trend: '+5% this month'
  },
  {
    name: 'SQL',
    current: 61,
    required: 80,
    gap: 19,
    category: 'Technical',
    level: 'needs-improvement',
    trend: '+2% this week'
  },
  {
    name: 'AI / Machine Learning',
    current: 48,
    required: 75,
    gap: 27,
    category: 'Technical',
    level: 'critical-gap',
    trend: '+1% this month'
  },
  {
    name: 'GIS',
    current: 55,
    required: 70,
    gap: 15,
    category: 'Technical',
    level: 'needs-improvement',
    trend: '+3% this month'
  },
];

export const allCompetenciesByCategory: Record<string, CompetencyScore[]> = {
  'Statistical Competencies': [
    { name: 'Survey Design', current: 85, required: 85, gap: 0, category: 'Statistical', level: 'strong' },
    { name: 'Sampling Techniques', current: 80, required: 85, gap: 5, category: 'Statistical', level: 'developing' },
    { name: 'National Accounts & GDP Estimation', current: 75, required: 80, gap: 5, category: 'Statistical', level: 'developing' },
    { name: 'Data Quality & Validation', current: 78, required: 80, gap: 2, category: 'Statistical', level: 'developing' },
    { name: 'Index Numbers (CPI/IIP)', current: 84, required: 85, gap: 1, category: 'Statistical', level: 'strong' },
  ],
  'Technical Competencies': [
    { name: 'Python for Statistical Computing', current: 68, required: 80, gap: 12, category: 'Technical', level: 'developing' },
    { name: 'R Programming', current: 72, required: 75, gap: 3, category: 'Technical', level: 'developing' },
    { name: 'SQL & Database Queries', current: 61, required: 80, gap: 19, category: 'Technical', level: 'needs-improvement' },
    { name: 'Data Visualization & BI (PowerBI/Tableau)', current: 74, required: 80, gap: 6, category: 'Technical', level: 'developing' },
    { name: 'AI / Machine Learning for Official Data', current: 48, required: 75, gap: 27, category: 'Technical', level: 'critical-gap' },
    { name: 'GIS & Spatial Data Analysis', current: 55, required: 70, gap: 15, category: 'Technical', level: 'needs-improvement' },
  ],
  'Digital Governance': [
    { name: 'Cybersecurity & Data Privacy', current: 70, required: 80, gap: 10, category: 'Digital Governance', level: 'needs-improvement' },
    { name: 'Digital Signatures & e-Office', current: 88, required: 80, gap: 0, category: 'Digital Governance', level: 'strong' },
    { name: 'APIs & Open Data Portals (NDAP)', current: 64, required: 75, gap: 11, category: 'Digital Governance', level: 'needs-improvement' },
    { name: 'Cloud Computing Infrastructure (MeghRaj)', current: 58, required: 70, gap: 12, category: 'Digital Governance', level: 'needs-improvement' },
  ],
  'Behavioural & Managerial': [
    { name: 'Leadership & Team Guidance', current: 72, required: 75, gap: 3, category: 'Behavioural & Managerial', level: 'developing' },
    { name: 'Official Communication & Reporting', current: 80, required: 80, gap: 0, category: 'Behavioural & Managerial', level: 'strong' },
    { name: 'Evidence-Based Decision Making', current: 76, required: 80, gap: 4, category: 'Behavioural & Managerial', level: 'developing' },
    { name: 'Project & Survey Timelines Management', current: 71, required: 75, gap: 4, category: 'Behavioural & Managerial', level: 'developing' },
  ]
};

export const initialWeeklyDays: DayProgress[] = [
  { day: 'Monday', shortDay: 'Mon', date: 'Oct 01', hours: 0.8, targetHours: 1.0, completedTasks: ['Completed Python Module 3: Functions & Lambdas'] },
  { day: 'Tuesday', shortDay: 'Tue', date: 'Oct 02', hours: 1.2, targetHours: 1.0, completedTasks: ['Completed Python Data Analysis Quiz (85%)', 'Data Cleaning Exercise'] },
  { day: 'Wednesday', shortDay: 'Wed', date: 'Oct 03', hours: 0.6, targetHours: 1.0, completedTasks: ['Watched Data Visualization Module 2: Matplotlib & Seaborn'] },
  { day: 'Thursday', shortDay: 'Thu', date: 'Oct 04', hours: 1.5, targetHours: 1.0, completedTasks: ['Completed SQL Module 1: Select, Where & Aggregations', 'Hands-on query sandbox'] },
  { day: 'Friday', shortDay: 'Fri', date: 'Oct 05', hours: 1.0, targetHours: 1.0, completedTasks: ['Scored 85% in Statistics Methods Quiz', 'Reviewed feedback report'] },
  { day: 'Saturday', shortDay: 'Sat', date: 'Oct 06', hours: 0.9, targetHours: 1.0, completedTasks: ['Completed recommended iGOT Karmayogi video lecture'] },
  { day: 'Sunday', shortDay: 'Sun', date: 'Oct 07', hours: 0.5, targetHours: 1.0, completedTasks: ['Reviewed weekly progress & next week recommendation path'] },
];

export const initialWeeklyBreakdown: WeeklyBreakdownItem[] = [
  { id: 'wb-1', course: 'Python for Statistics', timeSpent: '2.5 hrs', hoursSpent: 2.5, progress: 85, category: 'Technical' },
  { id: 'wb-2', course: 'Data Visualization with Seaborn', timeSpent: '1.5 hrs', hoursSpent: 1.5, progress: 70, category: 'Technical' },
  { id: 'wb-3', course: 'SQL Fundamentals for Officers', timeSpent: '1.5 hrs', hoursSpent: 1.5, progress: 60, category: 'Technical' },
  { id: 'wb-4', course: 'Statistical Methods & Survey Design', timeSpent: '1.0 hrs', hoursSpent: 1.0, progress: 90, category: 'Statistical' },
];

export const initialActivityTimeline: ActivityTimelineItem[] = [
  { id: 'act-1', day: 'Monday', date: '01 Oct 2026', title: 'Completed Python Module 3: Vectorized Computations', type: 'module', completed: true, duration: '48 mins' },
  { id: 'act-2', day: 'Tuesday', date: '02 Oct 2026', title: 'Completed Python Statistical Assessment Quiz', type: 'quiz', completed: true, score: '85%', duration: '25 mins' },
  { id: 'act-3', day: 'Wednesday', date: '03 Oct 2026', title: 'Watched Data Visualization Module 2', type: 'module', completed: true, duration: '36 mins' },
  { id: 'act-4', day: 'Thursday', date: '04 Oct 2026', title: 'Completed SQL Module 1: Filtering & Joins', type: 'module', completed: true, duration: '1 hr 30 mins' },
  { id: 'act-5', day: 'Friday', date: '05 Oct 2026', title: 'Scored 85% in Official Statistics Quiz', type: 'quiz', completed: true, score: '85%', duration: '30 mins' },
  { id: 'act-6', day: 'Saturday', date: '06 Oct 2026', title: 'Completed Recommended NSSTA Micro-Module', type: 'training', completed: true, duration: '54 mins' },
  { id: 'act-7', day: 'Sunday', date: '07 Oct 2026', title: 'Weekly Review and Reflection', type: 'module', completed: true, duration: '30 mins' },
];

export const sampleCourses: Course[] = [
  {
    id: 'course-python-stats',
    title: 'Python for Statistical Analysis',
    instructor: 'Dr. Anita Roy & NSSTA Faculty',
    organization: 'National Statistical Systems Training Academy',
    duration: '2.5 hours',
    difficulty: 'Beginner → Intermediate',
    skillCategory: 'Python',
    progress: 68,
    rating: 4.8,
    totalModules: 5,
    completedModules: 3,
    recommendationReason: 'Recommended because Python is high-priority for upcoming automated surveys and data validation.',
    priority: 'High',
    targetGapReduction: 'Reduces Python gap from 12% to 4%',
    description: 'Master Python libraries for official statistics: NumPy array operations, Pandas DataFrames, descriptive statistics calculations, and automated data validation workflows.',
    modules: [
      { id: 1, title: 'Introduction to Python for Statistical Officers', duration: '25 mins', completed: true, type: 'video' },
      { id: 2, title: 'Data Types, Lists, and NumPy Numerical Arrays', duration: '30 mins', completed: true, type: 'video' },
      { id: 3, title: 'Pandas DataFrames & Statistical Operations', duration: '40 mins', completed: true, type: 'interactive' },
      { id: 4, title: 'Missing Data Imputation & Outlier Detection', duration: '35 mins', completed: false, type: 'reading' },
      { id: 5, title: 'Automating Weekly Reports with Python Scripts', duration: '20 mins', completed: false, type: 'interactive' },
    ]
  },
  {
    id: 'course-sql-analytics',
    title: 'SQL for Data Analytics & Official Surveys',
    instructor: 'Shri Vikram Sen, Senior Data Architect',
    organization: 'Digital India & MoSPI Analytics Wing',
    duration: '3 hours',
    difficulty: 'Beginner → Intermediate',
    skillCategory: 'SQL',
    progress: 40,
    rating: 4.9,
    totalModules: 5,
    completedModules: 2,
    recommendationReason: 'Recommended because SQL is currently your highest competency gap (61% current vs 80% target).',
    priority: 'High',
    targetGapReduction: 'Reduces SQL gap from 19% to 7%',
    description: 'Learn relational queries, multi-table joins, subqueries, window functions, and indexing to aggregate large-scale national census and survey databases.',
    modules: [
      { id: 1, title: 'Relational Database Concepts in Government Records', duration: '30 mins', completed: true, type: 'video' },
      { id: 2, title: 'SELECT, WHERE, and Aggregate Functions (SUM, AVG, COUNT)', duration: '40 mins', completed: true, type: 'interactive' },
      { id: 3, title: 'INNER, LEFT, and FULL OUTER JOINS on Survey IDs', duration: '35 mins', completed: false, type: 'interactive' },
      { id: 4, title: 'GROUP BY, HAVING, and Window Partition Functions', duration: '45 mins', completed: false, type: 'reading' },
      { id: 5, title: 'SQL Query Optimization for Large Datasets', duration: '30 mins', completed: false, type: 'interactive' },
    ]
  },
  {
    id: 'course-intro-ml',
    title: 'Introduction to Machine Learning in Public Policy',
    instructor: 'Prof. K. Subramanian, IIT Delhi & NITI Aayog Fellow',
    organization: 'iGOT Karmayogi Bharat',
    duration: '4 hours',
    difficulty: 'Intermediate',
    skillCategory: 'AI / Machine Learning',
    progress: 20,
    rating: 4.7,
    totalModules: 6,
    completedModules: 1,
    recommendationReason: 'Recommended to address your 27% critical gap in AI/ML for automated trend forecasting.',
    priority: 'Medium',
    targetGapReduction: 'Reduces AI/ML gap from 27% to 14%',
    description: 'Supervised vs unsupervised learning, scikit-learn pipelines, regression models for economic indicators, and ethical AI guidelines in government administration.',
    modules: [
      { id: 1, title: 'Foundations of AI/ML in Official Statistics', duration: '35 mins', completed: true, type: 'video' },
      { id: 2, title: 'Data Preprocessing and Feature Engineering', duration: '45 mins', completed: false, type: 'interactive' },
      { id: 3, title: 'Linear & Logistic Regression for Public Trends', duration: '40 mins', completed: false, type: 'video' },
      { id: 4, title: 'Decision Trees and Random Forests', duration: '45 mins', completed: false, type: 'interactive' },
      { id: 5, title: 'Time Series Forecasting with ML', duration: '45 mins', completed: false, type: 'reading' },
      { id: 6, title: 'Ethical AI & Bias Mitigation in Govt Data', duration: '30 mins', completed: false, type: 'video' },
    ]
  },
  {
    id: 'course-gis-mapping',
    title: 'GIS and Spatial Data Analysis for Field Surveys',
    instructor: 'Survey of India & MoSPI Geospatial Cell',
    organization: 'National Remote Sensing Centre (NRSC)',
    duration: '2.5 hours',
    difficulty: 'Intermediate',
    skillCategory: 'GIS',
    progress: 55,
    rating: 4.6,
    totalModules: 4,
    completedModules: 2,
    recommendationReason: 'Recommended to strengthen your GIS capability (55% vs 70% required) for geo-tagging survey units.',
    priority: 'Medium',
    targetGapReduction: 'Reduces GIS gap from 15% to 5%',
    description: 'Geospatial fundamentals, shapefiles, QGIS, spatial overlays, and thematic map creation for administrative district surveys.',
    modules: [
      { id: 1, title: 'Introduction to Spatial Coordinates & CRS', duration: '35 mins', completed: true, type: 'video' },
      { id: 2, title: 'Working with Vector Shapefiles and GeoJSON', duration: '45 mins', completed: true, type: 'interactive' },
      { id: 3, title: 'Spatial Joins with Administrative Boundaries', duration: '40 mins', completed: false, type: 'interactive' },
      { id: 4, title: 'Creating Choropleth District Maps', duration: '30 mins', completed: false, type: 'reading' },
    ]
  }
];

export const sampleQuiz: Quiz = {
  id: 'quiz-python-stats',
  courseId: 'course-python-stats',
  title: 'Python for Statistical Analysis – Competency Assessment',
  subject: 'Official Statistics Computing & Python',
  relatedSkill: 'Python',
  timeLimitMinutes: 15,
  questions: [
    {
      id: 1,
      question: 'Which of the following data structures in Python is immutable?',
      options: [
        { key: 'A', text: 'List' },
        { key: 'B', text: 'Tuple' },
        { key: 'C', text: 'Dictionary' },
        { key: 'D', text: 'Set' }
      ],
      correctAnswer: 'B',
      explanation: 'Tuples are immutable sequences in Python, meaning their elements cannot be modified once created, making them ideal for constant statistical survey metadata.'
    },
    {
      id: 2,
      question: 'In NumPy, which attribute is used to inspect the dimensionality or shape of an array?',
      options: [
        { key: 'A', text: 'arr.dim' },
        { key: 'B', text: 'arr.size()' },
        { key: 'C', text: 'arr.shape' },
        { key: 'D', text: 'arr.length' }
      ],
      correctAnswer: 'C',
      explanation: 'The .shape attribute in NumPy returns a tuple representing the dimensions of the array (e.g. (rows, columns)).'
    },
    {
      id: 3,
      question: 'Which Python library is commonly used for data manipulation and tabular data analysis in official statistics?',
      options: [
        { key: 'A', text: 'NumPy' },
        { key: 'B', text: 'Pandas' },
        { key: 'C', text: 'Matplotlib' },
        { key: 'D', text: 'TensorFlow' }
      ],
      correctAnswer: 'B',
      explanation: 'Pandas is the primary library for data manipulation and analysis, offering DataFrame objects with labeled axes and high-performance aggregate operations.'
    },
    {
      id: 4,
      question: 'In Pandas, which method is used to return summary descriptive statistics such as mean, standard deviation, and quartiles?',
      options: [
        { key: 'A', text: 'df.summary()' },
        { key: 'B', text: 'df.info()' },
        { key: 'C', text: 'df.describe()' },
        { key: 'D', text: 'df.stats()' }
      ],
      correctAnswer: 'C',
      explanation: 'df.describe() generates descriptive statistics that summarize the central tendency, dispersion, and shape of a dataset distribution.'
    },
    {
      id: 5,
      question: 'How do you filter a Pandas DataFrame "df" for rows where column "State" is equal to "Maharashtra"?',
      options: [
        { key: 'A', text: 'df.filter(State == "Maharashtra")' },
        { key: 'B', text: 'df[df["State"] == "Maharashtra"]' },
        { key: 'C', text: 'df.select("State" = "Maharashtra")' },
        { key: 'D', text: 'df.where("State", "Maharashtra")' }
      ],
      correctAnswer: 'B',
      explanation: 'Boolean indexing using df[df["State"] == "Maharashtra"] extracts matching rows in Pandas.'
    },
    {
      id: 6,
      question: 'Which Pandas function is most appropriate to detect missing values (NaN) in a survey dataset?',
      options: [
        { key: 'A', text: 'df.isna() or df.isnull()' },
        { key: 'B', text: 'df.empty()' },
        { key: 'C', text: 'df.zero()' },
        { key: 'D', text: 'df.void()' }
      ],
      correctAnswer: 'A',
      explanation: 'df.isna() or df.isnull() returns a boolean mask indicating where values are missing or NaN.'
    },
    {
      id: 7,
      question: 'Which method in Pandas calculates the arithmetic mean along a specified axis?',
      options: [
        { key: 'A', text: 'df.average()' },
        { key: 'B', text: 'df.mean()' },
        { key: 'C', text: 'df.median()' },
        { key: 'D', text: 'df.arithmetic()' }
      ],
      correctAnswer: 'B',
      explanation: 'df.mean() calculates the mean of numerical values along axis 0 (rows) or axis 1 (columns).'
    },
    {
      id: 8,
      question: 'Which visualization library in Python is built on top of Matplotlib and integrates closely with Pandas data structures?',
      options: [
        { key: 'A', text: 'Seaborn' },
        { key: 'B', text: 'Pygame' },
        { key: 'C', text: 'Django' },
        { key: 'D', text: 'Flask' }
      ],
      correctAnswer: 'A',
      explanation: 'Seaborn is a statistical data visualization library built on top of Matplotlib that provides a high-level interface for drawing informative statistical graphics.'
    },
    {
      id: 9,
      question: 'In SQL, which clause is used to filter records resulting from a GROUP BY aggregate calculation?',
      options: [
        { key: 'A', text: 'WHERE' },
        { key: 'B', text: 'HAVING' },
        { key: 'C', text: 'ORDER BY' },
        { key: 'D', text: 'LIMIT' }
      ],
      correctAnswer: 'B',
      explanation: 'The HAVING clause was added to SQL because the WHERE keyword cannot be used with aggregate functions.'
    },
    {
      id: 10,
      question: 'What is the primary purpose of a train-test split in machine learning predictive modeling for official economic trends?',
      options: [
        { key: 'A', text: 'To compress dataset storage size' },
        { key: 'B', text: 'To evaluate model generalization on unseen data and prevent overfitting' },
        { key: 'C', text: 'To sort records chronologically' },
        { key: 'D', text: 'To convert categorical text to numbers' }
      ],
      correctAnswer: 'B',
      explanation: 'Splitting data into training and test sets ensures that model performance is measured objectively on unseen data, mitigating overfitting.'
    }
  ]
};

export const sampleHistory: LearningHistoryRecord[] = [
  { id: 'hist-1', date: '02 Oct 2026', course: 'Python Statistics', activity: 'Module', duration: '45 min', score: '—', status: 'Completed', skill: 'Python' },
  { id: 'hist-2', date: '03 Oct 2026', course: 'Python Statistics', activity: 'Quiz', duration: '20 min', score: '85%', status: 'Completed', skill: 'Python' },
  { id: 'hist-3', date: '04 Oct 2026', course: 'SQL Fundamentals', activity: 'Module', duration: '60 min', score: '—', status: 'Completed', skill: 'SQL' },
  { id: 'hist-4', date: '05 Oct 2026', course: 'Data Visualization', activity: 'Module', duration: '50 min', score: '—', status: 'Completed', skill: 'Data Visualization' },
  { id: 'hist-5', date: '06 Oct 2026', course: 'Statistics Quiz', activity: 'Quiz', duration: '30 min', score: '82%', status: 'Completed', skill: 'Statistical Analysis' },
  { id: 'hist-6', date: '28 Sep 2026', course: 'National Survey Design', activity: 'Assessment', duration: '40 min', score: '88%', status: 'Completed', skill: 'Statistical Analysis' },
  { id: 'hist-7', date: '25 Sep 2026', course: 'Digital Governance & Cybersecurity', activity: 'Module', duration: '35 min', score: '—', status: 'Completed', skill: 'Digital Governance' },
  { id: 'hist-8', date: '22 Sep 2026', course: 'GIS Spatial Data Analysis', activity: 'Interactive Lab', duration: '55 min', score: '78%', status: 'Completed', skill: 'GIS' },
];

export const sampleAdminEmployees: AdminEmployee[] = [
  { id: 'emp-1', name: 'Rahul Sharma', employeeId: 'STAT1024', department: 'Data Analytics Division', role: 'Statistical Officer', competency: 72, skillGapsCount: 4, weeklyHours: 6.5, status: 'On Track' },
  { id: 'emp-2', name: 'Priyanka Sen', employeeId: 'STAT1032', department: 'National Accounts Division (NAD)', role: 'Senior Statistical Officer', competency: 78, skillGapsCount: 2, weeklyHours: 8.2, status: 'Exceeding Target' },
  { id: 'emp-3', name: 'Amitabh Verma', employeeId: 'STAT0981', department: 'National Sample Survey Office (NSSO)', role: 'Assistant Director', competency: 64, skillGapsCount: 5, weeklyHours: 5.0, status: 'Needs Attention' },
  { id: 'emp-4', name: 'Sunita Meena', employeeId: 'STAT1140', department: 'Economic Statistics Division', role: 'Statistical Officer', competency: 75, skillGapsCount: 3, weeklyHours: 7.5, status: 'On Track' },
  { id: 'emp-5', name: 'Karthik Raja', employeeId: 'STAT1055', department: 'Price Statistics Division', role: 'Statistical Investigator', competency: 69, skillGapsCount: 4, weeklyHours: 6.0, status: 'On Track' },
  { id: 'emp-6', name: 'Deepa Narayanan', employeeId: 'STAT1201', department: 'Field Operations Division (FOD)', role: 'Field Statistical Officer', competency: 59, skillGapsCount: 6, weeklyHours: 4.2, status: 'Needs Attention' },
  { id: 'emp-7', name: 'Rajesh Mukherjee', employeeId: 'STAT0923', department: 'Data Analytics Division', role: 'Senior Director', competency: 88, skillGapsCount: 1, weeklyHours: 8.5, status: 'Exceeding Target' },
  { id: 'emp-8', name: 'Sneha Patel', employeeId: 'STAT1308', department: 'Computer Centre (MoSPI)', role: 'Data Systems Specialist', competency: 81, skillGapsCount: 2, weeklyHours: 7.8, status: 'On Track' },
];

export const mockTrainingPrograms = [
  {
    id: 'prog-1',
    provider: 'iGOT Karmayogi Bharat',
    badge: 'National Platform',
    title: 'Mission Karmayogi: Integrated Competency Framework for Statistical Officers',
    duration: '6 Weeks (Self-paced)',
    enrollment: 'Open to All Cadre Officers',
    status: 'Recommended for Q4',
    url: 'https://igotkarmayogi.gov.in',
    skills: ['Evidence-Based Policy', 'Public Governance', 'Digital Ethics']
  },
  {
    id: 'prog-2',
    provider: 'NSSTA Greater Noida',
    badge: 'Premier Academy',
    title: 'NSSTA Specialized Programme on Modernization of Official Statistics & Big Data',
    duration: '2 Weeks Residential / Hybrid',
    enrollment: 'Next Batch: 15 Nov 2026',
    status: 'Nomination Pending Approval',
    url: 'https://mospi.gov.in/nssta',
    skills: ['National Accounts', 'Sample Survey Quality', 'Python/R Lab']
  },
  {
    id: 'prog-3',
    provider: 'MoSPI Analytics Cell & NITI Aayog',
    badge: 'Hands-on Workshop',
    title: 'Hands-on Workshop: Geospatial Integration & National Data Analytics Platform (NDAP)',
    duration: '3 Days Intensive',
    enrollment: '50 Seats Available',
    status: 'Recommended for Gap Closure (GIS)',
    url: 'https://ndap.niti.gov.in',
    skills: ['GIS Mapping', 'API Automation', 'District Level Indicators']
  }
];
