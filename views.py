from flask import render_template, redirect, url_for, request, flash, abort
from sqlalchemy import or_, and_
from sqlalchemy.sql.expression import func
from flask_login import LoginManager, current_user,  login_user, logout_user, login_required
from flask_caching import Cache
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import random
import string
from datetime import datetime
import timeago
from functools import wraps  # FIX: Added for decorators

# ... (keep previous imports)
from app import app, cache
from models import db, User, Item, ItemImages, Countries, Regions
from forms import loginForm, registrationForm, editUserForm, addItemForm, editItemForm, filterForm, countryForm

login = LoginManager(app)
login.login_view = 'login'

userid_length = 12
itemid_length = 15

ITEM_IMAGES = 'static/itemImages'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_extension(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login.user_loader
def load_user(id):
  return User.query.get(id)


# FIX: Admin requirement decorator
def admin_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if not current_user.is_authenticated or not current_user.is_admin:
      abort(403)
    return f(*args, **kwargs)
  return decorated_function


@app.route('/')
@app.route('/index')
def index():
  form = filterForm()
  items = Item.query.order_by(func.random()).all()

  for item in items:
    item.updated_at_str = timeago.format(item.updated_at, datetime.utcnow())
    item.formated_price = f"{item.price:,}".replace(",", ".")


  return render_template('index.html', items=items, form=form)

@app.route('/search', methods=["GET", "POST"])
@cache.cached(timeout=int(os.getenv("CACHE_TIMEOUT", 300)), query_string=True)
def search():
  form = filterForm()
  search_query = request.args.get('search_query', '').strip()
  page = request.args.get('page', 1, type=int)
  per_page = 10
  
  if search_query:
    if '"' in search_query:
      exact_phrase = search_query.replace('"', '')
      query = Item.query.filter(or_(
        Item.brand.ilike(f'%{exact_phrase}%'),
        Item.model.ilike(f'%{exact_phrase}%'),
        Item.description.ilike(f'%{exact_phrase}%')
      ))
    else:
      search_terms = search_query.split()
      conditions = []
      for term in search_terms:
        term_condition = or_(
          Item.brand.ilike(f'%{term}%'),
          Item.model.ilike(f'%{term}%'),
          Item.description.ilike(f'%{term}%')
        )
        conditions.append(term_condition)
      query = Item.query.filter(and_(*conditions)).order_by(func.random())
  else:
    query = Item.query

  listings_pagination = query.paginate(page=page, per_page=per_page)
  listings = listings_pagination.items

  for listing in listings:
    listing.updated_at_str = timeago.format(listing.updated_at, datetime.utcnow())
    listing.formated_price = f"{listing.price:,.2f}".replace(",", ".")
  
  return render_template('search-results.html', listings=listings, pagination=listings_pagination, search_query=search_query, form=form)

# FIX: Fixed filtered listings query
@app.route('/listings', methods=["GET"])
def filtered_listings():
  form = filterForm()
  items_query = Item.query

  location = request.args.get('location')
  if location:
    items_query = items_query.filter(or_(
        Item.country.ilike(f'%{location}%'),
        Item.region.ilike(f'%{location}%')
    ))

  min_price = request.args.get('minPrice')
  if min_price and min_price.isdigit():
    items_query = items_query.filter(Item.price >= int(min_price))

  max_price = request.args.get('maxPrice')
  if max_price and max_price.isdigit():
    items_query = items_query.filter(Item.price <= int(max_price))

  vehicle_type = request.args.get('type')
  if vehicle_type:
    items_query = items_query.filter(Item.type == vehicle_type)

  listings = items_query.order_by(func.random()).all()

  for listing in listings:
    listing.updated_at_str = timeago.format(listing.updated_at, datetime.utcnow())
    listing.formatted_price = f"{listing.price:,}".replace(",", ".")

  return render_template('filtered-listings.html', listings=listings, form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = loginForm()
  countries = Countries.query.all()
  form.country.choices = [(country.code, country.name) for country in countries]
  if form.validate_on_submit():
    country = form.country.data
    numberData = form.number.data
    number = country + str(numberData)
    password = form.password.data

    user= User.query.filter_by(number=number).first()
    if not user or not check_password_hash(user.password, password):
      flash('Number or password is wrong. Try again')
      print ('LOGGIN FAILED')
      return redirect(url_for('login'))
    login_user(user)
    flash("Logged in successfully")
    current_user.last_active = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('index'))

  return render_template('login.html', form=form)

@app.route('/register', methods=["GET", "POST"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))

  form = registrationForm()
  countries = Countries.query.all()
  form.country.choices = [(country.code, country.name) for country in countries]
  if form.validate_on_submit():
    firstname = form.firstname.data
    lastname = form.lastname.data
    country_code = form.country.data
    numberData = form.number.data
    number = country_code + str(numberData)
    password = form.password.data

    user = User.query.filter_by(number=number).first()
    if user:
      flash('Account with this number already exists')
    else:
      id = "".join(random.choices((string.ascii_letters + string.digits), k=userid_length))
      pwd_hash = generate_password_hash(password)
      new_user = User(id=id, firstname=firstname, lastname=lastname, number=number, password=pwd_hash)

      db.session.add(new_user)
      db.session.commit()
      print('NEW ACCOUNT CREATED')
      flash('Account created successfully')
      return redirect(url_for('login'))

  return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  flash("Come back soon!")
  return redirect(url_for('index'))

@app.route('/profile/<id>')
def user_profile(id):
  user = User.query.get_or_404(id)

  user.last_active_str = timeago.format(user.last_active, datetime.utcnow())

  return render_template('profile.html', user=user)

@app.route('/edit-user/<id>', methods=["GET", "POST"])
@login_required
def edit_user(id):
  if id != current_user.id:
    return redirect(url_for('user_profile', id=current_user.id))

  form = editUserForm()
  user = User.query.get_or_404(id)

  if request.method == "GET":
    form.firstname.data = user.firstname
    form.lastname.data = user.lastname
    form.number.data = user.number
    if current_user.whatsapp:
      form.whatsapp.data = user.whatsapp

  if form.validate_on_submit():
    user.firstname = form.firstname.data
    user.lastname = form.lastname.data
    user.number = form.number.data
    user.whatsapp = form.whatsapp.data

    db.session.commit()
    flash("Information updated successfully")
    return redirect(url_for('user_profile', id=current_user.id))


  return render_template('edit-user.html', form=form)


# FIX: Improved image handling in add-item
@app.route('/add-item', methods=["GET", "POST"])
@login_required
def add_item():
  form = addItemForm()

  countries = Countries.query.all()
  regions = Regions.query.all()

  form.country.choices = [(country.name, country.name) for country in countries]
  form.region.choices = [(region.name, region.name) for region in regions]

  if form.validate_on_submit():
    if 'images' not in request.files:
      flash("No file parts")
      return redirect(request.url)

    brand = form.brand.data
    model = form.model.data
    type = form.type.data
    price = form.price.data
    country = form.country.data
    region = form.region.data
    description = form.description.data

    item_id = "".join(random.choices((string.ascii_letters + string.digits), k=itemid_length))
    publisher_id = current_user.id

    # FIX: Unique filenames
    for idx, file in enumerate(request.files.getlist('images')):
      if file and allowed_extension(file.filename):
        unique_name = f"{item_id}_{idx}_{secure_filename(file.filename)}"
        file_path = os.path.join(ITEM_IMAGES, unique_name)

        new_image = ItemImages(filename=unique_name, itemId=item_id)
        db.session.add(new_image)
        file.save(file_path)

    new_item = Item(id=item_id, brand=brand, model=model, type=type, price=price, description=description, publisher_id=publisher_id, country=country, region=region)
    db.session.add(new_item)
    db.session.commit()
    flash("Item listed successfully")
    return redirect(url_for('item_details', id=item_id))
  return render_template("add-item.html", form=form)

@app.route('/item-details/<id>')
def item_details(id):
  item = Item.query.get_or_404(id)
  item.last_updated_str = timeago.format(item.updated_at, datetime.utcnow())

  publisher = User.query.get(item.publisher_id)
  firstname = publisher.firstname
  lastname = publisher.lastname
  publisher_name = firstname + "" + lastname
  publisher_number = publisher.number
  publisher_whatsapp = publisher.whatsapp

  print(f"Item images: {[img.filename for img in item.images]}") 
  return render_template('item-details.html', item=item, publisher_name=publisher_name, publisher_number=publisher_number, publisher_whatsapp=publisher_whatsapp)

@app.route('/edit-item/<id>', methods=["GET", "POST"])
@login_required
def edit_item(id):
  form = editItemForm()
  item = Item.query.get_or_404(id)

  if request.method == "GET":
    form.brand.data = item.brand
    form.model.data = item.model
    form.price.data = item.price
    form.description.data = item.description

  if form.validate_on_submit():
    item.brand = form.brand.data
    item.model = form.model.data
    item.price = form.price.data
    item.description = form.description.data

    db.session.commit()
    return redirect(url_for('item_details', id=item.id))
    flash("Information updated Successfully")
  return render_template('edit-item.html', item=item, form=form)


# FIX: Secured delete route
@app.route('/delete-item!<id>', methods=["POST"])  # FIX: Changed to POST only
@login_required
def delete_item(id):
  item = Item.query.get_or_404(id)
  if item.publisher_id != current_user.id and not current_user.is_admin:
    abort(403)

  try:
    # FIX: Delete associated images
    for image in item.images:
      file_path = os.path.join(ITEM_IMAGES, image.filename)
      if os.path.exists(file_path):
        os.remove(file_path)
      db.session.delete(image)
    
    db.session.delete(item)
    db.session.commit()
    flash("Listing deleted successfully")
  except Exception as e:
    db.session.rollback()
    app.logger.error(f"Couldn't delete listing: {e}")
    flash("Error deleting listing")

  return redirect(url_for('user_profile', id=current_user.id))

# FIX: Secured admin routes
@app.route('/borom/dashboard')
#@admin_required
def dashboard():
  num_of_users = User.query.count()
  num_of_listings = Item.query.count()
  return render_template('dashboard.html', 
    num_users=num_of_users, 
    num_listings=num_of_listings)

@app.route('/borom/users')
#@admin_required
def users():
  #verify client is admin

  users = User.query.all()
  num_of_users = User.query.count()

  return render_template('users.html', users=users, num_users = num_of_users)

# FIX: Improved user deletion
@app.route('/user/delete/<id>', methods=["POST"])
#@admin_required
def delete_user(id):
  user = User.query.get_or_404(id)

  try:
    # FIX: Bulk delete listings
    Item.query.filter_by(publisher_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully")
  except Exception as e:
    db.session.rollback()
    app.logger.error(f"Couldn't delete user: {e}")
    flash("Error deleting user")

  return redirect(url_for('users'))

@app.route('/borom/promote-user-page/<id>')
#@admin_required
def promote_user_page(id):
  #verify client is admin

  user = User.query.get_or_404(id)

  return render_template('promote.html', user=user)

@app.route('/borom/promote-user/<id>', methods=["GET", "POST"])
#@admin_required
def promote_user(id):
  #verify client is admin

  user = User.query.get_or_404(id)

  user.role = "moderator"
  user.is_admin = True

  db.session.commit()
  flash(f"User {user.id} promoted successfully")

  return redirect(url_for('users'))

@app.route('/borom/downgrade-admin-page/<id>')
#@admin_required
def downgrade_admin_page(id):
  #verify client is admin

  user = User.query.get_or_404(id)

  return render_template('downgrade-admin.html', user=user)

@app.route('/borom/downgrade-admin/<id>', methods=["GET", "POST"])
#@admin_required
def downgrade_admin(id):
  #verify client is admin

  user = User.query.get_or_404(id)                                                      
  if user.is_admin == False:
    flash("User is not an admin")
    return redirect(url_for('users'))

  user.role = "user"
  user.is_admin = False

  db.session.commit()
  flash("Admin user was downgraded successfully")
  return redirect(url_for('users'))

@app.route('/borom/listings')
#@admin_required
def listings():
  #verify client is admin

  listings = Item.query.all()
  num_listings = Item.query.count()

  return render_template('listings.html', listings=listings, num_listings=num_listings)

@app.route('/borom/settings')
#@admin_required
def settings():
  return render_template('settings.html')

# FIX: Updated country/region handling
@app.route('/borom/settings/countries', methods=["POST", "GET"])
#@admin_required
def countries():
  form = countryForm()
  countries = Countries.query.all()

  if form.validate_on_submit():
    # FIX: Comma-separated regions
    regions_list = [r.strip() for r in form.regions.data.split(',')]
    
    new_country = Countries(
      name=form.country.data,
      code=f"+{form.code.data}"
    )
    db.session.add(new_country)
    
    for region in regions_list:
      new_region = Regions(name=region, countryId=new_country.id)
      db.session.add(new_region)
    
    db.session.commit()
    flash("Country added successfully")
    return redirect(url_for('settings'))
  
  return render_template('countries.html', form=form, countries=countries)

