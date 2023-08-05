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

## Tool's options:
1. [1] to start - It is the process of obtaining IP addresses, ports, and locations of cameras from the shodan.io website. All data is saved in the scraped-ips folder. Subsequently, there is a filtering of the data and saving of the working cameras in the results/results-DATE.txt folder in the following format:
<p align="left">  
<img src="https://i.imgur.com/uleFyDL.png">
</p>
2. [2] to change passwords - After selecting this option, a file selection screen with results will be displayed, for example:
<p align="left">  
<img src="https://i.imgur.com/oB8uf87.png">
</p>
After selecting a file, the tool will change the password for all users in all IP addresses to "12345abc" to allow logging into the cameras using [IVMS-4200](https://www.hikvision.com/en/support/download/software/ivms4200-series/).


# Contributing
If you have some ideas that you want to suggest please make a [pull requests](https://github.com/yunglean4171/HikVisionEye/pulls) and if you found some bugs please make an [issue](https://github.com/yunglean4171/HikVisionEye/issues). Every contribution will be appreciated.
