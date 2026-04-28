# CSP 558 — Final Project
**Web Attack Demonstration & Mitigation Study**

This project is a Flask web application that demonstrates common web attacks and compares mitigation techniques across multiple implementation layers. It covers two attack types: **SQL Injection** and **Cross-Site Scripting (XSS)**.

---

## Project Structure

```
CSP558_Project/
├── app.py               # Main Flask application, all routes
├── database.py          # Initializes users.db with mock user data
├── requirements.txt     # Python dependencies
├── static/
│   ├── login.css        # Shared stylesheet for all pages
│   └── index.css        # Landing page stylesheet
│   └── profile.css      # Profile page stylesheet
└── templates/
    ├── index.html             # Landing page + route navigator
    ├── profile.html           # Login success page
    ├── vuln_login.html        # SQLi — vulnerable login (bypass)
    ├── vuln_union.html        # SQLi — vulnerable UNION exfiltration
    ├── safe_login.html        # SQLi — shared template for safe login routes
    ├── vuln_xss.html          # XSS — vulnerable comment board
    ├── safe_xss_escaped.html  # XSS — Jinja2 escaping
    └── safe_xss_csp.html      # XSS — Content Security Policy
```

---

## Setup

**Requirements:** Python 3.8+

1. Clone the repository:
    ```bash
    git clone https://github.com/ratanakhek22/CSP558_Project.git
    cd CSP558_Project
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv

    # Windows
    .venv\Scripts\activate

    # Mac/Linux
    source .venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Initialize the database:
    ```bash
    python database.py
    ```

5. Run the app:
    ```bash
    python app.py
    ```

6. Open your browser and go to `http://localhost:5000`

---

## Demo Walkthrough

### SQL Injection

The app uses a mock `users.db` with two accounts:
| Username | Password  |
|----------|-----------|
| admin    | admin     |
| alice    | alice123  |

#### 1. Login Bypass — `/vuln/login`
The login query is built using an f-string, allowing the attacker to manipulate the SQL logic directly.

**Payload (username field):**
```
' OR '1'='1' --
```
**Result:** Logs in as the first user in the database without knowing any credentials.

#### 2. UNION Exfiltration — `/vuln/union`
The same vulnerable query is used but the attacker engineers a UNION to dump the entire users table.

**Payload (username field):**
```
' UNION SELECT 1, group_concat(username || ':' || password), 'x' FROM users --
```
**Result:** Raw tuple containing all usernames and passwords is displayed on the page.

#### 3. Parameterized Query Fix — `/safe/login/parameterized`
The query uses `?` placeholders. The query and user input are sent to the database separately, so injected input is never interpreted as SQL.

Try the same payloads from above — both fail.

#### 4. ORM Fix — `/safe/login/orm`
SQLAlchemy handles the query entirely through Python objects. No raw SQL is written, so there is no query string for input to break out of.

Try the same payloads from above — both fail.

---

### XSS (Cross-Site Scripting)

Each page is a comment board that stores and displays user input. Use the following payload on all three pages:

**Payload:**
```
<script>alert('XSS')</script>
```

#### 1. Vulnerable — `/vuln/xss`
Output is rendered with `| safe`, bypassing Jinja2 escaping. The browser receives a raw `<script>` tag and executes it.

**Result:** Alert popup fires.

#### 2. Jinja2 Escaping — `/safe/xss/escaped`
Output is rendered with default Jinja2 auto-escaping. The `<` and `>` characters are converted to `&lt;` and `&gt;` before the page is sent to the browser, so the tag is never parsed as HTML.

**Result:** The payload is displayed as plain text. Nothing executes.

#### 3. Content Security Policy — `/safe/xss/csp`
Escaping is intentionally disabled (`| safe`) to isolate CSP as the only protection. The Flask route sets a `Content-Security-Policy: script-src 'self'` response header, which instructs the browser to refuse execution of any inline scripts.

**Result:** No alert fires. Open DevTools → Console to see the CSP violation error. View page source to confirm the raw `<script>` tag is present in the HTML — the browser received it but refused to run it.

---

## Experiment Summary

| Route | Attack | Protection | Result |
|---|---|---|---|
| `/vuln/login` | SQLi bypass | None | ✅ Attack succeeds |
| `/vuln/union` | SQLi UNION | None | ✅ Attack succeeds |
| `/safe/login/parameterized` | SQLi bypass + UNION | Parameterized queries | ❌ Attack blocked |
| `/safe/login/orm` | SQLi bypass + UNION | SQLAlchemy ORM | ❌ Attack blocked |
| `/vuln/xss` | XSS | None | ✅ Attack succeeds |
| `/safe/xss/escaped` | XSS | Jinja2 escaping | ❌ Attack blocked |
| `/safe/xss/csp` | XSS | CSP header | ❌ Attack blocked |