# 🌍 Monjed AI — Multi-Hazard Early Warning System

> **Monjed AI** is a multi-hazard early warning and disaster resilience system that combines live environmental data, deterministic risk assessment, and Generative AI to produce explainable, validated, and actionable alerts.

---

## ✨ Key Features

- 🌋 Earthquake risk assessment using USGS data
- 🌧️ Flood risk assessment using NASA POWER precipitation data
- 📊 Multi-hazard composite risk scoring
- 🧠 Explainable risk reasons
- 🤖 Gemini-powered alert generation
- 🛡️ AI output validation and consistency checks
- 🔄 Automatic retry handling for temporary Gemini API failures
- 📊 Dashboard-ready structured JSON
- 📱 SMS-ready alert formatting
- 🔗 End-to-end Risk Engine → AI → Validation pipeline

---

## 🏗️ System Architecture

```text
                 ┌──────────────────────┐
                 │  USGS Earthquake API │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ earthquake.py        │
                 │ • Fetch              │
                 │ • Clean              │
                 │ • Extract Features   │
                 └──────────┬───────────┘
                            │
                            │
┌────────────────────────┐  │
│ NASA POWER API          │ │
│ Daily Precipitation     │ │
└───────────┬────────────┘  │
            │               │
            ▼               │
┌────────────────────────┐  │
│ flood.py               │  │
│ • Fetch Rainfall       │  │
│ • Clean Data           │  │
│ • Extract Features     │  │
└───────────┬────────────┘  │
            │               │
            └───────┬───────┘
                    ▼
          ┌──────────────────────┐
          │ scoring.py           │
          │                      │
          │ • Normalization      │
          │ • Hazard Scoring     │
          │ • Risk Classification│
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ engine.py            │
          │ evaluate_country_    │
          │ risk()               │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Structured Risk      │
          │ Report               │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Gemini AI Layer      │
          │                      │
          │ • Prompt Engineering │
          │ • Alert Generation   │
          │ • Structured JSON    │
          │ • Retry Handling     │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Validation Layer     │
          │                      │
          │ • Score Consistency  │
          │ • Level Consistency  │
          │ • Hazard Validation  │
          └──────────┬───────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
       ┌─────────────┐ ┌─────────────┐
       │  Dashboard  │ │     SMS     │
       │    JSON     │ │   Message   │
       └─────────────┘ └─────────────┘