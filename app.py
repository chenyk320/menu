from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
import uuid
from datetime import datetime
from functools import wraps
from PIL import Image

# 尝试导入CDN服务，如果失败则使用本地存储
try:
    from cdn_service import cdn_service
    from config import Config
    CDN_AVAILABLE = True
except ImportError:
    print("⚠️  CDN服务不可用，将使用本地存储")
    CDN_AVAILABLE = False
    cdn_service = None
    Config = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


# 身份验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 自动生成菜品序号
def generate_dish_number(category_id):
    """根据分类ID生成菜品序号，格式如 A1, B2, C3"""
    category = Category.query.get(category_id)
    if not category:
        return None
    
    # 获取该分类下现有的最大序号
    existing_dishes = Dish.query.filter_by(category_id=category_id).all()
    max_number = 0
    
    for dish in existing_dishes:
        # 提取序号中的数字部分
        if dish.dish_number and dish.dish_number.startswith(category.prefix_letter):
            try:
                number = int(dish.dish_number[1:])
                max_number = max(max_number, number)
            except ValueError:
                continue
    
    # 返回新的序号
    return f"{category.prefix_letter}{max_number + 1}"

# 重新排序分类下的所有菜品序号
def reorder_dishes_in_category(category_id):
    """重新排序指定分类下的所有菜品序号"""
    dishes = Dish.query.filter_by(category_id=category_id).order_by(Dish.sort_order, Dish.id).all()
    category = Category.query.get(category_id)
    
    if not category:
        return
    
    for i, dish in enumerate(dishes, 1):
        dish.dish_number = f"{category.prefix_letter}{i}"
    
    db.session.commit()

# 图片优化函数
def optimize_uploaded_image(file_path, max_width=800, quality=85):
    """
    优化上传的图片
    :param file_path: 图片文件路径
    :param max_width: 最大宽度
    :param quality: JPEG质量
    """
    try:
        with Image.open(file_path) as img:
            # 转换为RGB模式
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 调整尺寸
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存优化后的图片
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
            return True
            
    except Exception as e:
        print(f"图片优化失败: {e}")
        return False


# 管理员凭据
ADMIN_USERNAME = 'chenyaokang'
ADMIN_PASSWORD = '761748142'

# 过敏源模型
class Allergen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_cn = db.Column(db.String(50), nullable=False)
    name_it = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    description_cn = db.Column(db.String(200))
    description_it = db.Column(db.String(200))

# 菜品分类模型
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_cn = db.Column(db.String(50), nullable=False)
    name_it = db.Column(db.String(50), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    prefix_letter = db.Column(db.String(1), nullable=False)  # 分类前缀字母

# 菜品模型
class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_number = db.Column(db.String(10), nullable=False, unique=True)
    name_cn = db.Column(db.String(100), nullable=False)
    name_it = db.Column(db.String(100), nullable=False)
    description_it = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)  # 保留原价格字段作为默认价格
    image = db.Column(db.String(200))  # 本地图片路径
    image_cdn_url = db.Column(db.String(500))  # CDN图片URL
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    allergens = db.relationship('Allergen', secondary='dish_allergen', backref='dishes')
    portions = db.relationship('DishPortion', backref='dish', cascade='all, delete-orphan')
    sort_order = db.Column(db.Integer, default=0)
    surgelato = db.Column(db.Boolean, default=False)  # 冷冻食品标识
    is_popular = db.Column(db.Boolean, default=False)  # 人气菜标识
    is_new = db.Column(db.Boolean, default=False)  # 新菜标识
    is_vegan = db.Column(db.Boolean, default=False)  # 纯素食标识
    spiciness_level = db.Column(db.Integer, default=0)  # 辣度等级：0=不辣，1=微辣🔥，2=中辣🔥🔥，3=特辣🔥🔥🔥

# 菜品过敏源关联表
dish_allergen = db.Table('dish_allergen',
    db.Column('dish_id', db.Integer, db.ForeignKey('dish.id'), primary_key=True),
    db.Column('allergen_id', db.Integer, db.ForeignKey('allergen.id'), primary_key=True)
)

# 菜品分量价格模型
class DishPortion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    portion_name_cn = db.Column(db.String(50), nullable=False)  # 分量名称（中文）
    portion_name_it = db.Column(db.String(50), nullable=False)  # 分量名称（意大利语）
    price = db.Column(db.Float, nullable=False)  # 该分量的价格
    sort_order = db.Column(db.Integer, default=0)  # 排序
    is_default = db.Column(db.Boolean, default=False)  # 是否为默认分量

# 主页路由
@app.route('/')
def index():
    categories = Category.query.order_by(Category.sort_order).all()
    dishes = Dish.query.order_by(Dish.sort_order).all()
    allergens = Allergen.query.all()
    return render_template('menu.html', categories=categories, dishes=dishes, allergens=allergens)

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('admin'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    session.clear()
    flash('已成功登出！', 'info')
    return redirect(url_for('login'))

# 后台管理页面
@app.route('/admin')
@login_required
def admin():
    categories = Category.query.order_by(Category.sort_order).all()
    dishes = Dish.query.order_by(Dish.sort_order).all()
    allergens = Allergen.query.all()
    return render_template('admin.html', categories=categories, dishes=dishes, allergens=allergens)


# 添加菜品
@app.route('/api/dish', methods=['POST'])
@login_required
def add_dish():
    data = request.form
    
    # 检查是否选择了分类
    if not data.get('category_id'):
        return jsonify({'success': False, 'message': '请选择菜品分类'})
    
    category_id = int(data['category_id'])
    
    # 自动生成菜品序号
    dish_number = generate_dish_number(category_id)
    if not dish_number:
        return jsonify({'success': False, 'message': '无法生成菜品序号，请检查分类设置'})
    
    # 处理图片上传
    image_path = None
    image_cdn_url = None
    
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(file.filename)
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # 尝试上传到CDN
            if CDN_AVAILABLE and cdn_service and cdn_service.is_enabled():
                cdn_url = cdn_service.optimize_and_upload(file_path, unique_filename)
                if cdn_url:
                    image_cdn_url = cdn_url
                    # 如果CDN上传成功且不需要本地备份，删除本地文件
                    if not Config.LOCAL_BACKUP:
                        os.remove(file_path)
                        image_path = None
                    else:
                        image_path = f"images/{unique_filename}"
                else:
                    # CDN上传失败，使用本地文件
                    optimize_uploaded_image(file_path, max_width=800, quality=85)
                    image_path = f"images/{unique_filename}"
            else:
                # CDN未配置或不可用，使用本地文件
                optimize_uploaded_image(file_path, max_width=800, quality=85)
                image_path = f"images/{unique_filename}"
    
    # 创建菜品
    dish = Dish(
        dish_number=dish_number,
        name_cn=data['name_cn'],
        name_it=data['name_it'],
        description_it=data.get('description_it', ''),
        price=float(data['price']),
        image=image_path,
        image_cdn_url=image_cdn_url,
        category_id=category_id,
        surgelato=data.get('surgelato') == 'on',  # 复选框返回'on'或None
        is_popular=data.get('is_popular') == 'on',  # 人气菜标识
        is_new=data.get('is_new') == 'on',  # 新菜标识
        is_vegan=data.get('is_vegan') == 'on',  # 纯素食标识
        spiciness_level=int(data.get('spiciness_level', 0))  # 辣度等级
    )
    
    db.session.add(dish)
    db.session.flush()  # 获取dish的ID
    
    # 处理分量价格
    portions_data = request.form.get('portions', '')
    if portions_data:
        try:
            import json
            portions = json.loads(portions_data)
            for i, portion in enumerate(portions):
                dish_portion = DishPortion(
                    dish_id=dish.id,
                    portion_name_cn=portion.get('name_cn', ''),
                    portion_name_it=portion.get('name_it', ''),
                    price=float(portion.get('price', 0)),
                    sort_order=i,
                    is_default=portion.get('is_default', False)
                )
                db.session.add(dish_portion)
        except (json.JSONDecodeError, ValueError) as e:
            # 如果分量数据格式错误，继续使用默认价格
            pass
    
    # 添加过敏源
    allergen_ids = request.form.getlist('allergens')
    for allergen_id in allergen_ids:
        allergen = Allergen.query.get(int(allergen_id))
        if allergen:
            dish.allergens.append(allergen)
    
    db.session.commit()
    return jsonify({'success': True, 'message': f'菜品添加成功，序号为 {dish_number}'})

# 编辑菜品
@app.route('/api/dish/<int:dish_id>', methods=['PUT'])
@login_required
def edit_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    data = request.form
    
    # 检查是否选择了分类
    if not data.get('category_id'):
        return jsonify({'success': False, 'message': '请选择菜品分类'})
    
    new_category_id = int(data['category_id'])
    old_category_id = dish.category_id
    
    # 处理图片上传
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # 删除旧图片
            if dish.image:
                old_image_path = os.path.join('static', dish.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # 保存新图片
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # 尝试上传到CDN
            if CDN_AVAILABLE and cdn_service and cdn_service.is_enabled():
                cdn_url = cdn_service.optimize_and_upload(file_path, unique_filename)
                if cdn_url:
                    dish.image_cdn_url = cdn_url
                    if not Config.LOCAL_BACKUP:
                        os.remove(file_path)
                        dish.image = None
                    else:
                        dish.image = f"images/{unique_filename}"
                else:
                    # CDN上传失败，使用本地文件
                    optimize_uploaded_image(file_path, max_width=800, quality=85)
                    dish.image = f"images/{unique_filename}"
            else:
                # CDN未配置或不可用，使用本地文件
                optimize_uploaded_image(file_path, max_width=800, quality=85)
                dish.image = f"images/{unique_filename}"
    
    # 更新菜品信息
    dish.name_cn = data['name_cn']
    dish.name_it = data['name_it']
    dish.description_it = data.get('description_it', '')
    dish.price = float(data['price'])
    dish.category_id = new_category_id
    dish.surgelato = data.get('surgelato') == 'on'
    dish.is_popular = data.get('is_popular') == 'on'
    dish.is_new = data.get('is_new') == 'on'
    dish.is_vegan = data.get('is_vegan') == 'on'
    dish.spiciness_level = int(data.get('spiciness_level', 0))
    
    # 如果分类改变，重新生成序号
    if old_category_id != new_category_id:
        dish.dish_number = generate_dish_number(new_category_id)
        if not dish.dish_number:
            return jsonify({'success': False, 'message': '无法生成菜品序号，请检查分类设置'})
        
        # 重新排序旧分类的菜品
        if old_category_id:
            reorder_dishes_in_category(old_category_id)
    
    # 处理分量价格
    portions_data = request.form.get('portions', '')
    # 清除现有分量
    dish.portions.clear()
    
    if portions_data:
        try:
            import json
            portions = json.loads(portions_data)
            for i, portion in enumerate(portions):
                dish_portion = DishPortion(
                    dish_id=dish.id,
                    portion_name_cn=portion.get('name_cn', ''),
                    portion_name_it=portion.get('name_it', ''),
                    price=float(portion.get('price', 0)),
                    sort_order=i,
                    is_default=portion.get('is_default', False)
                )
                db.session.add(dish_portion)
        except (json.JSONDecodeError, ValueError) as e:
            # 如果分量数据格式错误，继续使用默认价格
            pass
    
    # 更新过敏源
    dish.allergens.clear()  # 清除现有过敏源
    allergen_ids = request.form.getlist('allergens')
    for allergen_id in allergen_ids:
        allergen = Allergen.query.get(int(allergen_id))
        if allergen:
            dish.allergens.append(allergen)
    
    db.session.commit()
    return jsonify({'success': True, 'message': '菜品更新成功'})

# 删除菜品图片
@app.route('/api/dish/<int:dish_id>/image', methods=['DELETE'])
@login_required
def delete_dish_image(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    
    if not dish.image:
        return jsonify({'success': False, 'message': '该菜品没有图片'})
    
    # 删除图片文件
    image_path = os.path.join('static', dish.image)
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # 清空数据库中的图片路径
    dish.image = None
    db.session.commit()
    
    return jsonify({'success': True, 'message': '图片删除成功'})

# 删除菜品
@app.route('/api/dish/<int:dish_id>', methods=['DELETE'])
@login_required
def delete_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    category_id = dish.category_id
    
    # 删除图片文件
    if dish.image:
        image_path = os.path.join('static', dish.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(dish)
    db.session.commit()
    
    # 重新排序该分类下的所有菜品
    if category_id:
        reorder_dishes_in_category(category_id)
    
    return jsonify({'success': True, 'message': '菜品删除成功'})

# 获取所有菜品数据（API）
@app.route('/api/dishes')
def get_dishes():
    dishes = Dish.query.join(Category).order_by(Category.sort_order, Dish.sort_order).all()
    result = []
    for dish in dishes:
        # 获取分量信息
        portions = []
        for portion in sorted(dish.portions, key=lambda x: x.sort_order):
            portions.append({
                'id': portion.id,
                'name_cn': portion.portion_name_cn,
                'name_it': portion.portion_name_it,
                'price': portion.price,
                'is_default': portion.is_default
            })
        
        # 确定图片URL（优先使用CDN）
        image_url = dish.image_cdn_url if dish.image_cdn_url else dish.image
        
        result.append({
            'id': dish.id,
            'dish_number': dish.dish_number,
            'name_cn': dish.name_cn,
            'name_it': dish.name_it,
            'description_it': dish.description_it,
            'price': dish.price,
            'image': image_url,
            'image_local': dish.image,
            'image_cdn': dish.image_cdn_url,
            'category_id': dish.category_id,
            'surgelato': dish.surgelato,
            'is_popular': dish.is_popular,
            'is_new': dish.is_new,
            'is_vegan': dish.is_vegan,
            'spiciness_level': dish.spiciness_level,
            'portions': portions,
            'allergens': [{'id': a.id, 'name_cn': a.name_cn, 'name_it': a.name_it, 'icon': a.icon} for a in dish.allergens]
        })
    return jsonify(result)

# 获取所有分类数据（API）
@app.route('/api/categories')
def get_categories():
    categories = Category.query.order_by(Category.sort_order).all()
    result = []
    for category in categories:
        result.append({
            'id': category.id,
            'name_cn': category.name_cn,
            'name_it': category.name_it,
            'sort_order': category.sort_order,
            'prefix_letter': category.prefix_letter
        })
    return jsonify(result)

# 添加分类
@app.route('/api/category', methods=['POST'])
@login_required
def add_category():
    data = request.json
    
    # 检查前缀字母是否已存在
    existing_category = Category.query.filter_by(prefix_letter=data['prefix_letter']).first()
    if existing_category:
        return jsonify({'success': False, 'message': f'前缀字母 {data["prefix_letter"]} 已被使用'})
    
    category = Category(
        name_cn=data['name_cn'],
        name_it=data['name_it'],
        sort_order=data.get('sort_order', 0),
        prefix_letter=data['prefix_letter']
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({'success': True, 'message': '分类添加成功'})

# 添加过敏源
@app.route('/api/allergen', methods=['POST'])
@login_required
def add_allergen():
    data = request.json
    allergen = Allergen(
        name_cn=data['name_cn'],
        name_it=data['name_it'],
        icon=data['icon'],
        description_cn=data.get('description_cn', ''),
        description_it=data.get('description_it', '')
    )
    db.session.add(allergen)
    db.session.commit()
    return jsonify({'success': True, 'message': '过敏源添加成功'})

# 删除分类
@app.route('/api/category/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # 检查是否有菜品使用此分类
    dishes_with_category = Dish.query.filter_by(category_id=category_id).count()
    if dishes_with_category > 0:
        return jsonify({'success': False, 'message': f'该分类下还有 {dishes_with_category} 个菜品，无法删除'})
    
    db.session.delete(category)
    db.session.commit()
    return jsonify({'success': True, 'message': '分类删除成功'})

# 删除过敏源
@app.route('/api/allergen/<int:allergen_id>', methods=['DELETE'])
@login_required
def delete_allergen(allergen_id):
    allergen = Allergen.query.get_or_404(allergen_id)
    
    # 从所有菜品中移除该过敏源
    dishes_with_allergen = Dish.query.filter(Dish.allergens.any(id=allergen_id)).all()
    for dish in dishes_with_allergen:
        dish.allergens.remove(allergen)
    
    db.session.delete(allergen)
    db.session.commit()
    return jsonify({'success': True, 'message': '过敏源删除成功'})

# 获取所有过敏源数据（API）
@app.route('/api/allergens')
def get_allergens():
    allergens = Allergen.query.all()
    result = []
    for allergen in allergens:
        result.append({
            'id': allergen.id,
            'name_cn': allergen.name_cn,
            'name_it': allergen.name_it,
            'icon': allergen.icon,
            'description_cn': allergen.description_cn,
            'description_it': allergen.description_it
        })
    return jsonify(result)

# 初始化数据库
def init_db():
    with app.app_context():
        db.create_all()
        
        # 初始化一些默认数据
        if not Category.query.first():
            categories = [
                Category(name_cn='主食', name_it='Piatti Principali', sort_order=1, prefix_letter='A'),
                Category(name_cn='凉菜', name_it='Piatti Freddi', sort_order=2, prefix_letter='B'),
                Category(name_cn='小吃', name_it='Spuntini', sort_order=3, prefix_letter='C'),
                Category(name_cn='汤类', name_it='Zuppe', sort_order=4, prefix_letter='D'),
                Category(name_cn='海鲜', name_it='Frutti di Mare', sort_order=5, prefix_letter='E'),
                Category(name_cn='肉类', name_it='Piatti di Carne', sort_order=6, prefix_letter='F'),
                Category(name_cn='素菜', name_it='Piatti Vegetariani', sort_order=7, prefix_letter='G'),
                Category(name_cn='饮品', name_it='Bevande', sort_order=8, prefix_letter='H')
            ]
            for category in categories:
                db.session.add(category)
        
        if not Allergen.query.first():
            allergens = [
                # 1. Cereali contenenti glutine
                Allergen(name_cn='含麸质谷物', name_it='Cereali contenenti glutine', icon='images/allergens/Gluten.jpg', 
                        description_cn='小麦、大麦、黑麦、燕麦等', 
                        description_it='Grano, orzo, segale, avena, ecc.'),
                
                # 2. Crostacei
                Allergen(name_cn='甲壳类', name_it='Crostacei', icon='images/allergens/Crustaceans.jpg', 
                        description_cn='虾、蟹、龙虾等', 
                        description_it='Gamberi, granchi, aragoste, ecc.'),
                
                # 3. Uova
                Allergen(name_cn='鸡蛋', name_it='Uova', icon='images/allergens/Eggs.jpg', 
                        description_cn='鸡蛋及其制品', 
                        description_it='Uova e derivati'),
                
                # 4. Pesce
                Allergen(name_cn='鱼类', name_it='Pesce', icon='images/allergens/Fish.jpg', 
                        description_cn='各种鱼类', 
                        description_it='Tutti i tipi di pesce'),
                
                # 5. Arachidi
                Allergen(name_cn='花生', name_it='Arachidi', icon='images/allergens/Peanuts.jpg', 
                        description_cn='花生及其制品', 
                        description_it='Arachidi e derivati'),
                
                # 6. Soia
                Allergen(name_cn='大豆', name_it='Soia', icon='images/allergens/Soya.jpg', 
                        description_cn='大豆及其制品', 
                        description_it='Soia e derivati'),
                
                # 7. Latte
                Allergen(name_cn='牛奶', name_it='Latte', icon='images/allergens/Milk.jpg', 
                        description_cn='牛奶及乳制品', 
                        description_it='Latte e latticini'),
                
                # 8. Frutta a guscio
                Allergen(name_cn='坚果', name_it='Frutta a guscio', icon='images/allergens/Tree_Nuts.jpg', 
                        description_cn='杏仁、榛子、核桃等', 
                        description_it='Mandorle, nocciole, noci, ecc.'),
                
                # 9. Sedano
                Allergen(name_cn='芹菜', name_it='Sedano', icon='images/allergens/Celery.jpg', 
                        description_cn='芹菜及其制品', 
                        description_it='Sedano e derivati'),
                
                # 10. Senape
                Allergen(name_cn='芥末', name_it='Senape', icon='images/allergens/Mustard.jpg', 
                        description_cn='芥末籽及其制品', 
                        description_it='Semi di senape e derivati'),
                
                # 11. Semi di sesamo
                Allergen(name_cn='芝麻', name_it='Semi di sesamo', icon='images/allergens/Sesame.jpg', 
                        description_cn='芝麻籽及其制品', 
                        description_it='Semi di sesamo e derivati'),
                
                # 12. Anidride solforosa e solfiti
                Allergen(name_cn='二氧化硫和亚硫酸盐', name_it='Anidride solforosa e solfiti', icon='images/allergens/Sulphites.jpg', 
                        description_cn='含量超过10 mg/kg', 
                        description_it='Concentrazione > 10 mg/kg'),
                
                # 13. Lupini
                Allergen(name_cn='羽扇豆', name_it='Lupini', icon='images/allergens/Lupin.jpg', 
                        description_cn='羽扇豆及其制品', 
                        description_it='Lupini e derivati'),
                
                # 14. Molluschi
                Allergen(name_cn='软体动物', name_it='Molluschi', icon='images/allergens/Molluscs.jpg', 
                        description_cn='贝类、鱿鱼、章鱼等', 
                        description_it='Cozze, vongole, calamari, ecc.')
            ]
            for allergen in allergens:
                db.session.add(allergen)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8081)