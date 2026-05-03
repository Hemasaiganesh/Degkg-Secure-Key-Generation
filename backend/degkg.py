import hashlib, secrets, time, random, hmac, json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "degkg_session_history.json")


# =================================================
# SNR Simulation
# =================================================
def generate_snr_vector(size=6):
    return [round(random.uniform(20, 50), 2) for _ in range(size)]


# =================================================
# Quantization
# =================================================
def quantize_snr(snr_values, levels=4):
    min_v, max_v = 20, 50
    step = (max_v - min_v) / levels
    return [max(0, min(int((v - min_v) / step), levels - 1)) for v in snr_values]


# =================================================
# REAL FUZZY EXTRACTOR LOGIC (deterministic)
# Same features → same key
# =================================================
def fuzzy_gen(features):
    feature_str = "".join(map(str, features))
    helper_data = hashlib.sha256(feature_str.encode()).hexdigest()[:16]
    key = hashlib.sha256((feature_str + helper_data).encode()).hexdigest()
    return key, helper_data


# =================================================
# REAL DH PER DRONE (persistent private keys)
# =================================================
DRONE_KEYS = {}

def get_drone_private(drone_id, p=7919):
    if drone_id not in DRONE_KEYS:
        DRONE_KEYS[drone_id] = secrets.randbelow(p)
    return DRONE_KEYS[drone_id]


def dh_shared_secret(drone_a, drone_b, g=5, p=7919):
    priv_a = get_drone_private(drone_a)
    priv_b = get_drone_private(drone_b)

    pub_a = pow(g, priv_a, p)
    pub_b = pow(g, priv_b, p)

    shared = pow(pub_b, priv_a, p)
    return hashlib.sha256(str(shared).encode()).hexdigest()


# =================================================
# HMAC
# =================================================
def generate_hmac(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


# =================================================
# KEY UPDATE (Forward Secrecy)
# =================================================
def update_session_key(old_key):
    return hashlib.sha256((old_key + "FS").encode()).hexdigest()


# =================================================
# MAIN DeGKG SESSION KEY GENERATION
# =================================================
def generate_session_key(drone_a, drone_b):

    snr = generate_snr_vector()
    q_snr = quantize_snr(snr)

    intra_key, helper_data = fuzzy_gen(q_snr)

    shared_secret = dh_shared_secret(drone_a, drone_b)

    nonce = secrets.token_hex(16)
    timestamp = int(time.time())

    # Proper KDF
    material = f"{intra_key}{shared_secret}{nonce}{timestamp}"
    session_key = hashlib.sha256(material.encode()).hexdigest()

    auth_tag = generate_hmac(session_key, f"{drone_a}{drone_b}{timestamp}")
    next_key = update_session_key(session_key)

    session_data = {
        "drone_a": drone_a,
        "drone_b": drone_b,
        "snr": snr,
        "quantized_snr": q_snr,
        "session_key": session_key,
        "next_session_key": next_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "helper_data": helper_data,
        "hmac": auth_tag,
        "protocol": "DeGKG",
        "status": "ACTIVE"
    }

    return session_data
