import requests, subprocess

def get_local_version(package_name: str) -> str:
    try:
        result = subprocess.run(
            [f"pip show {package_name}"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"): return line.split()[1]
    except Exception as e:
        print(f"Error retrieving local version: {e}")
        return "0.0.0"

def check_for_updates():
    local_version = get_local_version("dymoapi")
    
    try:
        response = requests.get(f"https://pypi.org/pypi/dymoapi/json")
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        if local_version != latest_version: print(f"A new version of dymoapi is available: {latest_version}. You are using {local_version}. Consider updating.")
        else: print(f"You are using the latest version of dymoapi: {local_version}.")
    except requests.RequestException as e: print(f"Error fetching the latest version: {e}")

