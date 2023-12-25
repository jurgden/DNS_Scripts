import requests
from dotenv import load_dotenv
import os

load_dotenv()

zone_id = os.getenv('ZONE_ID')
api_token = os.getenv('API_TOKEN')
record_type = "A"
ttl = 3600 * 24  # Time to live in seconds, set to 24 hours
proxied = True  # Set to True to enable Cloudflare's proxy

# List of domains to update
domains_to_update = ["eldritchnet.com", "www.eldritchnet.com"]

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        return response.json()["ip"]
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def update_dns_record(zone_id, record_name, record_type, content, ttl, proxied, api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    list_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"

    try:
        list_response = requests.get(list_url, headers=headers, params={"name": record_name, "type": record_type})
        list_response.raise_for_status()

        records = list_response.json()['result']
        if not records:
            raise ValueError(f"No DNS records found for {record_name}.")

        record_id, current_ip = records[0]['id'], records[0]['content']

        if current_ip != content:
            update_url = f"{list_url}/{record_id}"
            data = {"type": record_type, "name": record_name, "content": content, "ttl": ttl, "proxied": proxied}
            update_response = requests.put(update_url, json=data, headers=headers)
            update_response.raise_for_status()
            print(f"DNS record {record_name} updated successfully to {content}.")
        else:
            print(f"No update required for {record_name}. Current IP matches the DNS record.")
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except ValueError as e:
        raise SystemExit(e)

try:
    current_ip = get_public_ip()
    for domain in domains_to_update:
        update_dns_record(zone_id, domain, record_type, current_ip, ttl, proxied, api_token)
except Exception as e:
    print(str(e))
