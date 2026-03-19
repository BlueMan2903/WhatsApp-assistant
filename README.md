# Lola - AI Podiatry Clinic Assistant

**Lola** is an intelligent, multimodal AI assistant designed for **Nikol Verbitsky's Podiatry Clinic**. It automates the initial patient intake process via a web-based chat interface.

The system uses **Google Gemini** for natural language understanding and zero-shot image analysis to screen patients for fungal infections, plantar warts and ingrown nails, identifying high-risk cases (bleeding, diabetes) and routing them to the appropriate booking link or manual staff handoff.

---

## 🏗️ System Architecture

The project is a containerized web application designed for a production environment on AWS Lightsail. It serves both the static frontend and the dynamic API from a single, secure endpoint.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Vanilla JS | Static files served directly by the Caddy reverse proxy from the host. |
| **Backend** | Python, Flask, Gunicorn | API handling business logic, AI integration, and session state. |
| **Reverse Proxy** | **Caddy** | **Handles automated SSL (HTTPS), terminates traffic, and routes requests.** |
| **AI Model** | LangChain + Google Gemini | Handles conversation flow and image analysis. |
| **Session Storage**| **SQLite** | **Stores conversation history persistently in a database file.** |
| **Containerization** | Docker | Encapsulates the backend, proxy, and their networking. |
| **Host** | AWS Lightsail | Runs the Docker containers and provides a static IP. |
| **Notifications** | Resend | Sends email alerts for handoffs and critical errors. |

### Simplified Frontend
The `index.html` file now uses **relative paths** for all API calls (e.g., `/chat`, `/history`). This makes the frontend code simple and environment-agnostic, as the Caddy reverse proxy is solely responsible for routing requests.

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
*   **Booking Links:** Automatically provides deep links for specific treatments.
*   **Handoff:** If the AI is unsure or for specific queries (e.g., discounts), it triggers an `[ACTION: FORWARD_TO_NIKOL]` event, sending a transcript email to the clinic owner.

---

## 🛠️ Configuration (.env)

Create a `.env` file in the root of the deployment directory on the server (`~/Lola/.env`). **Do not commit this file to Git.**

```ini
GEMINI_API_KEY=your_google_gemini_key
RESEND_API_KEY=your_resend_api_key
SENDER_EMAIL=onboarding@resend.dev
NIKOL_EMAIL_ADDRESS=info@nikol.clinic
BOOKING_URL=https://appointments.com/nikol
```

---

## ☁️ Deployment Workflow (AWS Production)

Deployment is a two-stage process: building the application image locally, then deploying that image on the server.

### Part 1: Build & Push (From your Local Machine)
When you make changes to the Python application code, you must build a new Docker image and push it to Docker Hub.

1.  **Run the Build Script:** From your local project root, execute:
    ```bash
    ./Docker/build_and_push.sh
    ```
2.  **Copy the Tag:** The script will output a date-based tag (e.g., `2026-03-20-0130`). Copy this tag for the next part.

### Part 2: Deploy (On the AWS Server)
To update the live application to the new version.

1.  **SSH into AWS Lightsail.**
2.  **Navigate to the deployment directory:**
    ```bash
    cd ~/Lola
    ```
3.  **Run the Deployment Script:**
    ```bash
    sudo ./download_and_run.sh
    ```
4.  **Paste the Tag:** When prompted, paste the image tag you copied from Part 1. The script will pull the new image and restart the stack.

### Frontend Updates
The frontend is **not** deployed automatically. To update the `index.html` file or static assets (images):
1.  Modify the files on your local machine.
2.  Securely copy the files to the server using `scp` or `rsync`.
    ```bash
    # Example using scp from your local machine
    scp -i /path/to/key.pem index.html ubuntu@YOUR_IP:~/Lola/frontend/
    ```
3.  **Reload Caddy** to purge its cache and serve the new file.
    ```bash
    # Run this on the server
    sudo docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
    ```

---

## 🛡️ Privacy & Logging
*   **Images:** User images are processed in-memory by Gemini and are **not** saved to disk.
*   **Logs:** Application logs are containerized. View backend logs with `sudo docker logs assistant-backend` and proxy logs with `sudo docker logs caddy-proxy`.
*   **Sessions:** Conversations are stored persistently in a **SQLite database** located in a Docker volume (`lola_session_data`), ensuring history is retained across container restarts.

---

## ❓ Troubleshooting

**Q: The website says "I couldn't connect to the server."**
*   **Check the Backend:** Is the backend container running? Run `sudo docker ps`. If `assistant-backend` is not running or is restarting, check its logs: `sudo docker logs assistant-backend`.
*   **Check the Proxy:** Are there errors in the Caddy logs? Run `sudo docker logs caddy-proxy`.

**Q: The website isn't loading at all (e.g., 404 error, connection timed out).**
*   **Check DNS:** Use a tool like [dnschecker.org](https://dnschecker.org/) to confirm your domain's A record is pointing to the correct Lightsail Static IP.
*   **Check Firewall:** In the AWS Lightsail console, ensure the "Networking" firewall has rules allowing TCP traffic on ports **80** and **443**.

**Q: I updated `index.html` but I'm still seeing the old version.**
*   **Hard Refresh:** Your browser is likely caching the old file. Press **Ctrl+Shift+R** (or **Cmd+Shift+R** on Mac) to force a full reload.
*   **Reload Caddy:** If a hard refresh doesn't work, ensure you reloaded the Caddy service on the server after uploading the new file (see "Frontend Updates" section).