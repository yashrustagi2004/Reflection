import os
from pymongo import MongoClient
# ==================== MongoDB Setup ====================
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client[os.getenv("DATABASE_NAME", "Reflection")]
resources_collection = db["resources"]
resources_collection.delete_many({})
#data for resources
resources_data = [
       {
        "_id": "DevOps",
        "courses": [
            {"title": "Learn Git and Github", "link": "https://www.codecademy.com/learn/learn-git"},
            {"title": "Javascript", "link": "https://javascript.info/"},
            {"title": "Linux and Scripting", "link": "https://www.youtube.com/watch?v=lCq4mYQL0WY                ...                 https://www.guru99.com/powershell-tutorial.html"},
            {"title": "Networking and Security", "link": "https://www.professormesser.com/network-plus/n10-008/n10-008-video/n10-008-training-course/"},
            {"title": "Server Management", "link": "https://www.cloudflare.com/en-gb/learning/cdn/glossary/reverse-proxy/                                                https://www.freecodecamp.org/news/the-nginx-handbook/"},
            {"title": "Containers", "link": "https://www.youtube.com/watch?v=pg19Z8LL06w                                                   https://iximiuz.com/en/posts/container-learning-path/"},
            {"title": "Container Orchestration", "link": "https://kodekloud.com/learning-path/kubernetes/"},
            {"title": "Terraform", "link": "https://www.youtube.com/watch?v=SPcwo0Gq9T8"},
            {"title": "CI/CD", "link": "https://semaphoreci.com/blog/cicd-pipeline                                                                                https://milan.milanovic.org/post/ci-cd-with-azure-devops-yaml/"},
            {"title": "Monitoring (Grafana and Promethus)", "link": "https://grafana.com/tutorials/                                 https://prometheus.io/docs/tutorials/getting_started/"},
            {"title": "Introduction to Microsoft Azure", "link": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals-describe-azure-architecture-services/"},
            {"title": "Microsoft Azure Administrator", "link": "https://learn.microsoft.com/en-us/credentials/certifications/azure-administrator/?practice-assessment-type=certification#two-ways-to-prepare"}
        ],
        "certifications": [
            {"title": "DevOps Course Certification", "link": "https://intellipaat.com/academy/course/devops-free-course"}
        ],
        "projects": [
            {
            "title": "CI/CD Pipeline for a Static Website",
            "objective": "Automate the build and deployment of a simple website to a hosting service.",
            "description": "Use GitHub/GitLab for version control, set up a pipeline with GitHub Actions or GitLab CI, and deploy to GitHub Pages, Netlify, or AWS S3. Covers source control, CI/CD basics, and deployment automation."
            },
            {
            "title": "Kubernetes Deployment of a Microservice App",
            "objective": "Deploy and manage a multi-service application on Kubernetes.",
            "description": "Break down an app into frontend, backend, and database microservices. Deploy each using Kubernetes manifests or Helm, configure ConfigMaps, Secrets, Ingress, and enable autoscaling (HPA). Covers orchestration, scaling, and basic K8s security."
            },
            {
            "title": "Automated Infrastructure with Terraform and Monitoring",
            "objective": "Provision cloud infrastructure as code and monitor application performance.",
            "description": "Use Terraform to spin up resources (e.g., AWS EC2/Load Balancer), install a sample app (like Nginx + demo service), and integrate Prometheus & Grafana for monitoring CPU, memory, and request metrics. Covers IaC, cloud automation, and observability setup."
            }
        ]

    },
    {
        "_id": "Social Media Marketing",
        "courses": [
            {"title": "HubSpot Academy – Social Media Marketing", "link": "https://academy.hubspot.com/courses/social-media"},
            {"title": "Coursera – Social Media Management by Meta", "link": "https://www.coursera.org/learn/social-media-management"},
            {"title": "Great Learning Academy – Social Media Marketing", "link": "https://www.mygreatlearning.com/academy/learn-for-free/courses/social-media-marketing"},
            {"title": "HubSpot Academy – SEO Certification Course", "link": "https://academy.hubspot.com/courses/seo-training"},
            {"title": "Simplilearn – SEO Certification Course", "link": "https://www.simplilearn.com/free-advanced-seo-course-skillup"},
            {"title": "Google Data Analytics Course", "link": "https://grow.google/intl/en_in/data-analytics-course/?tab=get-started-in-the-field"}
        ],
        "certifications": [
            {"title": "HubSpot Academy – Social Media Marketing Certification", "link": "https://academy.hubspot.com/courses/social-media"},
            {"title": "Coursera – Social Media Management Professional Certificate by Meta", "link": "https://www.coursera.org/learn/social-media-management"},
            {"title": "Simplilearn – SEO Advanced Certificate", "link": "https://www.simplilearn.com/free-advanced-seo-course-skillup"},
            {"title": "Google Data Analytics Professional Certificate", "link": "https://grow.google/intl/en_in/data-analytics-course/?tab=get-started-in-the-field"}
        ],
        "projects": [
            {
                "title": "Social Media Strategy Plan",
                "objective": "Develop a comprehensive social media marketing strategy for a small business or nonprofit.",
                "description": "Analyze the organization’s target audience, set measurable goals, and design a content calendar. The project covers competitive analysis, social media advertising, and performance tracking using analytics tools."
            },
            {
                "title": "Social Media Campaign Performance Analysis",
                "objective": "Evaluate the effectiveness of an ongoing or completed social media campaign.",
                "description": "Use tools like Google Analytics or Meta Insights to assess engagement, reach, and conversion metrics. Prepare a visual performance report and provide improvement recommendations."
            },
            {
                "title": "SEO Optimization for Small Business Website",
                "objective": "Implement SEO best practices for a small business or personal project website.",
                "description": "Conduct keyword research, optimize metadata, improve content structure, and submit the site to Google Search Console. Track ranking changes and organic traffic over time."
            }
        ]
    },
    {
        "_id": "VAPT",
        "courses": [
            {
            "title": "Web Security",
            "link": "https://portswigger.net/web-security"
            },
            {
            "title": "Ethical Hacking",
            "link": "https://www.netacad.com/courses/ethical-hacker?courseLang=en-US"
            },
            {
            "title": "Cybersecurity Essentials",
            "link": "https://www.netacad.com/courses/cybersecurity-essentials?courseLang=en-US"
            },
            {
            "title": "Cybersecurity Tools",
            "link": "https://www.coursera.org/learn/introduction-cybersecurity-cyber-attacks"
            },
            {
            "title": "Penetration Testing",
            "link": "https://www.youtube.com/watch?v=qJ9ZmkMvkcA&list=PLBf0hzazHTGOepimcP15eS6Y-aR4m6ql3"
            },
            {
            "title": "OWASP Top 10",
            "link": "https://tryhackme.com/room/owasptop10"
            },
            {
            "title": "OSINT",
            "link": "https://alison.com/course/fundamentals-of-open-source-intelligence-osint"
            }
        ],
        "certifications": [],
        "projects": [
            {
            "title": "AI-Driven Threat Intelligence Platform",
            "objective": "To build a platform that collects and organizes information about common cybersecurity threats using AI models.",
            "description": "The project will focus on gathering open-source threat data such as recent phishing websites, malware hashes, or vulnerability reports. Using basic text classification or keyword matching, the system will categorize threats and display them in a dashboard."
            },
            {
            "title": "AI-Powered Malware and Phishing Detector",
            "objective": "To create a detection tool that uses AI to identify whether an email, URL, or file might be malicious.",
            "description": "This project will work with small, freely available datasets of phishing emails and malware samples. The AI component will be a basic classifier that looks for suspicious patterns like strange email addresses, unusual keywords, or suspicious links. The scope includes building a simple interface where users can paste an email, URL, or text to check if it looks safe."
            },
            {
            "title": "Web Application Vulnerability Scanner",
            "objective": "To design a scanner that checks websites for common and beginner-friendly vulnerabilities.",
            "description": "The project will cover crawling a website, identifying input fields, and testing them for common issues such as SQL Injection, Cross-Site Scripting (XSS), and missing security headers."
            }
        ]
    },
    {
        "_id": "Biotech",
        "courses": [
            {
            "title": "Fundamentals in Biotechnology and Genetics",
            "link": "https://alison.com/course/fundamentals-in-biotechnology-and-genetics"
            },
            {
            "title": "Basic Molecular Biology",
            "link": "https://www.cdc.gov/lab-training/php/courses/basic-molecular-biology-elearning-series.html"
            },
            {
            "title": "Introduction to RT-qPCR & Gene Expression",
            "link": "https://academy.bio-rad.com/collections/real-time-qpcr"
            },
            {
            "title": "Introductory bioinformatics",
            "link": "https://www.ebi.ac.uk/training/online/courses/introductory-bioinformatics-pathway"
            },
            {
            "title": "Diploma in bioinformatics",
            "link": "https://alison.com/course/diploma-in-bioinformatics"
            },
            {
            "title": "GMP Training",
            "link": "https://www.pharmalessons.com/free-courses/gmptraining"
            },
            {
            "title": "Regulatory Affairs Course",
            "link": "https://www.entrytoregulatory.com/challenge-page/free-regulatory-affairs-course"
            }
        ]
    },
    {
        "_id": "SOC",
        "courses": [
            {"title": "Splunk Fundamentals", "link": "https://www.splunk.com/en_us/training/splunk-fundamentals.html"},
            {"title": "IBM Cybersecurity Analyst Professional Certificate", "link": "https://www.coursera.org/professional-certificates/ibm-cybersecurity-analyst"},
            {"title": "Cybersecurity Fundamentals", "link": "https://www.edx.org/course/cybersecurity-fundamentals"},
            {"title": "Elastic Security for SIEM", "link": "https://www.elastic.co/training/elastic-security-for-siem"},
            {"title": "KQL: Analysing security logs", "link": "https://tryhackme.com/room/kqlkustobasicqueries"},
            {"title": "Log Analysis", "link": "https://app.cybrary.it/browse/paths/skill-paths/log-analysis"},
            {"title": "Host based detection", "link": "https://app.cybrary.it/browse/paths/skill-paths/host-based-detection"},
            {"title": "Network based detection", "link": "https://app.cybrary.it/browse/paths/skill-paths/network-based-detection"},
            {"title": "Blue Team Labs", "link": "https://blueteamlabs.online/"},
            {"title": "Cybersecurity training", "link": "https://www.fortinet.com/training/cybersecurity-professionals"}
        ],
        "certifications": [
            {"title": "IBM Cybersecurity Analyst Professional Certificate", "link": "https://www.coursera.org/professional-certificates/ibm-cybersecurity-analyst"}
        ],
        "projects": [
            {
                "title": "AI-Powered Intrusion Detection System (IDS)",
                "description": "The project will involve capturing network traffic data and training a basic machine learning model to distinguish between normal and suspicious activity using publicly available datasets like KDD Cup 99 or CICIDS for training and testing. The IDS will provide alerts when suspicious traffic patterns are detected",
                "objective": "Use machine learning to identify anomalous network activity and potential intrusions."
            },
            {
                "title": "File Type Identification Tool",
                "description": "This project will focus on building a simple command-line tool that can identify file types based on their magic numbers (unique signatures at the beginning of files). The tool will read the file headers, match them against a small database of known magic numbers, and display the identified file type.",
                "objective": "Create a tool to identify file types using magic numbers."
            },
            {
                "title": "Network Vulnerability Scanner",
                "description": "The project will use Nmap or similar tools to scan a small network and detect open ports, running services, and potential weaknesses. The scanner will generate a simple report listing detected vulnerabilities and possible recommendations.",
                "objective": "Build a tool using Nmap or other tools to scan and identify network weaknesses."
            }
        ]
    },
    {
        "_id": "Data Science",
        "courses": [
            {"title": "Data Analysis with Python", "link": "https://www.freecodecamp.org/learn/data-analysis-with-python/"},
            {"title": "Foundations of Data Science", "link": "https://www.coursera.org/learn/data-science-k-means-clustering-python"},
            {"title": "Machine Learning Pipelines with Azure ML studio", "link": "https://www.coursera.org/projects/azure-machine-learning-studio-pipeline"},
            {"title": "IBM - Data Science", "link": "https://www.edx.org/certificates/professional-certificate/ibm-data-science"},
            {"title": "Harvard - R basics", "link": "https://pll.harvard.edu/course/data-science-r-basics"},
            {"title": "Building Machine Learning models", "link": "https://pll.harvard.edu/course/data-science-building-machine-learning-models"}
        ],
        "certifications": [
            {"title": "Google Data Analytics Certificate", "link": "https://grow.google/intl/en_in/data-analytics-course/?tab=get-started-in-the-field"},
            {"title": "Microsoft Certified: Data Scientist Associate", "link": "https://learn.microsoft.com/en-us/certifications/data-scientist-associate/"}
        ],
        "projects": [
            {
                "title": "Customer Segmentation Using Clustering",
                "description": "This project will focus on analyzing a simple dataset of customers and applying clustering algorithms like K-Means to divide them into groups and visualizing clusters using graphs.",
                "objective": "To group customers into different segments based on their characteristics such as age, income, and purchase behavior, so businesses can understand their audience better."
            },
            {
                "title": "E-commerce Product Recommendation Engine",
                "description": "This project focuses on building and comparing both Content-Based and Collaborative Filtering (Matrix Factorization) models using transactional data. You will preprocess the data, implement the two core models, and then evaluate performance using metrics like Precision@K to measure recommendation accuracy. The final step is creating a function that simulates the top product recommendations for any given user ID.",
                "objective": "To develop a working recommendation system that suggests products to users based on their historical purchase and browsing behavior, aiming to increase click-through rates and sales."
            },
            {
                "title": "Flight Delay Prediction and Impact Analysis",
                "description": "Acquire and merge flight and historical weather data. Engineer new features like airport-specific delay history. Build and tune advanced classification models (e.g., LightGBM). Evaluate performance using the F1-score, and use feature importance methods to identify the top causal drivers of delays.",
                "objective": "To predict whether a scheduled flight will be delayed by a significant margin and to analyze how weather, time of day, and airport traffic influence prediction accuracy."
            }
        ]
    },
    {
        "_id": "AI",
        "courses": [
            {"title": "Deep Learning Specialisation", "link": "https://www.coursera.org/specializations/deep-learning"},
            {"title": "Stanford - Machine Learning", "link": "https://www.youtube.com/playlist?list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU"},
            {"title": "NLP specialisation", "link": "https://www.coursera.org/specializations/natural-language-processing"},
            {"title": "Introduction to LLM", "link": "https://www.udacity.com/course/introduction-large-language-models-google-cloud--cd12959"},
            {"title": "Introduction to AI with python", "link": "https://cs50.harvard.edu/ai/"},
            {"title": "Pytorch bootcamp", "link": "https://opencv.org/university/free-pytorch-course/"},
            {"title": "Deep Reinforcement Learning", "link": "https://rail.eecs.berkeley.edu/deeprlcourse/"}
        ],
        "certifications": [
            {"title": "Google Professional Machine Learning Engineer", "link": "https://cloud.google.com/learn/certification/machine-learning-engineer"},
            {"title": "IBM AI Engineering Professional Certificate", "link": "https://www.coursera.org/professional-certificates/ai-engineer"}
        ],
        "projects": [
            {
                "title": "AI Chatbot for Customer Support",
                "description": "Design a simple chatbot that can answer customer FAQs using NLP models.",
                "objective": "To understand practical AI applications in real-world contexts."
            },
            {
                "title": "Resume/CV Parser",
                "description": "Utilize Named Entity Recognition (NER) using a library like spaCy or NLTK to train a custom model for domain-specific entities (e.g., skill names, company names). Must handle multiple file types and output data in a clean JSON format.",
                "objective": "To automatically extract and structure key information (Name, Skills, Experience, Education) from uploaded resumes (PDF, DOCX)."
            },
            {
                "title": "Filtering Movie Recommender",
                "description": "Implement an Item-Based or User-Based Collaborative Filtering model (e.g., using Surprise library or pure Python with k-Nearest Neighbors or Cosine Similarity). The scope must include model evaluation using metrics like Recall or Precision@K.",
                "objective": "To build a system that suggests new movies to a user based on the preferences of similar users."
            },
            {
                "title": "Product Price Comparison via Image",
                "description": "Combines Computer Vision (Object Recognition/Classification) to identify the product category/ID, followed by Web Scraping (e.g., using BeautifulSoup or Scrapy) to dynamically fetch and display the lowest price from a predefined set of retailers.",
                "objective": "To identify a product from an image uploaded by the user and then scrape/search the current price across multiple e-commerce websites."
            }
        ]
    },
    {
        "_id": "Management",
        "courses": [
            {"title": "Coursera – Introduction to Project Management", "link": "https://www.coursera.org/courses?query=management"},
            {"title": "Harvard Online – Management Essentials", "link": "https://pll.harvard.edu/subject/management"},
            {"title": "Alison – Diploma in Business Management", "link": "https://alison.com/courses/management"},
            {"title": "Oxford Home Study – Free Business Management Course", "link": "https://www.oxfordhomestudy.com/courses/online-management-courses/free-online-certificate-courses-in-management"},
            {"title": "Great Learning – Free Management Courses", "link": "https://www.mygreatlearning.com/management/free-courses"},
            {"title": "SafetyCulture – Free Leadership and Management Courses", "link": "https://training.safetyculture.com/course-collection/free-online-management-courses-with-certificates/"},
            {"title": "MasterClass Management – Business Management Course", "link": "https://www.masterclassmanagement.com/"},
            {"title": "PMI – Project Management Basics", "link": "https://www.pmi.org/learning/free-online-courses"}
        ],
        "certifications": [
            {"title": "Google Project Management Certificate", "link": "https://grow.google/projectmanagement/"},
            {"title": "PMP Certification", "link": "https://www.pmi.org/certifications/project-management-pmp"}
        ],
        "projects": [
            {
                "title": "Blueprints for Strategic Planning and Organizational Achievement",
                "description": "This project focuses on optimizing strategic planning to enhance organizational effectiveness. It seeks to identify and resolve inefficiencies in current planning models, set clear, actionable goals, and align these with general management principles to support sustainable success. The overarching goal is to develop a robust framework that significantly contributes to the organization’s strategic achievements.",
                "objective": "To develop a robust strategic planning framework that enhances organizational effectiveness"
            },
            {
                "title": "Building Effective Teams and Promoting Workplace Collaboration",
                "description": "This project aims to enhance teamwork and collaboration within the workplace to improve productivity and employee satisfaction. It will investigate how structured team-building activities and collaborative environments contribute to improved project outcomes and operational efficiencies.",
                "objective": "To enhance workplace productivity and employee satisfaction by fostering effective teamwork and collaboration"
            },
            {
                "title": "Effective Leadership Styles in the Technology Sector",
                "description": "This project seeks to identify and analyze effective leadership styles, particularly suited to the IT industry. It aims to determine how these leadership styles can drive technological innovation and operational efficiency, thus contributing to organizational success. The objective is to provide actionable insights that can be applied to foster a conducive environment for tech industry leaders.",
                "objective": "To identify and analyze leadership styles in the technology sector that drive innovation and operational efficiency, providing actionable insights to foster effective leadership and organizational success."
            }
        ]
    },
    {
        "_id": "Accounting",
        "courses": [
            {"title": " Accounting Ethics", "link": "https://www.linkedin.com/learning/accounting-ethics/the-purpose-of-accounting-ethics?courseClaim=AQFaCwmXeS2f_AAAAZACM8dxgbo5xGfFiuS3FdhMslcRx8cWZtnaPHlvlv8AFmXJCgRwW4UXNOMfx01ttYYIrk-yrqZEmcNBF9eCbfFfRFm38w-H2GEZpfxRKjaPDk2bTC-oo1ysjd-V-WbQUaJWoxaIzDjeT_m3dGD4zkmcdyYFfJZPzFbBDgF0Unupk8VQF9jRmF0-KJPZGFeTLoej6tob0tqBvs4Ox5ge3uGS3ksaGqQDCADUNa1IsVHnu-AVB4A8imAeD0BOVA3n0takCkJV3uRO1ToiOTG5zR-MINdPq7H76asyQL_XyhNi3XTMbvNyJz1i3m8VdfGodiqhFL4bBQ_ol1Z_03uKG8elvHEmBL5_g1GEgAD-L_ATsmA769G14ODGLi2z9D2SXFjeDNdqYe2MArPaxlIfRlIxSjMqo6-cWHX5iHMNyWMXW9dg-M2bFK1FV_qmXWGlrD3833rCqMFxg7p7Vo33SfNgH__2q3cVPAdKPtqbF4If-vD6yfuhkjc7NeI_m0tSJoZKdkV1n7n8OwF22Ck2Vlz8Zur1lei4CIc4DHs4b6_5LHQ3KC_78R9luhnxkL6bFJmQ09RlDYK8Lib4iF_sOY5MmRbQofxcgiQwz6pMSvM_-JgRuIwrYVF2d2VjouRIzsxEg37ZGItOY8GsDYWZH74ub6Hlwom7L45hNx_u4vdwLRKCbSWqL-AKIOMotJUKn0KbsMq20gw9LqaFfl_EU-YNYjn3RNcVxgB8NEihLhmwbUtFcDd4L7Py3X_JO5kp5uXcZbOclNMlTSyTGHbwvtbjq9BUugW-Eyt12sZdbRUwO_Cq1Q8ryN3c4di6rZS0DyQy61-3X_bo94tKNT866jHzPSW1bBe9pxcEr6ax_PjWYoIP3paTuVs88-yVRD_jyhqUyLS1g7gakb2k9WpAlmSOQeICGUIBngI6vyg7lXOwYOcHzrZqTG8Nl0rx7KlCH9VJaiWzmrNc6zz_wSB1aumE3yR-CtZndEbyfyLVUdQHuGI0KUoxAPH_J0UDdoMn3tII5avrlBNXB3OA5etAurJfwpq2b2k0UwxS4jQy6oBMCoLL49Ili0G2mzHn-IPJ6KBMQr9exCuVFwYZZSa5bmz7BR4Ca7UvE-v1JtbwGjeMLi68u9EPCA"},
            {"title": "Setting Up Accounting Processes and Workflows", "link": "https://academy.financial-cents.com/courses/Setting%20Up%20Accounting%20Processes%20and%20Workflows?_gl=1*17uxwp7*_gcl_au*MzgxNjI4MzQ3LjE3NTkzODg1MzU.*_ga*MTcxODA5ODI5MS4xNzU5Mzg4NTM1*_ga_3443NED6H5*czE3NTkzODg1MzUkbzEkZzEkdDE3NTkzODg2MjYkajU5JGwwJGgw"},
            {"title": "Managerial Accounting: Cost Behaviors, Systems, and Analysis", "link": "https://www.coursera.org/learn/accounting-for-managers?irclickid=zKh1a02jixyKTW3WILTH-VUEUkHX7w0Bv1I12g0&irgwc=1&utm_medium=partners&utm_source=impact&utm_campaign=259799&utm_content=b2c"},
            {"title": "Forensic Accounting and Fraud Examination", "link": "https://www.coursera.org/learn/forensic-accounting"},
            {"title": "Accounting for Decision-Making", "link": "https://www.coursera.org/learn/accounting?"},
            {"title": "Accounting for the Charity Sector", "link": "https://alison.com/course/accounting-for-the-charity-sector"},
            {"title": "edX – Accounting Essentials", "link": "https://www.edx.org/course/accounting-essentials"}
        ],
        "certifications": [
            {"title": "Tally Certified Professional", "link": "https://tallyeducation.com/tallycertified/"},
            {"title": "Certificate in Accounting and Finance", "link": "https://www.oxfordhomestudy.com/courses/accounting-courses-online/accounting-certificate-online-free"}
        ],
        "projects": [
            {
                "title": "EDGAR Search Project",
                "description": "In this assignment, your students examine the most recent annual financial statements of three companies: Microsoft, Google, and Apple. Next, they navigate to the Securities and Exchange Commission’s website and search for the respective companies’ filings using the provided instructions. Students locate the companies’ most recent 10-K filings, focusing on the financial statements within these reports.",
                "objective": "To develop students’ ability to locate and analyze the latest 10-K filings of major companies on the SEC’s EDGAR database"
            },
            {
                "title": "Computing Google’s Goodwill Project",
                "description": "In this project, students will analyze Google’s 2022 balance sheet to compute the company’s goodwill. They will identify key financial metrics, including total assets, total liabilities, and equity, to understand the components that contribute to goodwill.",
                "objective": "To analyze Google’s 2022 balance sheet by identifying key financial metrics, enabling students to understand asset composition, liabilities, equity, and the computation of goodwill."
            },
            {
                "title": "Cost of Production at Your Favorite Restaurant Project",
                "description": "students visit their favorite restaurants to gather information and compute the production cost of their favorite meal. They write a concise description of the restaurant and the meal, followed by the computation of the production cost. The production cost includes direct materials, direct labor, and overhead costs. ",
                "objective": "To calculate the production cost of a selected meal by analyzing direct materials, labor, and overhead, while developing practical skills in cost accounting and financial analysis for real-world business operations."
            },
            {
                "title": "Small Business Valuation Project",
                "description": "Students step into the roles of managing partners of the investment fund, and they choose a small business for valuation. Notably, the valuation process must be passive, meaning they cannot directly question the business owners or employees to obtain financial data. The project includes two deliverables: a written report and a presentation. ",
                "objective": "To perform passive valuations of small businesses, analyzing available financial and market data to produce a comprehensive report and presentation on the business’s estimated value."
            },
            {
                "title": "Financial Statement Analysis Project",
                "description": "In this project, students analyze financial statements for a publicly-traded company of their choice. They access the SEC archives to obtain the financial statements. The group then submits a written executive summary of their analysis and presents their findings to the class. ",
                "objective": "To develop students’ skills in analyzing and interpreting financial statements of publicly-traded companies, producing an executive summary, and presenting insights to enhance understanding of corporate financial performance"
            }
        ]
    }
]

# ---------------------------
# Insert data into MongoDB
# ---------------------------
resources_collection.insert_many(resources_data)

print("✅ MongoDB 'resources' collection populated successfully!")
