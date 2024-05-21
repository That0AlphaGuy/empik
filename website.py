from flask import Flask, redirect, url_for, session, request, render_template_string
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = '1242452285552857160'
DISCORD_CLIENT_SECRET = '1242452285552857160'
DISCORD_REDIRECT_URI = 'http://portal.empikrblx.com/auth/discord/callback'
DISCORD_API_BASE_URL = 'https://discord.com/api'

# HTML content template with inline CSS
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Empik Staff Portal</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #333;
            color: #fff;
            padding: 10px 20px;
        }
        .empik-logo h1 {
            font-family: 'EmpikFont'; /* Assuming you have a custom font for Empik */
        }
        .user-info img {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .user-info a {
            color: #fff;
            text-decoration: none;
        }
        main {
            padding: 20px;
        }
        footer {
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 10px 0;
            position: fixed;
            bottom: 0;
            width: 100%;
        }
    </style>
</head>
<body>
    <header>
        <nav>
            <div class="empik-logo">
                <h1>Empik</h1>
            </div>
            <div class="user-info">
                {% if user %}
                    <img src="{{ user.avatar_url }}" alt="User Avatar">
                    <p>Hello, {{ user.username }}!</p>
                    <a href="{{ url_for('logout') }}">Logout</a>
                {% else %}
                    <a href="{{ url_for('login') }}">Login with Discord</a>
                {% endif %}
            </div>
        </nav>
    </header>
    <main>
        <h2>Welcome to the Empik Staff Portal</h2>
        {% if user %}
            <p>Hello, {{ user.username }}!</p>
        {% else %}
            <p>Please log in to access the portal.</p>
        {% endif %}
    </main>
    <footer>
        <p>&copy; 2024 Empik. All rights reserved.</p>
    </footer>
</body>
</html>
"""

# Route for the main page
@app.route('/')
def home():
    user = session.get('user')
    return render_template_string(html_content, user=user)

# Route for initiating the Discord login flow
@app.route('/login')
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify")

# Route for handling the OAuth2 callback from Discord
@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        data = {
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI,
            'scope': 'identify'
        }
        response = requests.post(f"{DISCORD_API_BASE_URL}/oauth2/token", data=data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            if access_token:
                headers = {'Authorization': f'Bearer {access_token}'}
                user_response = requests.get(f"{DISCORD_API_BASE_URL}/users/@me", headers=headers)
                if user_response.status_code == 200:
                    user = user_response.json()
                    session['user'] = user
    return redirect(url_for('home'))

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
