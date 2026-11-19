from datetime import datetime
from flask import Flask, jsonify, request
import holidays
import pytz

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "World Time, Date & Holidays API",
        "endpoints": {
            "single_country": "/api/IN (or /api/US?year=2026)",
            "all_countries": "/api/all"
        }
    })

@app.route("/api/all")
def all_countries():
    data = {}
    supported = holidays.list_supported_countries(include_aliases=False)

    for code in sorted(supported.keys()):
        tz_list = pytz.country_timezones.get(code)
        if not tz_list:
            continue

        # Use the country's primary timezone
        now = datetime.now(pytz.timezone(tz_list[0]))
        country_holidays = holidays.country_holidays(code, years=now.year)
        today_holiday = country_holidays.get(now.date())

        data[code] = {
            "country": pytz.country_names.get(code, code),
            "timezone": tz_list[0],
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "is_holiday_today": bool(today_holiday),
            "today_holiday": today_holiday
        }

    return jsonify(data)

@app.route("/api/<country_code>")
def country_info(country_code):
    code = country_code.upper()
    tz_list = pytz.country_timezones.get(code)

    if not tz_list:
        return jsonify({"error": f"Invalid country code: {code}"}), 404

    year = request.args.get("year", default=datetime.now().year, type=int)

    # Current date & time across all timezones in the country
    times = []
    for tz_name in tz_list:
        now = datetime.now(pytz.timezone(tz_name))
        times.append({
            "timezone": tz_name,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S")
        })

    # Public holidays for the requested year
    try:
        country_holidays = holidays.country_holidays(code, years=year)
        holiday_list = [
            {"date": str(date), "name": name}
            for date, name in sorted(country_holidays.items())
        ]
    except NotImplementedError:
        holiday_list = []

    return jsonify({
        "country_code": code,
        "country_name": pytz.country_names.get(code, code),
        "times": times,
        "year": year,
        "holidays": holiday_list
    })