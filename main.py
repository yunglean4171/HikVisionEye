import sys
from src.ip_scraper import IpScraper
from termcolor import colored

def main():
    logo = """
  ___ ___ .__ __   ____   ____.__       .__              ___________             
 /   |   \|__|  | _\   \ /   /|__| _____|__| ____   ____ \_   _____/__.__. ____  
/    ~    \  |  |/ /\   Y   / |  |/  ___/  |/  _ \ /    \ |    __)<   |  |/ __ \ 
\    Y    /  |    <  \     /  |  |\___ \|  (  <_> )   |  \|        \___  \  ___/ 
 \___|_  /|__|__|_ \  \___/   |__/____  >__|\____/|___|  /_______  / ____|\___  >
       \/         \/                  \/               \/        \/\/         \/ 

    ➜  input [1] to start                                ,-""-.
    ➜  input [2] to quit                                /--.   \  .-.-'`-~
                                                       | () )   |<_.-.
                                                        \--'   / `~._ `~'
                                                         `-..-'      `-  
"""
    print(colored(logo, "green"))
    choice = input("%~ ")
    if choice == "1":
        scraper = IpScraper()
        scraper.run_threads()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()