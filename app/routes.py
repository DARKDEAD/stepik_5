from flask import jsonify
from flask import make_response, redirect
from flask import render_template, session, request
from flask import url_for

from app.models import Category, Dish, User, Order
from app.models import register_client, add_new_order
from app.forms import UserCartForm, AuthForm
from app import app


def init_user():
    session['auth'] = {
        'login'    : False,
        'user_name': '',
        'user_mail': ''
    }


def set_user_session(name, mail):
    session['auth'] = {
        'login'    : True,
        'user_name': name,
        'user_mail': mail
    }


@app.route("/")
def render_index():
    # session.pop('cart')
    if session.get('cart') is None:
        session['cart'] = []

    if session.get('auth') is None:
        init_user()

    categories = Category.query.all()
    return render_template(
            "main.html",
            categories=categories,
            dishes=Dish,

    )


@app.route("/addtocart", methods=['POST', 'GET'])
def render_addtocart():
    s_cart = session.get('cart', [])
    if not request.form.get('id_dish') == '':
        id_dish = int(request.form.get('id_dish'))
        dish = Dish.query.filter(Dish.id == id_dish).first()

        s_cart.append({
            'id_dish': id_dish,
            'amount' : 1,
            'price'  : dish.price,
            'title'  : dish.title
        })
        session['cart'] = s_cart
        # s_cart = session.get('cart', {})

    sum_dish = 0
    for item in s_cart:
        sum_dish += item['price']

    resp = {'amount': len(s_cart), 'sum': sum_dish}
    return make_response(jsonify(resp), 200)


@app.route("/deldish", methods=['POST', 'GET'])
def render_deldish():
    id_dish = int(request.form.get('id_dish'))

    old_cart = session.pop('cart', None)
    s_cart = []
    no_one_find = True
    for dish in old_cart:
        if dish['id_dish'] == id_dish and no_one_find:
            no_one_find = False
            continue

        s_cart.append({
            'id_dish': dish['id_dish'],
            'amount' : 1,
            'price'  : dish['price'],
            'title'  : dish['title']
        })
    session['cart'] = s_cart

    resp = {"id" : id_dish,
            'url': render_template('base_list_dish.html')}

    return make_response(jsonify(resp), 200)


@app.route("/cart", methods=['POST', 'GET'])
def render_cart():
    form = UserCartForm()
    user = ''
    if request.method == 'POST':
        phone = form.phone.data
        if phone is None:
            form.phone.errors = tuple(list(["Заполните телефон."]))
            return render_template('cart.html', form=form, user=user)

        if session['auth']['login']:
            add_new_order(session.get('cart'), session.get('auth'), phone)
            session['cart'] = []
            return render_template('ordered.html')

        if form.validate_on_submit():
            add_new_order(session.get('cart'),
                          {
                              'user_mail': form.mail.data,
                              'address'  : form.address.data,
                          },
                          phone)
            session['cart'] = []
            return render_template('ordered.html')

    if session['auth']['login']:
        user = User.query.filter_by(mail=session['auth']['user_mail'])

    return render_template('cart.html', form=form, user=user)


@app.route("/logout")
def render_logout():
    init_user()
    return redirect(url_for('render_index'))


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    session['auth'] = {'user_mail': ''}
    form = AuthForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(mail=form.mail.data).first()

            if user and user.password_valid(form.password.data):
                set_user_session(name=user.name, mail=user.mail)

                return redirect(url_for('render_index'))
            else:
                form.password.errors.append("Не верный пароль.")
                form.mail.errors.append("Не верная почта.")

    return render_template('login.html', form=form)


@app.route("/register", methods=['POST', 'GET'])
def render_register():
    form = AuthForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            mail = form.mail.data
            password = form.password.data
            name = form.name.data

            if not User.query.filter_by(mail=mail).first() is None:
                session['auth'] = {'user_mail': mail}
                return render_template('login.html', form=form)

            if register_client(name, mail, password):
                set_user_session(name, mail)
                return redirect(url_for('render_index'))

    return render_template('register.html', form=form)


@app.route("/account")
def render_account():
    orders = Order.query.filter(Order.mail == session['auth']['user_mail']).order_by(Order.date.desc()).all()
    for order in orders:
        print (order.date)

    return render_template("account.html", orders=orders)
