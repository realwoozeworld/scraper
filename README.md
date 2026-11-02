# scraper

How to run the script:

Install requirements: pip install selenium webdriver-manager pandas

Run the script: python scraper.py

The browser will launch. Accept cookies and manually log in to your Conrad.de account, then press Enter in the terminal to let the script automatically collect 100 products and export them to CSV.

Implementation details:
The scraper is implemented in Python using Selenium to bypass strict Cloudflare anti-bot restrictions and handle dynamic elements. It utilizes a semi-automated approach where the user performs a manual login in an un-automated browser session to establish a valid authenticated state. Once authorized, the script automatically navigates the search pages, extracts unique product URLs, and iterates through each item to parse all required fields (such as breadcrumbs, titles, prices, identifiers, technical tables, datasheet links, and third-party offers) before structuring and saving the output into a CSV file.
