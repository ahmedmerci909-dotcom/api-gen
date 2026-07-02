# BY JAGWAR KING - FLASK API WRAPPER (2099 MODE)
# جميع الملفات والدوال والخيارات محفوظة كما هي. تم إضافة واجهة API فقط.

import json
import requests
import time
import random
import base64
import threading
import os
import string
import codecs
import sys
import urllib3
import warnings
import subprocess
import queue
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, render_template_string

# ===== الكود الأصلي بالكامل (بدون أي تعديل) =====
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")
init(autoreset=True)
white = Fore.WHITE
reset = Fore.RESET

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi",
    "TH": "th", "BD": "bn", "PK": "ur", "TW": "zh",
    "EU": "en", "CIS": "ru", "NA": "en", "SAC": "es", "BR": "pt"
}

HEX_KEY = bytes.fromhex("32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533")

USER_AGENTS = [
    'GarenaMSDK/4.0.39(SM-A325M;Android 13;en;HK;)',
    'GarenaMSDK/4.0.45(iPhone14,2;iOS 16.0;en;US;)',
    'GarenaMSDK/4.0.38(Xiaomi Mi9;Android 12;en;CN;)',
    'Dalvik/2.1.0 (Linux; U; Android 11; SM-G973F Build/RP1A.200720.012)',
    'GarenaMSDK/4.0.41(OPPO CPH2219;Android 13;en;IN;)'
]

save_queue = queue.Queue()
save_thread_running = True
save_thread_lock = threading.Lock()
accounts_saved_count = 0
accounts_saved_lock = threading.Lock()
file_lock = threading.Lock()
print_lock = threading.Lock()
counter_lock = threading.Lock()

def get_random_ua():
    return random.choice(USER_AGENTS)

def to_superscript(num):
    superscript_digits = {
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
    }
    return ''.join(superscript_digits[d] for d in str(num))

def encode_varint(n):
    if n < 0:
        return b''
    result = []
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            byte |= 0x80
        result.append(byte)
        if not n:
            break
    return bytes(result)

def create_proto_field(field_num, value):
    if isinstance(value, dict):
        nested = create_proto_field(field_num, value)
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(nested)) + nested
    elif isinstance(value, int):
        header = (field_num << 3) | 0
        return encode_varint(header) + encode_varint(value)
    elif isinstance(value, (str, bytes)):
        encoded_val = value.encode() if isinstance(value, str) else value
        header = (field_num << 3) | 2
        return encode_varint(header) + encode_varint(len(encoded_val)) + encoded_val
    return b''

def build_proto(fields):
    return b''.join(create_proto_field(k, v) for k, v in fields.items())

def aes_encrypt(hex_data):
    data = bytes.fromhex(hex_data)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))

def encrypt_api(plain_hex):
    plain = bytes.fromhex(plain_hex)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plain, AES.block_size)).hex()

def generate_random_name(base, number=None):
    if number is not None:
        return f"{base}{to_superscript(number)}"
    exp_digits = {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'}
    num = random.randint(1, 9999)
    return f"{base}{''.join(exp_digits[d] for d in f'{num:04d}')}"

def generate_custom_password(user_prefix):
    random_part = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(8))
    return f"{user_prefix}_BY_JAGWAR_{random_part}"

def save_worker():
    global save_thread_running, accounts_saved_count
    filename = "JAGWAR.json"
    while save_thread_running or not save_queue.empty():
        try:
            account_data = save_queue.get(timeout=1)
            if account_data is None:
                save_queue.task_done()
                break
            with save_thread_lock:
                accounts_list = []
                if os.path.exists(filename):
                    try:
                        with open(filename, 'r', encoding='utf-8') as f:
                            accounts_list = json.load(f)
                            if not isinstance(accounts_list, list):
                                accounts_list = []
                    except (json.JSONDecodeError, ValueError, IOError):
                        backup_name = f"JAGWAR_CORRUPTED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        if os.path.exists(filename):
                            os.rename(filename, backup_name)
                        accounts_list = []
                accounts_list.append(account_data)
                temp_file = filename + ".tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(accounts_list, f, ensure_ascii=False, indent=4)
                os.replace(temp_file, filename)
            with accounts_saved_lock:
                accounts_saved_count += 1
            save_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            save_queue.task_done()

def save_account_to_file(account_data, region):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_account = {
        "name": account_data['name'],
        "uid": str(account_data['uid']),
        "password": account_data['password'],
        "region": region,
        "status_code": 200,
        "created_at": current_time
    }
    save_queue.put(new_account)
    return True

def create_account(region, account_name, password_prefix, number=None, retry_count=0):
    if retry_count >= 5:
        return None
    try:
        password = generate_custom_password(password_prefix)
        url = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
        payload = {"app_id": 100067, "client_type": 2, "password": password, "source": 2}
        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        if response.status_code == 429:
            time.sleep(30)
            return create_account(region, account_name, password_prefix, number, retry_count + 1)
        if response.status_code == 403:
            return None
        response.raise_for_status()
        res_json = response.json()
        if "data" in res_json and "uid" in res_json["data"]:
            uid = res_json["data"]["uid"]
            return get_token(uid, password, region, account_name, password_prefix, number)
        else:
            return None
    except requests.exceptions.RequestException as e:
        if retry_count < 3:
            time.sleep(5)
            return create_account(region, account_name, password_prefix, number, retry_count + 1)
        return None
    except Exception as e:
        return None

def get_token(uid, password, region, account_name, password_prefix, number=None, retry_count=0):
    if retry_count >= 5:
        return None
    try:
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "100067.connect.garena.com",
            "User-Agent": get_random_ua(),
        }
        body = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": HEX_KEY,
            "client_id": "100067"
        }
        response = requests.post(url, headers=headers, data=body, timeout=30, verify=False)
        if response.status_code == 429:
            time.sleep(30)
            return get_token(uid, password, region, account_name, password_prefix, number, retry_count + 1)
        response.raise_for_status()
        if 'open_id' in response.json():
            open_id = response.json()['open_id']
            access_token = response.json()["access_token"]
            keystream = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
            encoded = ""
            for i in range(len(open_id)):
                encoded += chr(ord(open_id[i]) ^ keystream[i % len(keystream)])
            field = codecs.decode(''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in encoded), 'unicode_escape').encode('latin1')
            return major_register(access_token, open_id, field, uid, password, region, account_name, password_prefix, number)
        return None
    except Exception as e:
        if retry_count < 3:
            time.sleep(5)
            return get_token(uid, password, region, account_name, password_prefix, number, retry_count + 1)
        return None

def major_register(access_token, open_id, field, uid, password, region, account_name, password_prefix, number=None):
    for attempt in range(3):
        try:
            if region.upper() in ["ME", "TH"]:
                url = "https://loginbp.common.ggbluefox.com/MajorRegister"
                host = "loginbp.common.ggbluefox.com"
            else:
                url = "https://loginbp.ggblueshark.com/MajorRegister"
                host = "loginbp.ggblueshark.com"
            name = generate_random_name(account_name, number)
            headers = {
                "Accept-Encoding": "gzip",
                "Authorization": "Bearer",
                "Connection": "Keep-Alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Expect": "100-continue",
                "Host": host,
                "ReleaseVersion": "OB54",
                "User-Agent": get_random_ua(),
                "X-GA": "v1 1",
                "X-Unity-Version": "2018.4."
            }
            lang_code = REGION_LANG.get(region.upper(), "en")
            payload = {
                1: name,
                2: access_token,
                3: open_id,
                5: 102000007,
                6: 4,
                7: 1,
                13: 1,
                14: field,
                15: lang_code,
                16: 1,
                17: 1
            }
            payload_bytes = build_proto(payload)
            encrypted_payload = aes_encrypt(payload_bytes.hex())
            requests.post(url, headers=headers, data=encrypted_payload, verify=False, timeout=30)
            login_result = major_login(uid, password, access_token, open_id, region)
            account_id = login_result.get("account_id", "N/A")
            if account_id != "N/A":
                return {
                    "uid": uid,
                    "password": password,
                    "name": name,
                    "region": region,
                    "status": "success",
                    "account_id": account_id
                }
            else:
                return None
        except Exception as e:
            time.sleep(3)
    return None

def major_login(uid, password, access_token, open_id, region):
    try:
        lang = REGION_LANG.get(region.upper(), "en")
        payload_parts = [
    b'\x1a\x132026-06-24 14:30:00"\tfree fire(\x01:\x071.130.1B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\x0cMTN/SpacetelZ\x04WIFI`\x80\nh\xd0\x05r\x03240z-x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4\x80\x01\xe6\x1e\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|625f716f-91a7-495b-9f16-08fe9d3c6533\xa2\x01\x0e176.28.139.185\xaa\x01\x02',
    lang.encode("ascii"),
    b'\xb2\x01 4306245793de86da425a52caadf21eed\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\rOnePlus A5010\xea\x01@c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94\xf0\x01\x01\xca\x02\x0cMTN/Spacetel\xd2\x02\x04WIFI\xca\x03 1ac4b80ecf0478a44203bf8fac6120f5\xe0\x03\xb5\xee\x02\xe8\x03\x9a\x80\x02\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xa7\x8f\x02\x88\x04\xb5\xee\x02\x90\x04\xa7\x8f\x02\x98\x04\xb5\xee\x02\xb0\x04\x04\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/lib/arm\xe0\x04\x01\xea\x04_e62ab9354d8fb5fb081db338acb33491|/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/base.apk\xf0\x04\x06\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019119026\xa8\x05\x03\xb2\x05\tOpenGLES2\xb8\x05\xff\x01\xc0\x05\x04\xe0\x05\xbe~\xea\x05\t3rd_party\xf2\x05pKqsHT8W93GdcG3ZozENfFwVHtm7qq1eRUNaIDNgRobozIBtLOiYCc4Y6zvvpcICxzQF2sOE4cbytwLs4xZbRnpRMpmWRQKmeO5vcs8nQYBhwqH7K\xf8\x05\xe7\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"\x13R\x11FP\x0eY\x03IQ\x0eF\t\x00\x11XC9_\x00[Q\x0fh[V\na\x07Wm\x0f\x03f'
]
        payload = b''.join(payload_parts)
        if region.upper() in ["ME", "TH"]:
            url = "https://loginbp.common.ggbluefox.com/MajorLogin"
            host = "loginbp.common.ggbluefox.com"
        else:
            url = "https://loginbp.ggblueshark.com/MajorLogin"
            host = "loginbp.ggblueshark.com"
        headers = {
            "Accept-Encoding": "gzip",
            "Authorization": "Bearer",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Expect": "100-continue",
            "Host": host,
            "ReleaseVersion": "OB54",
            "User-Agent": get_random_ua(),
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.11f1"
        }
        data = payload.replace(b'c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94', access_token.encode())
        data = data.replace(b'4306245793de86da425a52caadf21eed', open_id.encode())
        d = encrypt_api(data.hex())
        response = requests.post(url, headers=headers, data=bytes.fromhex(d), verify=False, timeout=30)
        if response.status_code == 200 and len(response.text) > 10:
            jwt_start = response.text.find("eyJ")
            if jwt_start != -1:
                jwt_token = response.text[jwt_start:]
                second_dot = jwt_token.find(".", jwt_token.find(".") + 1)
                if second_dot != -1:
                    jwt_token = jwt_token[:second_dot + 44]
                    try:
                        parts = jwt_token.split('.')
                        if len(parts) >= 2:
                            payload_part = parts[1]
                            padding = 4 - len(payload_part) % 4
                            if padding != 4:
                                payload_part += '=' * padding
                            decoded = base64.urlsafe_b64decode(payload_part)
                            data = json.loads(decoded)
                            account_id = data.get('account_id') or data.get('external_id')
                            if account_id:
                                choose_region_url = "https://loginbp.common.ggbluefox.com/ChooseRegion" if region.upper() in ["ME", "TH"] else "https://loginbp.ggpolarbear.com/ChooseRegion"
                                region_code = "RU" if region.upper() == "CIS" else region.upper()
                                choose_fields = {1: region_code}
                                choose_proto = build_proto(choose_fields)
                                choose_encrypted = encrypt_api(choose_proto.hex())
                                choose_payload = bytes.fromhex(choose_encrypted)
                                choose_headers = {
                                    "Accept-Encoding": "gzip",
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Expect": "100-continue",
                                    "Authorization": f"Bearer {jwt_token}",
                                    "X-Unity-Version": "1.123.1",
                                    "X-GA": "v1 1",
                                    "ReleaseVersion": "OB54",
                                    "User-Agent": get_random_ua(),
                                    "Connection": "Keep-Alive"
                                }
                                requests.post(choose_region_url, headers=choose_headers, data=choose_payload, verify=False, timeout=15)
                                return {"account_id": str(account_id)}
                    except:
                        pass
        return {"account_id": "N/A"}
    except:
        return {"account_id": "N/A"}

def activate_accounts():
    clear_screen()
    print_banner()
    if not os.path.exists("activator.py"):
        print(f"\n{white}[ERROR] activator.py file not found!{reset}")
        input(f"\n{white}Press ENTER to return to menu...{reset}")
        return
    print(f"{white}Running activator script...{reset}")
    print(f"{white}{'=' * 50}{reset}")
    try:
        result = subprocess.run(
            [sys.executable, "activator.py"],
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            print(f"\n{white}activator.py completed successfully!{reset}")
        else:
            print(f"\n{white}[Error] Failed to run activator.py. Error code: {result.returncode}{reset}")
    except Exception as e:
        print(f"\n{white}[Error] An error occurred while running activator.py: {str(e)}{reset}")
    print(f"{white}{'=' * 50}{reset}")
    input(f"\n{white}Press ENTER to return to main menu...{reset}")

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print(f"{white}===================================================")
    print(f"        GUEST ACCOUNT GENERATOR")
    print(f"==================================================={reset}")

def create_single_account_menu():
    clear_screen()
    print_banner()
    print(f"{white}ACCOUNT NAME: {reset}", end="")
    custom_name = input().strip()
    if not custom_name:
        print(f"\n{white}[ERROR] NAME REQUIRED!{reset}")
        input(f"\n{white}PRESS ENTER TO CONTINUE...{reset}")
        return create_single_account_menu()
    print(f"\n{white}AVAILABLE REGIONS: ME, IND, BD, PK, ID, TH, VN, BR, NA, EU, CIS, SAC, TW{reset}")
    print(f"{white}REGION: {reset}", end="")
    region_input = input().strip().upper()
    if region_input not in REGION_LANG:
        print(f"\n{white}[ERROR] INVALID REGION CODE!{reset}")
        input(f"\n{white}PRESS ENTER TO CONTINUE...{reset}")
        return create_single_account_menu()
    print(f"{white}PASSWORD PREFIX (default: JAGWAR): {reset}", end="")
    password_prefix_input = input().strip()
    if not password_prefix_input:
        password_prefix_input = "JAGWAR"
    print(f"\n{white}CREATING ACCOUNT IN REGION: {region_input}{reset}")
    print(f"{white}{'=' * 50}{reset}")
    global save_thread_running
    save_thread = threading.Thread(target=save_worker, daemon=True)
    save_thread_running = True
    save_thread.start()
    result = create_account(region_input, custom_name, password_prefix_input, number=1)
    if result and result.get('account_id') != "N/A":
        if save_account_to_file(result, region_input):
            save_queue.join()
            print(f"\n{white}SUCCESS!{reset}")
            print(f"{white}Name: {result['name']}{reset}")
            print(f"{white}UID: {result['uid']}{reset}")
            print(f"{white}Password: {result['password']}{reset}")
            print(f"{white}Account ID: {result.get('account_id', 'N/A')}{reset}")
            print(f"{white}Region: {region_input}{reset}")
    else:
        print(f"\n{white}[ERROR] ACCOUNT CREATION FAILED!{reset}")
    save_thread_running = False
    save_queue.put(None)
    save_thread.join(timeout=5)
    input(f"\n{white}PRESS ENTER TO RETURN TO MENU...{reset}")
    main_menu()

def create_single_account_thread(region, name_prefix, password_prefix, current_number, total_count):
    final_name = f"{name_prefix}{to_superscript(current_number)}"
    result = create_account(region, name_prefix, password_prefix, number=current_number)
    if result and result.get('account_id') != "N/A":
        if save_account_to_file(result, region):
            with print_lock:
                print(f"{white}[{current_number}/{total_count}] SUCCESS - Name: {result['name']} | UID: {result['uid']}{reset}")
            return "success"
    with print_lock:
        print(f"{white}[{current_number}/{total_count}] FAILED{reset}")
    return "failed"

def create_multiple_accounts():
    global save_thread_running, accounts_saved_count
    clear_screen()
    print_banner()
    save_thread = threading.Thread(target=save_worker, daemon=True)
    save_thread_running = True
    accounts_saved_count = 0
    save_thread.start()
    print(f"\n{white}REGION (ME/IND/BD/PK/ID/TH/VN/BR/NA/EU/CIS/SAC/TW):{reset}")
    print(f"{white}REGION: {reset}", end="")
    region_input = input().strip().upper()
    if region_input not in REGION_LANG:
        print(f"\n{white}[ERROR] INVALID REGION CODE!{reset}")
        time.sleep(1)
        save_thread_running = False
        save_queue.put(None)
        save_thread.join(timeout=5)
        return
    print(f"{white}NAME PREFIX (default: JAGWAR): {reset}", end="")
    name_prefix_input = input().strip()
    if not name_prefix_input:
        name_prefix_input = "JAGWAR"
    print(f"{white}PASSWORD PREFIX (default: JAGWAR): {reset}", end="")
    password_prefix_input = input().strip()
    if not password_prefix_input:
        password_prefix_input = "JAGWAR"
    print(f"{white}HOW MANY ACCOUNTS? (1-1000): {reset}", end="")
    try:
        account_count = int(input().strip())
        if account_count < 1:
            account_count = 1
        elif account_count > 1000:
            account_count = 1000
    except ValueError:
        account_count = 1
    print(f"\n{white}CREATING {account_count} ACCOUNTS IN REGION: {region_input}{reset}")
    print(f"{white}{'=' * 50}{reset}")
    success_count = 0
    failed_count = 0
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for i in range(1, account_count + 1):
            future = executor.submit(
                create_single_account_thread,
                region_input,
                name_prefix_input,
                password_prefix_input,
                i,
                account_count
            )
            futures.append(future)
        for future in as_completed(futures):
            result = future.result()
            if result == "success":
                with counter_lock:
                    success_count += 1
            else:
                with counter_lock:
                    failed_count += 1
    print(f"\n{white}Waiting for accounts to save...{reset}")
    save_queue.join()
    save_thread_running = False
    save_queue.put(None)
    save_thread.join(timeout=5)
    elapsed_time = time.time() - start_time
    print(f"\n{white}{'=' * 50}{reset}")
    print(f"{white}COMPLETED!{reset}")
    print(f"{white}SUCCESS: {success_count}{reset}")
    print(f"{white}FAILED: {failed_count}{reset}")
    print(f"{white}SAVED: {accounts_saved_count}{reset}")
    print(f"{white}TIME: {elapsed_time:.1f} SECONDS{reset}")
    print(f"{white}{'=' * 50}{reset}")
    input(f"\n{white}PRESS ENTER TO RETURN TO MENU...{reset}")
    main_menu()

def show_saved_accounts():
    clear_screen()
    print_banner()
    filename = "JAGWAR.json"
    if not os.path.exists(filename):
        print(f"\n{white}NO ACCOUNTS FOUND!{reset}")
        input(f"\n{white}PRESS ENTER TO RETURN TO MENU...{reset}")
        main_menu()
        return
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            accounts_list = json.load(f)
        if not accounts_list:
            print(f"\n{white}NO ACCOUNTS FOUND!{reset}")
        else:
            print(f"\n{white}TOTAL ACCOUNTS: {len(accounts_list)}{reset}")
            print(f"{white}{'=' * 50}{reset}")
            for i, account in enumerate(accounts_list, 1):
                print(f"{white}[{i}] {account.get('name', 'N/A')} | "
                      f"UID: {account.get('uid', 'N/A')} | "
                      f"Region: {account.get('region', 'N/A')}{reset}")
    except:
        print(f"\n{white}ERROR READING ACCOUNTS FILE!{reset}")
    input(f"\n{white}PRESS ENTER TO RETURN TO MENU...{reset}")
    main_menu()

def clear_saved_accounts():
    clear_screen()
    print_banner()
    filename = "JAGWAR.json"
    if not os.path.exists(filename):
        print(f"\n{white}NO ACCOUNTS TO CLEAR!{reset}")
        input(f"\n{white}PRESS ENTER TO RETURN TO MENU...{reset}")
        main_menu()
        return
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            accounts_list = json.load(f)
        if accounts_list:
            print(f"\n{white}ARE YOU SURE YOU WANT TO CLEAR {len(accounts_list)} ACCOUNTS? (y/n): {reset}", end="")
            confirm = input().strip().lower()
            if confirm == 'y':
                backup_file = f"JAGWAR_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(accounts_list, f, ensure_ascii=False, indent=4)
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print(f"\n{white}ACCOUNTS CLEARED! BACKUP SAVED AS: {backup_file}{reset}")
            else:
                print(f"\n{white}CANCELLED.{reset}")
        else:
            print(f"\n{white}NO ACCOUNTS TO CLEAR!{reset}")
    except Exception as e:
        print(f"\n{white}ERROR CLEARING ACCOUNTS: {str(e)}{reset}")
    input(f"\n{white}PRESS ENTER TO RETURN TO MENU...{reset}")
    main_menu()

def main_menu():
    while True:
        clear_screen()
        print_banner()
        print(f"{white}    [1] CREATE ACCOUNTS{reset}")
        print(f"{white}    [2] CREATE SINGLE ACCOUNT{reset}")
        print(f"{white}    [3] VIEW SAVED ACCOUNTS{reset}")
        print(f"{white}    [4] CLEAR ALL ACCOUNTS{reset}")
        print(f"{white}    [5] ACTIVATE ACCOUNTS{reset}")
        print(f"{white}    [6] EXIT{reset}")
        print(f"{white}{reset}")
        print(f"{white}CHOOSE OPTION (1-6): {reset}", end="")
        user_choice = input().strip()
        if user_choice == "1":
            create_multiple_accounts()
        elif user_choice == "2":
            create_single_account_menu()
        elif user_choice == "3":
            show_saved_accounts()
        elif user_choice == "4":
            clear_saved_accounts()
        elif user_choice == "5":
            activate_accounts()
        elif user_choice == "6":
            print(f"\n{white}GOODBYE!{reset}")
            time.sleep(1)
            sys.exit(0)
        else:
            print(f"\n{white}INVALID OPTION! PLEASE TRY AGAIN.{reset}")
            time.sleep(0.5)

# ===== واجهة Flask API الجديدة (فوق الكود الأصلي) =====
app = Flask(__name__)

# HTML بسيط لعرض الواجهة (اختياري)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><title>JAGWAR API - 2099</title></head>
<body>
<h1>JAGWAR Guest Account Generator - API</h1>
<p>استخدم الروابط التالية:</p>
<ul>
    <li><b>POST /create_single</b> - إنشاء حساب واحد (json: region, name, password_prefix)</li>
    <li><b>POST /create_multi</b> - إنشاء عدة حسابات (json: region, name_prefix, password_prefix, count)</li>
    <li><b>GET /saved</b> - عرض الحسابات المحفوظة</li>
    <li><b>POST /clear</b> - مسح الحسابات (json: confirm=true)</li>
    <li><b>POST /activate</b> - تشغيل activator.py</li>
    <li><b>GET /</b> - هذه الصفحة</li>
</ul>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/create_single', methods=['POST'])
def api_create_single():
    data = request.get_json()
    region = data.get('region', 'ME').upper()
    name = data.get('name', 'JAGWAR')
    password_prefix = data.get('password_prefix', 'JAGWAR')
    if region not in REGION_LANG:
        return jsonify({"error": "Invalid region"}), 400
    # تشغيل save_thread مؤقتاً
    global save_thread_running
    st = threading.Thread(target=save_worker, daemon=True)
    save_thread_running = True
    st.start()
    result = create_account(region, name, password_prefix, number=1)
    if result and result.get('account_id') != "N/A":
        save_account_to_file(result, region)
        save_queue.join()
        save_thread_running = False
        save_queue.put(None)
        st.join(timeout=5)
        return jsonify({"status": "success", "account": result})
    save_thread_running = False
    save_queue.put(None)
    st.join(timeout=5)
    return jsonify({"status": "failed"}), 500

@app.route('/create_multi', methods=['POST'])
def api_create_multi():
    data = request.get_json()
    region = data.get('region', 'ME').upper()
    name_prefix = data.get('name_prefix', 'JAGWAR')
    password_prefix = data.get('password_prefix', 'JAGWAR')
    count = int(data.get('count', 1))
    if region not in REGION_LANG:
        return jsonify({"error": "Invalid region"}), 400
    if count < 1 or count > 1000:
        return jsonify({"error": "Count must be 1-1000"}), 400
    global save_thread_running, accounts_saved_count
    st = threading.Thread(target=save_worker, daemon=True)
    save_thread_running = True
    accounts_saved_count = 0
    st.start()
    success_count = 0
    failed_count = 0
    accounts = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for i in range(1, count+1):
            futures.append(executor.submit(create_account, region, name_prefix, password_prefix, i))
        for future in as_completed(futures):
            res = future.result()
            if res and res.get('account_id') != "N/A":
                save_account_to_file(res, region)
                accounts.append(res)
                success_count += 1
            else:
                failed_count += 1
    save_queue.join()
    save_thread_running = False
    save_queue.put(None)
    st.join(timeout=5)
    return jsonify({
        "status": "done",
        "success": success_count,
        "failed": failed_count,
        "accounts": accounts
    })

@app.route('/saved', methods=['GET'])
def api_saved():
    filename = "JAGWAR.json"
    if not os.path.exists(filename):
        return jsonify({"accounts": [], "count": 0})
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            accounts_list = json.load(f)
        return jsonify({"count": len(accounts_list), "accounts": accounts_list})
    except:
        return jsonify({"error": "Corrupted file"}), 500

@app.route('/clear', methods=['POST'])
def api_clear():
    data = request.get_json()
    if data.get('confirm') != True:
        return jsonify({"error": "confirm must be true"}), 400
    filename = "JAGWAR.json"
    if os.path.exists(filename):
        backup_file = f"JAGWAR_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if os.path.exists(filename):
            os.rename(filename, backup_file)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return jsonify({"status": "cleared", "backup": backup_file})
    return jsonify({"status": "no file"})

@app.route('/activate', methods=['POST'])
def api_activate():
    if not os.path.exists("activator.py"):
        return jsonify({"error": "activator.py not found"}), 404
    try:
        result = subprocess.run(
            [sys.executable, "activator.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return jsonify({
            "status": "done",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== تشغيل الخادم =====
if __name__ == "__main__":
    # إذا أردت تشغيل الواجهة الطرفية الأصلية، استخدم main_menu() بدلاً من ذلك
    # ولكن هنا نبدأ الـ API افتراضياً
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)