# SnapClass — AI Powered Attendance System

> Revolutionizing the classroom with next-gen computer vision and voice biometrics.

[![Live App](https://img.shields.io/badge/🚀_Live_App-SnapClass-7C3AED?style=for-the-badge)](https://mohdabdulrah-snapclass-app-cpafiu.streamlit.app/)
[![Platform](https://img.shields.io/badge/Platform-Streamlit-FF4B4B?style=for-the-badge)](https://streamlit.io/)
[![AI](https://img.shields.io/badge/AI-Face_+_Voice_Biometrics-00C9A7?style=for-the-badge)](#)
[![Database](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge)](https://supabase.com/)

---

## 🌐 Live URL

**👉 [https://mohdabdulrah-snapclass-app-cpafiu.streamlit.app/](https://mohdabdulrah-snapclass-app-cpafiu.streamlit.app/)**

---

## 📌 Overview

**SnapClass** is an AI-powered classroom attendance system that eliminates manual roll-calls by combining **facial recognition** and **voice biometrics**. Teachers can mark attendance for an entire class in milliseconds from a single photo, or let students check in sequentially via voice — all backed by a secure, real-time cloud database.

---

## ✨ Core Features

| Feature | Description |
|---|---|
| 📸 **AI Face Analysis** | Neural networks recognize every student from a single class photo — instant and accurate. |
| 🎙️ **Sequential Voice ID** | Students say "Present" one-by-one; audio-AI matches their voice biometrics in real-time. |
| 📱 **QR-Driven Enrollment** | Course codes generate unique QR codes for instant student sign-up — zero manual data entry. |
| 📊 **Actionable Records** | View confidence scores, download CSV reports, and track long-term attendance trends. |
| 🔐 **Secure Auth** | Encrypted login with data synced across all devices via Supabase. |

---

## 🗺️ The Teacher's Journey

```
Step 01 → Secure Login          — Authenticate and access your session securely
Step 02 → Interactive Dashboard — Manage subjects, logs, and rosters in one place
Step 03 → Course Management     — Create a subject; SnapClass handles the rest
Step 04 → FaceID Attendance     — Snap a class photo; AI identifies every student
Step 05 → Voice ID Attendance   — Students speak "Present"; AI verifies each voice
Step 06 → Actionable Records    — Review logs, download CSV, track trends over time
```

---

## 🎓 The Student's Journey

```
Phase 01 → Instant Enrollment     — Join via QR code or course link in seconds
Phase 02 → Biometric Registration — Register FaceID + VoiceID once for all future sessions
Phase 03 → Personal Dashboard     — Track attendance % across all subjects in real-time
```

---

## 🛠️ Tech Stack

### Platform
- **Streamlit** — Reactive Python frontend powering the entire app

### Vision AI
- **FaceRecognition** — High-accuracy face detection and matching
- **Dlib** — High-fidelity facial biometrics and landmark detection

### Audio AI
- **Resemblyzer** — Deep voice embeddings for student voice signatures
- **Librosa** — Audio processing and feature extraction

### Cloud & Storage
- **Supabase** — Real-time PostgreSQL with secure auth, storage, and sync

---

## 🚀 Getting Started

### Prerequisites
```
Python 3.9+
pip
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/snapclass.git
   cd snapclass
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Streamlit secrets**

   Create `.streamlit/secrets.toml` in the project root:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-supabase-anon-key"
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## ⚙️ Secrets Configuration

SnapClass uses Streamlit's native secrets manager — no `.env` files needed.

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```

> ⚠️ `secrets.toml` is listed in `.gitignore` — never commit it to version control.

For **Streamlit Cloud** deployment, add `SUPABASE_URL` and `SUPABASE_KEY` via the app's **Secrets** panel in the Streamlit dashboard.

---

## 📁 Project Structure

```
SNAPCLASS/
├── .streamlit/
│   └── secrets.toml          # Supabase credentials (gitignored)
├── attend/                   # Attendance processing logic
├── src/
│   ├── components/           # Reusable UI components
│   ├── database/             # Supabase client & query helpers
│   ├── pipelines/            # Face & voice recognition pipelines
│   ├── screens/              # App screen views (teacher, student, etc.)
│   └── ui/                   # Styling and layout utilities
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

---

## 🔒 Privacy & Security

- All biometric data is encrypted at rest and in transit via Supabase's secure infrastructure.
- Face and voice embeddings are stored as numerical vectors — original images and audio are **never permanently stored**.
- Each teacher's data is isolated with row-level security (RLS) policies.
- Secrets are managed via Streamlit's secrets manager and never hardcoded.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for educators everywhere.**

[🚀 Try SnapClass Live](https://mohdabdulrah-snapclass-app-cpafiu.streamlit.app/) · [Report Bug](#) · [Request Feature](#)

© 2026 SnapClass AI

</div>