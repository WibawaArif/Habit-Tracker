from flask import Blueprint, redirect, render_template, request, url_for, current_app
import datetime as dt
import uuid

import os

template_dir = os.path.abspath('template_fs')


pages = Blueprint("habits", __name__, template_folder=template_dir, static_folder="static")

@pages.context_processor
def add_calc_date_range():  
    def date_range(start: dt.datetime):
        dates = [start + dt.timedelta(days=each) for each in range(-3, 4)]
        return dates
    
    return {"date_range": date_range}

def today_at_midnight():
    today = dt.datetime.today()
    return dt.datetime(today.year, today.month, today.day)

@pages.route('/')
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = dt.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()
        
    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})
    completions = [ 
        habit['habit']
        for habit in current_app.db.completions.find({"date": selected_date})
    ]
    return render_template('index.html', title='Habit Tracker | Home', habits=habits_on_date, selected_date=selected_date, completions=completions)

@pages.route('/add', methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()
    
    if request.form:
        new_habit = request.form.get("habit")
        if new_habit != None:
            current_app.db.habits.insert_one({"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")})
    return render_template('add_habit.html', title="Habit Tracker | Add Habit", selected_date=today)


@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    date = dt.datetime.fromisoformat(date_string)
    habit = request.form.get("habitId")
    current_app.db.completions.insert_one({"date": date, "habit": habit })
    
    return redirect(url_for("habits.index", date=date_string))
