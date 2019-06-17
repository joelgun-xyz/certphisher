from flask import *
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/certphisher"
mongo = PyMongo(app)


@app.route('/')
def start():
    sites = mongo.db.sites.find({"checked_vt": "true"}).limit(25).sort("_id", -1)
    sites_count = mongo.db.sites.find({"checked_vt": "true"}).count()
    sites_critical_count = mongo.db.sites.find({"checked_vt": "true","certphisher_score": { "$gt": 140}}).count()
    sites_high_count = mongo.db.sites.find({"checked_vt": "true","certphisher_score": { "$gte" : 90, "$lt": 140}}).count()
    sites_medium_count = mongo.db.sites.find({"checked_vt": "true","certphisher_score": { "$gte" : 80, "$lt": 90}}).count()
    return render_template("index.html",
        sites=sites, sites_count = sites_count, sites_critical_count = sites_critical_count, sites_high_count = sites_high_count, sites_medium_count = sites_medium_count)
@app.route('/alltime')
def alltime():
        sites = mongo.db.sites.find({"checked_vt": "true"}).sort("_id", -1)
        sites_count = mongo.db.sites.find({"checked_vt": "true"}).count()
        return render_template("alltime.html",
                sites=sites, sites_count = sites_count)