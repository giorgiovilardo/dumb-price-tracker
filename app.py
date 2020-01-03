from flask import Flask
import configparser

app = Flask(__name__)


@app.route("/")
def returnEmpty():
    return "up"


@app.route("/priceview/")
def getPrices():
    result = []
    with open("mr.ini", "r") as configfile:
        config = configparser.ConfigParser()
        config.read_file(configfile)
        for section in config.sections():
            k = {}
            for key in config[section]:
                k[key] = config[section][key]
            result.append(k)
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Price checker</title>
    </head>
    <body>
      <h1>Price Tracker</h1>
      <!-- example with two sites -->
      <h2>Sito 1 (<a href="{result[0]['url']}" target="_blank">link</a>)</h2>
      <p>Ultimo controllo: {result[0]['lastcheck']}</p>
      <p>Prezzo: {result[0]['price']}</p>
      <p>Il prezzo è <span style="font-weight: 700">{result[0]['changed']}</span>.</p>
      <p style="font-size: 10px;">Info tecniche - failedLast: {result[0]['failedlast']} laststatus: {result[0]['lasthttpstatus']}
      <hr>
      <h2>Sito 2 (<a href="{result[1]['url']}" target="_blank">link</a>)</h2>
      <p>Ultimo controllo: {result[1]['lastcheck']}</p>
      <p>Prezzo: {result[1]['price']}</p>
      <p>Il prezzo è <span style="font-weight: 700">{result[1]['changed']}</span>.</p>
      <p style="font-size: 10px;">Info tecniche - failedLast: {result[1]['failedlast']} laststatus: {result[1]['lasthttpstatus']}
    </body>
    </html>
    """
    # Translation of fields:
    # Site 1
    # Last check
    # Price
    # The price is -verb-
    # Technical info: failedLast, laststatus
