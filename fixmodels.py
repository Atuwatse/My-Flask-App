from models import User

users = User.query.all()

with app.app_context():
  for user in users:
    user_number = user.number
    number = '+221' + str(user_number)
    user.number = number
    db.session.commit()
