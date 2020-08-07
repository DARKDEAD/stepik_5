from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from app import db

dishes_in_order = db.Table(
    "dishes_in_order",
    db.Column("dish", db.Integer, db.ForeignKey("dishes.id")),
    db.Column("order", db.Integer, db.ForeignKey("orders.id")),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    mail = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))

    orders_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    @property
    def password(self):
        # Запретим прямое обращение к паролю
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
        # Устанавливаем пароль через этот метод
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        # Проверяем пароль через этот метод
        # Функция check_password_hash превращает password в хеш и сравнивает с хранимым
        return check_password_hash(self.password_hash, password)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    sum = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50),)
    address = db.Column(db.String(255),)
    mail = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

    dishes = db.relationship("Dish", secondary=dishes_in_order, back_populates="orders")


class Dish(db.Model):
    __tablename__ = "dishes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(255), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    categories = db.relationship("Category", back_populates="dish")

    orders = db.relationship(
        "Order", secondary=dishes_in_order, back_populates="dishes"
    )


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)

    dish = db.relationship("Dish", back_populates="categories")


def register_client(name, mail, password):
    client = User()
    client.password = password
    client.mail = mail
    client.name = name

    db.session.add(client)
    db.session.commit()
    return True


def add_new_order(dishes, client, phone):
    sum_dish = 0
    for item in dishes:
        sum_dish += item["price"]

    order = Order()
    user = User.query.filter_by(mail=client["user_mail"]).first()
    if user is not None:
        order.mail = user.mail
        order.address = user.address
    else:
        order.mail = client["user_mail"]
        order.address = client["address"]

    order.date = datetime.date.today()
    order.sum = sum_dish
    order.status = "new"
    order.phone = phone
    # db.session.commit()

    for d in dishes:
        dish = Dish.query.filter_by(id=d["id_dish"]).first()
        dish.orders.append(order)
        db.session.add(dish)

    db.session.add(order)
    db.session.commit()
