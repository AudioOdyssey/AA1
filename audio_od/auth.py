from audio_od import app


def authentication_required(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        remember = request.cookies.get('remember_')
        if remember is None:
            token = session.get('token')
            if token is None or decode_auth_token(token) == 0:
                return redirect(url_for('session_new'))
            else:
                return func(*args, **kwargs)
        else:
            uid = decode_auth_token(remember)
            if uid == 'Invalid token. please log in again' or uid == 0 or uid == "Signature expired. Please log in again.":
                return redirect(url_for('session_new'))
            return func(*args, **kwargs)
    return func_wrapper



@app.route("/user/new", methods=['GET', 'POST'])
@check_header
def user_new():  # fix later
    if request.method == "POST":
        details = request.form
        username = details['username']
        raw_password = details['password']
        if len(raw_password) < 8:
            return render_template("user/new.html", error="Please enter a password greater than 8 characters.")
        email = details['email_address']
        if not isValidEmail(email):
            return render_template("user/new.html", error="Invalid email")
        gender = int(details['gender'])
        country_of_origin = (details.get('country_of_origin'))
        profession = details['profession']
        disabilities = details.get('disabilities')
        if disabilities is None:
            disabilities_bool = 0
        else:
            disabilities_bool = 1
        language = int(details['language-id'])
        first_name = details['first_name']
        last_name = details['last_name']
        date_of_birth = datetime.strptime(
            details['birth-year'] + "-" + details['birth-month'] + "-" + details['birth-day'], '%Y-%m-%d')
        usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin,
                   profession_input=profession, disabilities_input=disabilities_bool, date_of_birth_input=date_of_birth,
                   first_name_input=first_name, last_name_input=last_name, language=language)
        result = usr.add_to_server()
        if result==-1:
            return render_template("user/new.html", error="Username already in use")
        elif result==-2:
            return render_template("user/new.html", error="Email already in use")
        else:
            return redirect(url_for("home"))
    return render_template("user/new.html")

    
@app.route("/app/user/new", methods=['POST', 'GET'])
def app_user_new():
    result = {}
    if request.method == "POST":
        details = request.get_json(force=True)
    return make_response(sign_up(details))
    

def sign_up(details_dict):
    username = details_dict['username']
    raw_password = details_dict['password']
    email = details_dict['email_address']
    gender = int(details_dict['gender'])
    country_of_origin = details_dict['country_of_origin']
    profession = details_dict['profession']
    disabilities = bool(details_dict['disabilities'])
    if disabilities:
        disabilities_bool = 1
    else:
        disabilities_bool = 0
    language = int(details_dict['language_id'])
    first_name = details_dict['first_name']
    last_name = details_dict['last_name']
    # date_of_birth = datetime.strptime(details_dict['date_of_birth'], '%Y-%m-%d')
    usr = User(username, raw_password, email_input=email, gender_input=gender, country_of_origin_input=country_of_origin,
               profession_input=profession, disabilities_input=disabilities_bool,
               first_name_input=first_name, last_name_input=last_name, language=language)
    result=usr.add_to_server()
    if result==-1:
        return json.dumps({"message" : "username already exists"})
    elif result==-2:
        return json.dumps({"message" : "email already in use"})
    else:
        cur = datetime.utcnow()
        exp = datetime.utcnow() + timedelta(days=30)
        return json.dumps({"token" : encode_auth_token(result, cur, exp), "message": "success"})


