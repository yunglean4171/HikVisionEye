from requests import Session, exceptions
from urllib.parse import urlencode
import time
from bs4 import BeautifulSoup
import concurrent.futures
import random
import json
import os
from datetime import datetime
from .hikvision_scanner import HikVisionScanner


class IpScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
        }
        self.login_url = "https://account.shodan.io/login"
        self.search_url = "https://www.shodan.io/search"
        self.accounts = self.read_account_file()
        self.queries = [
            '"App-webs" "200 OK"',
            'App-Webs "200 OK"',
            '"APP-WEBS" 200 OK',
            '"app webs" "200 OK"',
            'hikvision "App-webs" "200 OK"',
            'hikvision App-Webs "200 OK"',
            'hikvision "APP-WEBS" 200 OK',
            'hikvision"app webs" "200 OK"',
            '"App-webs" 200',
            '"APP-WEBS" 200',
            '"app webs" 200',
            'hikvision "App-webs" 200',
            'hikvision App-Webs 200',
            'hikvision "APP-WEBS" 200',
            'hikvision "app webs" 200',
        ]
        self.results = []
    def read_account_file(self):
        with open('accounts.txt', 'r') as f:
            accounts = [line.strip().split(':') for line in f]
        return accounts

    def login_shodan(self, username, password):
        session = Session()
        session.headers.update(self.headers)
        try:
            r = session.get(self.login_url)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, 'html.parser')
            csrf_token = soup.find('input', attrs={'name': 'csrf_token'}).get('value')

            login_data = {
                "username": username,
                "password": password,
                "grant_type": "password",
                "continue": "https://account.shodan.io/",
                "login_submit": "Login",
                "csrf_token": csrf_token
            }

            r = session.post(self.login_url, data=login_data)
            r.raise_for_status()
            print("\nAccount switched to:", username)
            #print("Session cookies:", session.cookies.get_dict())  
        except Exception as e:
            print(f"Error logging in: {e}")
        return session

    def scrape_website(self, query, session, login_required=True):
        time.sleep(random.randint(1,3))
        try:
            search_query = {"query": query}
            search_url_query = "%s?%s" % (self.search_url, urlencode(search_query))
            r = session.get(search_url_query)
            time.sleep(5)
            r.raise_for_status()

            if '<p>Daily search usage limit reached. Please wait a bit before doing more searches or use the API.</p>' in r.text and login_required:
                print("Daily search limit reached. Waiting and switching accounts...")
                time.sleep(random.randint(5,10))
                return "limit_reached"

            if "Error:" in r.text and not login_required:
                raise Exception("Daily limit reached for non-login scraping")

            print("Scraping website with query:", query)

            soup = BeautifulSoup(r.text, 'html.parser')

            divs = soup.find_all("div", class_="result")

            results = []

            for div in divs[:10]:
                ip = div.find("a", class_="title text-dark").get('href').replace('/host/', '')
                country = div.find("a", class_="filter-link text-dark").text
                city = div.find_all("a", class_="filter-link text-dark")[1].text

                # Scraping ports for the given ip
                base_url = "https://www.shodan.io/host/"
                r = session.get(base_url + ip)
                soup = BeautifulSoup(r.text, 'html.parser')
                port_div = soup.find("div", id="ports")
                ports = []
                if port_div:
                    ports = [a.text for a in port_div.find_all("a")]

                results.append({"ip": ip, "country": country, "city": city, "ports": ports})

            self.results.extend(results)

        except exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("429 Error, sleeping for a while...")
                time.sleep(random.randint(4, 6))
                return "limit_reached"
            else:
                print(f"Error scraping website: {e}")


    def no_login_scrape_website(self, query):
        session = Session()
        session.headers.update(self.headers)
        self.scrape_website(query, session, login_required=False)

    def run_queries(self, session):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.queries)) as executor:
            future_to_query = {executor.submit(self.scrape_website, query, session): query for query in self.queries}
            time.sleep(random.randint(1,3))
            for future in concurrent.futures.as_completed(future_to_query):
                result = future.result()
                if result == "limit_reached":
                    return "limit_reached"

    def run_threads(self):
        for account in self.accounts:
            username, password = account
            session = self.login_shodan(username, password)
            result = self.run_queries(session)
            if result == "limit_reached":
                print("Switching to the next account...")
            else:
                print("Queries finished successfully for this account, switching to the next one...")
                continue

        print("\nNo more accounts in accounts.txt to switch!")
        print("\nAttempting non-login scraping...")
        
        try:
            for query in self.queries:
                self.no_login_scrape_website(query)
        except Exception as e:
            print(f"{e}")

        # Save the results from all threads into a JSON file at the end
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        result_file_path = os.path.join("scraped-ips", f"scraped-ips-{current_datetime}.json")
        with open(result_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

        HikVisionScanner.load_ips_and_ports(result_file_path)
        
