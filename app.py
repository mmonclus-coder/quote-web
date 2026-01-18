import os
import tempfile
from datetime import date, timedelta

from flask import Flask, render_template, request, send_file, redirect, url_for
from dotenv import load_dotenv

from db import init_db, next_quote_no, save_quote, load_quote

from quote_pdf import QuoteItem, render_quote_pdf, UNIT_PRICE

load_dotenv()

app = Flask(__name__)
init_db()   # runs on startup in Render too

def mmddyyyy(d: date) -> str:
    return d.strftime("%m/%d/%Y")

@app.get("/")
def form():
    return render_template("form.html", mode="new", quote=None)


@app.route("/generate", methods=["POST"])

existing_quote_no = (request.form.get("quote_no") or "").strip()

def generate():
    job_number = (request.form.get("job_number") or "").strip()

    descriptions = request.form.getlist("description[]")
    hours_list = request.form.getlist("hours[]")

    items = []
    for d, h in zip(descriptions, hours_list):
        d = (d or "").strip()
        if not d:
            continue
        try:
            hrs = float(h or 0)
        except ValueError:
            hrs = 0.0
        items.append(QuoteItem(description=d, estimated_hours=hrs))

    submitted = mmddyyyy(date.today())
    due = mmddyyyy(date.today() + timedelta(days=14))

    if existing_quote_no:
    quote_no_text = existing_quote_no
    else:
    n = next_quote_no()
    quote_no_text = f"S{n:03d}"


    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    render_quote_pdf(
        path,
        quote_no_text=quote_no_text,
        submitted_on=submitted,
        work_order=job_number,
        due_date=due,
        items=items,
        logo_path="static/logo.png",
    )

    total = sum(it.total_price for it in items)
    
    save_quote(
        quote_no=quote_no_text,
        rep=(request.form.get("rep") or "").strip(),
        work_order=job_number,
        due_date=due,
        submitted_on=submitted,
        unit_price=float(UNIT_PRICE),
        items=[{"description": it.description, "estimated_hours": it.estimated_hours} for it in items],
        total=float(total),
        )

    return send_file(
        path,
        as_attachment=True,
        download_name=f"Quote_{quote_no_text}.pdf",
        mimetype="application/pdf",
        max_age=0,
    )
    
    @app.get("/edit")
    def edit_lookup():
        return render_template("edit_lookup.html")
    
    @app.post("/edit")
    def edit_lookup_post():
        q = (request.form.get("quote_no") or "").strip()
        return redirect(url_for("edit_quote", quote_no=q))
    
    @app.get("/edit/<quote_no>")
    def edit_quote(quote_no):
        q = load_quote(quote_no)
        if not q:
            return f"Quote not found: {quote_no}", 404
        return render_template("form.html", mode="edit", quote=q)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
