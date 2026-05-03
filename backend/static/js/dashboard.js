<!DOCTYPE html>
<html>
<head>
<title>DeGKG Dashboard</title>
<link rel="stylesheet" href="/static/css/style.css">
</head>
<body>

<header>
    Decentralized Secure Drone Communication Dashboard (DeGKG)
</header>

<div class="container">

    <!-- CONTROL PANEL -->
    <div class="card">
        <h3>Drone Session Key Generation</h3>

        <label>Source Drone:</label>
        <select id="droneA">
            <option>Drone_A</option>
            <option>Drone_B</option>
            <option>Drone_C</option>
        </select>

        <br><br>

        <label>Destination Drone:</label>
        <select id="droneB">
            <option>Drone_B</option>
            <option>Drone_A</option>
            <option>Drone_C</option>
        </select>

        <br><br>

        <button onclick="generateKey()">Generate Secure Session Key</button>
        <button onclick="simulateAttack()">Simulate Attack</button>
    </div>

    <!-- OUTPUT PANEL -->
    <div class="card">
        <h3>System Output</h3>
        <pre id="output">Waiting for action...</pre>
    </div>

</div>

<footer>
    Final Year Project | DeGKG Secure Drone Swarm System
</footer>

<script>
// ================= GENERATE SESSION KEY =================
function generateKey() {
    let A = document.getElementById("droneA").value;
    let B = document.getElementById("droneB").value;

    fetch("/generate", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({a:A, b:B})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("output").innerText =
            "SESSION KEY GENERATED\n\n" +
            "Drone A: " + A + "\n" +
            "Drone B: " + B + "\n" +
            "Session Key: " + data.session_key + "\n" +
            "Timestamp: " + data.timestamp + "\n" +
            "HMAC: " + data.hmac;
    });
}


// ================= SIMULATE ATTACK =================
function simulateAttack() {
    fetch("/attack")
    .then(res => res.json())
    .then(data => {
        alert("Attack: " + data.attack_type + "\nStatus: " + data.status);
    });
}
</script>

</body>
</html>
