import os
import tempfile
from datetime import date, timedelta

from flask import Flask, render_template, request, send_file

from db import init_db, next_quote_no
from quote_pdf import QuoteItem, render_quote_pdf

app = Flask(__name__)

def mmddyyyy(d: date) -> str:
    return d.strftime("%m/%d/%Y")

@app.route("/", methods=["GET"])
def form():
    return render_template("form.html")

@app.route("/generate", methods=["POST"])
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

    return send_file(
        path,
        as_attachment=True,
        download_name=f"Quote_{quote_no_text}.pdf",
        mimetype="application/pdf",
        max_age=0,
    )

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
