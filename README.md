<div align="center">

# HikVisionEye

</div>

<p align="center">  
<img src="https://i.imgur.com/vo3gteU.png">
</p>


### HikVisionEye is a tool for scraping potential IP addresses and ports of unsecured webcams from the [shodan.io](https://www.shodan.io/) and then verifying which data is correct.


## Built with:
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
* [Requests](https://pypi.org/project/requests/)
* [aiohttp](https://pypi.org/project/aiohttp/)
* [termcolor](https://pypi.org/project/termcolor/)

## Execution:
1. Clone the repository to your device.
2. Install the required libraries using the command: ``pip install -r requirements.txt``
3. Open ``accounts.txt`` and enter your login credentials for the [shodan.io](https://www.shodan.io/) website in the format username:password.
*If you don't do this, the tool will automatically attempt to scrape data without logging in, but this will result in a drastic decrease in accurate hits.*
5. Run the main script using the command: ``python main.py``
6. Follow the instructions displayed in the console.
