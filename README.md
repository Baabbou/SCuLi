# SCuLi

A beautiful named tool to perform blind SQLi injection.

# Install

No requirements except a working `python3`.

```bash
git clone https://github.com/Baabbou/SCuLi.git
cd SCuLi
pip3 install -r requirements.txt
```

# Uses

**Help:**
```bash
usage: SCuLi [-h] [-d DELAY] [-c CUSTOM] [--cookie COOKIE] [--proxy PROXY] [-i INPUT] URL type method engine

A blind SQL Injector.

positional arguments:
  URL
  type                  Can be: basic, error, xtime, xOAST, xcustom
  method                Can be: GET or POST
  engine                Can be: 'Oracle', 'Microsoft', 'PostGre', 'MySQL', 'SQLite'

options:
  -h, --help            show this help message and exit
  -d DELAY, --delay DELAY
                        In seconds. Example: `0.5`
  -c CUSTOM, --custom CUSTOM
                        Dict format. Example: `{'id': '<>', 'lang': 'fr'}` [Not implemented]
  --cookie COOKIE       Example: `PHPSESSID=JWT; csrf=MD5-STUFF`
  --proxy PROXY         Example: `http://127.0.0.1:8080`
  -i INPUT, --input INPUT
                        Example: `./example_input.json`

Don't hack good people pls.
```

**Example:**
```bash
python3 ./SCuLi.py "http://vulnerable.net/" basic GET mysql --proxy "http://127.0.0.1:8080" -i "example_input.json" -d 1.5
```

# Warning

Don't use it for bad things, it's just a CTF tool.
It's also still in developement so don't be rude with it :)

# Contact

Don't contact me.
