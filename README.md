# brandeis_publications

This script assumes the following Python packages are installed:

```
pip3 install requests
pip3 install pystace
```

The file `data.js` contains the DBLP IDs of all the professors in Brandeis CS -- the script will pull their publications.

To generate the site, run:
```
python3 main.py > index.html
```

The `publish` script will automatically delete cached data, generate the website, and upload it to your CS WWW folder.
