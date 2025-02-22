import pyrebase
from constants import FIREBASE_CONFIG

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
db = firebase.database()

def get_fb_reminder():
    """Fetches the reminder time from Firebase"""
    return db.child("reminder").get().val()

async def edit_fb_reminder(new_time):
    """Edits the reminder time in Firebase"""
    db.child("reminder").set(new_time)

def get_fb_roster():
    """Fetches the roster from Firebase"""
    return db.child("roster").get().val()

async def edit_fb_roster(day, new_roster):
    """Edits the roster in Firebase"""
    db.child("roster").child(day).set(new_roster)