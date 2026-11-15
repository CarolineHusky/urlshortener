import zlib, base64
from flask import Flask, redirect, request

with open("zurldict.txt","rb") as f:
    zdict = f.read()


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

@app.post("/")
def shorten():
    input_url = request.form['url'].replace("<", "")
    text = input_url.lstrip("https://").encode()
    co = zlib.compressobj(wbits=-15, zdict=zdict)
    c = co.compress(text) + co.flush()
    result = base64.urlsafe_b64encode(c).decode().rstrip("=")

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
    val = base64.urlsafe_b64decode(val.encode() + b'==')
    co = zlib.decompressobj(wbits=-15, zdict=zdict)
    c = co.decompress(val) + co.flush()
    return redirect("https://"+c.decode())

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
