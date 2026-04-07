from flask import Flask, render_template, request, jsonify
from instagrapi import Client
import threading
import time
import random
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sujal_final"

state = {"running": False, "sent": 0, "logs": [], "start_time": None}
cfg = {
    "sessionid": "",
    "hater_name": "HATER",
    "delay": 0.8,
    "thread_id": None,
    "max_groups": 12
}

# TERE AUTOMA NAMES (HATER replace hoga)
NAMES = [
    "HATER  𝗞𝗔𝗖𝗛𝗥𝗘 𝗪𝗔𝗟𝗘🥀",
    "HATER   𝗚𝗨𝗟𝗔𝗠",
    "HATER  𝗕𝗛𝗔𝗚 𝗠𝗔𝗔𝗧 🤟🏿",
    "HATER  𝗔𝗧𝗠𝗞𝗕𝗙𝗝 🥀 🖖🏿",
    "HATER  𝗛𝗔𝗚 𝗗𝗜𝗬𝗔 🤟🏿",
    "HATER  𝗚𝗕 𝗥𝗢𝗔𝗗 𝗪𝗔𝗟𝗘 🤙🏿",
    "HATER  𝗿𝗻𝗱𝗶 🤙🏿",
    "HATER  𝗦𝗨𝗣𝗣𝗢𝗥𝗧 𝗗𝗨🎀",
    "HATER  𝗞𝗜 𝗕𝗘𝗛𝗘𝗡 𝗖𝗛𝗨𝗗 🥀",
    "HATER 𝗕𝗔𝗔𝗣 𝗞𝗢 𝗕𝗛𝗨𝗟 𝗠𝗔𝗧 🥀",
    "HATER  𝗦𝗨𝗣𝗣𝗢𝗥𝗧 𝗟𝗔 🤙🏿",
    "𝗮𝗯𝗲 𝗻𝗰 𝗸𝘆𝗮 𝗱𝗲𝗸𝗵 𝗿𝗵𝗮 𝗵𝗮 🤟🏿",
    "HATER  𝗚𝗨𝗟𝗔𝗠",
    "HATER  𝗕𝗛𝗔𝗚 𝗠𝗔𝗔𝗧 🤟🏿",
    "HATER  𝗛𝗔𝗚 𝗗𝗜𝗬𝗔 🤟🏿"
]

def log(msg):
    entry = f"[{time.strftime('%H:%M:%S')}] {msg}"
    state["logs"].append(entry)
    if len(state["logs"]) > 500:
        state["logs"] = state["logs"][-500:]

def spam_bot():
    cl = Client()
    cl.delay_range = [6, 18]

    try:
        cl.login_by_sessionid(cfg["sessionid"])
        log("✅ LOGIN SUCCESS")
    except Exception as e:
        log(f"❌ LOGIN FAILED → {str(e)[:80]}")
        return

    name_index = 0
    while state["running"]:
        try:
            if cfg["thread_id"]:
                groups = [type('obj', (object,), {'id': int(cfg["thread_id"]), 'thread_title': 'Specific GC'})()]
                log("🎯 Specific Thread ID mode")
            else:
                threads = cl.direct_threads(amount=30)
                groups = [t for t in threads if getattr(t, "is_group", False)]
                groups = groups[:cfg["max_groups"]]

            if not groups:
                log("⚠ No groups found, retrying...")
                time.sleep(25)
                continue

            log(f"🔄 Processing {len(groups)} groups")

            for thread in groups:
                if not state["running"]:
                    break
                gid = thread.id
                title = getattr(thread, 'thread_title', 'Unknown')

                current_name = NAMES[name_index % len(NAMES)].replace("HATER", cfg["hater_name"])
                name_index += 1

                try:
                    cl.direct_thread_change_title(gid, current_name)
                    log(f"💠 NC SUCCESS → {current_name}")
                except Exception:
                    log(f"⚠ NC FAILED in {title} (continuing...)")

                time.sleep(cfg["delay"])

            time.sleep(10)

        except Exception as e:
            log(f"⚠ ERROR: {str(e)[:60]} → Continuing...")
            time.sleep(20)

        if state["running"]:
            log("❤️ HEARTBEAT - Bot alive")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    global state
    state["running"] = False
    time.sleep(0.3)

    state = {"running": True, "sent": 0, "logs": ["🚀 HARI GOD NC BOT STARTED"], "start_time": time.time()}

    cfg["sessionid"] = request.form.get("sessionid", "").strip()
    cfg["hater_name"] = request.form.get("hater_name", "HATER").strip()
    cfg["delay"] = float(request.form.get("delay", "0.8"))
    cfg["thread_id"] = request.form.get("thread_id", "").strip() or None
    cfg["max_groups"] = int(request.form.get("max_groups", "12"))

    threading.Thread(target=spam_bot, daemon=True).start()
    log("HARI GOD NC BOT STARTED")
    return jsonify({"ok": True})

@app.route("/stop", methods=["POST"])
def stop():
    state["running"] = False
    log("⛔ STOPPED BY USER")
    return jsonify({"ok": True})

@app.route("/status")
def status():
    uptime = "00:00:00"
    if state.get("start_time"):
        t = int(time.time() - state["start_time"])
        h, r = divmod(t, 3600)
        m, s = divmod(r, 60)
        uptime = f"{h:02d}:{m:02d}:{s:02d}"
    return jsonify({
        "running": state["running"],
        "sent": state["sent"],
        "uptime": uptime,
        "logs": state["logs"][-100:]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
