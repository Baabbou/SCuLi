from urllib.parse import urlparse
import questionary
import time
import json

# ------------------ GLOBAL VARS ----------------------
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ _-&#$!%*~<>"
# ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
# ALPHABET = "0123456789abcdef"
# ALPHABET = [str(i) for i in range(30, 121)]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

ARGS = None
QUERY_COUNT = 0
TIMING = 0
# -----------------------------------------------------

class HTTP_Request:
    def __init__(self):
        # HTTP_params: {"key1": "value1", "key2": "<>",}
        self.params = {}
        # cookie: "PHPSESSID": MD5-STUFF; "id": "<>"
        self.cookie = ""
        # SQLi => Tells where the SQLi is located: params by default
        self.SQLi = "params"

    def __str__(self):
        return f"{self.params}\n{self.cookie}"


def check_args(args: dict) -> bool:
    url = args.URL
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc):
        print("[error] Invalid arguments: Bad URL")
        return False

    type = args.type
    if type.lower() not in ["basic", "error", "time", "oast", "custom"]:
        print("[error] Invalid arguments: Bad type")
        return False

    payload = args.payload
    if not ("<index>" in payload and "<char>" in payload):
        print("[error] Invalid arguments: Payload missing argument =>\n\t['<index>', '<char>'] are required")
        return False

    delay = args.delay
    if delay:
        try:
            value = float(delay)
            if value < 0:
                raise ValueError
        except ValueError:
            print("[error] Invalid arguments: Bad delay")
            return False

    input_file = args.input
    if input_file:
        with open(input_file, "r") as in_file:
            in_json = in_file.read()
            try:
                data = json.loads(in_json)
                if "params" not in data:
                    raise json.decoder.JSONDecodeError
            except json.decoder.JSONDecodeError:
                print("[error] Invalid arguments: Input file isn't a correct Json")
                return False
    return True


def select_reference_len(arr_len_responses: list) -> int:
    val1, val2, val3 = arr_len_responses[0], arr_len_responses[1], arr_len_responses[2]
    if val1 == val2 or val1 == val3:
        return val1
    return val2


def select_reference_time(arr_time_responses: list) -> int:
    # Adapt to your needs
    minimum = min(*arr_time_responses)
    return 2


def countdown() -> None:
    print("[countdown] Launching attack in:")
    print("[countdown] 3...")
    time.sleep(1)
    print("[countdown] 2...")
    time.sleep(1)
    print("[countdown] 1...")
    time.sleep(1)
    print("[countdown] ... Processing attack.\n")


def print_request(request: dict) -> str:
    output = ""
    output += f"{request['method']} {request['url']} HTTP/2\n"
    for key, value in request['headers'].items():
        output += f"{key}: {value}\n"
    output += f"\n{request['data']}"
    return output


def print_response(response: dict) -> str:
    output = ""
    output += f"HTTP/2 {response['status']} ?\n"
    for key, value in response['headers'].items():
        output += f"{key}: {value}\n"
    output += f"\n{response['data']}"
    return output


def init_request(request: HTTP_Request) -> HTTP_Request:
    while 1:
        print("[setup] Let's setup this SQLi dude!")
        try:
            print("[setup] First, tell me how the request is made and where the sqli is.")
            while 1:
                user_input = questionary.select(
                    f"Current HTTP params `{request.params}`:",
                    choices=["Add", "Remove", "Reset", "Done"],
                ).ask()
                if user_input == "Done":
                    break
                elif user_input == "Add":
                    key = questionary.text("Key to add (CTRL+D to quit): ").ask()
                    value = questionary.text("Value to set (`<>` for sqli input):").ask()
                    request.params[key] = value
                elif user_input == "Remove":
                    key = questionary.text("Key to remove (CTRL+D to quit): ").ask()
                    request.params.pop(key, None)
                elif user_input == "Reset":
                    request.params = {}

            print("[setup] Good, tell me if there is cookies or headers.")
            while 1:
                user_input = questionary.select(
                    f"Current HTTP params `{request.params}`:",
                    choices=["Add", "Remove", "Reset", "Done"],
                ).ask()
                if user_input == "Done":
                    break
                elif user_input == "Add":
                    key = questionary.text("Key to add (CTRL+D to quit): ").ask()
                    value = questionary.text("Value to set (`<>` for targeted input):").ask()
                    request.params[key] = value
                elif user_input == "Remove":
                    key = questionary.text("Key to remove (CTRL+D to quit): ").ask()
                    request.params.pop(key, None)
                elif user_input == "Reset":
                    request.params = {}

            print("[setup] Perfect. Let's recap':")
            print(f"\tHTTP requests params are: {request.params}")
            confirm = questionary.confirm("Is that all good?").ask()
            if confirm:
                print("[setup] Yehaa. Let's earn some Root-Me points!")
                break
            else:
                print("[setup] Well, let's restart from the begining.")
                continue
        except EOFError:
            print("[info] Quitting...")
            exit(0)
    return request
