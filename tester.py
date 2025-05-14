import requests
import pyotp
import time
import base64
import json

# ganti dengan userid dan shared secret yang ingin dicoba
userid = "sister"
shared_secret = "ii2210_sister_1234"

# ganti dengan url server kalian (sesuaikan dengan IP publik VM)
server_url = "http://20.243.126.85:17787"

# ganti dengan motd yang diinginkan
motd = {"motd" : "testing from tester.py"}

# generate token TOTP
s = base64.b32encode(shared_secret.encode("utf-8")).decode("utf-8")
totp = pyotp.TOTP(s=s, digest="SHA256", digits=8)
x = f"{userid}:" + totp.now()

# encode basic auth
a = "Basic " + base64.b64encode(bytes(x, encoding="ascii")).decode("ascii")

# kirim request POST
resp = requests.post(url=server_url + "/motd", headers={"Authorization" : a}, json=motd)

# tampilkan hasil
print(resp.status_code)
print(resp.content.decode("utf-8"))
