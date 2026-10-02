from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Expense
from datetime import date, datetime
from sqlalchemy import func

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATABASE_PATH = BASE_DIR / "database"

app = Flask(__name__, template_folder=str(FRONTEND_DIR / "templates"), static_folder=str(FRONTEND_DIR / "static"))
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Education", "Entertainment", "Other"]

with app.app_context():
    db.create_all()

@app.template_filter("currency")
def currency(value):
    return f"₹{value:,.2f}"

@app.route("/")
def dashboard():
    expenses = Expense.query.order_by(Expense.spent_on.desc(), Expense.id.desc()).limit(8).all()
    total = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).scalar()
    today_total = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.spent_on == date.today()
    ).scalar()
    month_total = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.spent_on >= date.today().replace(day=1)
    ).scalar()
    category_rows = db.session.query(
        Expense.category, func.sum(Expense.amount)
    ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total=total,
        today_total=today_total,
        month_total=month_total,
        category_rows=category_rows,
        categories=CATEGORIES,
        today=date.today().isoformat()
    )

@app.route("/expenses")
def expenses():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    month = request.args.get("month", "").strip()

    query = Expense.query
    if q:
        query = query.filter(
            db.or_(Expense.title.ilike(f"%{q}%"), Expense.notes.ilike(f"%{q}%"))
        )
    if category:
        query = query.filter_by(category=category)
    if month:
        try:
            start = datetime.strptime(month, "%Y-%m").date()
            end = date(start.year + (start.month == 12), 1 if start.month == 12 else start.month + 1, 1)
            query = query.filter(Expense.spent_on >= start, Expense.spent_on < end)
        except ValueError:
            pass

    items = query.order_by(Expense.spent_on.desc(), Expense.id.desc()).all()
    return render_template("expenses.html", expenses=items, categories=CATEGORIES,
                           q=q, category=category, month=month)

@app.route("/add", methods=["POST"])
def add_expense():
    try:
        amount = float(request.form["amount"])
        if amount <= 0:
            raise ValueError
        spent_on = datetime.strptime(request.form["spent_on"], "%Y-%m-%d").date()
        expense = Expense(
            title=request.form["title"].strip(),
            amount=amount,
            category=request.form["category"],
            spent_on=spent_on,
            notes=request.form.get("notes", "").strip()
        )
        if not expense.title:
            raise ValueError
        db.session.add(expense)
        db.session.commit()
        flash("Expense added successfully.", "success")
    except (ValueError, KeyError):
        flash("Please enter valid expense details.", "error")
    return redirect(request.referrer or url_for("dashboard"))

@app.post("/delete/<int:expense_id>")
def delete_expense(expense_id):
    expense = db.get_or_404(Expense, expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(request.referrer or url_for("expenses"))

@app.get("/api/summary")
def summary():
    rows = db.session.query(Expense.category, func.sum(Expense.amount)).group_by(Expense.category).all()
    return jsonify({"labels": [r[0] for r in rows], "values": [float(r[1]) for r in rows]})

if __name__ == "__main__":
    app.run(debug=True)
