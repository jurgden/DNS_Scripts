import requests
from dotenv import load_dotenv
import os

load_dotenv()

zone_id = os.getenv('ZONE_ID')
api_token = os.getenv('API_TOKEN')


def get_public_ip():
    response = requests.get("https://api.ipify.org?format=json")
    if response.status_code == 200:
        return response.json()["ip"]
    else:
        raise Exception("Could not obtain public IP")


    # Test the function
try:
    my_ip = get_public_ip()
    print(f"My Public IP Address: {my_ip}")
except Exception as e:
    print(str(e))


def update_dns_record(zone_id, record_name, record_type, content, ttl, api_token):
    list_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {"Authorization": f"Bearer {api_token}",
               "Content-Type": "application/json"}

    # Find the DNS record ID
    response = requests.get(list_url, headers=headers, params={
                            "name": record_name, "type": record_type})
    if response.status_code != 200 or not response.json()['success']:
        raise Exception(f"Failed to find DNS record: {response.text}")

    records = response.json()['result']
    if not records:
        raise Exception("No DNS records found matching the criteria.")

    record_id, current_ip = records[0]['id'], records[0]['content']

    # Check if IP needs to be updated
    if current_ip != content:
        update_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        data = {"type": record_type, "name": record_name,
                "content": content, "ttl": ttl}
        response = requests.put(update_url, json=data, headers=headers)
        if response.status_code == 200 and response.json()['success']:
            print(
                f"DNS record {record_name} updated successfully to {content}.")
        else:
            raise Exception(f"Failed to update DNS record: {response.text}")
    else:
        print("No update required. Current IP matches the DNS record.")


# Configuration variables
zone_id = "your_zone_id"
record_name = "your_domain.com"
record_type = "A"
ttl = 3600  # Time to live in seconds
api_token = "your_api_token"

try:
    current_ip = get_public_ip()
    update_dns_record(zone_id, record_name, record_type,
                      current_ip, ttl, api_token)
except Exception as e:
    print(str(e))
