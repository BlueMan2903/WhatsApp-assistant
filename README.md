# Lola - AI Podiatry Clinic Assistant

**Lola** is an intelligent, multimodal AI assistant designed for **Nikol Verbitsky's Podiatry Clinic**. It automates the initial patient intake process via a web-based chat interface.

The system uses **Google Gemini (Flash)** for natural language understanding and zero-shot image analysis to screen patients for fungal infections, identifying high-risk cases (bleeding, diabetes) and routing them to the appropriate booking link or manual staff handoff.

---

## 🏗 System Architecture

The project operates on a **Split Environment** architecture to support both local development and a live production site on AWS.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Vanilla JS | Hosted on **GitHub Pages** (Production) / Flask (Local). |
| **Backend** | Python, Flask, Gunicorn | API handling business logic and state. |
| **AI Model** | LangChain + Google Gemini | Handles conversation flow and image analysis. |
| **Containerization** | Docker | Encapsulates the backend environment. |
| **Host** | AWS Lightsail | Runs the Docker container. |
| **Tunneling** | Ngrok | Exposes the localhost port on AWS to the public web. |
| **Notifications** | Resend / MailerSend | Sends email alerts for handoffs and errors. |

### The "Environment-Aware" Frontend
The `index.html` contains smart JavaScript logic to determine the API endpoint dynamically:
*   **Localhost:** Sends requests to `/chat` (Relative path).
*   **Production:** Sends requests to `https://stirring-yearly-anteater.ngrok-free.app/chat`.

---

## 🚀 Features

### 1. Multimodal Triage
*   **Text Analysis:** Understands Hebrew natural language to determine symptoms.
*   **Image Vision:** Analyzes uploaded photos to detect potential fungal infections vs. other wounds.

### 2. Medical Safeguards (Strict Rules)
The AI is programmed with strict `rules.txt` protocols:
*   **Bleeding:** If bleeding is detected (via text or image), the user is immediately routed to **First Aid** booking.
*   **Diabetes (Insulin):** Patients using insulin shots are referred to their HMO (Kupat Holim) and **cannot** book a standard pedicure.
*   **Diabetes (Pills):** Patients on pills are allowed to proceed with standard flows.

### 3. Action Handling
*   **Booking Links:** Automatically provides deep links for specific treatments (Ingrown nail, Wart removal, etc.).
*   **Handoff:** If the AI is unsure, it triggers a `[ACTION: FORWARD_TO_NIKOL]` event, logging the conversation and emailing the clinic owner.

---

## 📂 Project Structure

```text
.
├── app.py                  # Main Flask entry point (Configured for root template serving)
├── assistant/
│   ├── assistant.py        # Core AI logic (LangChain + Gemini)
│   └── session.py          # In-memory session management
├── contexts/
│   ├── prompt.txt          # System Persona
│   ├── rules.txt           # Medical Logic & Safeguards
│   └── assistant_assets.json # Booking IDs and Hebrew Messages
├── Docker/
│   ├── Dockerfile          # Python 3.11 Slim image config
│   └── rebuild_and_run.sh  # Automated deployment script
├── config/
│   ├── config.py           # Env var loading & URL config
│   └── logging_config.py   # Logs (excludes Base64 images for privacy)
├── static/                 # Images & Assets
├── index.html              # Frontend Client
└── requirements.txt        # Python Dependencies
```

---

## 🛠 Configuration (.env)

Create a `.env` file in the root directory. **Do not commit this file.**

```ini
ENVIRONMENT=testing
GEMINI_API_KEY=your_google_gemini_key
RESEND_API_KEY=your_resend_api_key
SENDER_EMAIL=onboarding@resend.dev
NIKOL_EMAIL_ADDRESS=info@nikol.clinic
BOOKING_URL=https://appointments.com/nikol
```

---

## 💻 Development Workflow (Local)

Use this mode for writing code, debugging, and testing logic. It uses the Flask development server for hot-reloading.

1.  **Activate Virtual Environment:**
    ```bash
    source .venv/bin/activate
    ```
2.  **Run the App:**
    ```bash
    python app.py
    ```
3.  **Access:** Open `http://localhost:5000` in your browser.

---

## ☁️ Deployment Workflow (AWS Production)

Use this mode when updating the live server on AWS Lightsail.

### Prerequisites
1.  **Ngrok** must be running in a background session on the AWS machine:
    ```bash
    ngrok http --url=stirring-yearly-anteater.ngrok-free.app 5000
    ```
    *(If this window closes, the site goes down).*

2.  **Docker** must be installed.

### Deployment Steps
1.  **SSH into AWS Lightsail.**
2.  **Pull latest code:**
    ```bash
    git pull origin main
    ```
3.  **Run the Build Script:**
    This script stops the old container, rebuilds the image, and starts the new one.
    ```bash
    ./Docker/rebuild_and_run.sh
    ```
4.  **Frontend Updates:**
    Any changes to `index.html` are deployed automatically via GitHub Pages when you push to `main`.

---

## 🛡 Privacy & Logging
*   **Images:** User images are processed in-memory by Gemini and are **not** saved to disk.
*   **Logs:** The `logging_config.py` explicitly prevents Base64 image strings from writing to `whatsapp_messages.log` to save space and maintain privacy.
*   **Sessions:** Currently stored in-memory (`session.py`). If the container restarts, active conversations are reset.

---

## ❓ Troubleshooting

**Q: The website says "Lola is typing..." but never responds.**
*   **Check Ngrok:** Is the Ngrok terminal window still open on the AWS machine?
*   **Check Docker:** Run `docker logs lola-assistant` to see if the Python app crashed.

**Q: I updated `index.html` but don't see changes.**
*   GitHub Pages can take 1-2 minutes to update. Try doing a "Hard Refresh" (Ctrl+F5) in your browser.

**Q: "TemplateNotFound: index.html" Error.**
*   Ensure `app.py` is configured with `template_folder='.'`. The file must be in the root directory.