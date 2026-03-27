# 🏏 Kric11 — Private Real-Time Fantasy Cricket Arena

> **A fast, real-time fantasy cricket platform built for private leagues — engineered for performance, automation, and social gameplay.**

Kric11 is a fully automated fantasy cricket web application created for the **IPL 2026 season**, designed specifically for small private groups who want deeper competition and custom rules beyond commercial fantasy platforms.

Instead of building another Dream11 clone, Kric11 focuses on **real-time interaction**, **custom tournament mechanics**, and **backend-driven live updates** using a lightweight architecture powered by **FastAPI + HTMX + Server-Sent Events (SSE)**.

---

## ✨ Overview

Kric11 delivers an app-like experience **without a heavy Single Page Application**.

Users can:

* Draft teams with constraints
* Predict match outcomes
* Compete in a season-long leaderboard
* Track live rankings during matches
* Reveal opponents' teams only after locking their own

All updates happen live — **no page refresh required**.

---

## 💡 Why Kric11 Exists

Commercial fantasy apps are optimized for scale, not personalization. For a competitive friend-group league, we needed:

### 🎯 Custom Competition Rules

* Formula-1 style sliding leaderboard scoring
* Consistent competitiveness across an entire season
* Reward strategy instead of one lucky match

### 🧑‍🤝‍🧑 Social Gameplay Mechanics

* Prediction bonuses for match winners
* Strategic secrecy during drafting
* Post-lock team reveal (“snooping”) system

### ⚙️ Engineering Challenge

As a Computer Science student focused on backend systems, this project explored:

* Real-time updates **without React/Vue**
* Server-driven UI architecture
* Efficient API usage under strict rate limits
* Event-driven backend design

Kric11 became a playground for pushing **FastAPI + HTMX** to production-style limits.

---

## 🚀 Key Features

### ⚡ Real-Time Live Leaderboards

* Powered by **Server-Sent Events (SSE)**
* Automatic re-ranking during live matches
* Zero refresh interaction model

### 🧠 Smart Team Draft System

* Role-based roster constraints:

  * WK / BAT / BOW / AR
* Overseas player limits enforced server-side
* Franchise color-coded player cards

### 🏎️ Tournament-Style Scoring

Instead of cumulative fantasy points:

| Position | Points |
| -------- | ------ |
| 1st      | 10     |
| 2nd      | 9      |
| ...      | ...    |

Keeps all players competitive throughout the season.

### 🔮 Match Winner Predictions

* Predict match outcome during lock-in
* Earn **+2 bonus leaderboard points**

### 🕵️ Secure Opponent Snooping

View opponents’ teams **only after locking yours**, preventing unfair advantages.

### 📊 Season Stats Hub

Track:

* Orange Cap
* Purple Cap
* Most Sixes
* Player form trends

### 🚦 Intelligent API Rate Limiting

* Background cron jobs aligned with match phases
* Optimized external API usage
* Designed for free-tier constraints

---

## 🏗️ Architecture Philosophy

Kric11 intentionally avoids a heavy SPA framework.

Instead:

| Traditional SPA        | Kric11 Approach       |
| ---------------------- | --------------------- |
| React state management | Server-driven HTML    |
| Frequent polling       | SSE streaming         |
| Large JS bundles       | HTMX partial updates  |
| Complex frontend logic | Backend orchestration |

Result:
✅ Faster development
✅ Lower complexity
✅ Real-time UX with minimal JavaScript

---

## 🛠️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **Alembic (Migrations)**

### Frontend

* HTML5
* **HTMX**
* Tailwind CSS + Custom Styling
* Minimal JavaScript (notifications only)

### Database

* PostgreSQL
* Supabase compatible

### Real-Time Layer

* Server-Sent Events (SSE)

### External Data

* CricketData.org API

---

## ⚙️ How Live Scoring Works

Instead of constant polling:

1. Scheduler monitors `Match.start_time`
2. When a match becomes active:

   * Background workers fetch live data at strategic intervals
   * Fantasy points are recalculated
   * Rankings are updated
3. SSE streams push updates instantly to connected clients

This design:

* Reduces API calls
* Prevents rate-limit issues
* Maintains real-time responsiveness

---

## 🧪 Running Locally

### Prerequisites

* Python **3.10+**
* PostgreSQL (local or Supabase)

---

### 1️⃣ Clone Repository

```bash
git clone https://github.com/VipranshOjha/Kric11.git
cd Kric11/backend
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Environment Variables

Create `.env` inside `/backend`:

```ini
# Database
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/kric11

# Security
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# External API
CRICKET_DATA_API_KEY=your_cricketdata_org_api_key
```

---

### 5️⃣ Initialize Database

```bash
alembic upgrade head
python app/seed.py
```

---

### 6️⃣ Run Server

```bash
uvicorn app.main:app --reload
```

Visit:

```
http://localhost:8000
```

---

## 🤝 Contributing

Contributions are welcome!

Ideas:

* New tournament formats
* Advanced analytics dashboards
* UI visualizations
* Performance optimizations

Open an issue or submit a PR 🚀

---

## 📄 License

MIT License

---

