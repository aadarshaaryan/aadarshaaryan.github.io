from flask import Blueprint, render_template, redirect, flash, url_for, jsonify
import sqlite3

main_bp = Blueprint("main", __name__)
DB_NAME = "database.db"

@main_bp.route('/')
def home():
    return render_template('main/index.html')

@main_bp.route('/contacts')
def contacts():
    return render_template('navs/contacts.html')

@main_bp.route('/unavaialable-user')
def unavailable_user():
    return render_template('extra/blocked_user.html')
