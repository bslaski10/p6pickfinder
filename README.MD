ScrapeDK.py- This scrapes DK for all of the data in the url. Saves items in the data folder.

Fetch.py- This takes the scraped DK data and converts it into player lines. Sves items in the lines folder.

ScrapeP6.py- This scrapes P6 for player names. Saves items in the options folder.

Selection.py- This uses the options folder to get player lines from the lines folder and sorts them. Saves items in the selections folder.

Picks.py- This creates the parlays and saves it to picks.json.

Locks.py- This runs all of the code and keeps track of progress while it is running.

App.py- This code runs the html page and runs locks.py which allows it to use the picks.json.