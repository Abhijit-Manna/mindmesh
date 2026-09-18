"""
MindMesh Frontend - Separate Dummy & Mock Data Module

This file contains dummy response payloads matching the FastAPI backend routes,
preset input templates for instant testing, simulated multi-agent execution steps,
and rotating tech insights to keep users engaged during 2-3 minute agent runs.
"""

import time
from typing import Dict, Any, List

# Preset templates for quick form filling
PRESET_TEMPLATES = {
    "ecommerce": {
        "title": "🛍️ Global E-Commerce Marketplace",
        "business_idea": "A high-concurrency multi-vendor marketplace platform where sellers list products, buyers place orders with real-time inventory tracking, integrated payment gateways, and automated logistics dispatch.",
        "technology_preference": "Open-Source (Python FastAPI + React + PostgreSQL)",
        "cloud_preference": "AWS",
        "expected_daily_traffic": "100,000 DAU (Peak 5,000 req/sec)",
        "delivery_timeline_months": 6,
        "data_hosting_country": "United States"
    },
    "fintech": {
        "title": "💳 AI-Powered FinTech Payment Gateway",
        "business_idea": "A micro-investment and real-time payment settlement platform featuring automated fraud detection ML models, multi-currency ledger management, and strict PCI-DSS compliance logging.",
        "technology_preference": "Enterprise Stack (Go / Java Spring + PostgreSQL + Kafka)",
        "cloud_preference": "Google Cloud (GCP)",
        "expected_daily_traffic": "500,000 DAU (High Security & Low Latency)",
        "delivery_timeline_months": 8,
        "data_hosting_country": "India"
    },
    "healthcare": {
        "title": "🏥 HIPAA Patient Health Portal",
        "business_idea": "A secure telehealth platform enabling encrypted video consultations, EHR record synchronization, smart prescription dispatch, and AI triage symptom checking.",
        "technology_preference": "Open-Source (Python / Node.js + React + MongoDB)",
        "cloud_preference": "Azure",
        "expected_daily_traffic": "25,000 DAU",
        "delivery_timeline_months": 4,
        "data_hosting_country": "Germany (EU)"
    }
}

# Simulated Multi-Agent Pipeline Steps for 2-3 minutes engagement animation
AGENT_WORKFLOW_STEPS = [
    {
        "agent": "Business Analyst",
        "icon": "🧠",
        "role": "Requirements Analysis & Scope Boundary Definition",
        "description": "Deconstructing core business objectives, identifying functional & non-functional constraints, and defining MVP scope priorities.",
        "duration": 25,
        "logs": [
            "Parsed raw business idea payload and domain parameters.",
            "Identified 4 primary user personas and 12 key functional requirements.",
            "Evaluating non-functional requirements (NFRs): SLA, latency limits, and security constraints.",
            "Drafting scope boundary: Isolating MVP features from post-launch enhancements.",
            "Accepted Business Analyst JSON payload validated against contract schema."
        ]
    },
    {
        "agent": "Solution Architect",
        "icon": "🏗️",
        "role": "System Topology & High-Level Architecture Design",
        "description": "Formulating architectural patterns (Event-Driven Microservices / Modular Monolith), API boundaries, and database isolation models.",
        "duration": 30,
        "logs": [
            "Receiving accepted JSON context from Business Analyst...",
            "Analyzing traffic scalability requirements (Peak load distribution)...",
            "Evaluating architectural topology: Selecting Modular Event-Driven Architecture.",
            "Designing data flow boundaries and storage isolation policies.",
            "Validating data residency compliance and localized region strategy.",
            "Accepted Solution Architect JSON payload generated successfully."
        ]
    },
    {
        "agent": "Technology Advisor",
        "icon": "⚡",
        "role": "Technology Stack Selection & Infrastructure Matrix",
        "description": "Selecting optimal frameworks, ORMs, cloud services, caching layers, and CI/CD pipelines aligned with tech & cloud preferences.",
        "duration": 35,
        "logs": [
            "Receiving architectural blueprints and component specifications...",
            "Comparing tech preferences against ecosystem support & community maturity.",
            "Selecting core stack: FastAPI / Spring Boot + React + PostgreSQL + Redis + Kafka.",
            "Mapping cloud infrastructure: Managed Kubernetes (EKS/GKE), Terraform, CloudFront.",
            "Conducting lock-in & licensing trade-off assessment.",
            "Accepted Technology Advisor JSON payload verified."
        ]
    },
    {
        "agent": "Delivery Planner",
        "icon": "📅",
        "role": "Implementation Roadmap & Execution Governance",
        "description": "Formulating sprint phases, milestone timelines, risk mitigation matrix, testing strategy, and team staffing allocations.",
        "duration": 30,
        "logs": [
            "Receiving full architecture & technology stack specification...",
            "Synthesizing delivery timeline requirements into 4 core sprint milestones.",
            "Constructing workstream schedule: Infrastructure, Core API, Frontend, Security audit.",
            "Estimating team staffing matrix (Backend, Frontend, DevOps, QA, Lead Architect).",
            "Assembling final canonical Solution Blueprint Markdown document.",
            "Final Delivery Planner task complete. Compilation finished!"
        ]
    }
]

# Tech insights to rotate during long agent processing
ARCHITECTURE_INSIGHTS = [
    "💡 **Pro-Tip:** Decoupling read & write models via CQRS (Command Query Responsibility Segregation) can boost database throughput by over 300% under high daily traffic.",
    "🔒 **Security First:** Storing sensitive user data requires field-level AES-256 encryption at rest, along with TLS 1.3 in transit.",
    "☁️ **Cloud Strategy:** Utilizing Infrastructure as Code (Terraform / Pulumi) ensures environment consistency across Staging, QA, and Production.",
    "🚀 **Performance Optimization:** Implementing Redis caching for read-heavy API endpoints reduces p99 database query latency from 120ms to under 8ms.",
    "🧠 **Multi-Agent Orchestration:** MindMesh CrewAI agents pass structured JSON handoffs sequentially, enforcing strict evaluation gates before final blueprint assembly."
]

# High-quality dummy blueprint markdown response matching backend outputs
DUMMY_BLUEPRINT_MARKDOWN = """# Solution Blueprint: Scalable Multi-Tenant Enterprise Platform

**Generated by MindMesh Multi-Agent Engine**  
**Run ID:** `run_demo_8f92a11b` | **Status:** `Completed` | **Evaluation Score:** `100/100`

---

## 1. Executive Summary & Business Vision
The proposed system is a high-availability, cloud-native enterprise application engineered to support high daily traffic with strict data residency compliance. The platform leverages a modular microservices architecture designed to scale seamlessly while keeping infrastructure overhead low during initial MVP launch.

---

## 2. Business Analyst Report
### Core Functional Requirements
- **FR-001 (User Authentication & RBAC):** Secure multi-factor authentication with granular Role-Based Access Control (Admin, Manager, Standard User).
- **FR-002 (Real-Time Workstream Engine):** Automated processing pipeline with WebSocket status notifications.
- **FR-003 (Audit & Compliance Tracker):** Immutable transaction logs for security auditing and regulatory compliance.

### Non-Functional Requirements (NFRs)
- **Availability:** 99.95% uptime SLA with multi-AZ automatic failover.
- **Latency:** Sub-100ms API response time for 95% of standard requests.
- **Data Residency:** All customer data hosted strictly within target region boundaries.

---

## 3. System Architecture & Topology
```mermaid
graph TD
    Client[Web & Mobile Clients] --> CloudFront[CDN / API Gateway]
    CloudFront --> Auth[Auth Service]
    CloudFront --> CoreAPI[Core Application Service]
    CoreAPI --> DB[(Primary PostgreSQL DB)]
    CoreAPI --> Cache[(Redis Cache Layer)]
    CoreAPI --> Queue[Kafka / Event Bus]
    Queue --> Worker[Background Async Workers]
```

### Key Architectural Decoupling
1. **API Gateway Layer:** Manages rate limiting, SSL termination, and request routing.
2. **Stateless Service Nodes:** Containerized microservices running on Kubernetes with Horizontal Pod Autoscaling (HPA).
3. **Isolated Persistence:** Primary relational database paired with Redis for read-heavy endpoint caching.

---

## 4. Recommended Technology Stack
| Category | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React / Next.js + TypeScript | Server-side rendering for speed and rich interactive UI components |
| **Backend API** | Python (FastAPI) / Go | High concurrency, asynchronous request handling, auto OpenAPI docs |
| **Database** | PostgreSQL + Redis | ACID compliance for transactions + sub-millisecond cache reads |
| **Messaging** | Apache Kafka / RabbitMQ | Asynchronous event processing and background task dispatch |
| **Cloud Infra** | AWS / GKE Container Ecosystem | Containerized auto-scaling, Terraform IaC, managed DB services |

---

## 5. Delivery Timeline & Implementation Roadmap
### Milestone Phase Breakdown
- **Month 1-2 (Foundation & Setup):** CI/CD pipeline, IaC deployment, core Auth service, DB schema migration scripts.
- **Month 3-4 (Core Feature Development):** Main business logic API endpoints, real-time WebSocket notifications, admin portal.
- **Month 5 (Integration & Security Audit):** Penetration testing, load testing (5,000 req/sec), data encryption validation.
- **Month 6 (Production Rollout & Go-Live):** Staged canary deployment, live telemetry monitoring, operational handover.

---

## 6. Risk Assessment & Mitigation Strategy
- **Risk:** Traffic spikes overwhelming database connection pools.
  - *Mitigation:* Implement PgBouncer connection pooling and aggressive Redis response caching.
- **Risk:** Regional data compliance enforcement.
  - *Mitigation:* Explicit AWS/GCP region pinning and database encryption at rest using AWS KMS.
"""

def get_dummy_response(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a structured API response dictionary matching FastAPI output format."""
    return {
        "run_id": f"run_demo_{int(time.time())}",
        "status": "completed",
        "file_saved": "outputs/run_demo_latest.md",
        "result": DUMMY_BLUEPRINT_MARKDOWN,
        "run_metadata": {
            "attempts": {
                "Business Analyst": 1,
                "Solution Architect": 1,
                "Technology Advisor": 1,
                "Delivery Planner": 1
            },
            "duration_ms": 14230,
            "accepted_evaluations": 4,
            "request_payload": request_data
        }
    }
