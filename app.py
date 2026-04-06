import hashlib
import json
import time
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# ─────────────────────────────────────────────
#  BLOCKCHAIN CORE
# ─────────────────────────────────────────────

class Block:
    def __init__(self, index, data, previous_hash, validator="SystemNode"):
        self.index = index
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.data = data
        self.previous_hash = previous_hash
        self.validator = validator
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_str = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "validator": self.validator,
            "nonce": self.nonce,
            "hash": self.hash
        }


class Blockchain:
    VALIDATORS = ["CooperativeA", "CertificationBureau", "GovernmentAgency", "LogisticsCompany"]

    def __init__(self):
        self.chain = []
        self.products = {}   # product_id -> list of block indices
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = Block(
            index=0,
            data={"type": "GENESIS", "message": "Agriculture blockchain initialized"},
            previous_hash="0" * 64,
            validator="GenesisNode"
        )
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def _pick_validator(self):
        import random
        return random.choice(self.VALIDATORS)

    def add_event(self, product_id, event_type, payload):
        """Adds a new event block for a product."""
        data = {
            "product_id": product_id,
            "event_type": event_type,
            "payload": payload
        }
        block = Block(
            index=len(self.chain),
            data=data,
            previous_hash=self.last_block.hash,
            validator=self._pick_validator()
        )
        self.chain.append(block)

        if product_id not in self.products:
            self.products[product_id] = []
        self.products[product_id].append(block.index)

        return block

    def get_product_chain(self, product_id):
        """Returns all blocks for a product."""
        if product_id not in self.products:
            return []
        return [self.chain[i].to_dict() for i in self.products[product_id]]

    def is_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.hash != curr.calculate_hash():
                return False, i
            if curr.previous_hash != prev.hash:
                return False, i
        return True, -1

    def tamper_block(self, index, new_payload):
        """Demo only: simulates chain tampering."""
        if 0 < index < len(self.chain):
            self.chain[index].data["payload"]["tampered"] = new_payload
            # intentionally do not recalculate hash -> chain breaks
            return True
        return False

    def stats(self):
        valid, _ = self.is_valid()
        return {
            "total_blocks": len(self.chain),
            "total_products": len(self.products),
            "chain_valid": valid,
            "validators": self.VALIDATORS
        }


# Single global blockchain instance
bc = Blockchain()

# Seed chain with sample products
def seed_data():
    # Quba Apple
    pid1 = "PROD-QUBA-001"
    bc.add_event(pid1, "PRODUCTION_RECORDED", {
        "product": "Quba Apple", "variety": "Golden", "location": "Quba, Azerbaijan",
        "coordinates": {"lat": 41.36, "lon": 48.51},
        "harvest_date": "2026-10-15", "farmer": "Əli Məmmədov"
    })
    bc.add_event(pid1, "QUALITY_CONTROL", {
        "certificate": "GlobalGAP", "result": "Passed",
        "auditor": "CertificationBureau", "score": 97
    })
    bc.add_event(pid1, "LOGISTICS_STARTED", {
        "vehicle": "TRUCK-4821", "departure": "Quba Warehouse", "arrival": "Baku Distribution Center",
        "temperature_c": 2.5, "cold_chain": "Secure"
    })
    bc.add_event(pid1, "CUSTOMS_APPROVED", {
        "customs_code": "AZ-08B-2026", "destination_country": "Turkey", "status": "Approved"
    })
    bc.add_event(pid1, "RETAIL_DELIVERY", {
        "store": "CarrefourSA Istanbul", "shelf_code": "A-14",
        "qr_code": f"QR-{pid1}", "consumer_verification": "Active"
    })

    # Tomato
    pid2 = "PROD-TOMAT-002"
    bc.add_event(pid2, "PRODUCTION_RECORDED", {
        "product": "Greenhouse Tomato", "variety": "Beef", "location": "Antalya, Turkey",
        "coordinates": {"lat": 36.88, "lon": 30.70},
        "harvest_date": "2026-04-01", "farmer": "Mehmet Yilmaz"
    })
    bc.add_event(pid2, "PESTICIDE_APPLICATION", {
        "pesticide": "BioControl-X", "amount_ml": 50, "application_date": "2026-03-20",
        "waiting_period_days": 7, "approved_by": "CooperativeA"
    })
    bc.add_event(pid2, "QUALITY_CONTROL", {
        "certificate": "Organic TR", "result": "Passed", "score": 94
    })
    bc.add_event(pid2, "LOGISTICS_STARTED", {
        "vehicle": "TRUCK-1133", "departure": "Antalya", "arrival": "Istanbul Market",
        "temperature_c": 8.0, "cold_chain": "Normal"
    })

seed_data()


# ─────────────────────────────────────────────
#  FLASK ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def api_stats():
    return jsonify(bc.stats())

@app.route("/api/chain")
def api_chain():
    return jsonify([b.to_dict() for b in bc.chain])

@app.route("/api/products")
def api_products():
    result = []
    for pid, indices in bc.products.items():
        first_block = bc.chain[indices[0]]
        result.append({
            "product_id": pid,
            "name": first_block.data["payload"].get("product", pid),
            "event_count": len(indices),
            "last_event": bc.chain[indices[-1]].data["event_type"],
            "last_timestamp": bc.chain[indices[-1]].timestamp
        })
    return jsonify(result)

@app.route("/api/product/<product_id>")
def api_product(product_id):
    chain = bc.get_product_chain(product_id)
    if not chain:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(chain)

@app.route("/api/add_event", methods=["POST"])
def api_add_event():
    body = request.json
    product_id = body.get("product_id", "").strip()
    event_type = body.get("event_type", "").strip()
    payload = body.get("payload", {})

    if not product_id or not event_type:
        return jsonify({"error": "product_id and event_type are required"}), 400

    block = bc.add_event(product_id, event_type, payload)
    return jsonify({"success": True, "block": block.to_dict()})

@app.route("/api/validate")
def api_validate():
    valid, idx = bc.is_valid()
    return jsonify({
        "valid": valid,
        "broken_at_index": idx if not valid else None,
        "total_blocks": len(bc.chain)
    })

@app.route("/api/tamper/<int:index>", methods=["POST"])
def api_tamper(index):
    """Demo: break chain (cyberattack simulation)"""
    bc.tamper_block(index, "*** ATTACK: DATA WAS MODIFIED ***")
    return jsonify({"message": f"Block {index} was tampered with. Validate the chain."})

@app.route("/api/new_product", methods=["POST"])
def api_new_product():
    body = request.json
    product_id = "PROD-" + uuid.uuid4().hex[:8].upper()
    payload = {
        "product": body.get("name", "Unknown"),
        "variety": body.get("variety", "-"),
        "location": body.get("origin", "-"),
        "harvest_date": body.get("harvest_date", "-"),
        "farmer": body.get("farmer", "-")
    }
    block = bc.add_event(product_id, "PRODUCTION_RECORDED", payload)
    return jsonify({"product_id": product_id, "block": block.to_dict()})

if __name__ == "__main__":
    app.run(debug=True, port=5050)
