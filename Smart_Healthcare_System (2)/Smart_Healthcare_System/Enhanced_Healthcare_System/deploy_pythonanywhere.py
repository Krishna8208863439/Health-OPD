"""
PythonAnywhere Auto-Deploy Script for kd3114
Run this once to set up/update the deployment.
Usage: python deploy_pythonanywhere.py YOUR_API_TOKEN
Get your API token from: https://www.pythonanywhere.com/user/kd3114/account/#api_token
"""

import sys
import requests
import json

USERNAME = "kd3114"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}"

def api(method, endpoint, data=None, token=None):
    url = API_BASE + endpoint
    headers = {"Authorization": f"Token {token}"}
    if method == "GET":
        r = requests.get(url, headers=headers)
    elif method == "POST":
        r = requests.post(url, headers=headers, data=data)
    elif method == "PATCH":
        r = requests.patch(url, headers=headers, data=data)
    elif method == "DELETE":
        r = requests.delete(url, headers=headers)
    print(f"  {method} {endpoint} -> {r.status_code}")
    try:
        return r.json()
    except:
        return r.text

def run_bash(cmd, token):
    print(f"  BASH: {cmd}")
    r = requests.post(
        f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/consoles/",
        headers={"Authorization": f"Token {token}"},
        data={"executable": "bash", "arguments": "", "working_directory": f"/home/{USERNAME}"}
    )
    if r.status_code not in [200, 201]:
        print(f"  Could not create console: {r.text}")
        return
    console_id = r.json()["id"]
    
    # Send command
    requests.post(
        f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/consoles/{console_id}/send_input/",
        headers={"Authorization": f"Token {token}"},
        data={"input": cmd + "\n"}
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_pythonanywhere.py YOUR_API_TOKEN")
        sys.exit(1)
    
    token = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"  Deploying HealthCare Plus to PythonAnywhere ({USERNAME})")
    print(f"{'='*60}\n")

    # 1. Check existing web apps
    print("[1/6] Checking existing web apps...")
    apps = api("GET", "/webapps/", token=token)
    print(f"  Found: {[a.get('domain_name') for a in apps] if isinstance(apps, list) else apps}")

    domain = f"{USERNAME}.pythonanywhere.com"
    existing = [a for a in apps if a.get("domain_name") == domain] if isinstance(apps, list) else []

    # 2. Clone/update repo
    print("\n[2/6] Cloning/updating GitHub repo...")
    repo_url = "https://github.com/Krishna8208863439/Health-OPD.git"
    project_dir = f"/home/{USERNAME}/Smart_Healthcare_System"
    
    # We'll use the API console for this
    print(f"  Repo: {repo_url}")
    print(f"  Target: {project_dir}")

    # 3. Create or update webapp
    if not existing:
        print("\n[3/6] Creating new web app...")
        result = api("POST", "/webapps/", data={
            "domain_name": domain,
            "python_version": "python312"
        }, token=token)
        print(f"  Result: {result}")
    else:
        print(f"\n[3/6] Web app already exists at {domain}")

    # 4. Set WSGI config
    print("\n[4/6] Updating WSGI configuration...")
    wsgi_path = f"/var/www/{USERNAME}_pythonanywhere_com_wsgi.py"
    wsgi_content = f'''
import sys
import os

project_home = "/home/{USERNAME}/Smart_Healthcare_System/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app as application
'''
    
    r = requests.get(
        f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path{wsgi_path}",
        headers={"Authorization": f"Token {token}"}
    )
    
    r2 = requests.post(
        f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path{wsgi_path}",
        headers={"Authorization": f"Token {token}"},
        files={"content": ("wsgi.py", wsgi_content, "text/plain")}
    )
    print(f"  WSGI write status: {r2.status_code}")

    # 5. Reload webapp
    print("\n[5/6] Reloading web app...")
    result = api("POST", f"/webapps/{domain}/reload/", token=token)
    print(f"  Result: {result}")

    # 6. Done
    print(f"\n[6/6] ✅ DONE!")
    print(f"\n{'='*60}")
    print(f"  🌐 Your app: https://{domain}")
    print(f"{'='*60}\n")
    print("NOTE: First time setup requires:")
    print("  1. Go to https://www.pythonanywhere.com/user/kd3114/consoles/")
    print("  2. Open a Bash console and run:")
    print(f"     cd /home/{USERNAME}")
    print(f"     git clone https://github.com/Krishna8208863439/Health-OPD.git Smart_Healthcare_System")
    print(f"     cd Smart_Healthcare_System/'Smart_Healthcare_System (2)'/Smart_Healthcare_System/Enhanced_Healthcare_System")
    print(f"     pip3.12 install --user flask==3.0.0 flask-login==0.6.3 werkzeug==3.0.1 pandas scikit-learn reportlab numpy")
    print(f"  3. Then reload the web app from the Web tab")
