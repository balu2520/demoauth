import requests
import platform
import datetime
import time
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from user_agents import parse

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://root:welcome123@localhost:3306/users"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    login_timestamp = db.Column(db.DateTime, nullable=False)
    round_trip_time_ms = db.Column(db.Float, nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    asn = db.Column(db.String(50), nullable=False)
    org = db.Column(db.String(50), nullable=False)
    browser_version = db.Column(db.String(50), nullable=False)
    os_name = db.Column(db.String(50), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)

    def __init__(
        self,
        username,
        password,
        email,
        login_timestamp,
        round_trip_time_ms,
        ip_address,
        country,
        region,
        city,
        asn,
        org,
        browser_version,
        os_name,
        device_type,
    ):
        self.username = username
        self.password = password
        self.email = email
        self.login_timestamp = login_timestamp
        self.round_trip_time_ms = round_trip_time_ms
        self.ip_address = ip_address
        self.country = country
        self.region = region
        self.city = city
        self.asn = asn
        self.org = org
        self.browser_version = browser_version
        self.os_name = os_name
        self.device_type = device_type


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]

    existing_user = Users.query.filter_by(username=username).first()
    if existing_user:
        return jsonify(message="Username already exists")

    existing_email = Users.query.filter_by(email=email).first()
    if existing_email:
        return jsonify(message="Email already exists")

    auth_data = capture_authentication_data()

    new_user = Users(
        username=username,
        password=password,
        email=email,
        login_timestamp=auth_data["login_timestamp"],
        round_trip_time_ms=auth_data["round_trip_time_ms"],
        ip_address=auth_data["ip_address"],
        country=auth_data["country"],
        region=auth_data["region"],
        city=auth_data["city"],
        asn=auth_data["asn"],
        org=auth_data["org"],
        browser_version=auth_data["browser_version"],
        os_name=auth_data["os_name"],
        device_type=auth_data["device_type"],
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(message="Registration successful")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = Users.query.filter_by(
        username=username,
        password=password,
    ).first()
    if user:
        auth_data = capture_authentication_data()
        changed_fields = []

        if user.ip_address != auth_data["ip_address"]:
            changed_fields.append("IP Address")
        if user.country != auth_data["country"]:
            changed_fields.append("Country")
        if user.region != auth_data["region"]:
            changed_fields.append("Region")
        if user.city != auth_data["city"]:
            changed_fields.append("City")
        if user.asn != auth_data["asn"]:
            changed_fields.append("ASN")
        if user.org != auth_data["org"]:
            changed_fields.append("Organization")
        if user.browser_version != auth_data["browser_version"]:
            changed_fields.append("Browser Version")
        if user.os_name != auth_data["os_name"]:
            changed_fields.append("OS Name")
        if user.device_type != auth_data["device_type"]:
            changed_fields.append("Device Type")

        if len(changed_fields) == 0:
            return jsonify(message="Login successful")
        else:
            return jsonify(
                message="Login failed, because the following fields have changed: {}".format(
                    ", ".join(changed_fields)
                )
            )
    else:
        return jsonify(message="Login failed. Username or password incorrect.")


def capture_authentication_data():
    login_timestamp = datetime.datetime.now()
    round_trip_time_ms = capture_round_trip_time()
    ip_info = capture_ip_info()
    user_agent = request.headers.get("User-Agent")
    browser_version = get_browser_name(user_agent)
    os_name = platform.system()
    device_type = get_device_type(request.headers.get("User-Agent"))

    authentication_data = {
        "login_timestamp": login_timestamp,
        "round_trip_time_ms": round_trip_time_ms,
        "ip_address": ip_info["ip"],
        "country": ip_info["country"],
        "region": ip_info["region"],
        "city": ip_info["city"],
        "asn": ip_info["asn"],
        "org": ip_info["org"],
        "browser_version": browser_version,
        "os_name": os_name,
        "device_type": device_type,
    }
    return authentication_data


def capture_round_trip_time():
    start_time = time.time()
    time.sleep(0.5)
    end_time = time.time()
    round_trip_time_ms = (end_time - start_time) * 1000
    return round_trip_time_ms


def capture_ip_info():
    ip_info = requests.get("https://ipapi.co/json").json()
    return {
        "ip": ip_info["ip"],
        "country": ip_info["country"],
        "region": ip_info["region"],
        "city": ip_info["city"],
        "asn": ip_info["asn"],
        "org": ip_info["org"],
    }


def get_browser_name(user_agent):
    ua = parse(user_agent)

    if ua.is_bot:
        return "Bot"
    elif ua.is_mobile:
        return "Mobile"
    elif ua.is_tablet:
        return "Tablet"
    else:
        return ua.browser.family


def get_device_type(user_agent):
    from user_agents import parse

    user_agent = parse(user_agent)

    if user_agent.is_mobile:
        return "Mobile"
    elif user_agent.is_tablet:
        return "Tablet"
    elif user_agent.is_pc:
        return "Desktop"
    else:
        return "Unknown"


if __name__ == "__main__":
    app.run(host="192.168.2.41", port=5000)
