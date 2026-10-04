from flask import Flask, request, session, redirect, url_for, render_template_string, make_response
import base64
import json

app = Flask(__name__)
app.secret_key = "CT8-BROKEN-SESSION-KEY-2026"

FLAG = "Flag_CT8{session_trust_was_broken}"

USERS = {
    "employee": {
        "password": "cybertec8",
        "role": "employee"
    },
    "admin": {
        "password": "admin2026",
        "role": "admin"
    }
}


# ============================================================
# SHARED CYBERTEC8 UI
# ============================================================

COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #05080c;
    --panel: #0a1118;
    --panel2: #0d161e;
    --border: #1b303c;
    --cyan: #00e5ff;
    --green: #39ff88;
    --red: #ff5364;
    --orange: #ffb84d;
    --text: #e8f4f7;
    --muted: #718691;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    min-height: 100vh;
    background:
        radial-gradient(circle at 15% 15%, rgba(0,229,255,.055), transparent 28%),
        radial-gradient(circle at 85% 80%, rgba(57,255,136,.035), transparent 30%),
        var(--bg);
    color: var(--text);
    font-family: "Space Grotesk", sans-serif;
}

/* subtle technical grid */
body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: .35;
    background-image:
        linear-gradient(rgba(0,229,255,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,255,.025) 1px, transparent 1px);
    background-size: 44px 44px;
    mask-image: linear-gradient(to bottom, black, transparent 90%);
}

/* scanline */
body::after {
    content: "";
    position: fixed;
    left: 0;
    right: 0;
    top: -10%;
    height: 1px;
    background: rgba(0,229,255,.16);
    box-shadow: 0 0 18px rgba(0,229,255,.18);
    pointer-events: none;
    animation: scan 8s linear infinite;
    z-index: 50;
}

@keyframes scan {
    0%   { top: -5%; }
    100% { top: 105%; }
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%,100% {
        opacity: 1;
        box-shadow: 0 0 0 rgba(57,255,136,0);
    }
    50% {
        opacity: .55;
        box-shadow: 0 0 14px rgba(57,255,136,.25);
    }
}

@keyframes blink {
    50% { opacity: 0; }
}

.shell {
    width: min(1180px, 92%);
    margin: 0 auto;
}

/* TOP BAR */

.topbar {
    height: 68px;
    border-bottom: 1px solid var(--border);
    background: rgba(5,8,12,.88);
    backdrop-filter: blur(14px);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4%;
    position: relative;
    z-index: 10;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-mark {
    width: 30px;
    height: 30px;
    border: 1px solid var(--cyan);
    display: grid;
    place-items: center;
    color: var(--cyan);
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    box-shadow: 0 0 16px rgba(0,229,255,.12);
}

.brand-name {
    font-weight: 700;
    letter-spacing: 2px;
}

.brand-name span {
    color: var(--cyan);
}

.top-status {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--muted);
    font: 11px "JetBrains Mono", monospace;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse 1.8s infinite;
}

/* PANELS */

.panel {
    background: linear-gradient(
        145deg,
        rgba(13,22,30,.94),
        rgba(7,13,18,.96)
    );
    border: 1px solid var(--border);
    box-shadow:
        0 20px 70px rgba(0,0,0,.22),
        inset 0 1px rgba(255,255,255,.015);
}

.panel-header {
    height: 45px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 18px;
    color: var(--muted);
    font: 10px "JetBrains Mono", monospace;
    letter-spacing: 1px;
}

.panel-code {
    color: var(--cyan);
}

/* BUTTONS */

.btn {
    border: 1px solid var(--cyan);
    background: rgba(0,229,255,.045);
    color: var(--cyan);
    padding: 13px 18px;
    font: 600 11px "JetBrains Mono", monospace;
    letter-spacing: 1px;
    cursor: pointer;
    transition: .25s ease;
}

.btn:hover {
    color: #001014;
    background: var(--cyan);
    box-shadow: 0 0 25px rgba(0,229,255,.2);
    transform: translateY(-1px);
}

/* TERMINAL */

.terminal-line {
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    color: var(--muted);
}

.prompt {
    color: var(--green);
}

.cursor {
    display: inline-block;
    width: 7px;
    height: 13px;
    background: var(--green);
    vertical-align: -2px;
    animation: blink 1s steps(2) infinite;
}

/* FOOTER */

.footer {
    text-align: center;
    color: #3d515b;
    font: 9px "JetBrains Mono", monospace;
    letter-spacing: 1px;
    padding: 35px 0;
}
</style>
"""


# ============================================================
# LOGIN PAGE
# ============================================================

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CT8 // Secure Access</title>
    {{ common_css|safe }}

    <style>
        .login-wrap {
            min-height: calc(100vh - 68px);
            display: grid;
            place-items: center;
            padding: 50px 0;
        }

        .login-panel {
            width: min(460px, 94%);
            animation: fadeUp .7s ease;
        }

        .login-body {
            padding: 34px;
        }

        .eyebrow {
            color: var(--cyan);
            font: 10px "JetBrains Mono", monospace;
            letter-spacing: 2px;
            margin-bottom: 14px;
        }

        h1 {
            margin: 0;
            font-size: 31px;
            letter-spacing: -1px;
        }

        .sub {
            margin-top: 10px;
            color: var(--muted);
            font-size: 13px;
        }

        .warning {
            margin: 26px 0;
            padding: 14px 16px;
            border-left: 3px solid var(--orange);
            background: rgba(255,184,77,.035);
            color: #c6a66e;
            font: 10px "JetBrains Mono", monospace;
            line-height: 1.7;
        }

        label {
            display: block;
            color: #8ea2ab;
            font: 10px "JetBrains Mono", monospace;
            margin: 18px 0 7px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        input {
            width: 100%;
            padding: 14px;
            border: 1px solid var(--border);
            background: #05090d;
            color: var(--text);
            outline: none;
            font: 12px "JetBrains Mono", monospace;
            transition: .25s;
        }

        input:focus {
            border-color: var(--cyan);
            box-shadow: 0 0 20px rgba(0,229,255,.08);
        }

        .login-btn {
            width: 100%;
            margin-top: 24px;
        }

        .error {
            margin: 18px 0;
            padding: 12px;
            border: 1px solid rgba(255,83,100,.35);
            background: rgba(255,83,100,.045);
            color: var(--red);
            font: 10px "JetBrains Mono", monospace;
        }

        .login-note {
            margin-top: 24px;
            color: #526771;
            font: 9px "JetBrains Mono", monospace;
            line-height: 1.8;
        }
    </style>
</head>

<body>

<header class="topbar">
    <div class="brand">
        <div class="brand-mark">C8</div>
        <div class="brand-name">CYBERTEC<span>8</span></div>
    </div>

    <div class="top-status">
        <span class="status-dot"></span>
        SECURE CHANNEL
    </div>
</header>

<div class="login-wrap">

    <section class="panel login-panel">

        <div class="panel-header">
            <span>CT8 // AUTHENTICATION GATEWAY</span>
            <span class="panel-code">01</span>
        </div>

        <div class="login-body">

            <div class="eyebrow">INTERNAL SECURITY OPERATIONS</div>

            <h1>Secure Access</h1>

            <div class="sub">
                Authenticate to access the Cybertec8 incident environment.
            </div>

            <div class="warning">
                [!] RESTRICTED ENVIRONMENT<br>
                Authorized personnel only.
            </div>

            {% if error %}
                <div class="error">
                    [AUTH ERROR] {{ error }}
                </div>
            {% endif %}

            <form method="POST">

                <label>Username</label>
                <input
                    name="username"
                    placeholder="enter username"
                    autocomplete="off"
                    required
                >

                <label>Password</label>
                <input
                    name="password"
                    type="password"
                    placeholder="enter password"
                    required
                >

                <button class="btn login-btn" type="submit">
                    [ AUTHENTICATE ]
                </button>

            </form>

            <div class="login-note">
                <span class="prompt">root@ct8</span>:~$ access_control --verify<br>
                authorization gateway online<span class="cursor"></span>
            </div>

        </div>
    </section>

</div>

<div class="footer">
    CYBERTEC8 SECURITY OPERATIONS // CT8-IR // AUTH-GATE
</div>

</body>
</html>
"""


# ============================================================
# DASHBOARD
# ============================================================

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CT8 // Security Portal</title>
    {{ common_css|safe }}

    <style>
        .dashboard {
            padding: 42px 0 0;
            animation: fadeUp .6s ease;
        }

        .hero {
            display: flex;
            justify-content: space-between;
            align-items: end;
            margin-bottom: 28px;
        }

        .eyebrow {
            color: var(--cyan);
            font: 10px "JetBrains Mono", monospace;
            letter-spacing: 2px;
            margin-bottom: 9px;
        }

        h1 {
            margin: 0;
            font-size: 30px;
        }

        .hero-sub {
            color: var(--muted);
            margin-top: 8px;
            font-size: 12px;
        }

        .user-chip {
            padding: 10px 14px;
            border: 1px solid var(--border);
            color: var(--muted);
            font: 10px "JetBrains Mono", monospace;
        }

        .user-chip strong {
            color: var(--green);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3,1fr);
            gap: 15px;
            margin-bottom: 18px;
        }

        .stat {
            padding: 20px;
            animation: fadeUp .7s ease;
        }

        .stat-label {
            color: var(--muted);
            font: 9px "JetBrains Mono", monospace;
            letter-spacing: 1px;
        }

        .stat-value {
            margin-top: 12px;
            font: 600 18px "JetBrains Mono", monospace;
            color: var(--cyan);
        }

        .content-grid {
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 18px;
        }

        .card-body {
            padding: 24px;
        }

        .card-title {
            margin: 0;
            font-size: 17px;
        }

        .card-text {
            color: var(--muted);
            font-size: 12px;
            line-height: 1.8;
            margin: 12px 0 22px;
        }

        .incident-link {
            display: inline-block;
            text-decoration: none;
        }

        .session-box {
            font: 10px "JetBrains Mono", monospace;
            line-height: 2;
            color: var(--muted);
        }

        .session-box .green {
            color: var(--green);
        }

        .session-box .cyan {
            color: var(--cyan);
        }

        .logout {
            margin-top: 20px;
            display: inline-block;
            color: #657780;
            font: 10px "JetBrains Mono", monospace;
            text-decoration: none;
        }

        .logout:hover {
            color: var(--red);
        }

        @media(max-width:800px) {
            .stats,
            .content-grid {
                grid-template-columns: 1fr;
            }

            .hero {
                display: block;
            }

            .user-chip {
                display: inline-block;
                margin-top: 18px;
            }
        }
    </style>
</head>

<body>

<header class="topbar">
    <div class="brand">
        <div class="brand-mark">C8</div>
        <div class="brand-name">CYBERTEC<span>8</span></div>
    </div>

    <div class="top-status">
        <span class="status-dot"></span>
        SYSTEM ONLINE
    </div>
</header>

<main class="shell dashboard">

    <section class="hero">
        <div>
            <div class="eyebrow">CT8 // INTERNAL SECURITY PORTAL</div>
            <h1>Operations Dashboard</h1>
            <div class="hero-sub">
                Incident monitoring and restricted resource management.
            </div>
        </div>

        <div class="user-chip">
            USER:
            <strong>{{ username }}</strong>
            &nbsp; // &nbsp;
            ROLE:
            <strong>{{ role }}</strong>
        </div>
    </section>

    <section class="stats">

        <div class="panel stat">
            <div class="stat-label">SYSTEM STATUS</div>
            <div class="stat-value">ONLINE</div>
        </div>

        <div class="panel stat">
            <div class="stat-label">ACCESS LEVEL</div>
            <div class="stat-value">{{ role|upper }}</div>
        </div>

        <div class="panel stat">
            <div class="stat-label">INCIDENT CHANNEL</div>
            <div class="stat-value">CT8-IR</div>
        </div>

    </section>

    <section class="content-grid">

        <div class="panel">

            <div class="panel-header">
                <span>INCIDENT RECORDS</span>
                <span class="panel-code">SEC-11</span>
            </div>

            <div class="card-body">

                <h2 class="card-title">
                    Internal Security Incidents
                </h2>

                <p class="card-text">
                    Security incident records contain restricted
                    investigation material. Access is controlled
                    according to the current authorization context.
                </p>

                <a class="btn incident-link" href="/incident">
                    OPEN INCIDENT RECORDS →
                </a>

            </div>
        </div>

        <div class="panel">

            <div class="panel-header">
                <span>SESSION MONITOR</span>
                <span class="panel-code">LIVE</span>
            </div>

            <div class="card-body">

                <div class="session-box">
                    <span class="cyan">SESSION</span> :: ACTIVE<br>
                    <span class="cyan">USERNAME</span> :: {{ username }}<br>
                    <span class="cyan">ROLE</span> :: <span class="green">{{ role }}</span><br>
                    <span class="cyan">CHANNEL</span> :: ENCRYPTED<br>
                    <span class="cyan">STATUS</span> :: <span class="green">AUTHORIZED</span>
                </div>

                <a class="logout" href="/logout">
                    [ TERMINATE SESSION ]
                </a>

            </div>
        </div>

    </section>

</main>

<div class="footer">
    CYBERTEC8 SECURITY OPERATIONS // CT8-IR
</div>

</body>
</html>
"""


# ============================================================
# INCIDENT PAGE
# ============================================================

INCIDENT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CT8 // Restricted Incident</title>
    {{ common_css|safe }}

    <style>
        .incident-wrap {
            width: min(900px, 92%);
            margin: 55px auto;
            animation: fadeUp .65s ease;
        }

        .danger-header {
            border-color: rgba(255,83,100,.35);
        }

        .danger-code {
            color: var(--red);
        }

        .incident-body {
            padding: 32px;
        }

        .classification {
            display: inline-block;
            padding: 7px 10px;
            border: 1px solid rgba(255,83,100,.35);
            color: var(--red);
            background: rgba(255,83,100,.04);
            font: 9px "JetBrains Mono", monospace;
            letter-spacing: 1px;
        }

        h1 {
            margin: 20px 0 8px;
            font-size: 29px;
        }

        .sub {
            color: var(--muted);
            font-size: 12px;
        }

        .incident-grid {
            display: grid;
            grid-template-columns: repeat(2,1fr);
            gap: 12px;
            margin: 28px 0;
        }

        .info {
            padding: 16px;
            border: 1px solid var(--border);
            background: rgba(0,0,0,.15);
        }

        .info-label {
            color: var(--muted);
            font: 9px "JetBrains Mono", monospace;
        }

        .info-value {
            margin-top: 8px;
            color: var(--text);
            font: 11px "JetBrains Mono", monospace;
        }

        .privileged {
            color: var(--green);
        }

        .evidence {
            margin-top: 24px;
            padding: 22px;
            background: #03070a;
            border: 1px solid rgba(57,255,136,.35);
            box-shadow: inset 0 0 35px rgba(57,255,136,.025);
        }

        .evidence-title {
            color: var(--green);
            font: 10px "JetBrains Mono", monospace;
            margin-bottom: 15px;
        }

        .flag {
            padding: 17px;
            border: 1px solid #1d4731;
            background: rgba(57,255,136,.035);
            color: var(--green);
            font: 600 13px "JetBrains Mono", monospace;
            word-break: break-all;
            text-shadow: 0 0 10px rgba(57,255,136,.25);
        }

        .back {
            display: inline-block;
            margin-top: 22px;
            color: var(--muted);
            text-decoration: none;
            font: 10px "JetBrains Mono", monospace;
        }

        .back:hover {
            color: var(--cyan);
        }

        @media(max-width:650px) {
            .incident-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>

<header class="topbar">
    <div class="brand">
        <div class="brand-mark">C8</div>
        <div class="brand-name">CYBERTEC<span>8</span></div>
    </div>

    <div class="top-status">
        <span class="status-dot"></span>
        INCIDENT SYSTEM
    </div>
</header>

<div class="incident-wrap">

    <section class="panel">

        <div class="panel-header danger-header">
            <span>CT8 // RESTRICTED INCIDENT RECORD</span>
            <span class="danger-code">PRIV-ACCESS</span>
        </div>

        <div class="incident-body">

            <span class="classification">
                INTERNAL SECURITY REVIEW
            </span>

            <h1>Restricted Incident Record</h1>

            <div class="sub">
                Privileged incident information has been accessed.
            </div>

            <div class="incident-grid">

                <div class="info">
                    <div class="info-label">INCIDENT ID</div>
                    <div class="info-value">CT8-INC-2026-11</div>
                </div>

                <div class="info">
                    <div class="info-label">AUTHORIZATION</div>
                    <div class="info-value privileged">{{ role|upper }}</div>
                </div>

                <div class="info">
                    <div class="info-label">CLASSIFICATION</div>
                    <div class="info-value">CONFIDENTIAL</div>
                </div>

                <div class="info">
                    <div class="info-label">STATUS</div>
                    <div class="info-value">INTERNAL SECURITY REVIEW</div>
                </div>

            </div>

            <div class="evidence">

                <div class="evidence-title">
                    > PRIVILEGED INCIDENT DATA
                </div>

                <div class="flag">
                    {{ flag }}
                </div>

            </div>

            <a class="back" href="/dashboard">
                ← RETURN TO DASHBOARD
            </a>

        </div>
    </section>

</div>

<div class="footer">
    CYBERTEC8 SECURITY OPERATIONS // RESTRICTED EVIDENCE SYSTEM
</div>

</body>
</html>
"""


# ============================================================
# APPLICATION LOGIC — UNCHANGED
# ============================================================

def encode_session(data):
    """
    Deliberately weak session representation for the CTF.
    The authorization context is stored in a client-readable,
    client-modifiable cookie.
    """
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode()


def decode_session(value):
    try:
        raw = base64.urlsafe_b64decode(value.encode())
        return json.loads(raw.decode())
    except Exception:
        return None


@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = USERS.get(username)

        if user and user["password"] == password:
            session.clear()

            response = make_response(
                redirect(url_for("dashboard"))
            )

            session_data = {
                "username": username,
                "role": user["role"]
            }

            response.set_cookie(
                "ct8_session",
                encode_session(session_data),
                httponly=False
            )

            return response

        error = "Invalid username or password."

    return render_template_string(
        LOGIN_PAGE,
        error=error,
        common_css=COMMON_CSS
    )


@app.route("/dashboard")
def dashboard():
    cookie = request.cookies.get("ct8_session")
    data = decode_session(cookie) if cookie else None

    if not data:
        return redirect(url_for("login"))

    return render_template_string(
        DASHBOARD_PAGE,
        username=data.get("username", "unknown"),
        role=data.get("role", "unknown"),
        common_css=COMMON_CSS
    )


@app.route("/incident")
def incident():
    cookie = request.cookies.get("ct8_session")
    data = decode_session(cookie) if cookie else None

    if not data:
        return redirect(url_for("login"))

    role = data.get("role", "employee")

    if role != "admin":
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CT8 // Access Denied</title>
            %s
            <style>
                .denied {
                    width: min(650px, 92%%);
                    margin: 100px auto;
                    animation: fadeUp .6s ease;
                }

                .denied-body {
                    padding: 35px;
                    text-align: center;
                }

                .icon {
                    width: 65px;
                    height: 65px;
                    margin: 0 auto 22px;
                    border: 1px solid var(--red);
                    color: var(--red);
                    display: grid;
                    place-items: center;
                    font: 700 22px "JetBrains Mono", monospace;
                    box-shadow: 0 0 25px rgba(255,83,100,.08);
                }

                h1 {
                    margin: 0;
                    color: var(--red);
                    font-size: 26px;
                }

                .message {
                    color: var(--muted);
                    font-size: 12px;
                    line-height: 1.8;
                    margin: 15px 0 25px;
                }

                .auth {
                    padding: 15px;
                    background: #03070a;
                    border: 1px solid var(--border);
                    color: var(--muted);
                    font: 10px "JetBrains Mono", monospace;
                }

                .auth strong {
                    color: var(--orange);
                }

                .back {
                    display: inline-block;
                    margin-top: 24px;
                    color: var(--cyan);
                    text-decoration: none;
                    font: 10px "JetBrains Mono", monospace;
                }
            </style>
        </head>

        <body>

        <header class="topbar">
            <div class="brand">
                <div class="brand-mark">C8</div>
                <div class="brand-name">CYBERTEC<span>8</span></div>
            </div>

            <div class="top-status">
                <span class="status-dot"></span>
                ACCESS CONTROL
            </div>
        </header>

        <div class="denied">

            <section class="panel">

                <div class="panel-header">
                    <span>CT8 // AUTHORIZATION FAILURE</span>
                    <span style="color:var(--red)">403</span>
                </div>

                <div class="denied-body">

                    <div class="icon">!</div>

                    <h1>ACCESS DENIED</h1>

                    <div class="message">
                        This incident record requires privileged authorization.
                    </div>

                    <div class="auth">
                        CURRENT AUTHORIZATION CONTEXT:
                        <strong>%s</strong>
                    </div>

                    <a class="back" href="/dashboard">
                        ← RETURN TO DASHBOARD
                    </a>

                </div>

            </section>

        </div>

        <div class="footer">
            CYBERTEC8 SECURITY OPERATIONS // ACCESS CONTROL
        </div>

        </body>
        </html>
        """ % (COMMON_CSS, role), 403

    return render_template_string(
        INCIDENT_PAGE,
        role=role,
        flag=FLAG,
        common_css=COMMON_CSS
    )


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("ct8_session")
    session.clear()
    return response


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )