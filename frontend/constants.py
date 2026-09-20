"""
MindMesh Frontend - Global Constants and Presets
"""

PRESET_TEMPLATES = {
    "healthcare": {
        "title": "🏥 HealthTech Telemedicine",
        "business_idea": "An AI-powered telemedicine and remote patient monitoring platform that connects patients with licensed doctors for video consultations, manages electronic health records (EHR), tracks vital signs from wearable IoT devices, and complies strictly with HIPAA and local data protection regulations.",
        "technology_preference": "Open-Source Stack",
        "cloud_preference": "AWS",
        "expected_daily_traffic": "50,000 DAU (Peak 2,500 req/sec)",
        "delivery_timeline_months": 4,
        "data_hosting_country": "United States"
    },
    "fintech": {
        "title": "💳 AI FinTech NeoBank",
        "business_idea": "A next-generation digital banking platform offering multi-currency mobile wallets, instant peer-to-peer micro-payments, AI-driven real-time fraud detection on transactions, automated budget categorization, and secure open banking API integrations.",
        "technology_preference": "Enterprise Stack",
        "cloud_preference": "Google Cloud (GCP)",
        "expected_daily_traffic": "100,000 DAU (High Concurrency & Load)",
        "delivery_timeline_months": 6,
        "data_hosting_country": "Germany (EU GDPR Compliant)"
    },
    "supply_chain": {
        "title": "📦 Smart Logistics & Fleet",
        "business_idea": "An end-to-end B2B supply chain visibility platform with real-time GPS fleet tracking, cold-chain temperature telemetry sensors, route optimization algorithms, dynamic warehouse inventory forecasting, and automated driver dispatch management.",
        "technology_preference": "Microservices Mesh",
        "cloud_preference": "AWS",
        "expected_daily_traffic": "50,000 DAU (Peak 2,500 req/sec)",
        "delivery_timeline_months": 5,
        "data_hosting_country": "India"
    }
}

ARCHITECTURE_INSIGHTS = [
    "💡 Architecture Insight: Decoupled microservices ensure independent scaling between compute-heavy background workloads and low-latency client APIs.",
    "🔒 Security Insight: Enforcing Zero-Trust network policies and token rotation at API boundaries protects sensitive user and payment data.",
    "📈 Scalability Tip: Implementing Redis distributed caching for read-heavy entities offloads 70%+ database query load.",
    "⏱️ Delivery Insight: Prioritizing core MVP user journeys first shortens time-to-market and enables faster feedback loops."
]

TECH_STACK_OPTIONS = [
    "-- Select Technology Stack --",
    "Open-Source Stack",
    "Enterprise Stack",
    "Microservices Mesh",
    "Serverless Ecosystem",
    "No Preference"
]

CLOUD_OPTIONS = [
    "-- Select Cloud Infrastructure --",
    "AWS",
    "Google Cloud (GCP)",
    "Azure",
    "Multi-Cloud Ecosystem",
    "On-Premises / Bare Metal",
    "No Preference"
]

TRAFFIC_OPTIONS = [
    "-- Select Expected Daily Traffic --",
    "10,000 DAU (Standard MVP Scale)",
    "50,000 DAU (Peak 2,500 req/sec)",
    "100,000 DAU (High Concurrency & Load)",
    "1,000,000+ DAU (Global Enterprise Scale)"
]

COUNTRY_OPTIONS = [
    "-- Select Data Hosting Region --",
    "United States",
    "India",
    "Germany (EU GDPR Compliant)",
    "Singapore (APAC Region)",
    "United Kingdom",
    "Global Multi-Region"
]

AGENT_METADATA = [
    {"name": "Business Analyst", "icon": "📋", "role": "Requirements & MVP Scope"},
    {"name": "Solution Architect", "icon": "🏗️", "role": "System Architecture & Components"},
    {"name": "Technology Advisor", "icon": "⚡", "role": "Tech Stack & Trade-Offs"},
    {"name": "Delivery Planner", "icon": "🚀", "role": "Delivery Roadmap & Milestones"},
    {"name": "Report Writer", "icon": "✍️", "role": "Master Blueprint Synthesis"}
]