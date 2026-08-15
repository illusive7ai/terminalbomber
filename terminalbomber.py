import requests
import base64
from datetime import datetime
import sqlite3
import time
import sys
import os
from colorama import init, Fore, Back, Style
import re
import json
import random

# Initialize colorama for Windows compatibility
init(autoreset=True)


CONSUMER_KEY = "7djS8Yr7qyTLh7A0EAXBrRi09doeO9s20QKNHeQM1l3ZHkXT"
CONSUMER_SECRET = "4Wrl97AkUYD4EpN7kF3F4AJxO7eAgtGj3hJMQtvraA6HBVXArc7WBgHQZFG5mBvE"
BUSINESS_SHORTCODE = "174379"
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
MPESA_API_ENDPOINT = "https://sandbox.safaricom.co.ke"

class PaymentTerminal:
    def __init__(self):
        self.clear_screen()
        self.show_banner()
        self.init_db()
        self.access_token = None
        self.token_expiry = 0
        self.request_count = 0
        self.successful_requests = 0
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_banner(self):
        """Display beautiful combined banner with dragon art left and bomber text right"""
        self.clear_screen()
        
        dragon_art = [
            "⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣤⡼⠀⢀⡀⣀⢱⡄⡀⠀⠀⠀⢲⣤⣤⣤⣤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⣿⣿⣿⡿⠛⠋⠁⣤⣿⣿⣿⣧⣷⠀⠀⠘⠉⠛⢻⣷⣿⣽⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⠀⠀⢀⣴⣞⣽⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠠⣿⣿⡟⢻⣿⣿⣇⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣟⢦⡀⠀⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⠀⣠⣿⡾⣿⣿⣿⣿⣿⠿⣻⣿⣿⡀⠀⠀⠀⢻⣿⣷⡀⠻⣧⣿⠆⠀⠀⠀⠀⣿⣿⣿⡻⣿⣿⣿⣿⣿⠿⣽⣦⡀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⣼⠟⣩⣾⣿⣿⣿⢟⣵⣾⣿⣿⣿⣧⠀⠀⠀⠈⠿⣿⣿⣷⣈⠁⠀⠀⠀⠀⣰⣿⣿⣿⣿⣮⣟⢯⣿⣿⣷⣬⡻⣷⡄⠀⠀⠀",
            "⠀⠀⢀⡜⣡⣾⣿⢿⣿⣿⣿⣿⣿⢟⣵⣿⣿⣿⣷⣄⠀⣰⣿⣿⣿⣿⣿⣷⣄⠀⢀⣼⣿⣿⣿⣷⡹⣿⣿⣿⣿⣿⣿⢿⣿⣮⡳⡄⠀⠀",
            "⠀⢠⢟⣿⡿⠋⣠⣾⢿⣿⣿⠟⢃⣾⢟⣿⢿⣿⣿⣿⣾⡿⠟⠻⣿⣻⣿⣏⠻⣿⣾⣿⣿⣿⣿⡛⣿⡌⠻⣿⣿⡿⣿⣦⡙⢿⣿⡝⣆⠀",
            "⠀⢯⣿⠏⣠⠞⠋⠀⣠⡿⠋⢀⣿⠁⢸⡏⣿⠿⣿⣿⠃⢠⣴⣾⣿⣿⣿⡟⠀⠘⢹⣿⠟⣿⣾⣷⠈⣿⡄⠘⢿⣦⠀⠈⠻⣆⠙⣿⣜⠆",
            "⢀⣿⠃⡴⠃⢀⡠⠞⠋⠀⠀⠼⠋⠀⠸⡇⠻⠀⠈⠃⠀⣧⢋⣼⣿⣿⣿⣷⣆⠀⠈⠁⠀⠟⠁⡟⠀⠈⠻⠀⠀⠉⠳⢦⡀⠈⢣⠈⢿⡄",
            "⣸⠇⢠⣷⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⠿⠋⠀⢻⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢾⣆⠈⣷",
            "⡟⠀⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣶⣤⡀⢸⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⢹",
            "⡇⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠈⣿⣼⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠃⢸",
            "⢡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠶⣶⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼",
            "⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁",
            "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡁⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
            "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣼⣀⣠⠂⠀⠀⠀"
        ]
        
        bomber_text = [
            "  __________              ___.",
            "  \\______   \\ ____   _____\\_ |__   ___________",
            "   |    |  _//  _ \\ /     \\| __ \\_/ __ \\_  __ \\",
            "   |    |   (  <_> )  Y Y  \\ \\_\\ \\  ___/|  | \\/",
            "   |______  /\\____/|__|_|  /___  /\\___  >__|",
            "          \\/             \\/    \\/     \\/",
            "",
            "       BOMBING SYSTEM v3.0",
            "   FOR EDUCATIONAL PURPOSES ONLY",
            "        Use at your own risk"
        ]
        
        max_lines = max(len(dragon_art), len(bomber_text))
        
        for i in range(max_lines):
            left = dragon_art[i] if i < len(dragon_art) else ""
            right = bomber_text[i] if i < len(bomber_text) else ""
            
            if i % 2 == 0:
                left_colored = f"{Fore.CYAN}{left}{Style.RESET_ALL}"
            else:
                left_colored = f"{Fore.MAGENTA}{left}{Style.RESET_ALL}"
            
            right_colored = f"{Fore.YELLOW}{right}{Style.RESET_ALL}"
            print(f"{left_colored}    {right_colored}")
        
        self.cyber_scan("SYSTEM INITIALIZATION")
    
    def cyber_scan(self, operation):
        """Enhanced cyber scanning animation"""
        print(f"\n{Fore.BLUE}[>] {Fore.CYAN}INITIATING {operation} SEQUENCE{Style.RESET_ALL}")
        time.sleep(0.5)
        
        chars = ["=", ">", ">>", ">>>", ">>>>", ">>>>>", ">>>>>>", ">>>>>>>", ">>>>>>>>", ">>>>>>>>>"]
        progress = ["[---]", "[#--]", "[##-]", "[###]", "[####]", "[#####]", "[######]", "[#######]", "[########]", "[#########]"]
        
        for i in range(10):
            perc = (i + 1) * 10
            prog = progress[i] if i < len(progress) else "[#########]"
            spin = chars[i % len(chars)]
            
            color = Fore.MAGENTA if i % 2 == 0 else Fore.CYAN
            print(f"\r{color}[{spin}] {Fore.YELLOW}{prog} {Fore.CYAN}{perc}% {Fore.GREEN}| Scanning system vectors...{Style.RESET_ALL}", end='')
            time.sleep(0.15)
        
        print(f"\n{Fore.GREEN}[+] {operation} COMPLETE{Style.RESET_ALL}\n")
        time.sleep(0.5)
    
    def init_db(self):
        """Initialize database for tracking transactions"""
        self.conn = sqlite3.connect("test_transactions.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT,
                amount REAL,
                reference TEXT,
                message TEXT,
                timestamp DATETIME,
                status TEXT,
                attempt_number INTEGER
            )
        ''')
        self.conn.commit()
    
    def print_header(self, text):
        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.MAGENTA}▶ {text}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def print_success(self, text):
        print(f"{Fore.GREEN}[+] {text}{Style.RESET_ALL}")
    
    def print_error(self, text):
        print(f"{Fore.RED}[-] {text}{Style.RESET_ALL}")
    
    def print_warning(self, text):
        print(f"{Fore.YELLOW}[!] {text}{Style.RESET_ALL}")
    
    def print_info(self, text):
        print(f"{Fore.CYAN}[*] {text}{Style.RESET_ALL}")
    
    def print_link(self, text):
        print(f"{Fore.BLUE}{text}{Style.RESET_ALL}")
    
    def is_url(self, text):
        url_pattern = re.compile(
            r'^(https?://)?'
            r'(([A-Z0-9-]+\.)+[A-Z]{2,6}|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(:\d+)?'
            r'(/.*)?$', re.IGNORECASE)
        return url_pattern.match(text) is not None
    
    def get_access_token(self):
        """Get OAuth token with exponential backoff on failure"""
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)  # 2, 4, 8 seconds
                    print(f"{Fore.YELLOW}[!] Retry in {delay}s...{Style.RESET_ALL}")
                    time.sleep(delay)
                
                print(f"{Fore.CYAN}[*] Requesting access token...{Style.RESET_ALL}")
                
                url = f"{MPESA_API_ENDPOINT}/oauth/v1/generate?grant_type=client_credentials"
                auth = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
                headers = {"Authorization": f"Basic {auth}"}
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if 'text/html' in response.headers.get('Content-Type', ''):
                    print(f"{Fore.RED}[-] API returned HTML - Sandbox may be down{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        continue
                    return None
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print(f"{Fore.RED}[-] Invalid JSON response{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        continue
                    return None
                
                if response.status_code == 200 and "access_token" in data:
                    token = data["access_token"]
                    print(f"{Fore.GREEN}[+] Access token obtained!{Style.RESET_ALL}")
                    self.access_token = token
                    self.token_expiry = time.time() + 3500  # ~1 hour
                    return token
                else:
                    error_msg = data.get('error_description', data.get('errorMessage', 'Unknown error'))
                    print(f"{Fore.RED}[-] Token failed: {error_msg}{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        continue
                    return None
                    
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    continue
                return None
        
        return None
    
    def send_payment_request(self, phone, amount, reference, message):
        """Send single bomb with message - with better handling"""
        try:
            # Check if token is expired or doesn't exist
            if not self.access_token or time.time() > self.token_expiry:
                self.access_token = self.get_access_token()
                if not self.access_token:
                    return {"error": "Failed to get access token"}
            
            url = f"{MPESA_API_ENDPOINT}/mpesa/stkpush/v1/processrequest"
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = base64.b64encode(f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
            
            # Add random user agent to avoid detection
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36'
            ]
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "User-Agent": random.choice(user_agents)
            }
            
            transaction_desc = message[:20]
            
            payload = {
                "BusinessShortCode": BUSINESS_SHORTCODE,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone,
                "PartyB": BUSINESS_SHORTCODE,
                "PhoneNumber": phone,
                "CallBackURL": "https://yourdomain.com/callback",
                "AccountReference": reference,
                "TransactionDesc": transaction_desc
            }
            
            amount_int = int(amount)
            if amount_int >= 1000:
                formatted_amount = f"{amount_int:,}"
                self.print_info(f"Sending bomb of {formatted_amount} KSh...")
            else:
                self.print_info(f"Sending bomb of {amount} KSh...")
            
            print(f"   {Fore.CYAN}Reference: {Fore.GREEN}{reference}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}Message: {Fore.GREEN}{transaction_desc}{'...' if len(message) > 20 else ''}{Style.RESET_ALL}")
            
            # Add random delay before request to avoid pattern detection
            time.sleep(random.uniform(0.5, 1.5))
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            # Check for HTML response
            if 'text/html' in response.headers.get('Content-Type', ''):
                return {"error": "API rate-limited - taking a break"}
            
            try:
                data = response.json()
                
                # Check for rate limiting
                if response.status_code == 429:
                    return {"error": "Rate limited - waiting"}
                
                return data
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON response"}
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def get_user_input(self):
        """Get input from user via terminal"""
        self.print_header("BOMBING SETUP")
        
        # Get number of requests - with warning about rate limiting
        while True:
            try:
                print(f"\n{Fore.YELLOW}[?] How many bombs to send?{Style.RESET_ALL}")
                print(f"{Fore.CYAN}(Recommended: 3-5 for best success rate){Style.RESET_ALL}")
                request_count = input(f"{Fore.CYAN}Enter number (1-1000): {Style.RESET_ALL}").strip()
                if not request_count:
                    request_count = 1
                else:
                    request_count = int(request_count)
                
                if 1 <= request_count <= 1000:
                    break
                else:
                    self.print_error("Please enter a number between 1 and 1000")
            except ValueError:
                self.print_error("Please enter a valid number")
        
        # Get phone number
        while True:
            print(f"\n{Fore.YELLOW}[?] Enter test phone number{Style.RESET_ALL}")
            phone = input(f"{Fore.CYAN}Format (2547XXXXXXXX): {Style.RESET_ALL}").strip()
            if phone and phone.startswith("254") and len(phone) == 12:
                break
            else:
                self.print_error("Invalid format. Must start with 254 and be 12 digits")
        
        # Get amount
        while True:
            print(f"\n{Fore.YELLOW}[?] Enter amount in Kenyan Shillings{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Enter any amount (digits only, no limits):{Style.RESET_ALL}")
            amount = input(f"{Fore.CYAN}Amount: {Style.RESET_ALL}").strip()
            
            if not amount:
                amount = "1"
            
            amount_clean = amount.replace(',', '').replace(' ', '').replace('KSh', '').replace('KES', '').replace('$', '')
            
            if amount_clean.isdigit() and int(amount_clean) > 0:
                amount = amount_clean
                amount_int = int(amount)
                
                if amount_int >= 1000:
                    formatted_amount = f"{amount_int:,}"
                    print(f"{Fore.GREEN}[+] Amount set to: {Fore.CYAN}{formatted_amount} KSh{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}[+] Amount set to: {Fore.CYAN}{amount} KSh{Style.RESET_ALL}")
                
                break
            else:
                self.print_error("Amount must be positive digits only")
        
        # Get reference
        while True:
            print(f"\n{Fore.YELLOW}[?] Enter bombing reference (for M-Pesa){Style.RESET_ALL}")
            print(f"{Fore.CYAN}This appears in M-Pesa statement (max 12 chars):{Style.RESET_ALL}")
            reference = input(f"{Fore.CYAN}Reference (default: BOMB): {Style.RESET_ALL}").strip()
            
            if not reference:
                reference = "BOMB"
            
            if len(reference) <= 12:
                break
            else:
                self.print_error(f"M-Pesa reference max is 12 characters (you entered {len(reference)})")
        
        # Get message
        print(f"\n{Fore.YELLOW}[?] Enter message to include with payment{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This can contain clickable links or custom text:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Examples:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Visit: https://example.com{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Claim your prize at: https://bit.ly/prize-link{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}Check this out: http://github.com/project{Style.RESET_ALL}")
        
        while True:
            message = input(f"{Fore.CYAN}Message (press Enter for none): {Style.RESET_ALL}").strip()
            
            if not message:
                message = "Test payment"
                print(f"{Fore.YELLOW}[!] Using default message: '{message}'{Style.RESET_ALL}")
                break
            
            urls_found = re.findall(r'https?://\S+', message)
            if urls_found:
                print(f"\n{Fore.GREEN}[+] URLs detected in message:{Style.RESET_ALL}")
                for url in urls_found:
                    self.print_link(f"  {url}")
                
                confirm = input(f"\n{Fore.YELLOW}Use this message? (y/n): {Style.RESET_ALL}").strip().lower()
                if confirm in ['y', 'yes']:
                    break
                else:
                    print(f"{Fore.YELLOW}Please enter a different message:{Style.RESET_ALL}")
                    continue
            else:
                print(f"\n{Fore.GREEN}[+] Message set: {Fore.CYAN}'{message}'{Style.RESET_ALL}")
                confirm = input(f"{Fore.YELLOW}Use this message? (y/n): {Style.RESET_ALL}").strip().lower()
                if confirm in ['y', 'yes']:
                    break
                else:
                    print(f"{Fore.YELLOW}Please enter a different message:{Style.RESET_ALL}")
                    continue
        
        return request_count, phone, amount, reference, message
    
    def process_payments(self):
        """Main bombing logic with better rate handling"""
        request_count, phone, amount, reference, message = self.get_user_input()
        
        self.print_header("PROCESSING BOMBS")
        
        # Show cyber scan before starting
        self.cyber_scan("BOMB SEQUENCE")
        
        print(f"\n{Fore.YELLOW}[>] Starting {Fore.CYAN}{request_count}{Fore.YELLOW} bombs{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[>] Target Phone: {Fore.CYAN}{phone}{Style.RESET_ALL}")
        
        amount_int = int(amount)
        if amount_int >= 1000:
            formatted_amount = f"{amount_int:,}"
            print(f"{Fore.YELLOW}[>] Amount: {Fore.CYAN}{formatted_amount} KSh{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[>] Amount: {Fore.CYAN}{amount} KSh{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}[>] M-Pesa Reference: {Fore.CYAN}{reference}{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}[>] Message: {Fore.CYAN}", end="")
        if self.is_url(message):
            self.print_link(message)
            print(f"{Fore.CYAN}    [=] Clickable URL in SMS{Style.RESET_ALL}")
        else:
            urls_in_message = re.findall(r'https?://\S+', message)
            if urls_in_message:
                for url in urls_in_message:
                    message = message.replace(url, f"{Fore.BLUE}{url}{Fore.CYAN}")
                print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}    [=] Contains clickable URL(s){Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        
        successful_count = 0
        failed_count = 0
        consecutive_failures = 0
        
        for i in range(1, request_count + 1):
            try:
                print(f"\n{Fore.MAGENTA}{'─' * 60}")
                print(f"{Fore.YELLOW}[>] Attempt {i}/{request_count}")
                print(f"{Fore.MAGENTA}{'─' * 60}{Style.RESET_ALL}")
                
                current_ref = f"{reference}-{i}"
                
                if i > 1:
                    current_msg = f"{message} #{i}"
                else:
                    current_msg = message
                
                # If we have consecutive failures, take a longer break
                if consecutive_failures >= 2:
                    wait_time = random.randint(10, 20)
                    print(f"{Fore.YELLOW}[!] Multiple failures detected - waiting {wait_time}s to reset...{Style.RESET_ALL}")
                    time.sleep(wait_time)
                    consecutive_failures = 0
                    # Refresh token
                    self.access_token = None
                
                response = self.send_payment_request(phone, amount, current_ref, current_msg)
                
                if "ResponseCode" in response and response["ResponseCode"] == "0":
                    self.print_success(f"Bomb {i} sent successfully!")
                    print(f"   {Fore.CYAN}Reference: {Fore.GREEN}{current_ref}{Style.RESET_ALL}")
                    print(f"   {Fore.CYAN}Message: {Fore.GREEN}{current_msg}{Style.RESET_ALL}")
                    print(f"   {Fore.CYAN}Checkout ID: {Fore.GREEN}{response.get('CheckoutRequestID', 'N/A')}{Style.RESET_ALL}")
                    print(f"   {Fore.CYAN}Response: {Fore.GREEN}{response.get('ResponseDescription', 'Success')}{Style.RESET_ALL}")
                    
                    self.log_transaction(phone, amount, current_ref, current_msg, "Pending", i)
                    successful_count += 1
                    consecutive_failures = 0
                else:
                    error = response.get("errorMessage", response.get("error", "API Error"))
                    self.print_error(f"Attempt {i} failed")
                    print(f"   {Fore.CYAN}Error: {Fore.RED}{error}{Style.RESET_ALL}")
                    print(f"   {Fore.CYAN}Reference: {Fore.YELLOW}{current_ref}{Style.RESET_ALL}")
                    self.log_transaction(phone, amount, current_ref, current_msg, "Failed", i)
                    failed_count += 1
                    consecutive_failures += 1
                
                # Dynamic delay - increase after failures
                if i < request_count:
                    if consecutive_failures > 0:
                        delay = 5 + random.randint(0, 5)  # 5-10 seconds after failure
                    else:
                        delay = 3 + random.randint(0, 3)  # 3-6 seconds normally
                    
                    print(f"\n{Fore.YELLOW}[>] Waiting {delay} seconds before next bomb...{Style.RESET_ALL}")
                    for remaining in range(delay, 0, -1):
                        print(f"   {Fore.CYAN}Next bomb in {remaining} seconds...{Style.RESET_ALL}", end='\r')
                        time.sleep(1)
                    print(" " * 50, end='\r')
                
            except KeyboardInterrupt:
                self.print_warning("\n\nProcess interrupted by user")
                break
            except Exception as e:
                self.print_error(f"Critical error on attempt {i}: {str(e)}")
                failed_count += 1
                consecutive_failures += 1
        
        # Summary
        self.print_header("BOMBING SEQUENCE COMPLETED")
        
        print(f"\n{Fore.CYAN}{'─' * 30} RESULTS {'─' * 30}{Style.RESET_ALL}")
        
        if successful_count > 0:
            self.print_success(f"SUCCESSFUL: {successful_count}")
        else:
            self.print_warning(f"SUCCESSFUL: {successful_count}")
        
        if failed_count > 0:
            self.print_error(f"FAILED: {failed_count}")
        else:
            self.print_success(f"FAILED: {failed_count}")
        
        total_amount = int(amount) * successful_count
        if total_amount >= 1000:
            formatted_total = f"{total_amount:,}"
        else:
            formatted_total = str(total_amount)
        
        print(f"\n{Fore.CYAN}TOTAL ATTEMPTS: {Fore.YELLOW}{request_count}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}TOTAL AMOUNT SENT: {Fore.YELLOW}{formatted_total} KSh{Style.RESET_ALL}")
        print(f"{Fore.CYAN}MESSAGE SENT: {Fore.YELLOW}{message[:50]}{'...' if len(message) > 50 else ''}{Style.RESET_ALL}")
        
        if request_count > 0:
            success_rate = (successful_count / request_count) * 100
            color = Fore.GREEN if success_rate >= 70 else Fore.YELLOW if success_rate >= 30 else Fore.RED
            print(f"{Fore.CYAN}SUCCESS RATE: {color}{success_rate:.1f}%{Style.RESET_ALL}")
            
            # Show tips for better success rate
            if success_rate < 50:
                print(f"\n{Fore.YELLOW}[!] TIPS FOR BETTER SUCCESS RATE:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}  • Use 3-5 bombs per session (not 10+){Style.RESET_ALL}")
                print(f"{Fore.CYAN}  • Wait 30-60 seconds between sessions{Style.RESET_ALL}")
                print(f"{Fore.CYAN}  • Use amounts between 1-100 KSh{Style.RESET_ALL}")
                print(f"{Fore.CYAN}  • The sandbox API has rate limits{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}[?] Would you like to run another bombing?{Style.RESET_ALL}")
        while True:
            again = input(f"{Fore.CYAN}Enter (y/n): {Style.RESET_ALL}").strip().lower()
            if again in ['y', 'yes']:
                # Wait before starting new session
                print(f"{Fore.YELLOW}[!] Waiting 10 seconds before new session...{Style.RESET_ALL}")
                time.sleep(10)
                self.clear_screen()
                self.show_banner()
                return True
            elif again in ['n', 'no']:
                print(f"\n{Fore.GREEN}[+] Thank you for bombing! Goodbye!{Style.RESET_ALL}")
                return False
            else:
                self.print_error("Please enter 'y' or 'n'")
    
    def log_transaction(self, phone, amount, reference, message, status, attempt):
        """Log transaction to database"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO test_transactions 
                (phone_number, amount, reference, message, timestamp, status, attempt_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (phone, amount, reference, message, timestamp, status, attempt))
            self.conn.commit()
        except Exception as e:
            self.print_error(f"Failed to log transaction: {str(e)}")

def main():
    """Main entry point"""
    terminal = PaymentTerminal()
    
    try:
        while True:
            if not terminal.process_payments():
                break
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] Program interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n\n{Fore.RED}[-] Critical error: {str(e)}{Style.RESET_ALL}")
    finally:
        if hasattr(terminal, 'conn'):
            terminal.conn.close()
            print(f"{Fore.CYAN}[+] Database connection closed.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()