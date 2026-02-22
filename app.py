import sqlite3
import json
import os
import requests
from flask import Flask, render_template, redirect, url_for, session, request, flash

# ---------------------------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------------------------
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR   = os.path.join(BASE_DIR, "static")
DB_PATH      = os.path.join(BASE_DIR, "instance", "shop.db")

print("=" * 60)
print(f"  BASE_DIR    : {BASE_DIR}")
print(f"  TEMPLATE_DIR: {TEMPLATE_DIR}")
print(f"  templates exist: {os.path.isdir(TEMPLATE_DIR)}")
print("=" * 60)
PUBLIC_ROUTES = {"login", "static"}


        
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "ecommerce-scm-demo-secret-2024"

# Pages that don't require login
PUBLIC_ROUTES = {"login", "static"}

@app.before_request
def require_login():
    if request.endpoint and request.endpoint not in PUBLIC_ROUTES:
        if not session.get("user"):
            return redirect(url_for("login"))
# ---------------------------------------------------------------------------
# RELAY PROXY
# ---------------------------------------------------------------------------
RELAY_PROXY_URL = "http://localhost:1031"

# ---------------------------------------------------------------------------
# VALID COUPON CODES
# ---------------------------------------------------------------------------
VALID_COUPONS = {
    "SAVE10":  10,
    "SAVE20":  20,
    "SAVE30":  30,
    "WELCOME": 15,
    "FESTIVE": 25,
}

# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            price    REAL NOT NULL,
            image    TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            items      TEXT NOT NULL,
            total      REAL NOT NULL,
            payment    TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO products (name, price, image, category) VALUES (?, ?, ?, ?)",
            [
                ("Wireless Headphones", 2999.00, "headphones", "Electronics"),
                ("Running Shoes",       1499.00, "shoes",       "Footwear"),
                ("Cotton T-Shirt",       499.00, "tshirt",      "Clothing"),
                ("Smart Watch",         3999.00, "watch",       "Electronics"),
                ("Backpack",             899.00, "bag",         "Accessories"),
                ("Sunglasses",           749.00, "glasses",     "Accessories"),
            ]
        )
    conn.commit()
    conn.close()

# ---------------------------------------------------------------------------
# FEATURE FLAGS
# ---------------------------------------------------------------------------
def evaluate_flag(flag_key, default_value, user_id="anonymous"):
    try:
        resp = requests.post(
            f"{RELAY_PROXY_URL}/ofrep/v1/evaluate/flags/{flag_key}",
            json={"context": {"targetingKey": user_id}},
            timeout=2
        )
        if resp.status_code == 200:
            return resp.json().get("value", default_value)
    except Exception:
        pass
    return default_value


def get_all_flags(user_id="anonymous"):
    return {
        # Original flags
        "discount-banner-enabled":  evaluate_flag("discount-banner-enabled",  False,                   user_id),
        "cash-on-delivery-enabled": evaluate_flag("cash-on-delivery-enabled", False,                   user_id),
        "promo-banner-enabled":     evaluate_flag("promo-banner-enabled",     False,                   user_id),
        "new-checkout-layout":      evaluate_flag("new-checkout-layout",      False,                   user_id),
        "discount-percentage":      evaluate_flag("discount-percentage",      "10",                    user_id),
        "promo-banner-text":        evaluate_flag("promo-banner-text",        "Grand Sale! Shop Now!", user_id),
        # New flags
        "free-shipping-enabled":    evaluate_flag("free-shipping-enabled",    False,                   user_id),
        "stock-alert-enabled":      evaluate_flag("stock-alert-enabled",      False,                   user_id),
        "dark-mode-enabled":        evaluate_flag("dark-mode-enabled",        False,                   user_id),
        "buy-now-enabled":          evaluate_flag("buy-now-enabled",          False,                   user_id),
        "ratings-enabled":          evaluate_flag("ratings-enabled",          False,                   user_id),
        "coupon-box-enabled":       evaluate_flag("coupon-box-enabled",       False,                   user_id),
    }

# ---------------------------------------------------------------------------
# CART HELPERS
# ---------------------------------------------------------------------------
def get_cart():
    return session.get("cart", {})


def cart_total(cart):
    conn  = get_db()
    total = 0.0
    for pid, qty in cart.items():
        row = conn.execute("SELECT price FROM products WHERE id=?", (int(pid),)).fetchone()
        if row:
            total += row["price"] * qty
    conn.close()
    return total

# ---------------------------------------------------------------------------
# ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    conn     = get_db()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    flags = get_all_flags()
    cart  = get_cart()
    return render_template("index.html", products=products,
                           flags=flags, cart_count=sum(cart.values()))


@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    cart      = get_cart()
    key       = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    flash("Item added to cart!", "success")
    return redirect(url_for("index"))


@app.route("/cart")
def cart():
    conn  = get_db()
    cart  = get_cart()
    items = []
    for pid, qty in cart.items():
        row = conn.execute("SELECT * FROM products WHERE id=?", (int(pid),)).fetchone()
        if row:
            items.append({
                "id":       row["id"],
                "name":     row["name"],
                "price":    row["price"],
                "qty":      qty,
                "subtotal": row["price"] * qty,
            })
    conn.close()

    total = cart_total(cart)
    flags = get_all_flags()

    # Flag-based discount
    flag_discount = round(total * float(flags["discount-percentage"]) / 100, 2) \
                    if flags["discount-banner-enabled"] else 0.0

    # Coupon discount
    coupon         = session.get("coupon", None)
    coupon_discount = round(total * coupon["discount"] / 100, 2) if coupon else 0.0

    # Apply the higher discount — cannot stack both
    best_discount   = max(flag_discount, coupon_discount)
    discount_source = "coupon" if coupon and coupon_discount >= flag_discount else "flag"

    return render_template(
        "cart.html",
        items=items,
        total=total,
        flag_discount=flag_discount,
        coupon=coupon,
        coupon_discount=coupon_discount,
        best_discount=best_discount,
        discount_source=discount_source,
        flags=flags,
        cart_count=sum(cart.values()),
    )


@app.route("/apply-coupon", methods=["POST"])
def apply_coupon():
    code = request.form.get("coupon_code", "").strip().upper()
    if code in VALID_COUPONS:
        session["coupon"] = {"code": code, "discount": VALID_COUPONS[code]}
        flash(f"Coupon {code} applied! {VALID_COUPONS[code]}% off.", "success")
    else:
        session.pop("coupon", None)
        flash("Invalid coupon code. Try SAVE10, SAVE20, WELCOME or FESTIVE.", "danger")
    return redirect(url_for("cart"))


@app.route("/remove-coupon")
def remove_coupon():
    session.pop("coupon", None)
    flash("Coupon removed.", "info")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    flags = get_all_flags()
    cart  = get_cart()
    total = cart_total(cart)

    # Flag-based discount
    flag_discount = round(total * float(flags["discount-percentage"]) / 100, 2) \
                    if flags["discount-banner-enabled"] else 0.0

    # Coupon discount
    coupon          = session.get("coupon", None)
    coupon_discount = round(total * coupon["discount"] / 100, 2) if coupon else 0.0

    # Best discount wins
    best_discount = max(flag_discount, coupon_discount)
    final_total   = round(total - best_discount, 2)

    if request.method == "POST":
        payment = request.form.get("payment_method", "card")

        # Block COD if flag is off
        if payment == "cod" and not flags["cash-on-delivery-enabled"]:
            flash("Cash on Delivery is currently unavailable.", "danger")
            return redirect(url_for("checkout"))

        # Save order
        conn = get_db()
        conn.execute(
            "INSERT INTO orders (items, total, payment) VALUES (?, ?, ?)",
            (json.dumps(dict(cart)), final_total, payment)
        )
        conn.commit()
        conn.close()

        # Clear cart and coupon
        session.pop("cart", None)
        session.pop("coupon", None)
        flash(f"Order placed! Payment: {payment.upper()}. Total Rs.{final_total:.2f}", "success")
        return redirect(url_for("order_success"))

    return render_template(
        "checkout.html",
        flags=flags,
        total=total,
        coupon=coupon,
        best_discount=best_discount,
        final_total=final_total,
        cart_count=sum(cart.values()),
    )


@app.route("/order-success")
def order_success():
    return render_template("order_success.html", flags=get_all_flags(), cart_count=0)


@app.route("/clear-cart")
def clear_cart():
    session.pop("cart", None)
    flash("Cart cleared.", "info")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username and password:          # any non-empty username + password works
            session["user"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("index"))
        flash("Please enter both username and password.", "danger")
    flags = {}
    try:
        flags = get_all_flags()
    except Exception:
        pass
    return render_template("login.html", flags=flags, cart_count=0)


@app.route("/logout")
def logout():
    username = session.get("user", "User")
    session.pop("user", None)
    flash(f"Goodbye, {username}! You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/admin/flags")
def admin_flags():
    return render_template("admin_flags.html", flags=get_all_flags(), cart_count=0)


@app.route("/admin/orders")
def admin_orders():
    conn   = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin_orders.html", orders=orders,
                           flags=get_all_flags(), cart_count=0)

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)