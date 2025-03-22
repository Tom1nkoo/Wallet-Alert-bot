# file: wallet_alert_bot.py

import time
import requests
from web3 import Web3
from dotenv import load_dotenv
import os

# === ENV VARS ===
load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS").lower()
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK")  # Discord/Slack/Webhook URL

# === SETTINGS ===
CHECK_INTERVAL = 60  # seconds
ETHERSCAN_URL = f"https://api.etherscan.io/api"

# === HELPERS ===
def get_eth_balance(address):
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.get(ETHERSCAN_URL, params=params)
    result = response.json()
    if result['status'] == '1':
        return int(result['result']) / 1e18  # convert from wei
    return None

def send_alert(message):
    if ALERT_WEBHOOK:
        requests.post(ALERT_WEBHOOK, json={"content": message})

# === MAIN LOOP ===
def run_monitor():
    print(f"📡 Monitoring wallet: {WALLET_ADDRESS}")
    prev_balance = get_eth_balance(WALLET_ADDRESS)
    print(f"💰 Starting balance: {prev_balance:.6f} ETH")

    while True:
        time.sleep(CHECK_INTERVAL)
        new_balance = get_eth_balance(WALLET_ADDRESS)
        if new_balance is None:
            print("⚠️ Error fetching balance.")
            continue

        if new_balance != prev_balance:
            delta = new_balance - prev_balance
            msg = f"📥 Balance change detected on {WALLET_ADDRESS}: {delta:+.6f} ETH (new: {new_balance:.6f} ETH)"
            print(msg)
            send_alert(msg)
            prev_balance = new_balance
        else:
            print(f"✅ No change ({new_balance:.6f} ETH)")

if __name__ == '__main__':
    run_monitor()
