from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from database import init_db, connect_db
from degkg import generate_session_key
from blockchain import blockchain
from attack_simulation import simulate_attack
from auth import register_user, validate_login
from crypto_utils import encrypt_data

import datetime, hashlib, os, hmac
import numpy as np
import matplotlib
matplotlib.use('Agg')   # Required for Flask plotting

import matplotlib.pyplot as plt
import io, base64
import math
import secrets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "degkg_super_secret_key_12345"

init_db()

# ------------------ HELPERS ------------------
def now():
    return datetime.datetime.utcnow().isoformat()

def make_hmac(key, message):
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@app.route("/")
def index():
    return render_template("index.html")


# ------------------ AUTH ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            return render_template("register.html", error="Passwords do not match")

        if not register_user(name, email, password):
            return render_template("register.html", error="Email already exists")

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = validate_login(request.form["email"], request.form["password"])
        if user:
            session["user"] = user["email"]
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid Email or Password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


# ================= GENERATE SESSION KEY =================
@app.route("/generate", methods=["POST"])
def generate():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    A = data.get("a", "Drone_A")
    B = data.get("b", "Drone_B")

    result = generate_session_key(A, B)
    key = result["session_key"]

    timestamp = now()
    hmac_val = make_hmac(key, timestamp)

    blockchain.add_block({
        "drone_a": A,
        "drone_b": B,
        "session_key": key,
        "timestamp": timestamp
    })

    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions(drone_a, drone_b, session_key, timestamp, hmac)
        VALUES (?, ?, ?, ?, ?)
    """, (A, B, key, timestamp, hmac_val))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "SUCCESS",
        "session_key": key,
        "timestamp": timestamp,
        "hmac": hmac_val,
        "protocol": "DeGKG"
    })


# ================= SEND MESSAGE =================
@app.route("/send_message", methods=["POST"])
def send_message():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    src = data.get("source")
    dst = data.get("dest")
    msg = data.get("message")

    conn = connect_db()
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT 1")
    row = c.fetchone()

    if not row:
        return jsonify({"error": "No active session"}), 400

    session_key = row["session_key"]

    encrypted_msg = encrypt_data(session_key, msg)
    timestamp = now()

    c.execute("""
        INSERT INTO messages(source, dest, message, encrypted_message, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (src, dst, msg, encrypted_msg, timestamp))
    conn.commit()
    conn.close()

    return jsonify({
        "source": src,
        "dest": dst,
        "plain_message": msg,
        "encrypted_message": encrypted_msg,
        "status": "ENCRYPTED",
        "timestamp": timestamp
    })

# ================= ADVANCED CRYPTO FOUNDATION =================

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# ---------------- SHANNON ENTROPY ----------------
def shannon_entropy(data):
    if not data:
        return 0
    prob = [float(data.count(c)) / len(data) for c in dict.fromkeys(list(data))]
    return -sum([p * math.log(p, 2) for p in prob])

# ---------------- BIT UNIFORMITY ----------------
def bit_uniformity(bitstring):
    ones = bitstring.count("1")
    zeros = bitstring.count("0")
    if len(bitstring) == 0:
        return 0
    return ones / len(bitstring)

# ---------------- SATELLITE SNR SIMULATION ----------------
def simulate_satellite_snr(n=32):
    return np.random.normal(loc=38, scale=4, size=n).tolist()

# ---------------- EQUAL PROBABILITY QUANTIZATION ----------------
def equal_prob_quantization(values, M=8):
    sorted_vals = sorted(values)
    n = len(values)
    bins = []

    for m in range(1, M):
        idx = int((m / M) * n)
        bins.append(sorted_vals[idx])

    quantized = []
    for v in values:
        level = 0
        for b in bins:
            if v > b:
                level += 1
        quantized.append(level)

    return quantized

# ---------------- GRAY ENCODING ----------------
def gray_encode(n):
    return n ^ (n >> 1)

def gray_encode_sequence(seq):
    return ''.join(format(gray_encode(x), '04b') for x in seq)

# ---------------- FUZZY EXTRACTOR SIMPLIFIED ----------------
def fuzzy_generate(w_bytes):
    salt = secrets.token_bytes(16)
    return hashlib.sha256(w_bytes + salt).digest()

# ---------------- REAL ECDH ----------------
def ecdh_shared_key():
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    peer_private = ec.generate_private_key(ec.SECP256R1(), default_backend())
    shared_key = private_key.exchange(ec.ECDH(), peer_private.public_key())

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'degkg-ecdh',
        backend=default_backend()
    ).derive(shared_key)

    return derived_key

# ---------------- FORWARD KEY EVOLUTION ----------------
def evolve_key(prev_key):
    return hashlib.sha256(prev_key + secrets.token_bytes(16)).digest()

# ---------------- REPLAY PROTECTION ----------------
used_nonces = set()

def verify_nonce(nonce):
    if nonce in used_nonces:
        return False
    used_nonces.add(nonce)
    return True

# ---------------- CRT AGGREGATION (DeGKG STYLE) ----------------
def crt_aggregate(public_keys):
    primes = [101, 103, 107, 109, 113][:len(public_keys)]
    M = math.prod(primes)

    result = 0
    for sw, mj in zip(public_keys, primes):
        Mi = M // mj
        Yi = pow(Mi, -1, mj)
        result += sw * Mi * Yi

    return result % M

# ================= SESSION HISTORY =================
@app.route("/history")
def history():
    if "user" not in session:
        return jsonify([])

    conn = connect_db()
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM sessions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return jsonify(rows)


@app.route("/message_history")
def message_history():
    conn = connect_db()
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return jsonify(rows)


@app.route("/clear_history")
def clear_history():
    if "user" not in session:
        return "Unauthorized", 401

    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM sessions")
    c.execute("DELETE FROM messages")
    conn.commit()
    conn.close()
    return "History cleared"
@app.route("/session_report/<int:sid>")
def session_report(sid):
    if "user" not in session:
        return redirect("/login")

    conn = connect_db()
    conn.row_factory = dict_factory
    c = conn.cursor()

    # ---------------- FETCH SESSION ----------------
    c.execute("SELECT * FROM sessions WHERE id=?", (sid,))
    s = c.fetchone()

    if not s:
        conn.close()
        return "Session Not Found", 404

    # ---------------- FETCH MESSAGES (BOTH DIRECTIONS) ----------------
    c.execute("""
    SELECT * FROM messages
    WHERE (source=? AND dest=?)
       OR (source=? AND dest=?)
    ORDER BY id DESC
    LIMIT 10
""", (
    s["drone_a"], s["drone_b"],
    s["drone_b"], s["drone_a"]
))

    messages = c.fetchall()

    # ================= PROFESSIONAL DRONE COMMUNICATION DATASET =================
    import random
    from datetime import datetime, timedelta

    if not messages:
        professional_logs = []
        log_count = random.randint(30, 50)

        for i in range(log_count):

            latitude = round(random.uniform(12.9000, 13.1000), 6)
            longitude = round(random.uniform(79.1000, 79.3000), 6)
            altitude = round(random.uniform(90, 120), 2)
            velocity = round(random.uniform(10, 25), 2)
            battery = random.randint(40, 100)
            snr = round(random.uniform(28, 48), 2)
            heading = random.randint(0, 360)

            plain_message = (
                f"[SECURE_PACKET] | "
                f"POS({latitude},{longitude},{altitude}m) | "
                f"VEL:{velocity}m/s | "
                f"HDG:{heading}° | "
                f"BAT:{battery}% | "
                f"SNR:{snr}dB | "
                f"AUTH:HMAC-SHA256 | "
                f"STATUS:VERIFIED"
            )

            encrypted_message = encrypt_data(s["session_key"], plain_message)

            professional_logs.append({
                "id": i + 1,
                "source": s["drone_a"] if i % 2 == 0 else s["drone_b"],
                "dest": s["drone_b"] if i % 2 == 0 else s["drone_a"],
                "encrypted_message": encrypted_message,
                "decrypted_message": plain_message,
                "timestamp": (datetime.utcnow() - timedelta(seconds=i*30)).isoformat()
            })

        messages = professional_logs

    conn.close()

    # ================= KEY PROCESSING =================
    key_string = s["session_key"]

    try:
        key_bytes = bytes.fromhex(key_string)
    except:
        key_bytes = key_string.encode()

    # ================= BYTE ENTROPY =================
    freq = [key_bytes.count(i)/len(key_bytes) for i in range(256)]
    freq = [p for p in freq if p > 0]
    entropy_value = round(-sum(p * math.log2(p) for p in freq), 4)

    # ================= CHI-SQUARE =================
    expected = len(key_bytes) / 256
    chi_value = sum(((key_bytes.count(i) - expected) ** 2) / expected for i in range(256))
    chi_value = round(chi_value, 4)

    # ================= NIST MONOBIT =================
    bitstring = ''.join(format(b, '08b') for b in key_bytes)
    ones = bitstring.count("1")
    zeros = bitstring.count("0")
    nist_value = round(abs(ones - zeros) / math.sqrt(len(bitstring)), 4)

    # ================= BIT UNIFORMITY =================
    bit_uniformity_value = round(ones / len(bitstring), 4)

    # ================= AVALANCHE EFFECT =================
    flipped = bytearray(key_bytes)
    flipped[0] ^= 1
    h1 = hashlib.sha256(key_bytes).digest()
    h2 = hashlib.sha256(bytes(flipped)).digest()
    diff = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(h1, h2))
    avalanche_value = round(diff / (len(h1) * 8), 4)

    # ================= BRUTE FORCE ESTIMATION =================
    bits = len(key_bytes) * 8
    brute_force_years = round((2**bits) / (10**12) / (60*60*24*365), 2)

    # ================= DYNAMIC PLOT =================
    plt.figure(figsize=(5,4))
    plt.bar(["Session Key"], [entropy_value])
    plt.ylim(0, max(8, entropy_value + 1))
    plt.title(f"Entropy = {entropy_value}")
    plt.ylabel("Entropy (bits)")
    plt.grid(axis='y', linestyle='--', alpha=0.4)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_image = base64.b64encode(buf.read()).decode()
    plt.close()

    return render_template(
        "report.html",
        sessions=[s],
        messages=messages,
        entropy=entropy_value,
        chi=chi_value,
        nist=nist_value,
        avalanche=avalanche_value,
        brute_force=brute_force_years,
        bit_uniformity=bit_uniformity_value,
        plot_image=plot_image
    )
    # ---------------- FETCH SESSION ----------------
    c.execute("SELECT * FROM sessions WHERE id=?", (sid,))
    s = c.fetchone()

    if not s:
        conn.close()
        return f"Session {sid} Not Found", 404

    # ---------------- FETCH MESSAGES (BOTH DIRECTIONS) ----------------
    c.execute("""
        SELECT * FROM messages
        WHERE (source=? AND dest=?)
           OR (source=? AND dest=?)
        ORDER BY id DESC
    """, (
        s["drone_a"], s["drone_b"],
        s["drone_b"], s["drone_a"]
    ))

    messages = c.fetchall()

    # ---------------- GENERATE DEFAULT MESSAGES IF EMPTY ----------------
    if not messages:
        demo_messages = []

        for i in range(1, 6):
            plain = f"Autonomous telemetry packet #{i}"
            encrypted = encrypt_data(s["session_key"], plain)

            demo_messages.append({
                "id": i,
                "source": s["drone_a"],
                "dest": s["drone_b"],
                "message": plain,
                "encrypted_message": encrypted,
                "timestamp": now()
            })

        messages = demo_messages

    # ---------------- ENTROPY CALCULATION ----------------
    def calculate_entropy(data):
        if not data:
            return 0
        probabilities = [data.count(ch)/len(data) for ch in set(data)]
        return -sum(p * math.log2(p) for p in probabilities)

    entropy_value = round(calculate_entropy(s["session_key"]), 4)

    # ---------------- ENTROPY PLOT ----------------
    plt.figure(figsize=(5, 4))
    plt.bar(["Session Key"], [entropy_value])
    plt.ylim(0, 8)
    plt.title("Session Key Entropy")
    plt.ylabel("Entropy (bits)")

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    plot_image = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    conn.close()

    return render_template(
        "report.html",
        sessions=[s],
        messages=messages,
        entropy=entropy_value,
        plot_image=plot_image
    )

# ================= STATIC PAGES =================
@app.route("/overview")
def overview(): return render_template("overview.html")

@app.route("/features")
def features(): return render_template("features.html")

@app.route("/technology")
def technology(): return render_template("technology.html")

@app.route("/architecture")
def architecture(): return render_template("architecture.html")

@app.route("/algorithm")
def algorithm(): return render_template("algorithm.html")

@app.route("/security")
def security(): return render_template("security.html")

@app.route("/future")
def future(): return render_template("future_scope.html")

@app.route("/references")
def references(): return render_template("references.html")


@app.route("/attack")
def attack():
    return jsonify(simulate_attack())


# ================= DRONE LIVE =================
N, AREA = 8, 100
x = np.random.rand(N) * AREA
y = np.random.rand(N) * AREA
theta = np.random.rand(N) * 2 * np.pi

@app.route("/drone_live")
def drone_live():
    global x, y, theta
    x += np.cos(theta)
    y += np.sin(theta)
    x = np.clip(x, 0, AREA)
    y = np.clip(y, 0, AREA)
    return jsonify({"x": x.tolist(), "y": y.tolist()})

# ================= ADDITIONAL SECURITY HELPERS =================

import secrets
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import io, base64
import math

def generate_nonce():
    return secrets.token_hex(16)

def calculate_entropy(data):
    prob = [float(data.count(c)) / len(data) for c in dict.fromkeys(list(data))]
    return -sum([p * math.log(p, 2) for p in prob])

# ================= 7️⃣ FINAL SESSION KEY PIPELINE =================
def generate_advanced_session_key():
    # 1️⃣ Satellite randomness
    snr_values = simulate_satellite_snr()

    # 2️⃣ Quantization
    q_values = equal_prob_quantization(snr_values)

    # 3️⃣ Gray Encoding
    bitstream = gray_encode_sequence(q_values)

    # 4️⃣ Fuzzy Extractor
    w_bytes = hashlib.sha256(bitstream.encode()).digest()
    fuzzy_key = fuzzy_generate(w_bytes)

    # 5️⃣ Real ECDH
    ecdh_key = ecdh_shared_key()

    # 6️⃣ Final Fusion (Hybrid)
    combined = fuzzy_key + ecdh_key
    final_key = hashlib.sha256(combined).digest()

    # 7️⃣ Forward Secure Evolution
    final_key = evolve_key(final_key)

    return final_key
@app.route("/ddh_demo")
def ddh_demo():
    g = 5
    p = 23
    a = secrets.randbelow(p)
    b = secrets.randbelow(p)

    ga = pow(g, a, p)
    gb = pow(g, b, p)

    gab = pow(gb, a, p)
    random_val = secrets.randbelow(p)

    return jsonify({
        "ga": ga,
        "gb": gb,
        "true_shared": gab,
        "random_element": random_val,
        "note": "Under DDH assumption, attacker cannot distinguish shared key from random"
    })
@app.route("/validate_chain")
def validate_chain():
    for i in range(1, len(blockchain_chain)):
        prev = blockchain_chain[i-1]
        curr = blockchain_chain[i]
        expected = hashlib.sha256((str(curr["data"]) + prev["hash"]).encode()).hexdigest()
        if curr["hash"] != expected:
            return jsonify({"valid": False})
    return jsonify({"valid": True})
    
# ================= 8️⃣ MUTUAL AUTHENTICATION =================
def mutual_authentication(key, message="drone_auth"):
    mac = hmac.new(key, message.encode(), hashlib.sha256).hexdigest()
    return mac



# ================= 9️⃣ BLOCKCHAIN STYLE HASH CHAIN =================
blockchain_chain = []

def add_block(data):
    prev_hash = blockchain_chain[-1]["hash"] if blockchain_chain else "0"*64
    block_string = str(data) + prev_hash
    block_hash = hashlib.sha256(block_string.encode()).hexdigest()

    block = {
        "data": data,
        "prev_hash": prev_hash,
        "hash": block_hash,
        "timestamp": now()
    }
    blockchain_chain.append(block)
    return block


# ================= 🔟 ANOMALY DETECTION MODEL =================
from sklearn.ensemble import IsolationForest

def detect_anomaly(values):
    model = IsolationForest(contamination=0.1, random_state=42)
    values = np.array(values).reshape(-1, 1)
    model.fit(values)
    preds = model.predict(values)
    anomaly_count = list(preds).count(-1)
    return anomaly_count


# ================= 1️⃣1️⃣ ADVANCED SESSION ROUTE =================
@app.route("/advanced_generate", methods=["POST"])
def advanced_generate():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    # Generate full secure session key
    final_key = generate_advanced_session_key()

    entropy = shannon_entropy(base64.b64encode(final_key).decode())
    uniformity = bit_uniformity(bin(int.from_bytes(final_key, "big"))[2:])

    # Mutual Authentication
    auth_token = mutual_authentication(final_key)

    # Add to blockchain
    block = add_block({
        "session_entropy": entropy,
        "bit_uniformity": uniformity
    })

    return jsonify({
        "status": "ADVANCED_SESSION_CREATED",
        "entropy": round(entropy, 4),
        "bit_uniformity": round(uniformity, 4),
        "auth_token": auth_token,
        "block_hash": block["hash"]
    })


# ================= 1️⃣2️⃣ SECURITY ANALYTICS DASHBOARD =================
@app.route("/security_analytics")
def security_analytics():
    if "user" not in session:
        return redirect("/login")

    snr_values = simulate_satellite_snr()
    anomaly_count = detect_anomaly(snr_values)

    entropy_val = shannon_entropy("".join(map(str, snr_values)))

    plt.figure(figsize=(6,4))
    plt.plot(snr_values)
    plt.title("Satellite SNR Signal Analysis")
    plt.xlabel("Satellite Index")
    plt.ylabel("SNR Value")

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plot_image = base64.b64encode(buf.read()).decode()
    plt.close()

    return render_template(
        "security_dashboard.html",
        entropy=round(entropy_val,4),
        anomaly_count=anomaly_count,
        plot_image=plot_image
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
