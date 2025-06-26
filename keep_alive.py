from flask import Flask, render_template, jsonify
from threading import Thread

app = Flask(__name__, template_folder="templates")

# Bot 狀態：你可以用變數來控制，如果你未來想讓 bot.py 來設定也可以
bot_status = "online"


@app.route("/")
def index():
    return render_template("status.html")


@app.route("/api/status")
def status():
    return jsonify({"status": bot_status})


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
