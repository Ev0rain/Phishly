#!/usr/bin/env python3
"""
Seed Landing Pages Script

Imports pre-built landing page templates from templates/landing_pages
into the database with self-contained HTML (inline CSS).

Usage:
    cd webadmin
    uv run python scripts/seed_landing_pages.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database import db
from db.models import LandingPage, AdminUser


# Landing page templates with inline CSS (self-contained)

UPS_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UPS - Log In</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #351c15;
            padding: 1rem 2rem;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .logo svg { width: 45px; height: 52px; }
        .main {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 3rem 1rem;
        }
        .login-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 2.5rem;
            width: 100%;
            max-width: 420px;
        }
        h1 {
            font-size: 1.75rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #121212;
        }
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #333;
        }
        input[type="text"],
        input[type="email"],
        input[type="password"] {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 1rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #351c15;
            box-shadow: 0 0 0 3px rgba(53,28,21,0.1);
        }
        .btn-primary {
            width: 100%;
            padding: 1rem;
            background: #351c15;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-primary:hover { background: #4a2a20; }
        .divider {
            display: flex;
            align-items: center;
            margin: 2rem 0;
            color: #666;
        }
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #ddd;
        }
        .divider span { padding: 0 1rem; font-size: 0.875rem; }
        .social-btns {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        .social-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.875rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        .social-btn:hover { background: #f5f5f5; }
        .create-account {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #eee;
        }
        .create-account a {
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }
        .footer {
            background: #351c15;
            color: white;
            padding: 1rem;
            text-align: center;
            font-size: 0.875rem;
        }
        .footer a { color: #ffc400; text-decoration: none; }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <svg viewBox="0 0 45 52" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.5 0L45 13v26L22.5 52 0 39V13L22.5 0z" fill="#351c15"/>
                <path d="M22.5 4L41 15v22l-18.5 11L4 37V15L22.5 4z" fill="#ffc400"/>
                <text x="50%" y="60%" text-anchor="middle" fill="#351c15" font-size="18" font-weight="bold">ups</text>
            </svg>
        </div>
    </header>

    <main class="main">
        <div class="login-card">
            <h1>Log In</h1>
            <p class="subtitle">Enter your UPS.com User ID</p>

            <form method="POST" action="/api/submit">
                <input type="hidden" name="page_type" value="ups_login">
                <div class="form-group">
                    <label for="username">User ID or Email</label>
                    <input type="text" id="username" name="username" required autocomplete="email" autofocus>
                </div>

                <button type="submit" class="btn-primary">Continue</button>
            </form>

            <div class="divider"><span>Or continue with</span></div>

            <div class="social-btns">
                <button type="button" class="social-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
                    Continue with Google
                </button>
                <button type="button" class="social-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#000" d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.53 4.08zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
                    Continue with Apple
                </button>
            </div>

            <div class="create-account">
                <p>New to UPS? <a href="#">Create an Account</a></p>
            </div>
        </div>
    </main>

    <footer class="footer">
        <p>&copy; 1994-2024 United Parcel Service of America, Inc. All rights reserved. | <a href="#">Privacy Policy</a></p>
    </footer>
</body>
</html>"""


UPS_PASSWORD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UPS - Enter Password</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #351c15;
            padding: 1rem 2rem;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .logo svg { width: 45px; height: 52px; }
        .main {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 3rem 1rem;
        }
        .login-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 2.5rem;
            width: 100%;
            max-width: 420px;
        }
        h1 {
            font-size: 1.75rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #121212;
        }
        .user-info {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #f8f8f8;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1.5rem;
        }
        .user-email {
            font-weight: 500;
            color: #333;
        }
        .edit-link {
            color: #0066cc;
            text-decoration: none;
            font-size: 0.875rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #333;
        }
        input[type="password"] {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 1rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #351c15;
            box-shadow: 0 0 0 3px rgba(53,28,21,0.1);
        }
        .btn-primary {
            width: 100%;
            padding: 1rem;
            background: #351c15;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-primary:hover { background: #4a2a20; }
        .forgot-password {
            text-align: center;
            margin-top: 1rem;
        }
        .forgot-password a {
            color: #0066cc;
            text-decoration: none;
            font-size: 0.875rem;
        }
        .footer {
            background: #351c15;
            color: white;
            padding: 1rem;
            text-align: center;
            font-size: 0.875rem;
        }
        .footer a { color: #ffc400; text-decoration: none; }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <svg viewBox="0 0 45 52" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.5 0L45 13v26L22.5 52 0 39V13L22.5 0z" fill="#351c15"/>
                <path d="M22.5 4L41 15v22l-18.5 11L4 37V15L22.5 4z" fill="#ffc400"/>
                <text x="50%" y="60%" text-anchor="middle" fill="#351c15" font-size="18" font-weight="bold">ups</text>
            </svg>
        </div>
    </header>

    <main class="main">
        <div class="login-card">
            <h1>Enter Password</h1>

            <div class="user-info">
                <span class="user-email" id="displayEmail">user@example.com</span>
                <a href="#" class="edit-link" onclick="history.back()">Edit</a>
            </div>

            <form method="POST" action="/api/submit">
                <input type="hidden" name="page_type" value="ups_password">
                <input type="hidden" name="username" id="hiddenUsername" value="">

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required autocomplete="current-password" autofocus>
                </div>

                <button type="submit" class="btn-primary">Log In</button>
            </form>

            <div class="forgot-password">
                <a href="#">Forgot User ID or Password?</a>
            </div>
        </div>
    </main>

    <footer class="footer">
        <p>&copy; 1994-2024 United Parcel Service of America, Inc. All rights reserved. | <a href="#">Privacy Policy</a></p>
    </footer>

    <script>
        // Get username from URL query parameter
        const params = new URLSearchParams(window.location.search);
        const username = params.get('u') || params.get('username') || 'user@example.com';
        document.getElementById('displayEmail').textContent = username;
        document.getElementById('hiddenUsername').value = username;
    </script>
</body>
</html>"""


AMAZON_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amazon Sign-In</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Amazon Ember', Arial, sans-serif;
            background: #fff;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            padding: 1rem;
            border-bottom: 1px solid #ddd;
        }
        .logo {
            width: 100px;
            margin: 0.5rem 0;
        }
        .main {
            max-width: 350px;
            margin: 1rem auto;
            padding: 1rem;
        }
        .signin-box {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 1.25rem;
        }
        h1 {
            font-size: 1.75rem;
            font-weight: 400;
            margin-bottom: 1.25rem;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        label {
            display: block;
            font-weight: 700;
            font-size: 0.8125rem;
            margin-bottom: 0.25rem;
        }
        input[type="email"],
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #888;
            border-radius: 3px;
            font-size: 0.8125rem;
        }
        input:focus {
            outline: none;
            border-color: #e77600;
            box-shadow: 0 0 3px 2px rgba(228,121,17,.5);
        }
        .btn-primary {
            width: 100%;
            padding: 0.5rem;
            background: linear-gradient(to bottom, #f7dfa5, #f0c14b);
            border: 1px solid #a88734;
            border-radius: 3px;
            font-size: 0.8125rem;
            cursor: pointer;
            margin-top: 0.75rem;
        }
        .btn-primary:hover {
            background: linear-gradient(to bottom, #f5d78e, #eeb933);
        }
        .conditions {
            font-size: 0.75rem;
            color: #111;
            margin-top: 1rem;
        }
        .conditions a {
            color: #0066c0;
            text-decoration: none;
        }
        .divider {
            display: flex;
            align-items: center;
            margin: 1.25rem 0;
        }
        .divider::before,
        .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #ddd;
        }
        .divider span {
            padding: 0 0.75rem;
            color: #767676;
            font-size: 0.75rem;
        }
        .btn-secondary {
            width: 100%;
            padding: 0.5rem;
            background: linear-gradient(to bottom, #f7f8fa, #e7e9ec);
            border: 1px solid #adb1b8;
            border-radius: 3px;
            font-size: 0.8125rem;
            cursor: pointer;
        }
        .footer {
            text-align: center;
            font-size: 0.6875rem;
            color: #555;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        .footer a {
            color: #0066c0;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <header class="header">
        <svg class="logo" viewBox="0 0 100 30" xmlns="http://www.w3.org/2000/svg">
            <path fill="#232f3e" d="M.0 25.4c.3-.1 35.5-13 63.4-13 13.9 0 23.2 2.9 32.5 5.8.5.2.9.8.4 1.3-.3.4-.9.5-1.3.3C86.3 17 77.5 14 64.1 14c-27.6 0-62.2 12.9-62.5 13-.5.2-1-.1-1.2-.5-.2-.4 0-.9.4-1.1zm58.4-4.4c0-2.3.7-4.1 2.2-5.5 1.5-1.4 3.5-2.1 5.9-2.1 2.2 0 4 .6 5.4 1.9 1.4 1.3 2.1 3.1 2.1 5.4 0 2.4-.7 4.3-2.1 5.6-1.4 1.4-3.3 2.1-5.5 2.1-2.3 0-4.2-.7-5.7-2-1.5-1.3-2.3-3.1-2.3-5.4zm3.9.1c0 1.4.4 2.5 1.1 3.3.8.8 1.7 1.2 2.9 1.2 1.3 0 2.3-.4 3-1.2.7-.8 1.1-2 1.1-3.5 0-1.5-.4-2.6-1.1-3.4-.7-.8-1.7-1.1-2.9-1.1-1.2 0-2.2.4-2.9 1.2-.8.8-1.2 1.9-1.2 3.5zM5.4 17.9l-1.2 5.6h3.7l1.2-5.6H5.4zm17.1.4c0 .7-.2 1.3-.6 1.9-.4.5-1 .9-1.7 1.1.6.2 1 .5 1.3.9.2.4.4.9.4 1.5v1.1c0 .3 0 .5.1.8l.1.3v.1h-3.6l-.1-.2v-.1c-.1-.2-.1-.5-.1-.8v-1c0-.6-.1-1-.4-1.2-.3-.2-.7-.3-1.3-.3h-1.3l-.8 3.6H11l2.3-10.8h5.2c1.4 0 2.4.3 3.1.9.7.6 1 1.4 1 2.4zm-3.7.1c0-.4-.1-.6-.4-.8-.3-.2-.7-.3-1.2-.3h-1.5l-.5 2.6h1.6c.6 0 1.1-.1 1.4-.4.4-.3.6-.6.6-1.1zm28.7-5h3.8l1.6 10.8h-3.9l-.2-1.6H45l-.8 1.6h-3.9l6.2-10.8zm.6 6.4h2l-.4-3-1.6 3zm-4.1.1c0 1-.3 1.9-.8 2.6-.5.8-1.3 1.3-2.2 1.6-.9.3-2.1.5-3.6.5-1.1 0-2-.1-2.8-.2-.8-.1-1.6-.4-2.3-.7l.6-2.9c.7.3 1.4.6 2.2.7.8.2 1.5.3 2.3.3 1.1 0 1.9-.1 2.3-.4.5-.3.7-.7.7-1.2 0-.4-.2-.7-.5-.9-.3-.2-.9-.5-1.8-.7l-1.3-.3c-1.2-.3-2.1-.8-2.7-1.4-.6-.6-.9-1.4-.9-2.5 0-1.6.6-2.7 1.7-3.5 1.1-.8 2.7-1.2 4.6-1.2 1 0 1.8.1 2.6.2.8.1 1.5.3 2.2.6l-.7 2.8c-1.3-.5-2.6-.7-4-.7-.9 0-1.6.1-2 .4-.4.2-.7.6-.7 1 0 .4.1.6.4.8.3.2.8.4 1.5.6l1.6.4c1.2.3 2.2.8 2.8 1.4.5.7.8 1.5.8 2.6zm8.2 1l-2.1 3.3H46l4.9-6.7-2-6.1h4l.8 3.1 2.2-3.1h4.2l-4.6 5.7 2.3 7.1h-4l-1.1-3.3zm30.9-7.5h3.8l-2.2 10.8h-3.8l1.5-7.2-3.2 4.9h-2.7l-.6-4.9-1.5 7.2h-3.8L73 13.4h5.9l.5 4.9 2.7-4.9z"/>
        </svg>
    </header>

    <main class="main">
        <div class="signin-box">
            <h1>Sign in</h1>

            <form method="POST" action="/api/submit">
                <input type="hidden" name="page_type" value="amazon_login">

                <div class="form-group">
                    <label for="email">Email or mobile phone number</label>
                    <input type="email" id="email" name="email" required autofocus>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>

                <button type="submit" class="btn-primary">Sign in</button>
            </form>

            <p class="conditions">
                By continuing, you agree to Amazon's <a href="#">Conditions of Use</a> and <a href="#">Privacy Notice</a>.
            </p>

            <div class="divider"><span>New to Amazon?</span></div>

            <button type="button" class="btn-secondary">Create your Amazon account</button>
        </div>
    </main>

    <footer class="footer">
        <p><a href="#">Conditions of Use</a> &nbsp; <a href="#">Privacy Notice</a> &nbsp; <a href="#">Help</a></p>
        <p>&copy; 1996-2024, Amazon.com, Inc. or its affiliates</p>
    </footer>
</body>
</html>"""


POST_CAMPAIGN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Awareness - Phishly</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --page-bg: #030914;
            --card-bg: rgba(7, 16, 36, 0.85);
            --card-border: rgba(77, 232, 255, 0.25);
            --text: #f6f8ff;
            --muted: #a3b5d9;
            --accent: #4de8ff;
            --accent-strong: #9e6bff;
        }

        *, *::before, *::after { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            background: radial-gradient(circle at 20% 20%, rgba(77, 232, 255, 0.12), transparent 55%),
                        radial-gradient(circle at 80% 0%, rgba(155, 107, 255, 0.16), transparent 50%),
                        linear-gradient(150deg, #02050c, #050c18 45%, #07142d),
                        var(--page-bg);
            color: var(--text);
            font-family: 'Inter', system-ui, sans-serif;
            line-height: 1.7;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }

        .hero {
            text-align: center;
            padding: 3rem 0;
        }

        .hero-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }

        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.25em;
            font-size: 0.8rem;
            color: var(--accent);
            font-weight: 600;
            margin-bottom: 1rem;
        }

        h1 {
            font-size: clamp(2rem, 5vw, 3rem);
            margin-bottom: 1rem;
            line-height: 1.2;
        }

        .subtitle {
            color: var(--muted);
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto 2rem;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 1.5rem;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 25px 60px rgba(3, 7, 18, 0.6);
        }

        .card h2 {
            color: var(--accent);
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }

        .card p {
            color: var(--muted);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }

        .grid-item {
            background: rgba(9, 18, 42, 0.75);
            border-radius: 1rem;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }

        .grid-item h3 {
            color: var(--accent);
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }

        .grid-item p {
            color: var(--muted);
            font-size: 0.95rem;
        }

        .checklist {
            list-style: none;
            padding: 0;
        }

        .checklist li {
            position: relative;
            padding-left: 2rem;
            margin-bottom: 0.75rem;
            color: var(--muted);
        }

        .checklist li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: var(--accent);
            font-weight: bold;
        }

        .contact-card {
            background: linear-gradient(135deg, rgba(6, 15, 35, 0.9), rgba(16, 0, 43, 0.75));
            border-color: var(--accent-strong);
            text-align: center;
        }

        .contact-card a {
            color: var(--accent);
            text-decoration: none;
            font-weight: 600;
        }

        footer {
            text-align: center;
            padding: 2rem;
            color: var(--muted);
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="hero">
            <div class="hero-icon">🛡️</div>
            <p class="eyebrow">Phishing Awareness Update</p>
            <h1>You participated in our phishing simulation</h1>
            <p class="subtitle">
                Thank you for taking part in the recent security exercise. The simulated email was designed
                to look convincing - here's what to do if this ever happens for real.
            </p>
        </header>

        <main>
            <div class="card">
                <h2>What this means</h2>
                <p>
                    Falling for the exercise doesn't mean you failed. It means attackers are good at their job
                    and we need to stay sharp. Review the guidance below and keep it in mind the next time
                    something suspicious hits your inbox.
                </p>
            </div>

            <div class="grid">
                <div class="grid-item">
                    <h3>1. Pause before you click</h3>
                    <p>Hover over links to verify the destination, and double-check sender addresses.
                       If the tone is urgent or unexpected, confirm through a secondary channel.</p>
                </div>
                <div class="grid-item">
                    <h3>2. Report suspicious messages</h3>
                    <p>Use the "Report Phish" button or forward the email to your security team right away.
                       Early reporting keeps everyone safe.</p>
                </div>
                <div class="grid-item">
                    <h3>3. Reset if you entered credentials</h3>
                    <p>If you typed your username or password anywhere questionable, reset it immediately
                       and notify IT so they can monitor for misuse.</p>
                </div>
                <div class="grid-item">
                    <h3>4. Share what you learned</h3>
                    <p>Talk with your team about the clues you missed. Turning your experience into a
                       teachable moment helps strengthen our human firewall.</p>
                </div>
            </div>

            <div class="card">
                <h2>Keep this checklist handy</h2>
                <ul class="checklist">
                    <li>Bookmark the reporting instructions</li>
                    <li>Enable multi-factor authentication everywhere</li>
                    <li>Verify sensitive requests with a quick call or chat</li>
                    <li>Celebrate teammates who report suspicious emails</li>
                </ul>
            </div>

            <div class="card contact-card">
                <h2>Need help?</h2>
                <p>Have questions about the campaign or what to do next? Reach out to your security team.</p>
                <p><a href="mailto:security@example.com">security@example.com</a></p>
            </div>
        </main>

        <footer>
            <p>Security Awareness Team · Building resilient habits together</p>
            <p>Powered by Phishly</p>
        </footer>
    </div>
</body>
</html>"""


MICROSOFT_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in to your account</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background: #f2f2f2;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: white;
            width: 100%;
            max-width: 440px;
            min-height: 338px;
            padding: 44px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        .logo {
            margin-bottom: 1rem;
        }
        .logo svg { height: 24px; }
        h1 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        input[type="email"],
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 0.5rem 0;
            border: none;
            border-bottom: 1px solid #666;
            font-size: 0.9375rem;
            outline: none;
        }
        input:focus {
            border-bottom-color: #0067b8;
            border-bottom-width: 2px;
        }
        .forgot {
            font-size: 0.8125rem;
            color: #0067b8;
            text-decoration: none;
            display: block;
            margin: 1rem 0;
        }
        .btn-primary {
            width: 100%;
            padding: 0.5rem 1.25rem;
            background: #0067b8;
            color: white;
            border: none;
            font-size: 0.9375rem;
            cursor: pointer;
            margin-top: 1rem;
        }
        .btn-primary:hover { background: #005a9e; }
        .options {
            font-size: 0.8125rem;
            margin-top: 1rem;
        }
        .options a {
            color: #0067b8;
            text-decoration: none;
        }
        .footer-text {
            font-size: 0.75rem;
            color: #666;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <svg viewBox="0 0 108 24" xmlns="http://www.w3.org/2000/svg">
                <path fill="#737373" d="M44.836 4.6v14.8h-2.4V7.583H42.4L38.119 19.4h-1.588L32.168 7.583h-.037V19.4h-2.246V4.6h3.2l3.9 10.854h.073L40.966 4.6h3.87zm3.474 3.592a1.325 1.325 0 01-.423-.987 1.3 1.3 0 01.423-.974 1.417 1.417 0 011.011-.4 1.383 1.383 0 011.011.4 1.312 1.312 0 01.41.974 1.337 1.337 0 01-.41.987 1.362 1.362 0 01-1.011.411 1.4 1.4 0 01-1.011-.411zm-.037 2.283h2.173V19.4h-2.173V10.475zm10.361-.242a3.665 3.665 0 012.6.921 3.539 3.539 0 01.979 2.711v5.535h-2.16v-5.15a2.423 2.423 0 00-.532-1.71 1.947 1.947 0 00-1.5-.575 2.063 2.063 0 00-1.612.672 2.762 2.762 0 00-.606 1.919v4.844h-2.17V10.475h2.059v1.315h.049a2.7 2.7 0 011.074-1.074 3.227 3.227 0 011.819-.483zm8.287 9.408a4.717 4.717 0 01-2.209-.508 3.658 3.658 0 01-1.517-1.47 4.549 4.549 0 01-.545-2.264 4.7 4.7 0 01.533-2.283 3.772 3.772 0 011.5-1.508 4.447 4.447 0 012.2-.532 4.12 4.12 0 012.612.787 3.867 3.867 0 011.376 2.174l-2.1.484a2.065 2.065 0 00-.69-1.155 1.88 1.88 0 00-1.237-.4 1.952 1.952 0 00-1.573.69 2.879 2.879 0 00-.581 1.919 2.7 2.7 0 00.59 1.867 2 2 0 001.564.666 1.971 1.971 0 001.261-.4 2.09 2.09 0 00.714-1.143l2.124.4a4.227 4.227 0 01-1.452 2.235 4.148 4.148 0 01-2.57.806zm5.574-.241V10.475h2.059v1.339h.049a2.458 2.458 0 01.963-1.119 2.754 2.754 0 011.488-.411 2.5 2.5 0 01.521.049v2.063a3.052 3.052 0 00-.739-.085 2.039 2.039 0 00-1.612.654 2.589 2.589 0 00-.581 1.79v4.645zm5.505-4.462a4.66 4.66 0 01.545-2.283 3.827 3.827 0 011.517-1.5 4.544 4.544 0 012.258-.532 4.37 4.37 0 012.244.545 3.612 3.612 0 011.456 1.5 4.947 4.947 0 01.508 2.27 4.854 4.854 0 01-.52 2.283 3.7 3.7 0 01-1.469 1.508 4.435 4.435 0 01-2.219.532 4.49 4.49 0 01-2.246-.532 3.723 3.723 0 01-1.517-1.5 4.62 4.62 0 01-.557-2.291zm2.234 0a2.823 2.823 0 00.575 1.883 2.057 2.057 0 003.146 0 3.365 3.365 0 000-3.766 2.057 2.057 0 00-3.146 0 2.823 2.823 0 00-.575 1.883zm8.118 2.308a1.242 1.242 0 01.363-.932 1.3 1.3 0 01.945-.356 1.28 1.28 0 01.933.356 1.253 1.253 0 01.363.932 1.207 1.207 0 01-.363.9 1.3 1.3 0 01-.933.345 1.323 1.323 0 01-.945-.345 1.2 1.2 0 01-.363-.9zm5.5-.023a1.336 1.336 0 01.375-.981 1.312 1.312 0 01.969-.387 1.265 1.265 0 01.957.387 1.357 1.357 0 01.363.981 1.311 1.311 0 01-.363.969 1.284 1.284 0 01-.957.375 1.33 1.33 0 01-.969-.375 1.316 1.316 0 01-.375-.969zm5.492.023a1.242 1.242 0 01.363-.932 1.3 1.3 0 01.945-.356 1.28 1.28 0 01.933.356 1.253 1.253 0 01.363.932 1.207 1.207 0 01-.363.9 1.3 1.3 0 01-.933.345 1.323 1.323 0 01-.945-.345 1.2 1.2 0 01-.363-.9z"/>
                <path fill="#f25022" d="M0 0h11.377v11.372H0z"/>
                <path fill="#00a4ef" d="M0 12.623h11.377V24H0z"/>
                <path fill="#7fba00" d="M12.623 0H24v11.372H12.623z"/>
                <path fill="#ffb900" d="M12.623 12.623H24V24H12.623z"/>
            </svg>
        </div>

        <h1>Sign in</h1>

        <form method="POST" action="/api/submit">
            <input type="hidden" name="page_type" value="microsoft_login">

            <div class="form-group">
                <input type="email" name="email" placeholder="Email, phone, or Skype" required autofocus>
            </div>

            <div class="form-group">
                <input type="password" name="password" placeholder="Password" required>
            </div>

            <a href="#" class="forgot">Forgot password?</a>

            <button type="submit" class="btn-primary">Sign in</button>
        </form>

        <div class="options">
            <p>No account? <a href="#">Create one!</a></p>
        </div>

        <p class="footer-text">
            Can't access your account?
        </p>
    </div>
</body>
</html>"""


def seed_landing_pages():
    """Seed the database with pre-built landing page templates."""
    app = create_app()

    with app.app_context():
        # Get or create admin user for created_by
        admin = db.session.query(AdminUser).filter_by(username="admin").first()
        admin_id = admin.id if admin else None

        landing_pages_data = [
            {
                "name": "UPS Login (Username)",
                "url_path": "/ups-login",
                "html_content": UPS_LOGIN_HTML,
                "capture_credentials": True,
                "capture_form_data": True,
                "redirect_url": None,  # Redirect to password page
                "description": "UPS login page - Username/Email collection step",
            },
            {
                "name": "UPS Login (Password)",
                "url_path": "/ups-password",
                "html_content": UPS_PASSWORD_HTML,
                "capture_credentials": True,
                "capture_form_data": True,
                "redirect_url": "https://www.ups.com",
                "description": "UPS login page - Password collection step",
            },
            {
                "name": "Amazon Sign-In",
                "url_path": "/amazon-signin",
                "html_content": AMAZON_LOGIN_HTML,
                "capture_credentials": True,
                "capture_form_data": True,
                "redirect_url": "https://www.amazon.com",
                "description": "Amazon login page with email and password fields",
            },
            {
                "name": "Microsoft Sign-In",
                "url_path": "/microsoft-signin",
                "html_content": MICROSOFT_LOGIN_HTML,
                "capture_credentials": True,
                "capture_form_data": True,
                "redirect_url": "https://www.office.com",
                "description": "Microsoft/Office 365 login page",
            },
            {
                "name": "Security Awareness (Post-Campaign)",
                "url_path": "/awareness",
                "html_content": POST_CAMPAIGN_HTML,
                "capture_credentials": False,
                "capture_form_data": False,
                "redirect_url": None,
                "description": "Educational page shown after phishing simulation - explains what happened and provides guidance",
            },
        ]

        created = 0
        skipped = 0

        for lp_data in landing_pages_data:
            # Check if landing page already exists
            existing = db.session.query(LandingPage).filter_by(url_path=lp_data["url_path"]).first()

            if existing:
                print(f"  [SKIP] {lp_data['name']} - already exists (url: {lp_data['url_path']})")
                skipped += 1
                continue

            landing_page = LandingPage(
                name=lp_data["name"],
                url_path=lp_data["url_path"],
                html_content=lp_data["html_content"],
                capture_credentials=lp_data["capture_credentials"],
                capture_form_data=lp_data["capture_form_data"],
                redirect_url=lp_data["redirect_url"],
                created_by_id=admin_id,
            )

            db.session.add(landing_page)
            print(f"  [CREATE] {lp_data['name']} (url: {lp_data['url_path']})")
            created += 1

        db.session.commit()

        print(f"\nLanding pages seeding complete:")
        print(f"  Created: {created}")
        print(f"  Skipped: {skipped}")
        print(f"  Total in DB: {db.session.query(LandingPage).count()}")


if __name__ == "__main__":
    print("=" * 60)
    print("Phishly Landing Pages Seeder")
    print("=" * 60)
    print()
    seed_landing_pages()
    print()
    print("Done!")
