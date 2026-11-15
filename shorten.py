import zlib, base64
from flask import Flask, redirect, request
import urllib

with open("zurldict.txt","rb") as f:
    zdict = f.read()

commonurls = []
commonurls_expanded = []
with open("commonurls.txt","r") as f: #source: https://archive.org/details/urlteam_2025-03-06-16-17-02
    for line in f.readlines():
        if "\t" in line:
            commonurl, expanded = line.rstrip("\n").split("\t")
            commonurls.append(commonurl)
            commonurls_expanded.append(expanded)

app = Flask(__name__)

prefix = "/"

@app.get("/")
def home():
    return """
<html>
    <head>
        <title>Url shortener</title>
    </head>
    <body>
        <h1>Url shortener</h1>
        <form method="post">
            <label for="url">Url:</label>
            <input type="url" id="url" name="url" value="https://">
            <input type="submit" value="Submit">
        </form>
    </body>
</html>
    """

b64dictionary = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

@app.post("/")
def shorten():
    input_url = request.form['url'].replace("<", "")
    fix = "_"
    parsed = urllib.parse.urlsplit(input_url)
    netloc = parsed.netloc.lstrip("www.")
    if netloc in commonurls:
        index = commonurls.index(netloc)
        fix = b64dictionary[index>>6] + b64dictionary[index&63]
        text = parsed._replace(scheme="", netloc="").geturl().lstrip("//").encode()
    else:
        text = parsed._replace(scheme="").geturl().lstrip("//").encode()
    co = zlib.compressobj(wbits=-15, zdict=zdict)
    c = co.compress(text) + co.flush()
    result = fix + base64.urlsafe_b64encode(c).decode().rstrip("=")

    return """
<html>
    <head>
        <title>Url shortener</title>
    </head>
    <style>
dd{
    font-family: monospace;
}
    </style>
    <body>
        <h1>Url shortener</h1>
        <dl>
            <dt>Input URL:</dt><dd>%s</dd>

            <dt>Shortened:</dt><dd><a href="http://%s">%s</a></dd>
        </dl>
        <a href="/">Back</a>
    </body>
</html>
"""%(input_url.replace("&","&amp;"), prefix+result, result)

@app.get("/<val>")
def result(val):
    if not val.startswith("_"):
        index = (b64dictionary.index(val[0])<<6)+b64dictionary.index(val[1])
        prefix = commonurls_expanded[index]+"/"
        val = val[2:]
    else:
        prefix = "https://"
        val = val[1:]
    val = base64.urlsafe_b64decode(val.encode() + b'==')
    co = zlib.decompressobj(wbits=-15, zdict=zdict)
    c = co.decompress(val) + co.flush()
    return redirect(prefix+c.decode())

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__=="__main__":
    ip=get_ip()
    port = 5679
    prefix = "%s:%s/"%(ip, port)
    print(prefix)
    app.run(host=ip, port=port)
