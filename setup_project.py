#!/usr/bin/env python3
"""
Run this script ONCE from inside your E-commerce/ folder:
    python setup_project.py

It will create all missing folders and files automatically.
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"  Created: {path}")

print(f"\nBuilding project inside: {BASE}\n")

# ── flags/flags.yaml ──────────────────────────────────────────────────────────
write("flags/flags.yaml", """\
discount-banner-enabled:
  variations:
    enabled: true
    disabled: false
  defaultRule:
    variation: disabled

discount-percentage:
  variations:
    ten: "10"
    twenty: "20"
    thirty: "30"
  defaultRule:
    variation: ten

cash-on-delivery-enabled:
  variations:
    enabled: true
    disabled: false
  defaultRule:
    variation: disabled

promo-banner-enabled:
  variations:
    enabled: true
    disabled: false
  defaultRule:
    variation: disabled

promo-banner-text:
  variations:
    sale:    "🔥 Grand Sale! Up to 50% off on all products. Shop Now!"
    festive: "🎊 Festive Offers: Free Shipping on orders above Rs.999!"
    default: "Welcome to ShopSmart — India's favourite online store!"
  defaultRule:
    variation: default

new-checkout-layout:
  variations:
    new:     true
    classic: false
  defaultRule:
    variation: classic
""")

# ── goff-proxy.yaml ───────────────────────────────────────────────────────────
write("goff-proxy.yaml", f"""\
listen: 1031
retrievers:
  - kind: file
    path: {os.path.join(BASE, "flags", "flags.yaml")}
pollingInterval: 5000
""")

# ── templates/layout.html ─────────────────────────────────────────────────────
write("templates/layout.html", """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{% block title %}ShopSmart{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"/>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"/>
  <style>
    body { background:#f8f9fa; }
    .navbar-brand { font-weight:700; font-size:1.4rem; }
    .discount-banner { background:linear-gradient(90deg,#ff6b6b,#feca57); color:#fff; font-weight:700; padding:10px 0; text-align:center; }
    .promo-banner    { background:linear-gradient(90deg,#6c5ce7,#a29bfe); color:#fff; padding:8px 0; text-align:center; }
    .product-card    { border:none; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,.08); transition:transform .2s,box-shadow .2s; }
    .product-card:hover { transform:translateY(-4px); box-shadow:0 6px 20px rgba(0,0,0,.14); }
    .product-img     { height:140px; display:flex; align-items:center; justify-content:center; background:#eee; border-radius:12px 12px 0 0; font-size:3.5rem; }
    footer { background:#212529; color:#adb5bd; font-size:.85rem; }
  </style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container">
    <a class="navbar-brand" href="{{ url_for('index') }}"><i class="bi bi-shop"></i> ShopSmart</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navMenu">
      <ul class="navbar-nav ms-auto align-items-center gap-2">
        <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}"><i class="bi bi-house"></i> Home</a></li>
        <li class="nav-item">
          <a class="nav-link" href="{{ url_for('cart') }}">
            <i class="bi bi-cart3"></i> Cart
            {% if cart_count > 0 %}<span class="badge bg-danger">{{ cart_count }}</span>{% endif %}
          </a>
        </li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('admin_flags') }}"><i class="bi bi-toggles"></i> Flags</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('admin_orders') }}"><i class="bi bi-receipt"></i> Orders</a></li>
      </ul>
    </div>
  </div>
</nav>

{% if flags is defined and flags['promo-banner-enabled'] %}
<div class="promo-banner"><i class="bi bi-megaphone-fill me-2"></i>{{ flags['promo-banner-text'] }}</div>
{% endif %}

{% if flags is defined and flags['discount-banner-enabled'] %}
<div class="discount-banner">
  <i class="bi bi-tag-fill me-2"></i>
  FLAT {{ flags['discount-percentage'] }}% OFF on your order today! Code: <strong>SAVE{{ flags['discount-percentage'] }}</strong>
</div>
{% endif %}

<div class="container mt-2">
  {% for cat, msg in get_flashed_messages(with_categories=True) %}
  <div class="alert alert-{{ cat }} alert-dismissible fade show" role="alert">
    {{ msg }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>
  {% endfor %}
</div>

<main class="container my-4">{% block content %}{% endblock %}</main>

<footer class="py-3 mt-5">
  <div class="container text-center">
    <p class="mb-0">ShopSmart &mdash; Real-Time Feature Management Demo &mdash; SCM with Git + GO Feature Flag</p>
    <small><a href="{{ url_for('admin_flags') }}" class="text-secondary">View Live Flag Status</a></small>
  </div>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

# ── templates/index.html ──────────────────────────────────────────────────────
write("templates/index.html", """\
{% extends "layout.html" %}
{% block title %}Home{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div>
    <h2 class="fw-bold mb-0">Featured Products</h2>
    <small class="text-muted">{{ products|length }} items available</small>
  </div>
  <a href="{{ url_for('cart') }}" class="btn btn-outline-dark">
    <i class="bi bi-cart3"></i> View Cart ({{ cart_count }})
  </a>
</div>

<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
  {% for p in products %}
  <div class="col">
    <div class="card product-card h-100">
      <div class="product-img">
        {% if p['category'] == 'Electronics' %}🎧
        {% elif p['category'] == 'Footwear' %}👟
        {% elif p['category'] == 'Clothing' %}👕
        {% else %}🎒{% endif %}
      </div>
      <div class="card-body d-flex flex-column">
        <span class="badge bg-secondary mb-2" style="width:fit-content">{{ p['category'] }}</span>
        <h5 class="card-title">{{ p['name'] }}</h5>
        <div class="mb-2">
          <span class="fw-bold fs-5 text-success">Rs.{{ "%.2f"|format(p['price']) }}</span>
          {% if flags['discount-banner-enabled'] %}
          <span class="text-muted text-decoration-line-through ms-2 small">
            Rs.{{ "%.2f"|format(p['price'] * 1.2) }}
          </span>
          <span class="badge bg-danger ms-1">{{ flags['discount-percentage'] }}% OFF</span>
          {% endif %}
        </div>
        <a href="{{ url_for('add_to_cart', product_id=p['id']) }}" class="btn btn-primary mt-auto">
          <i class="bi bi-cart-plus"></i> Add to Cart
        </a>
      </div>
    </div>
  </div>
  {% endfor %}
</div>

<div class="card mt-5 border-0 bg-white shadow-sm">
  <div class="card-body">
    <h5 class="card-title"><i class="bi bi-info-circle text-primary"></i> Live Feature Flag Status</h5>
    <p class="text-muted small mb-3">Read in real-time from GO Feature Flag Relay Proxy (flags/flags.yaml tracked by Git).</p>
    <div class="d-flex flex-wrap gap-2">
      {% for key, val in flags.items() %}
      <span class="badge rounded-pill px-3 py-2
        {% if val == true %}bg-success
        {% elif val == false %}bg-secondary
        {% else %}bg-info text-dark{% endif %}">
        {{ key }}: <strong>{{ val }}</strong>
      </span>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
""")

# ── templates/cart.html ───────────────────────────────────────────────────────
write("templates/cart.html", """\
{% extends "layout.html" %}
{% block title %}Cart{% endblock %}
{% block content %}
<h2 class="fw-bold mb-4"><i class="bi bi-cart3"></i> Your Cart</h2>
{% if items %}
<div class="row">
  <div class="col-lg-8">
    <div class="card border-0 shadow-sm">
      <div class="card-body p-0">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-dark">
            <tr><th>Product</th><th class="text-center">Qty</th><th class="text-end">Subtotal</th></tr>
          </thead>
          <tbody>
            {% for item in items %}
            <tr>
              <td><strong>{{ item.name }}</strong><br><small class="text-muted">Rs.{{ "%.2f"|format(item.price) }} each</small></td>
              <td class="text-center"><span class="badge bg-primary rounded-pill px-3 py-2">{{ item.qty }}</span></td>
              <td class="text-end fw-bold">Rs.{{ "%.2f"|format(item.subtotal) }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
    <div class="mt-3">
      <a href="{{ url_for('index') }}" class="btn btn-outline-secondary"><i class="bi bi-arrow-left"></i> Continue Shopping</a>
      <a href="{{ url_for('clear_cart') }}" class="btn btn-outline-danger ms-2"><i class="bi bi-trash"></i> Clear Cart</a>
    </div>
  </div>
  <div class="col-lg-4 mt-4 mt-lg-0">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-dark text-white fw-bold"><i class="bi bi-receipt"></i> Order Summary</div>
      <div class="card-body">
        <div class="d-flex justify-content-between mb-2"><span>Subtotal</span><span>Rs.{{ "%.2f"|format(total) }}</span></div>
        {% if flags['discount-banner-enabled'] %}
        <div class="d-flex justify-content-between mb-2 text-success">
          <span><i class="bi bi-tag-fill"></i> Discount ({{ flags['discount-percentage'] }}%) <span class="badge bg-success ms-1">FLAG ON</span></span>
          <span>-Rs.{{ "%.2f"|format(discount) }}</span>
        </div>
        {% else %}
        <div class="d-flex justify-content-between mb-2 text-muted">
          <span>Discount</span><span class="badge bg-secondary">FLAG OFF</span>
        </div>
        {% endif %}
        <hr/>
        <div class="d-flex justify-content-between fw-bold fs-5">
          <span>Total</span><span class="text-success">Rs.{{ "%.2f"|format(total - discount) }}</span>
        </div>
        <a href="{{ url_for('checkout') }}" class="btn btn-success w-100 mt-3">
          <i class="bi bi-credit-card"></i> Proceed to Checkout
        </a>
      </div>
    </div>
  </div>
</div>
{% else %}
<div class="text-center py-5">
  <div style="font-size:5rem">🛒</div>
  <h4 class="mt-3 text-muted">Your cart is empty</h4>
  <a href="{{ url_for('index') }}" class="btn btn-primary mt-2"><i class="bi bi-shop"></i> Start Shopping</a>
</div>
{% endif %}
{% endblock %}
""")

# ── templates/checkout.html ───────────────────────────────────────────────────
write("templates/checkout.html", """\
{% extends "layout.html" %}
{% block title %}Checkout{% endblock %}
{% block content %}
<h2 class="fw-bold mb-4"><i class="bi bi-bag-check"></i> Checkout</h2>

{% if flags['new-checkout-layout'] %}
<div class="alert alert-info mb-4">
  <i class="bi bi-toggles2 me-2"></i>
  <strong>New Two-Column Layout Active</strong> — controlled by <code>new-checkout-layout</code> flag
</div>
<form action="{{ url_for('checkout') }}" method="POST">
  <div class="row g-4">
    <div class="col-md-7">
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-primary text-white fw-bold"><i class="bi bi-geo-alt"></i> Shipping Details</div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-6"><label class="form-label">First Name</label><input type="text" class="form-control" placeholder="Ravi" required/></div>
            <div class="col-6"><label class="form-label">Last Name</label><input type="text" class="form-control" placeholder="Kumar" required/></div>
            <div class="col-12"><label class="form-label">Email</label><input type="email" class="form-control" placeholder="ravi@example.com" required/></div>
            <div class="col-12"><label class="form-label">Address</label><input type="text" class="form-control" placeholder="123, MG Road" required/></div>
            <div class="col-6"><label class="form-label">City</label><input type="text" class="form-control" placeholder="Bangalore" required/></div>
            <div class="col-6"><label class="form-label">PIN Code</label><input type="text" class="form-control" placeholder="560001" required/></div>
          </div>
        </div>
      </div>
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-dark text-white fw-bold"><i class="bi bi-credit-card"></i> Payment Method</div>
        <div class="card-body">
          <div class="form-check mb-2"><input class="form-check-input" type="radio" name="payment_method" id="c1" value="card" checked/><label class="form-check-label" for="c1"><i class="bi bi-credit-card-2-front text-primary"></i> Credit / Debit Card</label></div>
          <div class="form-check mb-2"><input class="form-check-input" type="radio" name="payment_method" id="u1" value="upi"/><label class="form-check-label" for="u1"><i class="bi bi-phone text-success"></i> UPI</label></div>
          <div class="form-check mb-2"><input class="form-check-input" type="radio" name="payment_method" id="n1" value="netbanking"/><label class="form-check-label" for="n1"><i class="bi bi-bank text-warning"></i> Net Banking</label></div>
          {% if flags['cash-on-delivery-enabled'] %}
          <div class="form-check"><input class="form-check-input" type="radio" name="payment_method" id="cod1" value="cod"/><label class="form-check-label" for="cod1"><i class="bi bi-cash-coin text-danger"></i> Cash on Delivery <span class="badge bg-success ms-2">COD Available</span></label></div>
          {% else %}
          <div class="text-muted mt-2 small"><i class="bi bi-x-circle text-danger"></i> Cash on Delivery unavailable <span class="badge bg-secondary ms-1">FLAG OFF</span></div>
          {% endif %}
        </div>
      </div>
    </div>
    <div class="col-md-5">
      <div class="card border-0 shadow-sm sticky-top" style="top:80px">
        <div class="card-header bg-success text-white fw-bold"><i class="bi bi-receipt"></i> Order Total</div>
        <div class="card-body">
          <div class="d-flex justify-content-between mb-2"><span>Subtotal</span><span>Rs.{{ "%.2f"|format(total) }}</span></div>
          {% if flags['discount-banner-enabled'] %}<div class="d-flex justify-content-between mb-2 text-success"><span>Discount ({{ flags['discount-percentage'] }}%)</span><span>-Rs.{{ "%.2f"|format(discount) }}</span></div>{% endif %}
          <div class="d-flex justify-content-between mb-2"><span>Shipping</span><span class="text-success">FREE</span></div>
          <hr/>
          <div class="d-flex justify-content-between fw-bold fs-5"><span>Grand Total</span><span class="text-success">Rs.{{ "%.2f"|format(final_total) }}</span></div>
          <button type="submit" class="btn btn-success w-100 mt-3 py-2 fw-bold"><i class="bi bi-lock-fill me-1"></i> Place Order</button>
          <a href="{{ url_for('cart') }}" class="btn btn-outline-secondary w-100 mt-2"><i class="bi bi-arrow-left"></i> Back to Cart</a>
        </div>
      </div>
    </div>
  </div>
</form>

{% else %}
<div class="alert alert-secondary mb-4">
  <i class="bi bi-layout-text-sidebar me-2"></i>
  <strong>Classic Layout</strong> — Set <code>new-checkout-layout: variation: new</code> in flags.yaml to try the new layout.
</div>
<div class="row justify-content-center">
  <div class="col-lg-6">
    <form action="{{ url_for('checkout') }}" method="POST">
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-dark text-white fw-bold"><i class="bi bi-geo-alt"></i> Shipping Details</div>
        <div class="card-body">
          <div class="mb-3"><label class="form-label">Full Name</label><input type="text" class="form-control" placeholder="Ravi Kumar" required/></div>
          <div class="mb-3"><label class="form-label">Email</label><input type="email" class="form-control" placeholder="ravi@example.com" required/></div>
          <div class="mb-3"><label class="form-label">Address</label><textarea class="form-control" rows="2" placeholder="123, MG Road, Bangalore" required></textarea></div>
        </div>
      </div>
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-dark text-white fw-bold"><i class="bi bi-credit-card"></i> Payment Method</div>
        <div class="card-body">
          <div class="form-check mb-2"><input class="form-check-input" type="radio" name="payment_method" id="c2" value="card" checked/><label class="form-check-label" for="c2"><i class="bi bi-credit-card-2-front text-primary"></i> Credit / Debit Card</label></div>
          <div class="form-check mb-2"><input class="form-check-input" type="radio" name="payment_method" id="u2" value="upi"/><label class="form-check-label" for="u2"><i class="bi bi-phone text-success"></i> UPI</label></div>
          <div class="form-check mb-2"><input class="form-check-input" type="radio" name="payment_method" id="n2" value="netbanking"/><label class="form-check-label" for="n2"><i class="bi bi-bank text-warning"></i> Net Banking</label></div>
          {% if flags['cash-on-delivery-enabled'] %}
          <div class="form-check"><input class="form-check-input" type="radio" name="payment_method" id="cod2" value="cod"/><label class="form-check-label" for="cod2"><i class="bi bi-cash-coin text-danger"></i> Cash on Delivery <span class="badge bg-success ms-2">Available</span></label></div>
          {% else %}
          <div class="text-muted mt-2 small"><i class="bi bi-x-circle text-danger"></i> Cash on Delivery unavailable <span class="badge bg-secondary ms-1">FLAG OFF</span></div>
          {% endif %}
        </div>
      </div>
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-success text-white fw-bold"><i class="bi bi-receipt"></i> Order Total</div>
        <div class="card-body">
          <div class="d-flex justify-content-between mb-1"><span>Subtotal</span><span>Rs.{{ "%.2f"|format(total) }}</span></div>
          {% if flags['discount-banner-enabled'] %}<div class="d-flex justify-content-between mb-1 text-success"><span>Discount ({{ flags['discount-percentage'] }}%)</span><span>-Rs.{{ "%.2f"|format(discount) }}</span></div>{% endif %}
          <hr/><div class="d-flex justify-content-between fw-bold"><span>Grand Total</span><span class="text-success">Rs.{{ "%.2f"|format(final_total) }}</span></div>
        </div>
      </div>
      <button type="submit" class="btn btn-success w-100 fw-bold py-2"><i class="bi bi-lock-fill me-1"></i> Place Order</button>
      <a href="{{ url_for('cart') }}" class="btn btn-outline-secondary w-100 mt-2"><i class="bi bi-arrow-left"></i> Back to Cart</a>
    </form>
  </div>
</div>
{% endif %}
{% endblock %}
""")

# ── templates/order_success.html ──────────────────────────────────────────────
write("templates/order_success.html", """\
{% extends "layout.html" %}
{% block title %}Order Placed!{% endblock %}
{% block content %}
<div class="text-center py-5">
  <div style="font-size:5rem">🎉</div>
  <h2 class="fw-bold text-success mt-3">Order Placed Successfully!</h2>
  <p class="text-muted mt-2 fs-5">Thank you for shopping with ShopSmart.<br>Your order will be delivered within 3–5 business days.</p>
  <a href="{{ url_for('index') }}" class="btn btn-primary btn-lg mt-3"><i class="bi bi-shop"></i> Continue Shopping</a>
  <a href="{{ url_for('admin_orders') }}" class="btn btn-outline-secondary btn-lg mt-3 ms-2"><i class="bi bi-receipt"></i> View All Orders</a>
</div>
{% endblock %}
""")

# ── templates/admin_flags.html ────────────────────────────────────────────────
write("templates/admin_flags.html", """\
{% extends "layout.html" %}
{% block title %}Flag Dashboard{% endblock %}
{% block content %}
<h2 class="fw-bold mb-1"><i class="bi bi-toggles"></i> Feature Flag Dashboard</h2>
<p class="text-muted mb-4">Live values from GO Feature Flag Relay Proxy. Demonstrates <strong>SCM Configuration Status Accounting</strong>.</p>
<div class="row g-4">
  {% for key, val in flags.items() %}
  <div class="col-md-6 col-lg-4">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-body">
        <h6 class="card-title text-monospace fw-bold">{{ key }}</h6>
        <div class="mt-2 p-3 rounded text-center"
             style="background:{% if val == true %}#d1fae5{% elif val == false %}#f3f4f6{% else %}#dbeafe{% endif %}">
          <span class="fw-bold fs-4">
            {% if val == true %}<i class="bi bi-check-circle-fill text-success"></i> true
            {% elif val == false %}<i class="bi bi-x-circle-fill text-secondary"></i> false
            {% else %}<i class="bi bi-type text-primary"></i> "{{ val }}"{% endif %}
          </span>
        </div>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
<div class="card mt-5 border-0 shadow-sm bg-light">
  <div class="card-body">
    <h5><i class="bi bi-terminal"></i> SCM Git Commands</h5>
    <pre class="bg-dark text-success rounded p-3 small mb-0">
# View commit history of flags
git log --oneline flags/flags.yaml

# See what changed
git diff HEAD~1 HEAD -- flags/flags.yaml

# Full audit trail
git log --format="%H %ai %an: %s" -- flags/flags.yaml</pre>
  </div>
</div>
{% endblock %}
""")

# ── templates/admin_orders.html ───────────────────────────────────────────────
write("templates/admin_orders.html", """\
{% extends "layout.html" %}
{% block title %}Orders{% endblock %}
{% block content %}
<h2 class="fw-bold mb-1"><i class="bi bi-receipt"></i> Orders — Audit Log</h2>
<p class="text-muted mb-4">All placed orders. Demonstrates <strong>SCM Audit Capability</strong>.</p>
{% if orders %}
<div class="card border-0 shadow-sm">
  <div class="card-body p-0">
    <table class="table table-hover mb-0 align-middle">
      <thead class="table-dark">
        <tr><th>#</th><th>Placed At</th><th>Total</th><th>Payment</th><th>Items</th></tr>
      </thead>
      <tbody>
        {% for order in orders %}
        <tr>
          <td><span class="badge bg-secondary">{{ order['id'] }}</span></td>
          <td><small>{{ order['created_at'] }}</small></td>
          <td><strong class="text-success">Rs.{{ "%.2f"|format(order['total']) }}</strong></td>
          <td>
            {% if order['payment'] == 'cod' %}<span class="badge bg-warning text-dark">COD</span>
            {% elif order['payment'] == 'upi' %}<span class="badge bg-success">UPI</span>
            {% elif order['payment'] == 'card' %}<span class="badge bg-primary">Card</span>
            {% else %}<span class="badge bg-info text-dark">{{ order['payment'] }}</span>{% endif %}
          </td>
          <td><small class="text-muted">{{ order['items'] }}</small></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% else %}
<div class="text-center py-5">
  <div style="font-size:4rem">📋</div>
  <h5 class="mt-3 text-muted">No orders yet.</h5>
  <a href="{{ url_for('index') }}" class="btn btn-primary mt-2">Start Shopping</a>
</div>
{% endif %}
{% endblock %}
""")

print("\nAll done! Run:\n")
print("  python app.py\n")