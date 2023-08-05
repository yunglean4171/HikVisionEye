import sys
import os
from src.ip_scraper import IpScraper
from src.hikvision_scanner import HikVisionScanner
from termcolor import colored
import time

def main():
    logo = """
  ___ ___ .__ __   ____   ____.__       .__              ___________             
 /   |   \|__|  | _\   \ /   /|__| _____|__| ____   ____ \_   _____/__.__. ____  
/    ~    \  |  |/ /\   Y   / |  |/  ___/  |/  _ \ /    \ |    __)<   |  |/ __ \ 
\    Y    /  |    <  \     /  |  |\___ \|  (  <_> )   |  \|        \___  \  ___/ 
 \___|_  /|__|__|_ \  \___/   |__/____  >__|\____/|___|  /_______  / ____|\___  >
       \/         \/                  \/               \/        \/\/         \/ 

    ↱ input [1] to start
    ↦ input [2] to change passwords                     ,-""-.
    ↳ input [3] to quit                                /--.   \  .-.-'`-~
                                                      | () )   |<_.-.
                                                       \--'   / `~._ `~'
                                                        `-..-'      `-  
"""
    print(colored(logo, "green"))
    choice = input("%~ ")
    if choice == "1":
        print(colored("◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤", "green"))
        scraper = IpScraper()
        scraper.run_threads()
    elif choice == "2":
        print(colored("◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤", "green"))

        def print_files(txt_files):
            print("\nPick one file:\n")
            for idx, file in enumerate(txt_files, start=1):
                print(f"\t[{idx}] - {file}")
            return txt_files


        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        txt_files = [filename for filename in os.listdir(results_dir) if filename.endswith('.txt')]
        while True:
            files = print_files(txt_files)
            choice_input = input("\n➤  ")
            if choice_input.isdigit() and 1 <= int(choice_input) <= len(files):
                choice = int(choice_input)
                selected_file = files[choice-1]
                path = os.path.join(results_dir, selected_file)
                process_file(path)
                break
            else:
                if not choice_input.isdigit():
                    print(colored("\nError: invalid input. Please enter a number.\n", "red"))
                    time.sleep(1)
                else:
                    print(colored(f"\nError: number out of range. Please select a valid number between 1 and {len(files)}.\n", "red"))
                    time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')


    else:
        sys.exit(1)

def process_file(path):
    with open(path, 'r') as file:
        lines = file.readlines()

    ip_dict = dict()

    for line in lines:
        try:
            ip_port = line.split("|")[0].replace("IP: ", "")
            ip, port = ip_port.split(" PORT: ")

            ip = ip.strip()
            port = port.strip()

            if ip not in ip_dict:
                ip_dict[ip] = port
        except ValueError:
            print(colored(f"Problem with line: {line}", "light_red"))

    hvision = HikVisionScanner()
    hvision.get_users_response(ip_dict)



if __name__ == "__main__":
    main()