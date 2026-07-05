import json
import asyncio
import aiohttp
import aiofiles
import socket
import ssl
import gzip
import time
from io import BytesIO
from datetime import datetime
import jwt as pyjwt
import urllib3
import binascii
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
from protobuf_decoder.protobuf_decoder import Parser
from flask import Flask, request, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def ua():
    versions = ['4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8',
                '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3',
                '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3']
    models = ['SM-A125F', 'SM-A225F', 'SM-A325M', 'SM-A515F', 'SM-A725F', 'SM-M215F', 'SM-M325FV',
              'Redmi 9A', 'Redmi 9C', 'POCO M3', 'POCO M4 Pro', 'RMX2185', 'RMX3085',
              'moto g(9) play', 'CPH2239', 'V2027', 'OnePlus Nord', 'ASUS_Z01QD']
    android_versions = ['9', '10', '11', '12', '13', '14']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID', 'ru-RU', 'hi-IN']
    countries = ['USA', 'MEX', 'BRA', 'IDN', 'RUS', 'IND']
    return f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {random.choice(android_versions)};{random.choice(languages)};{random.choice(countries)};)"

def encAEs(hexStr):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hexStr), AES.block_size)).hex()

def decAEs(hexStr):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return unpad(cipher.decrypt(bytes.fromhex(hexStr)), AES.block_size).hex()

def encPacket(hexStr, k, iv):
    return AES.new(k, AES.MODE_CBC, iv).encrypt(pad(bytes.fromhex(hexStr), 16)).hex()

def decPacket(hexStr, k, iv):
    return unpad(AES.new(k, AES.MODE_CBC, iv).decrypt(bytes.fromhex(hexStr)), 16).hex()

def encVarint(n):
    if n < 0: return b''
    h = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        h.append(b)
        if not n: break
    return bytes(h)

def createVarint(field, value):
    return encVarint((field << 3) | 0) + encVarint(value)

def createLength(field, value):
    hdr = encVarint((field << 3) | 2)
    enc = value.encode() if isinstance(value, str) else value
    return hdr + encVarint(len(enc)) + enc

def createProto(fields):
    pkt = bytearray()
    for f, v in fields.items():
        if isinstance(v, dict):
            nested = createProto(v)
            pkt.extend(createLength(f, nested))
        elif isinstance(v, int):
            pkt.extend(createVarint(f, v))
        elif isinstance(v, (str, bytes)):
            pkt.extend(createLength(f, v))
    return pkt

def decodeHex(h):
    r = hex(h)[2:]
    return "0" + r if len(r) == 1 else r

def fixParsed(parsed):
    d = {}
    for r in parsed:
        fd = {'wire_type': r.wire_type}
        if r.wire_type in ("varint", "string", "bytes"):
            fd['data'] = r.data
        elif r.wire_type == 'length_delimited':
            fd['data'] = fixParsed(r.data.results)
        d[r.field] = fd
    return d

def decodePacket(hexInput):
    try:
        parsed = Parser().parse(hexInput)
        return json.dumps(fixParsed(parsed))
    except Exception:
        return None

def xBunner():
    av = ['902000016', '902000031', '902000011', '902000065',
          '902000204', '902000192', '902000191', '902000179',
          '902000133', '902045001', '902038023', '902048004',
          '902039014', '902000063', '902000306', '902047009']
    return int(random.choice(av))

def genPkt(pkt, n, k, iv):
    enc = encPacket(pkt, k, iv)
    l = decodeHex(len(enc) // 2)
    if len(l) == 2: hdr = n + "000000"
    elif len(l) == 3: hdr = n + "00000"
    elif len(l) == 4: hdr = n + "0000"
    elif len(l) == 5: hdr = n + "000"
    else: hdr = n + "000000"
    return bytes.fromhex(hdr + l + enc)

def openRoom(k, iv):
    f = {1: 2, 2: {1: 1, 2: 15, 3: 5, 4: "JAGWAR KING", 5: "1", 6: 12, 7: 1,
                    8: 1, 9: 1, 11: 1, 12: 2, 14: 36981056,
                    15: {1: "IDC3", 2: 126, 3: "ME"},
                    16: "\u0001\u0003\u0004\u0007\t\n\u000b\u0012\u000f\u000e\u0016\u0019\u001a \u001d",
                    18: 2368584, 27: 1, 34: "\u0000\u0001", 40: "en", 48: 1,
                    49: {1: 21}, 50: {1: 36981056, 2: 2368584, 5: 2}}}
    return genPkt(str(createProto(f).hex()), '0E15', k, iv)

def spmRoom(k, iv, uid):
    f = {1: 22, 2: {1: int(uid)}}
    return genPkt(str(createProto(f).hex()), '0E15', k, iv)

async def gAccess(u, p, session):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": ua(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": str(u),
        "password": str(p),
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    async with session.post(url, headers=headers, data=data, ssl=False) as resp:
        if resp.status == 200:
            js = await resp.json()
            return js.get('access_token'), js.get('open_id')
    return None, None

async def majorLogin(pyl, session):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    conn = aiohttp.TCPConnector(ssl=ctx)
    async with aiohttp.ClientSession(connector=conn) as sess:
        headers = {
            'X-Unity-Version': '2022.3.47f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': 'UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
            'Host': 'loginbp.ggpolarbear.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'deflate, gzip'
        }
        async with sess.post("https://loginbp.ggpolarbear.com/MajorLogin", headers=headers, data=pyl) as resp:
            raw = await resp.read()
            if resp.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            if resp.status in (200, 201):
                return raw
    return None

async def getPorts(tok, pyl, session):
    headers = {
        'Expect': '100-continue',
        'Authorization': f'Bearer {tok}',
        'X-Unity-Version': '2022.3.47f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB54',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
        'Host': 'clientbp.ggpolarbear.com',
        'Connection': 'close',
        'Accept-Encoding': 'deflate, gzip'
    }
    async with session.post("https://clientbp.ggpolarbear.com/GetLoginData", headers=headers, data=pyl, ssl=False) as resp:
        raw = await resp.read()
        d = json.loads(decodePacket(raw.hex()))
        a1, a2 = d['32']['data'], d['14']['data']
        return a1[:len(a1)-6], a1[len(a1)-5:], a2[:len(a2)-6], a2[len(a2)-5:]

def getKiv(raw):
    class _runtime_version:
        class Domain: PUBLIC = 0
        @staticmethod
        def ValidateProtobufRuntimeVersion(*args, **kwargs): return True
    _runtime_version.ValidateProtobufRuntimeVersion()
    _sym_db = _symbol_database.Default()
    DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10my_message.proto\">\n\tMyMessage\x12\x0f\n\x07\x66ield21\x18\x15 \x01(\x03\x12\x0f\n\x07\x66ield22\x18\x16 \x01(\x0c\x12\x0f\n\x07\x66ield23\x18\x17 \x01(\x0c\x62\x06proto3')
    _globals = globals()
    _builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
    _builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'my_message_pb2', _globals)
    MyMessage = _globals['MyMessage']
    m = MyMessage()
    m.ParseFromString(raw)
    ts = Timestamp()
    ts.FromNanoseconds(m.field21)
    return ts.seconds * 1_000_000_000 + ts.nanos, m.field22, m.field23

def buildAuth(jwtTok, k, iv, ts):
    dec = pyjwt.decode(jwtTok, options={"verify_signature": False})
    enc = hex(dec['account_id'])[2:]
    tsH = decodeHex(ts)
    jH = jwtTok.encode().hex()
    hLen = hex(len(encPacket(jH, k, iv)) // 2)[2:]
    padMap = {9: '0000000', 8: '00000000', 10: '000000', 7: '000000000'}
    pad = padMap.get(len(enc), '00000000')
    return f'0115{pad}{enc}{tsH}00000{hLen}' + encPacket(jH, k, iv)

async def login(u, p, session):
    at, oid = await gAccess(u, p, session)
    if not at: return None
    dT = bytes.fromhex('1a12323032362d30362d323420393a31353a303922096672656520666972653a07312e3132362e31420a694f532031382e372e364a0848616e6468656c6452022d2d5a045749464960800e68bc0672033332367a0e61726d363465207c2030207c2036800198168a010d4170706c6520413132204750559201054d6574616c9a012a4170706c657c30323237413738322d313546382d343036342d393542452d443132464242423441463137a201037a6269aa01026672b201206561313135633934636566626539316135663661353832326534393436643165ba010134c2010848616e6468656c64ca010a6950686f6e6531312c38d201025347ea014062303034353365363136373565353764386339343037613839356430323163306362376431343533626561353764346261656364353331333263643235663030f00101f003acdc03f803870cb00402c80403e00401ea0409494f53446576696365f00403f804019a050a32303139313230323733a80503b205054d6574616cb805ff01c00504e005dee702ea0503696f73f205484b71734854304f2f6145394e6f4a765134686968366c5a4577554d4e35674c626d706b6a435970552f2f57646d416a396c2f562f764c647a6f596f325152316a7a564d4948513d3d8806019006019a060134a2060134b2060e675c10177317570877520d465d41b80601')
    dT = dT.replace(b'2025-07-30 11:02:51', str(datetime.now())[:-7].encode())
    dT = dT.replace(b'b00453e61675e57d8c9407a895d021c0cb7d1453bea57d4baecd53132cd25f00', at.encode())
    dT = dT.replace(b'ea115c94cefbe91a5f6a5822e4946d1e', oid.encode())
    dT = dT.replace(b'1.120.1', b'1.123.8')
    pyl = bytes.fromhex(encAEs(dT.hex()))
    raw = await majorLogin(pyl, session)
    if not raw: return None
    d = json.loads(decodePacket(raw.hex()))
    jwtTok = d['8']['data']
    ts, k, iv = getKiv(raw)
    ip, port, ip2, port2 = await getPorts(jwtTok, pyl, session)
    auth = buildAuth(jwtTok, k, iv, ts)
    return auth, k, iv, ip, port, ip2, port2

class AsyncCli:
    def __init__(self, u, p):
        self.u = u
        self.p = p
        self.key = None
        self.iv = None
        self.reader1 = self.writer1 = None
        self.reader2 = self.writer2 = None
        self.alive = False
        self.task = asyncio.create_task(self._run())

    async def _run(self):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    res = await login(self.u, self.p, session)
                    if not res:
                        await asyncio.sleep(10)
                        continue
                    auth, k, iv, ip, port, ip2, port2 = res
                    self.key, self.iv = k, iv

                    self.reader1, self.writer1 = await asyncio.open_connection(ip, int(port))
                    self.writer1.write(bytes.fromhex(auth))
                    await self.writer1.drain()
                    await asyncio.sleep(0.3)
                    await self.reader1.read(1024)

                    self.reader2, self.writer2 = await asyncio.open_connection(ip2, int(port2))
                    self.writer2.write(bytes.fromhex(auth))
                    await self.writer2.drain()
                    await asyncio.sleep(0.2)

                    self.alive = True
                    async with _clis_lock:
                        _clis.append(self)
                    print(f'[+] {self.u} connected')

                    while True:
                        try:
                            data = await asyncio.wait_for(self.reader1.read(4096), timeout=30)
                            if not data:
                                break
                        except asyncio.TimeoutError:
                            continue
            except Exception as e:
                print(f'[-] {self.u}: {e}')
            finally:
                self.alive = False
                async with _clis_lock:
                    if self in _clis:
                        _clis.remove(self)
                for w in (self.writer1, self.writer2):
                    if w:
                        w.close()
                        await w.wait_closed()
                self.reader1 = self.writer1 = self.reader2 = self.writer2 = None
            await asyncio.sleep(5)

_clis = []
_clis_lock = asyncio.Lock()
_tasks = {}
_MAX_ACTIVE = 50
_active_semaphore = asyncio.Semaphore(_MAX_ACTIVE)
_loop = None

async def _spamLoop(uid, stop_event):
    while not stop_event.is_set():
        async with _clis_lock:
            snap = [(c.writer2, c.key, c.iv, c.u) for c in _clis if c.alive and c.writer2 and c.key]
        for writer2, k, iv, u in snap:
            if stop_event.is_set():
                break
            try:
                roomPkt = openRoom(k, iv)
                spmPkt = spmRoom(k, iv, uid)
                writer2.write(roomPkt)
                await writer2.drain()
                for _ in range(10):
                    if stop_event.is_set():
                        break
                    writer2.write(spmPkt)
                    await writer2.drain()
                    await asyncio.sleep(0.05)
            except Exception as e:
                print(f'spam err {u}: {e}')
        await asyncio.sleep(0.3)

def add(uid):
    if uid in _tasks:
        return False
    stop = asyncio.Event()
    task = asyncio.create_task(_spamLoop(uid, stop))
    _tasks[uid] = (task, stop)
    return True

def remove(uid):
    if uid not in _tasks:
        return False
    task, stop = _tasks.pop(uid)
    stop.set()
    task.cancel()
    return True

def active():
    return list(_tasks.keys())

async def init():
    async with aiofiles.open("accs.json", "r") as f:
        content = await f.read()
        accs = json.loads(content)
    items = list(accs.items())
    bSz  = 5
    for i in range(0, len(items), bSz):
        batch = items[i:i+bSz]
        for u, p in batch:
            AsyncCli(u, p)
        print(f'[boot] batch {i//bSz+1}/{(len(items)+bSz-1)//bSz} — {len(batch)} accs')
        await asyncio.sleep(2)

async def _wAdd(uid):
    return add(uid)

async def _wRemove(uid):
    return remove(uid)

@app.route('/spam', methods=['GET'])
def start_spam():
    uid = request.args.get('user_id')
    if not uid or not uid.isdigit():
        return jsonify({'error': 'Missing or invalid uid parameter'}), 400
    ok = asyncio.run_coroutine_threadsafe(_wAdd(uid), _loop).result(timeout=5)
    return jsonify({'status': 'success' if ok else 'already running', 'uid': uid})

@app.route('/stop', methods=['GET'])
def stop_spam():
    uid = request.args.get('user_id')
    if not uid or not uid.isdigit():
        return jsonify({'error': 'Missing or invalid uid parameter'}), 400
    ok = asyncio.run_coroutine_threadsafe(_wRemove(uid), _loop).result(timeout=5)
    return jsonify({'status': 'success' if ok else 'not running', 'uid': uid})

_loop = None

if __name__ == '__main__':
    from threading import Thread
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    def runFlask():
        try:
            app.run(host='0.0.0.0', port=6272, threaded=True, use_reloader=False, debug=False)
        except Exception as e:
            print(f'[flask err] {e}')
    Thread(target=_loop.run_forever, daemon=True).start()
    asyncio.run_coroutine_threadsafe(init(), _loop)
    print('[*] Flask starting on port 8100')
    runFlask()
