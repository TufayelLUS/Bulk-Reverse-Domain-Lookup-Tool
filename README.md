# Bulk Reverse IP Domain Lookup Tool
This tool reads a list of domains or IPs from a text file and generates the reverse domain lookup data in another text file

# Requirements
```bash
pip install requests
```

# Usage
Load the <code>input.txt</code> with domains or IPs you want to find reverse IP lookup data for, and run the command below
```bash
python3 reverse.py
```
Get the final generated domains list in the <code>collected.txt</code> file<br>
Going forward, if you want to separate gov domains, use the supporting script
```bash
python3 gov_finder.py
```
This script will rewrite <code>input.txt</code> file with the filtered important domains once you run.
