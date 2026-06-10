import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

scenarios = [
    {
        "name": "Scenario A (Banglish/Utility)",
        "report": "Farmgate area te rasta bishal dube gese drainage system block hobar karone, sector 5 block hoye ache"
    },
    {
        "name": "Scenario B (English/Emergency)",
        "report": "Critical road accident near UIU campus circle, head-on collision between a bus and a car with severe injuries!"
    },
    {
        "name": "Scenario C (Bangla/Routine)",
        "report": "মিরপুর ১২ নম্বর ব্লকে রাস্তার লাইটগুলো অনেকদিন ধরে নষ্ট, রাতে চলাচল করতে সমস্যা হচ্ছে।"
    }
]

def run_evaluation():
    print("==================================================")
    print("Dhaka CivicPulse - End-to-End Operational Triage Check")
    print("==================================================")
    
    # 1. Check server connectivity
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)
    try:
        health_resp = client.get("/health")
        if health_resp.status_code != 200 or health_resp.json() != {"status": "ok"}:
            print("[-] Warning: Health check endpoint returned unexpected response.")
    except httpx.ConnectError:
        print("[-] Error: Cannot connect to the Uvicorn server at http://127.0.0.1:8000.")
        print("    Please ensure the server is running by executing: uvicorn main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        sys.exit(1)

    # 2. Authenticate and get JWT token
    print("[+] Authenticating against /token route...")
    try:
        token_resp = client.post(
            "/token",
            data={"username": "demo", "password": "secret"}
        )
        if token_resp.status_code != 200:
            print(f"[-] Authentication failed: HTTP {token_resp.status_code} - {token_resp.text}")
            sys.exit(1)
            
        token_data = token_resp.json()
        token = token_data.get("access_token")
        if not token:
            print("[-] Authentication failed: Token not found in response.")
            sys.exit(1)
        print("[+] Secure JWT bearer access token captured successfully.\n")
    except Exception as e:
        print(f"[-] Authentication Request Error: {e}")
        sys.exit(1)

    # 3. Perform triage POST requests
    headers = {"Authorization": f"Bearer {token}"}
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"--- Running {scenario['name']} ---")
        print(f"Prompt Sent: '{scenario['report']}'")
        
        try:
            triage_resp = client.post(
                "/civic/triage",
                json={"report": scenario["report"]},
                headers=headers
            )
            
            if triage_resp.status_code != 200:
                print(f"[-] Request failed: HTTP {triage_resp.status_code}")
                print(f"    Details: {triage_resp.text}\n")
                continue
                
            response_data = triage_resp.json()
            status = response_data.get("status")
            action_code = response_data.get("action_code", "N/A")
            
            print(f"Resulting Status: {status}")
            print(f"Action Code: {action_code}")
            
            # Print telemetry metadata based on route
            if action_code == "ADD_ROUTE":
                print(f"Priority Key: {response_data.get('priority_key')}")
                print(f"Metadata: {response_data.get('meta')}")
            elif action_code == "FACTORIAL_ROUTE":
                print(f"Routing Permutations: {response_data.get('routing_permutations')}")
                print(f"Metadata: {response_data.get('meta')}")
            else:
                print(f"Detail: {response_data.get('detail')}")
                
            print()
            
        except Exception as e:
            print(f"[-] Error executing triage scenario: {e}\n")

if __name__ == "__main__":
    run_evaluation()
