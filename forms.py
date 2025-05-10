from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, EqualTo

#Vehicule types
#vehicle_types = [("car", "Car"), ("suv", "Suv"), ("motocycle", "Motorcycle"), ("truck", "Truck"), ("van", "Van", ("bus", "Bus"), ("other", "Other"))]

class registrationForm(FlaskForm):
  firstname = StringField("Firstname", validators=[DataRequired()])
  lastname = StringField("Lastname", validators=[DataRequired()])
  country = SelectField("Country", choices=[], validators=[DataRequired()])
  number = IntegerField("Phone Number", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  confirm = PasswordField("Confirm Password", validators=[EqualTo('password')])
  submit = SubmitField("Register")

class loginForm(FlaskForm):
  country = SelectField("Country",choices=[], validators=[DataRequired()])
  number = IntegerField("Phone Number", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  submit = SubmitField("Login")

class editUserForm(FlaskForm):
  firstname = StringField("Firstname", validators=[DataRequired()])
  lastname = StringField("Lastname", validators=[DataRequired()])
  number = IntegerField("Phone Number", validators=[DataRequired()])
  whatsapp = IntegerField("Whatsapp Number", validators=[DataRequired()])
  submit = SubmitField("Save Info")

class addItemForm(FlaskForm):
  brand = StringField("Brand", validators=[DataRequired()])
  model = StringField("Model", validators=[DataRequired()])
  type = SelectField("Vehicle type", choices=[("car", "Car"), ("suv", "Suv"), ("motocycle", "Motorcycle"), ("truck", "Truck"), ("van", "Van"), ("bus", "Bus"), ("other", "Other")], validators=[DataRequired()])
  price = IntegerField("Price", validators=[DataRequired()])
  country = SelectField("Country", choices=[], validators=[DataRequired()])
  region = SelectField("Region", choices=[], validators=[DataRequired()])
  description = TextAreaField("Description", validators=[DataRequired()])
  submit = SubmitField("Post")

class editItemForm(FlaskForm):
  brand = StringField("Brand", validators=[DataRequired()])
  model = StringField("Model", validators=[DataRequired()])
  price = IntegerField("Price", validators=[DataRequired()])
  description = TextAreaField("Description", validators=[DataRequired()])
  submit = SubmitField("Update Information")

class filterForm(FlaskForm):
  type = SelectField("Vehicle type", choices=[("car", "Car"), ("suv", "Suv"), ("motocycle", "Motorcycle"), ("truck", "Truck"), ("van", "Van"), ("bus", "Bus"), ("other", "Other")], validators=[DataRequired()])

class countryForm(FlaskForm):
  country = StringField("Country Name", validators=[DataRequired()])
  code = IntegerField("Country code", validators=[DataRequired()])
  regions = TextAreaField("Regions", validators=[DataRequired()])
  submit = SubmitField("Add Country")
