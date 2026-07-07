from flask import Blueprint, render_template, session, flash, redirect, url_for

hackathons_bp = Blueprint("hackathons", __name__)

@hackathons_bp.route("/built-for-impact")
def hackathon_1():
    return render_template("hackathons/built-for-impact.html")