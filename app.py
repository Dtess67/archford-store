from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import database
from functools import wraps

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'archford-secret-key-2026'
database.init_db()

# ─── HOME ───────────────────────────────────────────
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

# ─── LOGIN ──────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = database.get_user(username, password)
        if user:
            session['user'] = user
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

# ─── LOGOUT ─────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── HOME PAGE ──────────────────────────────────────
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    featured = database.get_featured_products()
    categories = database.get_categories()
    return render_template('home.html', featured=featured, categories=categories)

# ─── SHOP ───────────────────────────────────────────
@app.route('/shop')
def shop():
    if 'user' not in session:
        return redirect(url_for('login'))
    category = request.args.get('category', 'ALL')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'default')
    products = database.get_products(category=category, search=search, sort=sort)
    categories = database.get_categories()
    print(categories)
    return render_template('shop.html', products=products, categories=categories,
                         active_category=category, search=search, sort=sort)

# ─── PRODUCT DETAIL ─────────────────────────────────
@app.route('/product/<item_id>')
def product(item_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    item = database.get_product(item_id)
    related = database.get_related_products(item['cat'], item_id)
    return render_template('product.html', product=item, related=related)

# ─── CART ───────────────────────────────────────────
@app.route('/cart')
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    cart_items = session.get('cart', [])
    total = sum(i['price'] * i['qty'] for i in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    item_id = request.form.get('item_id')
    qty = int(request.form.get('qty', 1))
    product = database.get_product(item_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    cart = session.get('cart', [])
    existing = next((i for i in cart if i['id'] == item_id), None)
    if existing:
        existing['qty'] += qty
    else:
        cart.append({
            'id': item_id,
            'name': product['name'],
            'price': product['price'],
            'pkg': product['pkg'],
            'img': product['img'],
            'qty': qty
        })
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart_count': sum(i['qty'] for i in cart)})

@app.route('/cart/remove/<item_id>')
def remove_from_cart(item_id):
    cart = session.get('cart', [])
    session['cart'] = [i for i in cart if i['id'] != item_id]
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart/update', methods=['POST'])
def update_cart():
    item_id = request.form.get('item_id')
    qty = int(request.form.get('qty', 1))
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == item_id:
            item['qty'] = qty
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))

# ─── CHECKOUT ───────────────────────────────────────
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect(url_for('login'))
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('shop'))
    if request.method == 'POST':
        order_data = {
            'school': request.form.get('school'),
            'contact': request.form.get('contact'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip': request.form.get('zip'),
            'po_number': request.form.get('po_number'),
            'payment': request.form.get('payment'),
            'ship_later': request.form.get('ship_later', 'N'),
            'notes': request.form.get('notes'),
            'items': cart_items,
            'user': session['user']
        }
        order_num = database.save_order(order_data)
        session['cart'] = []
        session['last_order'] = order_num
        session.modified = True
        return redirect(url_for('confirmation'))
    subtotal = sum(i['price'] * i['qty'] for i in cart_items)
    shipping = 0 if subtotal >= 50 else 7.50
    return render_template('checkout.html', cart=cart_items,
                         subtotal=subtotal, shipping=shipping,
                         total=subtotal + shipping, user=session['user'])

# ─── CONFIRMATION ───────────────────────────────────
@app.route('/confirmation')
def confirmation():
    if 'user' not in session:
        return redirect(url_for('login'))
    order_num = session.get('last_order')
    order = database.get_order(order_num) if order_num else None
    return render_template('confirmation.html', order=order)

# ─── ORDER HISTORY ──────────────────────────────────
@app.route('/orders')
def orders():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_orders = database.get_user_orders(session['user']['username'])
    return render_template('orders.html', orders=user_orders)

# ─── CONTACT ────────────────────────────────────────
@app.route('/contact')
def contact():
    settings = database.get_settings()
    return render_template('contact.html', settings=settings)

# ─── ADMIN ──────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'archford-admin-2026':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin.html', error='Invalid admin credentials')
    return render_template('admin.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = database.get_admin_stats()
    return render_template('admin.html', stats=stats)

@app.route('/admin/products')
@admin_required
def admin_products():
    products = database.get_all_products()
    return render_template('admin.html', products=products)

@app.route('/admin/products/edit/<item_id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(item_id):
    product = database.get_product(item_id)
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'pkg': request.form.get('pkg'),
            'cat': request.form.get('cat'),
            'active': int(request.form.get('active'))
        }
        database.update_product(item_id, data)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = database.get_categories()
    return render_template('admin.html', product=product, categories=categories)

@app.route('/admin/products/new', methods=['GET', 'POST'])
@admin_required
def admin_product_new():
    if request.method == 'POST':
        data = {
            'id': request.form.get('id'),
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'pkg': request.form.get('pkg'),
            'cat': request.form.get('cat'),
            'active': int(request.form.get('active'))
        }
        database.add_product(data)
        flash('New product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = database.get_categories()
    return render_template('admin.html', categories=categories)

@app.route('/admin/contact', methods=['GET', 'POST'])
@admin_required
def admin_contact():
    if request.method == 'POST':
        data = {
            'address': request.form.get('address'),
            'phone': request.form.get('phone'),
            'hours': request.form.get('hours')
        }
        database.update_settings(data)
        flash('Contact information updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    settings = database.get_settings()
    return render_template('admin.html', settings=settings)

# ─── RUN ────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)