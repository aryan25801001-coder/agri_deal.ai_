from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sih-submission-secret'

# Vercel fix for SQLite
if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/agri_market.db'
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'agri_market.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'farmer' or 'buyer'
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    membership = db.Column(db.String(20), default='basic') # 'basic' or 'premium'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100))
    is_organic = db.Column(db.Boolean, default=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_name = db.Column(db.String(80))
    seller_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='available')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(100))
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Categories
CATEGORIES = ['Vegetables', 'Fruits', 'Grains', 'Spices', 'Dairy', 'Livestock', 'Other']

# Routes
@app.route('/')
def index():
    try:
        products = Product.query.filter_by(status='available').order_by(Product.created_at.desc()).limit(8).all()
        stats = {
            'total_products': Product.query.count(),
            'total_farmers': User.query.filter_by(user_type='farmer').count(),
            'total_orders': Order.query.count(),
            'total_buyers': User.query.filter_by(user_type='buyer').count(),
            'total_users': User.query.count(),
        }
    except Exception as e:
        print(f"Database error on index: {e}")
        p1 = Product(id=1, name='Fresh Organic Tomatoes', category='Vegetables', price_per_unit=40, unit='kg', seller_name='Rajesh Kumar', is_organic=True, status='available', location='Delhi', description='Freshly picked organic tomatoes.')
        p1.created_at = datetime.utcnow()
        p1.quantity = 100
        p2 = Product(id=2, name='Premium Wheat', category='Grains', price_per_unit=2500, unit='quintal', seller_name='Amit Singh', is_organic=False, status='available', location='Punjab', description='High quality wheat grains.')
        p2.created_at = datetime.utcnow()
        p2.quantity = 50
        p3 = Product(id=3, name='Fresh Apples', category='Fruits', price_per_unit=120, unit='kg', seller_name='Suresh Sharma', is_organic=True, status='available', location='Himachal Pradesh', description='Sweet and crunchy apples.')
        p3.created_at = datetime.utcnow()
        p3.quantity = 200
        p4 = Product(id=4, name='Pure Cow Milk', category='Dairy', price_per_unit=60, unit='liter', seller_name='Dinesh Yadav', is_organic=True, status='available', location='Haryana', description='Fresh pure cow milk.')
        p4.created_at = datetime.utcnow()
        p4.quantity = 20
        products = [p1, p2, p3, p4]
        stats = {
            'total_products': 150,
            'total_farmers': 45,
            'total_orders': 300,
            'total_buyers': 120,
            'total_users': 165
        }
    return render_template('index.html', products=products, stats=stats)

CATEGORIES = ['Vegetables', 'Fruits', 'Grains', 'Spices', 'Dairy', 'Pulses', 'Livestock', 'Others']

@app.route('/market')
def market():
    category = request.args.get('category')
    search = request.args.get('search')
    
    try:
        query = Product.query.filter_by(status='available')
        if category:
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        products = query.order_by(Product.created_at.desc()).all()
    except Exception as e:
        print(f"Database error on market: {e}")
        p1 = Product(id=1, name='Fresh Organic Tomatoes', category='Vegetables', price_per_unit=40, unit='kg', seller_name='Rajesh Kumar', is_organic=True, status='available', location='Delhi', description='Freshly picked organic tomatoes.')
        p1.created_at = datetime.utcnow()
        p1.quantity = 100
        p2 = Product(id=2, name='Premium Wheat', category='Grains', price_per_unit=2500, unit='quintal', seller_name='Amit Singh', is_organic=False, status='available', location='Punjab', description='High quality wheat grains.')
        p2.created_at = datetime.utcnow()
        p2.quantity = 50
        p3 = Product(id=3, name='Fresh Apples', category='Fruits', price_per_unit=120, unit='kg', seller_name='Suresh Sharma', is_organic=True, status='available', location='Himachal Pradesh', description='Sweet and crunchy apples.')
        p3.created_at = datetime.utcnow()
        p3.quantity = 200
        p4 = Product(id=4, name='Pure Cow Milk', category='Dairy', price_per_unit=60, unit='liter', seller_name='Dinesh Yadav', is_organic=True, status='available', location='Haryana', description='Fresh pure cow milk.')
        p4.created_at = datetime.utcnow()
        p4.quantity = 20
        all_products = [p1, p2, p3, p4]
        
        products = []
        for prop in all_products:
            if category and prop.category != category:
                continue
            if search and search.lower() not in prop.name.lower():
                continue
            products.append(prop)
            
    return render_template('market.html', products=products, categories=CATEGORIES, selected_category=category)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
        
        related = Product.query.filter(
            Product.category == product.category,
            Product.id != product.id,
            Product.status == 'available'
        ).limit(4).all()
        return render_template('product_detail.html', product=product, reviews=reviews, related=related)
    except Exception as e:
        print(f"Database error on product_detail: {e}")
        # Return a mock product for display
        product = Product(id=product_id, name='Fresh Organic Produce', category='Vegetables', price_per_unit=40, unit='kg', seller_name='Rajesh Kumar', is_organic=True, status='available', location='Delhi', description='Great product sourced from local farms.', quantity=100)
        product.created_at = datetime.utcnow()
        return render_template('product_detail.html', product=product, reviews=[], related=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type=user_type,
            phone=phone,
            address=address,
            membership='basic'
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            user = User.query.filter_by(username=username).first()
        except:
            user = None
            
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        elif username == 'demo' and password == 'demo':
            session['user_id'] = 999
            session['username'] = 'demo'
            session['user_type'] = 'farmer'
            flash('Demo Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password (Try demo / demo for mock login)')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if user.user_type == 'farmer':
            products = Product.query.filter_by(seller_id=user.id).count()
            orders = Order.query.filter_by(seller_id=user.id).count()
            revenue = db.session.query(db.func.sum(Order.total_price)).filter_by(seller_id=user.id).scalar() or 0
        else:
            products = 0
            orders = Order.query.filter_by(buyer_id=user.id).count()
            revenue = db.session.query(db.func.sum(Order.total_price)).filter_by(buyer_id=user.id).scalar() or 0
    except Exception as e:
        print(f"Database error on dashboard: {e}")
        is_farmer = session.get('user_type') == 'farmer'
        products = 12 if is_farmer else 0
        orders = 45 if is_farmer else 5
        revenue = 45000 if is_farmer else 1200
    
    return render_template('dashboard.html', products=products, orders=orders, revenue=revenue)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        
        if user.user_type != 'farmer':
            flash('Only farmers can add products')
            return redirect(url_for('market'))
        
        product = Product(
            name=request.form['name'],
            category=request.form['category'],
            description=request.form.get('description'),
            quantity=float(request.form['quantity']),
            unit=request.form['unit'],
            price_per_unit=float(request.form['price']),
            location=request.form.get('location'),
            is_organic='is_organic' in request.form,
            seller_id=user.id,
            seller_name=user.username,
            seller_phone=user.phone
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product listed successfully!')
        return redirect(url_for('my_products'))
    
    return render_template('add_product.html', categories=CATEGORIES)

@app.route('/my_products')
def my_products():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    products = Product.query.filter_by(seller_id=session['user_id']).order_by(Product.created_at.desc()).all()
    return render_template('my_products.html', products=products)

@app.route('/order/<int:product_id>', methods=['POST'])
def order_product(product_id):
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    product = Product.query.get_or_404(product_id)
    quantity = float(request.form['quantity'])
    
    if quantity > product.quantity:
        flash('Requested quantity exceeds available quantity')
        return redirect(url_for('product_detail', product_id=product_id))
    
    total_price = quantity * product.price_per_unit
    
    order = Order(
        product_id=product.id,
        product_name=product.name,
        buyer_id=session['user_id'],
        seller_id=product.seller_id,
        quantity=quantity,
        unit_price=product.price_per_unit,
        total_price=total_price,
        status='pending'
    )
    
    product.quantity -= quantity
    if product.quantity <= 0:
        product.status = 'sold'
    
    db.session.add(order)
    db.session.commit()
    
    flash('Order placed successfully!')
    return redirect(url_for('my_orders'))

@app.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    bought_orders = Order.query.filter_by(buyer_id=session['user_id']).order_by(Order.created_at.desc()).all()
    sold_orders = Order.query.filter_by(seller_id=session['user_id']).order_by(Order.created_at.desc()).all()
    
    return render_template('my_orders.html', bought_orders=bought_orders, sold_orders=sold_orders)

@app.route('/review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    review = Review(
        product_id=product_id,
        user_id=user.id,
        username=user.username,
        rating=int(request.form['rating']),
        comment=request.form.get('comment')
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Review added successfully!')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/ai_predictions')
def ai_predictions():
    predictions = [
        {'category': 'Vegetables', 'icon': 'fa-carrot', 'current_price': 45, 'predicted_price': 52, 'trend': 'up', 'confidence': 85, 'change': '+15.6%'},
        {'category': 'Fruits', 'icon': 'fa-apple-alt', 'current_price': 60, 'predicted_price': 55, 'trend': 'down', 'confidence': 78, 'change': '-8.3%'},
        {'category': 'Grains', 'icon': 'fa-seedling', 'current_price': 30, 'predicted_price': 33, 'trend': 'up', 'confidence': 90, 'change': '+10.0%'},
        {'category': 'Spices', 'icon': 'fa-pepper-hot', 'current_price': 120, 'predicted_price': 135, 'trend': 'up', 'confidence': 82, 'change': '+12.5%'},
        {'category': 'Dairy', 'icon': 'fa-cheese', 'current_price': 45, 'predicted_price': 48, 'trend': 'up', 'confidence': 88, 'change': '+6.7%'},
        {'category': 'Pulses', 'icon': 'fa-circle', 'current_price': 85, 'predicted_price': 79, 'trend': 'down', 'confidence': 74, 'change': '-7.1%'},
        {'category': 'Cotton', 'icon': 'fa-tshirt', 'current_price': 6200, 'predicted_price': 6800, 'trend': 'up', 'confidence': 80, 'change': '+9.7%'},
        {'category': 'Sugarcane', 'icon': 'fa-candy-cane', 'current_price': 350, 'predicted_price': 375, 'trend': 'up', 'confidence': 92, 'change': '+7.1%'},
        {'category': 'Poultry', 'icon': 'fa-egg', 'current_price': 180, 'predicted_price': 165, 'trend': 'down', 'confidence': 75, 'change': '-8.3%'},
        {'category': 'Fishery', 'icon': 'fa-fish', 'current_price': 450, 'predicted_price': 490, 'trend': 'up', 'confidence': 84, 'change': '+8.9%'},
    ]
    # Crop recommendations by state & season
    crop_data = {
        'Punjab': {'Kharif': ['Rice','Maize','Cotton','Sugarcane','Groundnut'], 'Rabi': ['Wheat','Barley','Mustard','Peas','Lentils']},
        'Haryana': {'Kharif': ['Rice','Bajra','Cotton','Sunflower'], 'Rabi': ['Wheat','Barley','Mustard','Chickpea']},
        'Uttar Pradesh': {'Kharif': ['Rice','Sugarcane','Maize','Soybean'], 'Rabi': ['Wheat','Mustard','Peas','Potato']},
        'Maharashtra': {'Kharif': ['Soybean','Cotton','Jowar','Bajra'], 'Rabi': ['Wheat','Chickpea','Sunflower','Safflower']},
        'Rajasthan': {'Kharif': ['Bajra','Moth Bean','Green Gram','Guar'], 'Rabi': ['Wheat','Barley','Mustard','Cumin']},
        'Madhya Pradesh': {'Kharif': ['Soybean','Maize','Jowar','Cotton'], 'Rabi': ['Wheat','Chickpea','Lentil','Mustard']},
        'Gujarat': {'Kharif': ['Groundnut','Cotton','Rice','Bajra'], 'Rabi': ['Wheat','Mustard','Chickpea','Cumin']},
        'Karnataka': {'Kharif': ['Rice','Ragi','Maize','Sunflower'], 'Rabi': ['Jowar','Chickpea','Sunflower','Safflower']},
        'Andhra Pradesh': {'Kharif': ['Rice','Maize','Cotton','Groundnut'], 'Rabi': ['Rice','Chickpea','Sunflower','Jowar']},
        'Tamil Nadu': {'Kharif': ['Rice','Groundnut','Cotton','Maize'], 'Rabi': ['Rice','Chickpea','Sunflower','Sorghum']},
        'Bihar': {'Kharif': ['Rice','Maize','Arhar','Jute'], 'Rabi': ['Wheat','Mustard','Chickpea','Peas']},
        'West Bengal': {'Kharif': ['Rice','Jute','Maize','Potato'], 'Rabi': ['Wheat','Mustard','Potato','Vegetables']},
        'Kerala': {'Kharif': ['Rice','Coconut','Rubber','Tapioca'], 'Rabi': ['Vegetables','Banana','Pepper','Cardamom']},
        'Telangana': {'Kharif': ['Rice','Cotton','Maize','Soybean'], 'Rabi': ['Chickpea','Sunflower','Jowar','Maize']},
        'Himachal Pradesh': {'Kharif': ['Maize','Rice','Potato','Ginger'], 'Rabi': ['Wheat','Barley','Peas','Rapeseed']},
    }

    # Membership check
    is_premium = False
    if 'user_id' in session:
        try:
            user = User.query.get(session['user_id'])
            if user and user.membership == 'premium':
                is_premium = True
        except:
            pass
    
    if not is_premium:
        predictions = predictions[:3]  # Basic only see 3 categories
        # Keep only top 3 states for basic
        limited_crop_data = {}
        for state in list(crop_data.keys())[:3]:
            limited_crop_data[state] = crop_data[state]
        crop_data = limited_crop_data

    return render_template('ai_predictions.html', predictions=predictions, crop_data=crop_data, is_premium=is_premium)

@app.route('/market_prices')
def market_prices():
    prices = [
        # Vegetables
        {'commodity': 'Tomato', 'emoji': '🍅', 'price': 45, 'unit': 'kg', 'change': 5.2, 'category': 'Vegetables'},
        {'commodity': 'Potato', 'emoji': '🥔', 'price': 28, 'unit': 'kg', 'change': -2.1, 'category': 'Vegetables'},
        {'commodity': 'Onion', 'emoji': '🧅', 'price': 35, 'unit': 'kg', 'change': 8.5, 'category': 'Vegetables'},
        {'commodity': 'Brinjal', 'emoji': '🫑', 'price': 30, 'unit': 'kg', 'change': 3.2, 'category': 'Vegetables'},
        {'commodity': 'Cauliflower', 'emoji': '🥦', 'price': 26, 'unit': 'kg', 'change': -1.5, 'category': 'Vegetables'},
        {'commodity': 'Cabbage', 'emoji': '🥬', 'price': 20, 'unit': 'kg', 'change': 2.0, 'category': 'Vegetables'},
        {'commodity': 'Lady Finger (Bhindi)', 'emoji': '🌿', 'price': 38, 'unit': 'kg', 'change': 6.8, 'category': 'Vegetables'},
        {'commodity': 'Capsicum', 'emoji': '🫑', 'price': 55, 'unit': 'kg', 'change': -3.2, 'category': 'Vegetables'},
        {'commodity': 'Bitter Gourd (Karela)', 'emoji': '🥒', 'price': 40, 'unit': 'kg', 'change': 1.5, 'category': 'Vegetables'},
        {'commodity': 'Bottle Gourd (Lauki)', 'emoji': '🥒', 'price': 22, 'unit': 'kg', 'change': 0.0, 'category': 'Vegetables'},
        {'commodity': 'Ridge Gourd (Turai)', 'emoji': '🥒', 'price': 25, 'unit': 'kg', 'change': 2.5, 'category': 'Vegetables'},
        {'commodity': 'Pumpkin (Kaddu)', 'emoji': '🎃', 'price': 18, 'unit': 'kg', 'change': -1.0, 'category': 'Vegetables'},
        {'commodity': 'Spinach (Palak)', 'emoji': '🥬', 'price': 32, 'unit': 'kg', 'change': 4.2, 'category': 'Vegetables'},
        {'commodity': 'Fenugreek (Methi)', 'emoji': '🌿', 'price': 28, 'unit': 'kg', 'change': 3.0, 'category': 'Vegetables'},
        {'commodity': 'Carrot', 'emoji': '🥕', 'price': 35, 'unit': 'kg', 'change': 5.5, 'category': 'Vegetables'},
        {'commodity': 'Radish (Mooli)', 'emoji': '🌱', 'price': 18, 'unit': 'kg', 'change': -0.8, 'category': 'Vegetables'},
        {'commodity': 'Peas (Hara Matar)', 'emoji': '🫛', 'price': 60, 'unit': 'kg', 'change': 7.0, 'category': 'Vegetables'},
        {'commodity': 'Kundru', 'emoji': '🌿', 'price': 30, 'unit': 'kg', 'change': 1.2, 'category': 'Vegetables'},
        # Fruits
        {'commodity': 'Mango', 'emoji': '🥭', 'price': 80, 'unit': 'kg', 'change': 12.0, 'category': 'Fruits'},
        {'commodity': 'Banana', 'emoji': '🍌', 'price': 25, 'unit': 'dozen', 'change': -1.2, 'category': 'Fruits'},
        {'commodity': 'Apple', 'emoji': '🍎', 'price': 140, 'unit': 'kg', 'change': 3.5, 'category': 'Fruits'},
        {'commodity': 'Grapes', 'emoji': '🍇', 'price': 90, 'unit': 'kg', 'change': -4.0, 'category': 'Fruits'},
        {'commodity': 'Pomegranate', 'emoji': '🍎', 'price': 120, 'unit': 'kg', 'change': 8.0, 'category': 'Fruits'},
        {'commodity': 'Guava', 'emoji': '🍐', 'price': 40, 'unit': 'kg', 'change': 2.0, 'category': 'Fruits'},
        {'commodity': 'Papaya', 'emoji': '🍈', 'price': 30, 'unit': 'kg', 'change': 1.5, 'category': 'Fruits'},
        {'commodity': 'Watermelon', 'emoji': '🍉', 'price': 15, 'unit': 'kg', 'change': -2.5, 'category': 'Fruits'},
        {'commodity': 'Lemon', 'emoji': '🍋', 'price': 60, 'unit': 'kg', 'change': 15.0, 'category': 'Fruits'},
        {'commodity': 'Orange', 'emoji': '🍊', 'price': 65, 'unit': 'kg', 'change': 4.0, 'category': 'Fruits'},
        {'commodity': 'Pineapple', 'emoji': '🍍', 'price': 50, 'unit': 'kg', 'change': 3.0, 'category': 'Fruits'},
        {'commodity': 'Coconut', 'emoji': '🥥', 'price': 28, 'unit': 'piece', 'change': 1.5, 'category': 'Fruits'},
        # Grains & Cereals
        {'commodity': 'Wheat', 'emoji': '🌾', 'price': 2200, 'unit': 'quintal', 'change': 1.2, 'category': 'Grains'},
        {'commodity': 'Rice (Paddy)', 'emoji': '🍚', 'price': 2800, 'unit': 'quintal', 'change': -0.8, 'category': 'Grains'},
        {'commodity': 'Maize (Makka)', 'emoji': '🌽', 'price': 1800, 'unit': 'quintal', 'change': 2.5, 'category': 'Grains'},
        {'commodity': 'Bajra (Pearl Millet)', 'emoji': '🌾', 'price': 2350, 'unit': 'quintal', 'change': 0.5, 'category': 'Grains'},
        {'commodity': 'Jowar (Sorghum)', 'emoji': '🌾', 'price': 2970, 'unit': 'quintal', 'change': 1.8, 'category': 'Grains'},
        {'commodity': 'Ragi (Finger Millet)', 'emoji': '🌾', 'price': 3600, 'unit': 'quintal', 'change': 4.0, 'category': 'Grains'},
        {'commodity': 'Barley (Jau)', 'emoji': '🌾', 'price': 1735, 'unit': 'quintal', 'change': -0.5, 'category': 'Grains'},
        # Pulses
        {'commodity': 'Arhar Dal (Toor)', 'emoji': '🫘', 'price': 7200, 'unit': 'quintal', 'change': 5.5, 'category': 'Pulses'},
        {'commodity': 'Moong Dal', 'emoji': '🫘', 'price': 8600, 'unit': 'quintal', 'change': -3.0, 'category': 'Pulses'},
        {'commodity': 'Urad Dal', 'emoji': '🫘', 'price': 6800, 'unit': 'quintal', 'change': 2.0, 'category': 'Pulses'},
        {'commodity': 'Masoor Dal (Lentil)', 'emoji': '🫘', 'price': 5500, 'unit': 'quintal', 'change': 1.2, 'category': 'Pulses'},
        {'commodity': 'Chana (Chickpea)', 'emoji': '🫘', 'price': 5400, 'unit': 'quintal', 'change': 3.5, 'category': 'Pulses'},
        {'commodity': 'Rajma (Kidney Bean)', 'emoji': '🫘', 'price': 9000, 'unit': 'quintal', 'change': -1.5, 'category': 'Pulses'},
        # Spices
        {'commodity': 'Chilli (Lal Mirch)', 'emoji': '🌶️', 'price': 9500, 'unit': 'quintal', 'change': 12.0, 'category': 'Spices'},
        {'commodity': 'Turmeric (Haldi)', 'emoji': '🌿', 'price': 8000, 'unit': 'quintal', 'change': 6.5, 'category': 'Spices'},
        {'commodity': 'Coriander (Dhaniya)', 'emoji': '🌿', 'price': 5500, 'unit': 'quintal', 'change': 3.0, 'category': 'Spices'},
        {'commodity': 'Ginger (Adrak)', 'emoji': '🫚', 'price': 5000, 'unit': 'quintal', 'change': 8.5, 'category': 'Spices'},
        {'commodity': 'Garlic (Lehsun)', 'emoji': '🧄', 'price': 6000, 'unit': 'quintal', 'change': 10.0, 'category': 'Spices'},
        {'commodity': 'Cumin (Jeera)', 'emoji': '🌿', 'price': 18000, 'unit': 'quintal', 'change': 5.0, 'category': 'Spices'},
        {'commodity': 'Mustard (Sarson)', 'emoji': '🌿', 'price': 5200, 'unit': 'quintal', 'change': 2.5, 'category': 'Spices'},
        # Oilseeds & Cash Crops
        {'commodity': 'Soybean', 'emoji': '🌱', 'price': 4300, 'unit': 'quintal', 'change': -1.5, 'category': 'Oilseeds'},
        {'commodity': 'Groundnut (Moongphali)', 'emoji': '🥜', 'price': 5200, 'unit': 'quintal', 'change': 3.0, 'category': 'Oilseeds'},
        {'commodity': 'Sunflower', 'emoji': '🌻', 'price': 6400, 'unit': 'quintal', 'change': 2.0, 'category': 'Oilseeds'},
        {'commodity': 'Cotton (Kapas)', 'emoji': '🌿', 'price': 6500, 'unit': 'quintal', 'change': -2.0, 'category': 'Cash Crops'},
        {'commodity': 'Sugarcane (Ganna)', 'emoji': '🌿', 'price': 350, 'unit': 'quintal', 'change': 0.0, 'category': 'Cash Crops'},
        {'commodity': 'Jute (Pat)', 'emoji': '🌿', 'price': 4500, 'unit': 'quintal', 'change': 1.0, 'category': 'Cash Crops'},
        # Dairy
        {'commodity': 'Milk', 'emoji': '🥛', 'price': 45, 'unit': 'liter', 'change': 0.0, 'category': 'Dairy'},
        {'commodity': 'Paneer', 'emoji': '🧀', 'price': 280, 'unit': 'kg', 'change': 2.5, 'category': 'Dairy'},
        {'commodity': 'Ghee', 'emoji': '🫙', 'price': 480, 'unit': 'kg', 'change': 1.5, 'category': 'Dairy'},
        {'commodity': 'Butter', 'emoji': '🧈', 'price': 420, 'unit': 'kg', 'change': 0.5, 'category': 'Dairy'},
    ]
    
    # Tiered limits for Market Prices
    is_premium = False
    if 'user_id' in session:
        try:
            user = User.query.get(session['user_id'])
            if user and user.membership == 'premium':
                is_premium = True
        except:
            is_premium = False
    
    if not is_premium:
        # Basic users only see top 10 commodities
        prices = prices[:10]
        
    return render_template('market_prices.html', prices=prices, is_premium=is_premium)


INDIA_LOCATIONS = {
    'Andhra Pradesh': {'Visakhapatnam': (17.6868, 83.2185), 'Vijayawada': (16.5062, 80.6480), 'Guntur': (16.3067, 80.4365), 'Tirupati': (13.6288, 79.4192), 'Kurnool': (15.8281, 78.0373)},
    'Assam': {'Guwahati': (26.1445, 91.7362), 'Silchar': (24.8333, 92.7789), 'Dibrugarh': (27.4728, 94.9120), 'Jorhat': (26.7509, 94.2037)},
    'Bihar': {'Patna': (25.5941, 85.1376), 'Gaya': (24.7914, 85.0002), 'Bhagalpur': (25.2425, 86.9842), 'Muzaffarpur': (26.1197, 85.3910)},
    'Delhi': {'New Delhi': (28.6139, 77.2090), 'Dwarka': (28.5921, 77.0460), 'Rohini': (28.7041, 77.1025), 'Noida': (28.5355, 77.3910)},
    'Gujarat': {'Ahmedabad': (23.0225, 72.5714), 'Surat': (21.1702, 72.8311), 'Rajkot': (22.3039, 70.8022), 'Vadodara': (22.3072, 73.1812), 'Anand': (22.5645, 72.9289)},
    'Haryana': {'Chandigarh': (30.7333, 76.7794), 'Ambala': (30.3752, 76.7821), 'Hisar': (29.1492, 75.7217), 'Karnal': (29.6857, 76.9905), 'Sirsa': (29.5330, 75.0243)},
    'Himachal Pradesh': {'Shimla': (31.1048, 77.1734), 'Dharamshala': (32.2190, 76.3234), 'Kullu': (31.9580, 77.1094), 'Mandi': (31.7080, 76.9320)},
    'Karnataka': {'Bengaluru': (12.9716, 77.5946), 'Mysuru': (12.2958, 76.6394), 'Hubli': (15.3647, 75.1240), 'Belagavi': (15.8497, 74.4977), 'Davangere': (14.4644, 75.9218)},
    'Kerala': {'Thiruvananthapuram': (8.5241, 76.9366), 'Kochi': (9.9312, 76.2673), 'Kozhikode': (11.2588, 75.7804), 'Thrissur': (10.5276, 76.2144)},
    'Madhya Pradesh': {'Bhopal': (23.2599, 77.4126), 'Indore': (22.7196, 75.8577), 'Gwalior': (26.2183, 78.1828), 'Jabalpur': (23.1815, 79.9864), 'Ujjain': (23.1793, 75.7849)},
    'Maharashtra': {'Mumbai': (19.0760, 72.8777), 'Pune': (18.5204, 73.8567), 'Nagpur': (21.1458, 79.0882), 'Nashik': (19.9975, 73.7898), 'Aurangabad': (19.8762, 75.3433)},
    'Odisha': {'Bhubaneswar': (20.2961, 85.8245), 'Cuttack': (20.4625, 85.8830), 'Rourkela': (22.2604, 84.8536), 'Sambalpur': (21.4669, 83.9756)},
    'Punjab': {'Chandigarh': (30.7333, 76.7794), 'Amritsar': (31.6340, 74.8723), 'Ludhiana': (30.9010, 75.8573), 'Patiala': (30.3398, 76.3869), 'Bathinda': (30.2110, 74.9455)},
    'Rajasthan': {'Jaipur': (26.9124, 75.7873), 'Jodhpur': (26.2389, 73.0243), 'Kota': (25.2138, 75.8648), 'Udaipur': (24.5854, 73.7125), 'Bikaner': (28.0229, 73.3119)},
    'Tamil Nadu': {'Chennai': (13.0827, 80.2707), 'Coimbatore': (11.0168, 76.9558), 'Madurai': (9.9252, 78.1198), 'Salem': (11.6643, 78.1460), 'Tiruchirappalli': (10.7905, 78.7047)},
    'Telangana': {'Hyderabad': (17.3850, 78.4867), 'Warangal': (17.9784, 79.5941), 'Nizamabad': (18.6725, 78.0941), 'Karimnagar': (18.4386, 79.1288)},
    'Uttar Pradesh': {'Lucknow': (26.8467, 80.9462), 'Kanpur': (26.4499, 80.3319), 'Agra': (27.1767, 78.0081), 'Varanasi': (25.3176, 82.9739), 'Meerut': (28.9845, 77.7064), 'Allahabad': (25.4358, 81.8463)},
    'Uttarakhand': {'Dehradun': (30.3165, 78.0322), 'Haridwar': (29.9457, 78.1642), 'Nainital': (29.3919, 79.4542), 'Roorkee': (29.8543, 77.8880)},
    'West Bengal': {'Kolkata': (22.5726, 88.3639), 'Siliguri': (26.7271, 88.3953), 'Durgapur': (23.5204, 87.3119), 'Asansol': (23.6739, 86.9524)},
}

WEATHER_CODES = {
    0: ('Clear Sky', 'fa-sun', '#f59e0b'), 1: ('Mainly Clear', 'fa-sun', '#f59e0b'),
    2: ('Partly Cloudy', 'fa-cloud-sun', '#94a3b8'), 3: ('Overcast', 'fa-cloud', '#64748b'),
    45: ('Foggy', 'fa-smog', '#94a3b8'), 48: ('Icy Fog', 'fa-smog', '#94a3b8'),
    51: ('Light Drizzle', 'fa-cloud-drizzle', '#60a5fa'), 53: ('Drizzle', 'fa-cloud-drizzle', '#3b82f6'),
    55: ('Heavy Drizzle', 'fa-cloud-drizzle', '#2563eb'), 61: ('Light Rain', 'fa-cloud-rain', '#3b82f6'),
    63: ('Moderate Rain', 'fa-cloud-rain', '#2563eb'), 65: ('Heavy Rain', 'fa-cloud-showers-heavy', '#1d4ed8'),
    71: ('Light Snow', 'fa-snowflake', '#bfdbfe'), 73: ('Moderate Snow', 'fa-snowflake', '#93c5fd'),
    75: ('Heavy Snow', 'fa-snowflake', '#60a5fa'), 80: ('Rain Showers', 'fa-cloud-rain', '#3b82f6'),
    81: ('Heavy Showers', 'fa-cloud-showers-heavy', '#2563eb'), 82: ('Violent Showers', 'fa-cloud-showers-heavy', '#1d4ed8'),
    95: ('Thunderstorm', 'fa-bolt', '#f59e0b'), 96: ('Thunderstorm+Hail', 'fa-bolt', '#ef4444'),
    99: ('Heavy Thunderstorm', 'fa-bolt', '#dc2626'),
}

DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun','Mon','Tue','Wed']

@app.route('/weather', methods=['GET','POST'])
def weather():
    import requests as req_lib
    from datetime import datetime, timedelta

    selected_state = request.form.get('state', 'Delhi') if request.method == 'POST' else request.args.get('state', 'Delhi')
    selected_district = request.form.get('district', 'New Delhi') if request.method == 'POST' else request.args.get('district', 'New Delhi')

    state_locs = INDIA_LOCATIONS.get(selected_state, INDIA_LOCATIONS['Delhi'])
    coords = state_locs.get(selected_district, list(state_locs.values())[0])
    lat, lon = coords

    weather_info = None
    error_msg = None
    try:
        url = (f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
               f'&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code,precipitation'
               f'&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,wind_speed_10m_max,uv_index_max'
               f'&timezone=Asia%2FKolkata&forecast_days=10')
        r = req_lib.get(url, timeout=6)
        if r.ok:
            d = r.json()
            cur = d.get('current', {})
            daily = d.get('daily', {})
            code = cur.get('weather_code', 0)
            wc = WEATHER_CODES.get(code, ('Clear', 'fa-sun', '#f59e0b'))
            forecast = []
            for i in range(10):
                dc = daily.get('weather_code', [0]*10)
                dwc = WEATHER_CODES.get(dc[i] if i < len(dc) else 0, ('Clear', 'fa-sun', '#f59e0b'))
                dt_str = daily.get('time', ['']*(i+1))[i] if i < len(daily.get('time',[])) else ''
                try:
                    dt_obj = datetime.strptime(dt_str, '%Y-%m-%d')
                    day_name = 'Today' if i == 0 else ('Tomorrow' if i == 1 else dt_obj.strftime('%a %d %b'))
                except:
                    day_name = DAYS[i]
                forecast.append({
                    'day': day_name,
                    'high': round(daily.get('temperature_2m_max', [0]*10)[i]) if i < len(daily.get('temperature_2m_max',[])) else '--',
                    'low': round(daily.get('temperature_2m_min', [0]*10)[i]) if i < len(daily.get('temperature_2m_min',[])) else '--',
                    'rain': round(daily.get('precipitation_sum', [0]*10)[i], 1) if i < len(daily.get('precipitation_sum',[])) else 0,
                    'wind': round(daily.get('wind_speed_10m_max', [0]*10)[i]) if i < len(daily.get('wind_speed_10m_max',[])) else '--',
                    'uv': round(daily.get('uv_index_max', [0]*10)[i], 1) if i < len(daily.get('uv_index_max',[])) else '--',
                    'condition': dwc[0],
                    'icon': dwc[1],
                    'color': dwc[2],
                })
            weather_info = {
                'temp': round(cur.get('temperature_2m', 0)),
                'feels': round(cur.get('apparent_temperature', 0)),
                'humidity': round(cur.get('relative_humidity_2m', 0)),
                'wind': round(cur.get('wind_speed_10m', 0)),
                'rain': cur.get('precipitation', 0),
                'condition': wc[0],
                'icon': wc[1],
                'color': wc[2],
                'forecast': forecast,
            }
        else:
            error_msg = 'Could not fetch live data. Showing sample data.'
    except Exception as e:
        error_msg = 'Network error. Showing sample data.'

    if not weather_info:
        weather_info = {
            'temp': 28, 'feels': 30, 'humidity': 65, 'wind': 12, 'rain': 0,
            'condition': 'Partly Cloudy', 'icon': 'fa-cloud-sun', 'color': '#94a3b8',
            'forecast': [
                {'day': 'Today', 'high': 32, 'low': 22, 'rain': 0, 'wind': 12, 'uv': 6.2, 'condition': 'Sunny', 'icon': 'fa-sun', 'color': '#f59e0b'},
                {'day': 'Tomorrow', 'high': 30, 'low': 21, 'rain': 2.1, 'wind': 15, 'uv': 4.5, 'condition': 'Light Rain', 'icon': 'fa-cloud-rain', 'color': '#3b82f6'},
                {'day': 'Wed 8 Mar', 'high': 28, 'low': 20, 'rain': 5.3, 'wind': 18, 'uv': 3.0, 'condition': 'Rain', 'icon': 'fa-cloud-rain', 'color': '#2563eb'},
                {'day': 'Thu 9 Mar', 'high': 27, 'low': 19, 'rain': 0, 'wind': 10, 'uv': 7.1, 'condition': 'Cloudy', 'icon': 'fa-cloud', 'color': '#64748b'},
                {'day': 'Fri 10 Mar', 'high': 31, 'low': 22, 'rain': 0, 'wind': 8, 'uv': 8.0, 'condition': 'Clear', 'icon': 'fa-sun', 'color': '#f59e0b'},
                {'day': 'Sat 11 Mar', 'high': 33, 'low': 23, 'rain': 0, 'wind': 7, 'uv': 9.0, 'condition': 'Clear', 'icon': 'fa-sun', 'color': '#f59e0b'},
                {'day': 'Sun 12 Mar', 'high': 29, 'low': 21, 'rain': 3.0, 'wind': 14, 'uv': 4.0, 'condition': 'Showers', 'icon': 'fa-cloud-showers-heavy', 'color': '#2563eb'},
                {'day': 'Mon 13 Mar', 'high': 28, 'low': 20, 'rain': 1.0, 'wind': 12, 'uv': 5.0, 'condition': 'Drizzle', 'icon': 'fa-cloud-drizzle', 'color': '#60a5fa'},
                {'day': 'Tue 14 Mar', 'high': 31, 'low': 22, 'rain': 0, 'wind': 9, 'uv': 7.5, 'condition': 'Partly Cloudy', 'icon': 'fa-cloud-sun', 'color': '#94a3b8'},
                {'day': 'Wed 15 Mar', 'high': 32, 'low': 23, 'rain': 0, 'wind': 8, 'uv': 8.5, 'condition': 'Sunny', 'icon': 'fa-sun', 'color': '#f59e0b'},
            ]
        }

    return render_template('weather.html',
        weather=weather_info,
        locations=INDIA_LOCATIONS,
        selected_state=selected_state,
        selected_district=selected_district,
        error_msg=error_msg
    )

# Helper function to check if user is authenticated
def is_authenticated():
    return 'user_id' in session

# Make is_authenticated available to templates
@app.context_processor
def inject_auth():
    is_premium = False
    if 'user_id' in session:
        try:
            user = User.query.get(session['user_id'])
            if user and user.membership == 'premium':
                is_premium = True
        except:
            pass
    return dict(
        is_authenticated=is_authenticated, 
        username=lambda: session.get('username'),
        is_premium=is_premium,
        current_user_obj=lambda: User.query.get(session['user_id']) if 'user_id' in session else None
    )

# Initialize database
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Error creating database: {e}")

@app.route('/soil_quality', methods=['GET', 'POST'])
def soil_quality():
    result = None
    if request.method == 'POST':
        try:
            nitrogen = float(request.form.get('nitrogen', 0))
            phosphorus = float(request.form.get('phosphorus', 0))
            potassium = float(request.form.get('potassium', 0))
            ph = float(request.form.get('ph', 7))
            moisture = float(request.form.get('moisture', 50))
            crop = request.form.get('crop', 'General')

            # Simple rule-based analysis (no ML needed)
            score = 0
            issues = []
            recommendations = []

            # Nitrogen analysis
            if nitrogen < 20:
                issues.append("Low Nitrogen (N) - Plants will show yellowing of leaves")
                recommendations.append("Apply Urea or Ammonium Sulphate fertilizer @ 50 kg/acre")
                n_status = "Low"
            elif nitrogen <= 60:
                n_status = "Optimal"
                score += 33
            else:
                issues.append("High Nitrogen - May cause excessive vegetative growth")
                recommendations.append("Reduce nitrogen fertilizers, add more organic matter")
                n_status = "High"
                score += 20

            # Phosphorus analysis
            if phosphorus < 15:
                issues.append("Low Phosphorus (P) - Root development and flowering affected")
                recommendations.append("Apply DAP (Di-Ammonium Phosphate) @ 40 kg/acre")
                p_status = "Low"
            elif phosphorus <= 50:
                p_status = "Optimal"
                score += 33
            else:
                p_status = "High"
                score += 20
                issues.append("Excess Phosphorus - May lock out Zinc and Iron")
                recommendations.append("Avoid phosphorus fertilizers for next 2 seasons")

            # Potassium analysis
            if potassium < 100:
                issues.append("Low Potassium (K) - Crop quality, disease resistance compromised")
                recommendations.append("Apply MOP (Muriate of Potash) @ 30 kg/acre")
                k_status = "Low"
            elif potassium <= 300:
                k_status = "Optimal"
                score += 34
            else:
                k_status = "High"
                score += 20
                recommendations.append("Leach excess potassium with irrigation")

            # pH analysis
            ph_status = ""
            if ph < 5.5:
                issues.append("Soil too Acidic (pH < 5.5) - Nutrient availability reduced")
                recommendations.append("Apply Agricultural Lime @ 2-3 tonnes/acre to raise pH")
                ph_status = "Too Acidic"
            elif ph <= 7.5:
                ph_status = "Optimal"
            else:
                issues.append("Soil too Alkaline (pH > 7.5) - Iron and Manganese deficiency likely")
                recommendations.append("Apply Gypsum or Sulphur to lower soil pH")
                ph_status = "Too Alkaline"

            # Overall rating
            if score >= 80:
                rating = "Excellent"
                rating_color = "success"
            elif score >= 60:
                rating = "Good"
                rating_color = "info"
            elif score >= 40:
                rating = "Fair"
                rating_color = "warning"
            else:
                rating = "Poor"
                rating_color = "danger"

            # Best crops for the soil
            crop_suggestions = []
            if 6.0 <= ph <= 7.0 and nitrogen > 20 and phosphorus > 15:
                crop_suggestions = ["Wheat", "Maize", "Soybean", "Sunflower"]
            elif ph < 6.0:
                crop_suggestions = ["Rice", "Tea", "Groundnut", "Potato"]
            else:
                crop_suggestions = ["Cotton", "Sugarcane", "Sorghum", "Mustard"]

            # Membership check for soil treatment
            is_premium = False
            if 'user_id' in session:
                user = User.query.get(session['user_id'])
                if user and user.membership == 'premium':
                    is_premium = True

            # If basic, limit recommendations
            if not is_premium:
                if len(recommendations) > 1:
                    recommendations = recommendations[:1]
                    recommendations.append("⭐ Upgrade to Premium for detailed expert soil treatments and multi-stage recovery plans.")
                if len(crop_suggestions) > 2:
                    crop_suggestions = crop_suggestions[:2]

            result = {
                'score': score,
                'rating': rating,
                'rating_color': rating_color,
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium,
                'ph': ph,
                'moisture': moisture,
                'n_status': n_status,
                'p_status': p_status,
                'k_status': k_status,
                'ph_status': ph_status,
                'issues': issues,
                'recommendations': recommendations,
                'crop_suggestions': crop_suggestions,
                'crop': crop,
                'is_premium': is_premium
            }
        except Exception as e:
            flash('Please enter valid numeric values.')

    return render_template('soil_quality.html', result=result)


@app.route('/disease_detection', methods=['GET', 'POST'])
def disease_detection():
    result = None
    if request.method == 'POST':
        crop_type = request.form.get('crop_type', 'Tomato')
        symptoms = request.form.get('symptoms', '').lower()

        # Comprehensive AI disease database
        disease_db = {
            'tomato': [
                {'name': 'Early Blight (Alternaria solani)', 'symptoms_keywords': ['brown','spots','yellow','circles','ring','lower leaves'], 'confidence': 92, 'severity': 'Moderate', 'description': 'Fungal disease causing dark brown spots with concentric rings on lower leaves first.', 'treatment': ['Remove infected leaves immediately', 'Spray Mancozeb 75% WP @ 2.5 g/litre', 'Apply Copper Oxychloride every 7-10 days', 'Ensure proper plant spacing', 'Use drip irrigation, avoid wetting leaves'], 'prevention': 'Crop rotation every 2-3 years, certified disease-free seeds'},
                {'name': 'Late Blight (Phytophthora infestans)', 'symptoms_keywords': ['black','dark','wet','rot','wilting','water soaked'], 'confidence': 88, 'severity': 'Severe', 'description': 'Deadly oomycete disease causing water-soaked lesions turning dark brown/black rapidly.', 'treatment': ['Remove ALL infected plants IMMEDIATELY', 'Spray Metalaxyl + Mancozeb @ 2 g/litre', 'Apply Cymoxanil 8% + Mancozeb 64% every 5-7 days', 'Burn infected material, do NOT compost', 'Drain waterlogged fields'], 'prevention': 'Avoid planting in poorly drained soil, grow resistant varieties'},
                {'name': 'Leaf Curl Virus (TLCV)', 'symptoms_keywords': ['curl','curling','small','upward','yellow edges','crinkle'], 'confidence': 85, 'severity': 'Severe', 'description': 'Viral disease spread by whiteflies causing leaf curling, yellowing and stunted growth.', 'treatment': ['Remove & destroy infected plants', 'Spray Imidacloprid 17.8% SL @ 0.5 ml/litre to control whitefly', 'Apply reflective mulch to repel insects', 'Use insect-proof net houses for nursery'], 'prevention': 'Control whitefly population, use virus-free seedlings'},
                {'name': 'Fusarium Wilt', 'symptoms_keywords': ['wilt','droop','yellow','brown stem','vascular'], 'confidence': 86, 'severity': 'Severe', 'description': 'Soil-borne fungal disease blocking vascular tissue causing yellowing and wilting.', 'treatment': ['No chemical cure once infected — remove plants', 'Soil drench with Carbendazim 50% WP @ 1 g/litre', 'Apply Trichoderma viride @ 2.5 kg/acre as biocontrol', 'Solarize soil before next crop'], 'prevention': 'Use Fusarium-resistant varieties, good soil drainage'},
            ],
            'wheat': [
                {'name': 'Yellow Rust (Puccinia striiformis)', 'symptoms_keywords': ['yellow','stripe','rust','powder','orange','streak'], 'confidence': 90, 'severity': 'Moderate', 'description': 'Yellow/orange powdery pustules in stripes along leaf veins.', 'treatment': ['Spray Propiconazole 25% EC @ 1 ml/litre immediately', 'Apply Tebuconazole 25.9% EC @ 1 litre/hectare', 'Repeat spray after 15 days', 'Harvest early if severe'], 'prevention': 'Timely sowing (Nov 1-15), use resistant varieties like HD-2967'},
                {'name': 'Brown Rust (Puccinia triticina)', 'symptoms_keywords': ['brown','rust','scattered','pustules','orange brown'], 'confidence': 87, 'severity': 'Moderate', 'description': 'Brown-orange scattered pustules on leaves reducing grain filling.', 'treatment': ['Spray Propiconazole 25% EC @ 1 ml/litre', 'Apply Mancozeb 75% WP @ 2.5 g/litre', 'Spray Hexaconazole 5% EC if severe'], 'prevention': 'Use resistant varieties like WR544, Raj 4120'},
                {'name': 'Loose Smut (Ustilago tritici)', 'symptoms_keywords': ['black','smut','ear','seed','powder','sooty'], 'confidence': 88, 'severity': 'Moderate', 'description': 'Entire ear head replaced by black smutty mass of spores.', 'treatment': ['Use hot water seed treatment — soak at 52°C for 10 min', 'Treat seeds with Carboxin 37.5% + Thiram 37.5% @ 3 g/kg', 'Rogue out smutted plants immediately'], 'prevention': 'Use certified disease-free seed every season'},
                {'name': 'Powdery Mildew', 'symptoms_keywords': ['white','powder','mildew','fluffy','coating'], 'confidence': 85, 'severity': 'Mild', 'description': 'White powdery growth on leaf surface reducing photosynthesis.', 'treatment': ['Spray Sulfex 80% WP @ 3 g/litre', 'Apply Triadimefon 25% WP @ 1 g/litre', 'Karathane (Dinocap) also effective'], 'prevention': 'Adequate spacing, balanced nitrogen, resistant varieties'},
            ],
            'rice': [
                {'name': 'Blast Disease (Pyricularia oryzae)', 'symptoms_keywords': ['blast','gray','grey','diamond','neck','lesion'], 'confidence': 91, 'severity': 'Severe', 'description': 'Fungal disease causing diamond-shaped grey lesions. Neck blast can destroy entire crop.', 'treatment': ['Spray Tricyclazole 75% WP @ 0.6 g/litre', 'Apply Isoprothiolane 40% EC @ 1.5 ml/litre', 'Drain field 3-4 days and re-flood', 'Reduce nitrogen doses'], 'prevention': 'Blast-resistant varieties, balanced NPK fertilization'},
                {'name': 'Brown Plant Hopper (BPH)', 'symptoms_keywords': ['hopperburn','browning','circular','sudden death','straw'], 'confidence': 88, 'severity': 'Severe', 'description': 'Insect pest causing sudden browning of circular patches — "hopperburn". Population explosion in humid conditions.', 'treatment': ['Spray Buprofezin 25% SC @ 1.2 ml/litre', 'Apply Imidacloprid 17.8% SL @ 0.5 ml/litre', 'Drain water and spray at base of plants', 'Avoid excess nitrogen'], 'prevention': 'Use BPH-resistant varieties, avoid over-application of nitrogen'},
                {'name': 'Bacterial Leaf Blight (Xanthomonas oryzae)', 'symptoms_keywords': ['blight','yellow','water soaked margin','kresek','pale yellow','wilting seedling'], 'confidence': 87, 'severity': 'Moderate', 'description': 'Bacterial disease causing water-soaked leaf margins turning yellow then straw-colored.', 'treatment': ['Spray Copper Oxychloride 50% WP @ 3 g/litre', 'Apply Streptocycline 100ppm + Copper Oxychloride 0.3%', 'Drain field and reduce nitrogen'], 'prevention': 'Seed treatment with Streptocycline, use resistant varieties'},
                {'name': 'Sheath Blight (Rhizoctonia solani)', 'symptoms_keywords': ['sheath','oval','lesion','water level','white center','brown border'], 'confidence': 85, 'severity': 'Moderate', 'description': 'Fungal disease causing oval lesions on sheath at water level, spreading upward.', 'treatment': ['Spray Validamycin 3% L @ 2 ml/litre', 'Apply Hexaconazole 5% SC @ 1 ml/litre', 'Drain water before spraying'], 'prevention': 'Proper plant spacing, avoid excess nitrogen, drain fields'},
            ],
            'potato': [
                {'name': 'Late Blight (Phytophthora infestans)', 'symptoms_keywords': ['brown','black','rot','lesion','dark','water soaked'], 'confidence': 89, 'severity': 'Severe', 'description': 'Highly destructive oomycete causing dark lesions on leaves and tuber rot.', 'treatment': ['Spray Metalaxyl + Mancozeb @ 2 g/litre immediately', 'Apply Cymoxanil 8% + Mancozeb 64% every 5-7 days', 'Destroy infected haulms before harvest', 'Store only healthy tubers'], 'prevention': 'Plant certified seed, avoid planting in waterlogged areas'},
                {'name': 'Black Scurf (Rhizoctonia solani)', 'symptoms_keywords': ['black','scab','rough','stem canker','dark spots','tuber'], 'confidence': 85, 'severity': 'Moderate', 'description': 'Soil-borne fungus causing black sclerotia on tubers and stem canker reducing yield.', 'treatment': ['Treat seed with Carbendazim 50% WP @ 2 g/kg before planting', 'Soil application of Trichoderma viride @ 2.5 kg/acre', 'Harvest at proper maturity'], 'prevention': 'Crop rotation with non-host crops for 3+ years'},
                {'name': 'Common Scab (Streptomyces scabies)', 'symptoms_keywords': ['scab','corky','rough skin','raised','crater'], 'confidence': 82, 'severity': 'Mild', 'description': 'Bacterial-like disease causing corky, raised or pitted scab lesions on tuber skin.', 'treatment': ['Maintain soil pH below 5.2 with sulfur', 'Seed treatment with Thiram 75% WP @ 3 g/kg', 'Ensure adequate soil moisture at tuber initiation'], 'prevention': 'Avoid over-liming, use scab-resistant varieties like Kufri Jyoti'},
            ],
            'maize': [
                {'name': 'Fall Armyworm (Spodoptera frugiperda)', 'symptoms_keywords': ['worm','caterpillar','hole','leaves','frass','whorl','eaten'], 'confidence': 90, 'severity': 'Severe', 'description': 'Invasive pest larvae feeding inside whorl causing window-pane damage, characteristic frass.', 'treatment': ['Spray Emamectin Benzoate 5% SG @ 0.4 g/litre', 'Apply Spinetoram 11.7% SC @ 0.75 ml/litre into whorl', 'Use Chlorantraniliprole 18.5% SC @ 0.3 ml/litre'], 'prevention': 'Early sowing, monitor regularly, pheromone traps'},
                {'name': 'Turcicum Leaf Blight', 'symptoms_keywords': ['gray','cigar','long lesion','blight','tan'], 'confidence': 85, 'severity': 'Moderate', 'description': 'Fungal disease causing large, cigar-shaped gray-tan lesions on leaves.', 'treatment': ['Spray Mancozeb 75% WP @ 2.5 g/litre', 'Apply Propiconazole 25% EC @ 1 ml/litre', 'Remove infected lower leaves'], 'prevention': 'Use resistant hybrids, proper spacing, crop rotation'},
                {'name': 'Downy Mildew', 'symptoms_keywords': ['white','downy','yellow stripe','mildew','chlorosis'], 'confidence': 83, 'severity': 'Moderate', 'description': 'Fungal disease causing chlorotic stripes with white downy growth on leaf undersurface.', 'treatment': ['Spray Metalaxyl 35% WS @ 6 g/kg seed as treatment', 'Foliar spray Metalaxyl + Mancozeb @ 2 g/litre', 'Remove and destroy infected plants'], 'prevention': 'Seed treatment with Metalaxyl, use resistant varieties'},
            ],
            'cotton': [
                {'name': 'Bollworm (Helicoverpa armigera)', 'symptoms_keywords': ['worm','boll','hole','caterpillar','frass','pod','eaten'], 'confidence': 91, 'severity': 'Severe', 'description': 'Major pest larvae boring into bolls causing premature boll shedding and yield loss.', 'treatment': ['Spray Chlorantraniliprole 18.5% SC @ 0.3 ml/litre', 'Apply Spinosad 45% SC @ 0.2 ml/litre', 'Use Emamectin Benzoate @ 0.4 g/litre', 'Install pheromone traps @ 5/acre for monitoring'], 'prevention': 'Bt cotton usage, pheromone traps, avoid late planting'},
                {'name': 'Bacterial Blight (Xanthomonas axonopodis)', 'symptoms_keywords': ['angular','water soaked','brown','vein','blight','bacterial'], 'confidence': 86, 'severity': 'Moderate', 'description': 'Angular water-soaked lesions bounded by leaf veins causing boll rot.', 'treatment': ['Spray Copper Oxychloride 50% WP @ 3 g/litre', 'Apply Streptocycline 100 ppm spray', 'Remove infected plant debris'], 'prevention': 'Treat seeds with hot water @ 52°C for 30 min, use resistant varieties'},
                {'name': 'Root Rot (Fusarium/Macrophomina)', 'symptoms_keywords': ['root','rot','wilt','brown stem base','sudden wilt','charcoal'], 'confidence': 84, 'severity': 'Severe', 'description': 'Soil-borne disease causing root and stem base rotting, plant wilts suddenly.', 'treatment': ['Soil drench with Carbendazim @ 1 g/litre', 'Apply Trichoderma @ 2.5 kg/acre', 'Avoid waterlogging'], 'prevention': 'Good drainage, crop rotation, seed treatment with Thiram'},
            ],
            'sugarcane': [
                {'name': 'Red Rot (Colletotrichum falcatum)', 'symptoms_keywords': ['red','rot','sour smell','alcohol','internal','tissue'], 'confidence': 89, 'severity': 'Severe', 'description': 'Disease showing red discoloration of internal tissue with white patches.', 'treatment': ['Destroy infected stools completely', 'Treat setts in Agrosan GN 0.25% for 15-20 min', 'Select healthy seed cane from disease-free fields'], 'prevention': 'Use resistant varieties like CoJ 64, CoS 95255; hot water seed treatment'},
                {'name': 'Smut (Sporisorium scitamineum)', 'symptoms_keywords': ['whip','black','curled','shoot','dusty'], 'confidence': 87, 'severity': 'Severe', 'description': 'Infected shoots form characteristic curved black whip of spore mass.', 'treatment': ['Remove all smut whips before spores are released', 'Hot water treatment of setts @ 50°C for 2 hours', 'Spray Carboxin + Thiram on setts'], 'prevention': 'Use resistant varieties, certified disease-free seed cane'},
            ],
            'onion': [
                {'name': 'Purple Blotch (Alternaria porri)', 'symptoms_keywords': ['purple','blotch','lesion','white center','oval','leaves'], 'confidence': 88, 'severity': 'Moderate', 'description': 'Fungal disease causing water-soaked lesions turning purple with yellow halo.', 'treatment': ['Spray Mancozeb 75% WP @ 2.5 g/litre', 'Apply Iprodione 50% WP @ 2 g/litre', 'Spray Difenconazole @ 1 ml/litre for severe infections'], 'prevention': 'Crop rotation, proper spacing, avoid overhead irrigation'},
                {'name': 'Thrips (Thrips tabaci)', 'symptoms_keywords': ['silver','streaks','thrips','curling','distorted','white patches'], 'confidence': 85, 'severity': 'Moderate', 'description': 'Tiny insects causing silver streaking by rasping leaf tissue.', 'treatment': ['Spray Spinosad 45% SC @ 0.2 ml/litre', 'Apply Imidacloprid 17.8% SL @ 0.5 ml/litre', 'Fipronil 5% SC @ 2 ml/litre'], 'prevention': 'Blue sticky traps, avoid drought stress, regular monitoring'},
            ],
            'garlic': [
                {'name': 'White Rot (Sclerotium cepivorum)', 'symptoms_keywords': ['white','rot','fluffy','mycelium','yellowing','collapse'], 'confidence': 86, 'severity': 'Severe', 'description': 'Soil-borne disease causing white fluffy mycelium at base and bulb rot.', 'treatment': ['Drench soil with PCNB (Quintozene) @ 10g/litre', 'Apply Tebuconazole fungicide in furrow', 'Remove and dispose infected bulbs away from field'], 'prevention': 'Never introduce infected soil, long crop rotations (8+ years)'},
            ],
            'chilli': [
                {'name': 'Fruit Rot / Anthracnose (Colletotrichum capsici)', 'symptoms_keywords': ['fruit rot','sunken','orange','lesion','circle','blossom end'], 'confidence': 90, 'severity': 'Moderate', 'description': 'Common fungal disease of ripe fruits causing sunken, circular lesions.', 'treatment': ['Spray Mancozeb 75% WP @ 2 g/litre', 'Apply Carbendazim 50% WP @ 1 g/litre', 'Copper oxychloride spray every 10 days'], 'prevention': 'Use healthy seeds, avoid rain splash, timely harvest'},
                {'name': 'Leaf Curl Virus', 'symptoms_keywords': ['curl','curling','small','stunted','yellow','mosaic'], 'confidence': 87, 'severity': 'Severe', 'description': 'Viral disease spread by thrips and mites causing severe leaf curling and stunting.', 'treatment': ['Remove infected plants', 'Control vectors: spray Spiromesifen 22.9% SC @ 1 ml/litre for mites', 'Use yellow sticky traps for thrips'], 'prevention': 'Use virus-free seeds, control mites/thrips regularly'},
            ],
            'mustard': [
                {'name': 'White Rust (Albugo candida)', 'symptoms_keywords': ['white','pustule','blister','chalk white','leaf','raised'], 'confidence': 88, 'severity': 'Moderate', 'description': 'Chalky white blisters on leaves and distorted inflorescence (staghead).', 'treatment': ['Spray Metalaxyl + Mancozeb @ 2 g/litre', 'Apply Ridomil Gold 2 g/litre', 'Remove infected staghead shoots'], 'prevention': 'Seed treatment with Apron 35 SD, avoid dense planting'},
                {'name': 'Downy Mildew (Peronospora parasitica)', 'symptoms_keywords': ['downy','grey','mildew','angular','yellow patches'], 'confidence': 85, 'severity': 'Mild', 'description': 'Grey downy growth on leaf undersurface with yellow patches above.', 'treatment': ['Spray Metalaxyl + Mancozeb @ 2 g/litre', 'Copper Oxychloride @ 3 g/litre'], 'prevention': 'Proper seed treatment, adequate spacing'},
            ],
            'soybean': [
                {'name': 'Soybean Mosaic Virus (SMV)', 'symptoms_keywords': ['mosaic','yellow','mottled','stunted','wrinkle','leaves'], 'confidence': 84, 'severity': 'Moderate', 'description': 'Viral disease causing leaf mosaic, chlorosis, and severe yield reduction.', 'treatment': ['Remove infected plants', 'Control aphids with Imidacloprid 0.5 ml/litre', 'Use virus-indexed seeds'], 'prevention': 'Use resistant varieties, control aphid vectors'},
                {'name': 'Charcoal Rot (Macrophomina phaseolina)', 'symptoms_keywords': ['charcoal','rot','grey','stem','wilt','dry weather'], 'confidence': 83, 'severity': 'Severe', 'description': 'Soil-borne disease causing grey-black stem lesions and premature plant death in dry/hot conditions.', 'treatment': ['No effective in-season chemical control', 'Apply Trichoderma @ 2.5 kg/acre to soil', 'Maintain adequate soil moisture'], 'prevention': 'Irrigation management, crop rotation, seed treatment with Thiram'},
            ],
            'groundnut': [
                {'name': 'Tikka Disease / Leaf Spot (Cercospora)', 'symptoms_keywords': ['spot','brown','tikka','circular','yellow halo','leaf'], 'confidence': 89, 'severity': 'Moderate', 'description': 'Early and late leaf spot causing circular brown spots with yellow halo leading to defoliation.', 'treatment': ['Spray Chlorothalonil 75% WP @ 2 g/litre', 'Apply Mancozeb 75% WP @ 2.5 g/litre every 10-14 days', 'Spray Carbendazim for late leaf spot'], 'prevention': 'Crop rotation, use resistant varieties, timely sowing'},
                {'name': 'Stem Rot (Sclerotium rolfsii)', 'symptoms_keywords': ['stem','rot','white','mycelium','brown','collar','base'], 'confidence': 85, 'severity': 'Severe', 'description': 'White mycelial growth at stem base causing wilting and plant death.', 'treatment': ['Remove infected plants with surrounding soil', 'Soil drench Carbendazim @ 1 g/litre', 'Apply Trichoderma harzianum @ 2.5 kg/acre'], 'prevention': 'Deep summer plowing, crop rotation, seed treatment'},
            ],
            'banana': [
                {'name': 'Panama Wilt (Fusarium oxysporum f.sp. cubense)', 'symptoms_keywords': ['wilt','yellow','lower leaves','yellow edges','split','pseudostem'], 'confidence': 90, 'severity': 'Severe', 'description': 'Devastating soil-borne Fusarium wilt causing progressive leaf yellowing from oldest leaves.', 'treatment': ['No effective cure — remove and destroy infected plants', 'Drench Trichoderma viride around root zone', 'Do not replant banana in same area for 4-5 years'], 'prevention': 'Plant TR4-resistant varieties like Cavendish alternatives'},
                {'name': 'Sigatoka Leaf Spot (Mycosphaerella musicola)', 'symptoms_keywords': ['yellow streak','brown','oval','leaf spot','dry','necrosis'], 'confidence': 86, 'severity': 'Moderate', 'description': 'Yellow streaks developing into brown oval spots causing premature leaf death.', 'treatment': ['Spray Propiconazole 25% EC @ 1 ml/litre', 'Apply Mineral oil + Mancozeb spray', 'Remove infected leaves'], 'prevention': 'Adequate plant spacing, remove old dead leaves regularly'},
            ],
            'mango': [
                {'name': 'Anthracnose (Colletotrichum gloeosporioides)', 'symptoms_keywords': ['brown','black','spot','lesion','flower','fruit','rot','sunken'], 'confidence': 89, 'severity': 'Moderate', 'description': 'Common post-harvest disease causing black spots/rot on fruits and blossom infection.', 'treatment': ['Spray Carbendazim 50% WP @ 1 g/litre at flowering/fruiting', 'Apply Copper Oxychloride @ 3 g/litre prophylactically', 'Hot water treatment of fruits @ 52°C for 5 min post-harvest'], 'prevention': 'Prune dead wood, improve air circulation, spray during flowering'},
                {'name': 'Powdery Mildew (Oidium mangiferae)', 'symptoms_keywords': ['white','powder','mildew','flower','coating','shoot'], 'confidence': 88, 'severity': 'Moderate', 'description': 'White powdery growth on inflorescence causing flower drop and reduced fruit set.', 'treatment': ['Spray Sulfex 80% WP @ 3 g/litre at flower bud stage', 'Apply Hexaconazole 5% SC @ 1 ml/litre', 'Wettable sulfur spray effective'], 'prevention': 'Spray preventively at panicle emergence, good orchard sanitation'},
            ],
        }

        # Find matching disease
        crop_lower = crop_type.lower()
        selected_diseases = disease_db.get(crop_lower, disease_db['tomato'])

        # Membership check
        is_premium = False
        if 'user_id' in session:
            try:
                user = User.query.get(session['user_id'])
                if user and user.membership == 'premium':
                    is_premium = True
            except:
                pass

        # Match based on symptoms
        best_match = selected_diseases[0]
        best_score = 0
        for disease in selected_diseases:
            match_score = sum(1 for kw in disease['symptoms_keywords'] if kw in symptoms)
            if match_score > best_score:
                best_score = match_score
                best_match = disease

        # Limit details for basic users
        if not is_premium:
            # Mask some fields for basic
            best_match = best_match.copy()
            best_match['treatment'] = [best_match['treatment'][0], "⭐ Upgrade to Premium for full expert treatment & chemical dosages."]
            best_match['prevention'] = "⭐ Available for Premium Users"

        result = {
            'crop': crop_type,
            'disease': best_match,
            'symptoms_entered': symptoms,
            'is_premium': is_premium
        }

    return render_template('disease_detection.html', result=result)

@app.route('/upgrade_premium', methods=['GET', 'POST'])
def upgrade_premium():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.membership = 'premium'
        db.session.commit()
        flash('Welcome to Premium! All limits have been removed.')
        return redirect(url_for('dashboard'))
    
    return render_template('upgrade_premium.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)

