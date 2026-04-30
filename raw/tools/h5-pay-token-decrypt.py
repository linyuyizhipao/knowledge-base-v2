import hashlib
import base64
import urllib.parse
import time
import json

def md5_hex(s):
    """Return MD5 as hex string, matching PHP md5()"""
    if isinstance(s, str):
        s = s.encode()
    return hashlib.md5(s).hexdigest()

def authcode(string, operation, key, expiry=2592000):
    if operation == 1:  # DECODE
        string = urllib.parse.unquote(string.replace("__", "%"))

    ckey_length = 4

    key_md5 = md5_hex(key)  # 32-char hex string
    keya = md5_hex(key_md5[:16])   # MD5 of first 16 hex chars
    keyb = md5_hex(key_md5[16:32]) # MD5 of last 16 hex chars

    if ckey_length:
        if operation == 1:  # DECODE
            keyc = string[:ckey_length]
        else:
            keyc = md5_hex(str(time.time()))[-ckey_length:]
    else:
        keyc = ""

    # PHP: $cryptkey = $keya . md5($keya . $keyc);
    # Both are 32-char hex strings, concatenation = 64-char hex string
    # PHP ord($cryptkey[$i]) gets ASCII value of hex char, not hex-decoded byte
    cryptkey_str = keya + md5_hex(keya + keyc)
    cryptkey = cryptkey_str.encode()  # ASCII bytes of hex string
    key_length = len(cryptkey)

    if operation == 1:  # DECODE
        b64_part = string[ckey_length:]
        padding = 4 - len(b64_part) % 4
        if padding != 4:
            b64_part += '=' * padding
        string_bytes = base64.b64decode(b64_part)
    else:
        expiry_str = f"{int(expiry + time.time()):010d}" if expiry else "0" * 10
        hash_check = md5_hex(string + keyb)[:16]
        string_bytes = (expiry_str + hash_check + string).encode()

    string_length = len(string_bytes)

    # RC4 key scheduling algorithm (KSA)
    box = list(range(256))
    rndkey = [cryptkey[i % key_length] for i in range(256)]

    j = 0
    for i in range(256):
        j = (j + box[i] + rndkey[i]) % 256
        box[i], box[j] = box[j], box[i]

    # RC4 pseudo-random generation algorithm (PRGA) + XOR
    result = bytearray()
    a = 0
    j = 0
    for i in range(string_length):
        a = (a + 1) % 256
        j = (j + box[a]) % 256
        box[a], box[j] = box[j], box[a]
        result.append(string_bytes[i] ^ box[(box[a] + box[j]) % 256])

    if operation == 1:  # DECODE
        result_str = result.decode('latin-1')
        timestamp = int(result_str[:10])
        md5_check = result_str[10:26]
        content = result_str[26:]
        expected_md5 = md5_hex(content + keyb)[:16]

        if timestamp != 0:
            exp_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            if timestamp - time.time() <= 0:
                print(f"⚠️  Token 已过期 (过期时间: {exp_time})")
            else:
                remain = timestamp - int(time.time())
                print(f"✅ Token 有效 (过期时间: {exp_time}, 剩余 {remain} 秒)")

        if md5_check == expected_md5:
            print("✅ MD5 校验通过")
        else:
            print(f"❌ MD5 校验失败! (expected: {expected_md5}, got: {md5_check})")

        return content
    else:
        encoded = base64.b64encode(bytes(result)).rstrip(b'=').decode()
        return urllib.parse.quote(keyc + encoded).replace("%", "__")


H5_Pay_Key = '98nnju$@/**('
token = '9ba7fYbyOijvDZmKjDo75nLgo3TBi1K6R5fWRgU4__2B4MYjJI8JX1j__2FzXjbSzbXf6nrl5NeRrtpLWx2D22dmsRnAt7e0aqluVECMlNWXPIHRXFjLhFCbbGxrhhSu__2BYDkpTddu2WFmyzoHmYtrWfJvLy__2BmSsOE0x84Z4ucqfWsKxdY9FBZvKCpkB7i7UBww3pFSnuDxjNl__2FJDbftFPhW92G7wLwai7iayXRwoYoQOXN6UyT2TvwLLYRg__2F0ttWjYdy__2BogIc1mifGBgx3aOTbyfUKT48yPXGfwyz1k2aLUoj0x4Gw__2Fxw7lI86'

result = authcode(token, 1, H5_Pay_Key)

if not result:
    print("\n❌ 解密失败")
else:
    print("\n" + "=" * 60)
    print("解密原始数据:")
    print("=" * 60)
    print(result)
    print()

    data = urllib.parse.parse_qs(result)
    print("=" * 60)
    print("解析后字段:")
    print("=" * 60)
    for k, v in data.items():
        val = v[0] if len(v) == 1 else v
        print(f"  {k}: {val}")

    if 'dateline' in data:
        ts = int(data['dateline'][0])
        print(f"\n生成时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}")
        age = int(time.time()) - ts
        print(f"Token 已存在: {age} 秒 ({age/60:.1f} 分钟)")

    if 'params' in data:
        print("\nparams 字段 (JSON):")
        params_str = data['params'][0]
        try:
            params_obj = json.loads(params_str)
            print(json.dumps(params_obj, indent=2, ensure_ascii=False))
        except:
            print(params_str)
