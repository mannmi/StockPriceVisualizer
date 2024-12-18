<p align="center">
  <a href="https://github.com/mannmi/StockPriceVisualizer/issues?q=is%3Aopen+is%3Aissue+-label%3A%22Application+Proposal%22+-label%3A%22WIP%22+">🚀 Apply for Open Task</a> | <a href="https://github.com/mannmi/StockPriceVisualizer/issues">✍️ Submit Your Idea</a> | <a href="https://github.com/mannmi/StockPriceVisualizer/issues/new?assignees=&labels=&projects=&template=bug_report.md&title="> 🐛 Submit Bug Report</a>
</p>

<p align="center">
  <!-- PSE Acceleration Program logo -->
  <img width=40% src="../../StockPriceVisualizer/docs/screenImage.png">
</p>

<p align="center">
  <img src="PROFILE_PICTURE_URL" alt="Profile Icon" />
</p>

# Stock Price Visualizer

StockPriceVisualizer: 📈 Dive into the world of stock prices with real-time visualizations and insights. Perfect for
traders, investors, and finance enthusiasts!

## Features

- Server (data Scaper)
- Server (API) (for fetching data and or updating said data)
- UI/API using



### TODO List

- [ ] Fix database Graper (there still seems to be an issue with the fucntion fetch_active_period)
  for now i have commented it out but this would improve performance when updating the database
- [ ] switch the Graph rendering for the table its kind of bad  
  (qt web seems to be broken on my systm so i can test it). It now opens a browser tab instead
- [ ] Fix Filter Rules
- [ ] There is currently no protection against race conditions (The watch List Load has to be manual trigger )


## Installation

For a guid to how to install the application Refer to INSTALL.md
=> [docs/INSTAL.md](docs/INSTAL.md)

## Starting Server(API)/DB/UI
For a guid to how to Run the application Refer to RUN.md
[docs/RUN.md](docs/RUN.md)

## Usage
On a guid on the button functioality Please read
[Userguide](docs/USING_APP.md)

### API Run

[docs](../../StockPriceVisualizer/docs/api_documentation.md)
or run web server:  
http://127.0.0.1:8000/api/rawDocumentation/
http://127.0.0.1:8000/documentation/

## Contributing

Contributions are welcome! Please see the CONTRIBUTING.md, COMMIT_MESSAGE.md,CODE_OF_CONDUCT.md for guidelines.

* CONTRIBUTING.md => [CONTRIBUTING.md](docs/CONTRIBUTING.md)
* COMMIT_MESSAGE.md => [COMMIT_MESSAGE.md](docs/COMMIT_MESSAGE.md)
* CODE_OF_CONDUCT.md => [CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md)

## License

This project is licensed under the AGPL3 License. See the LICENSE file for details.

*

License => [https://github.com/mannmi/StockPriceVisualizer?tab=LGPL-2.1-1-ov-file](https://github.com/mannmi/StockPriceVisualizer/blob/main/LICENSE)

Contributor List:
mannmi
