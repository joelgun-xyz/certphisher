from flask import *
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/certphisher"
mongo = PyMongo(app)


@app.route('/')
def start():
    sites = mongo.db.sites.find({"checked_vt": "true"}).limit(25).sort("_id", -1)
    sites_count = mongo.db.sites.count_documents({"checked_vt": "true"})
    sites_critical_count = mongo.db.sites.count_documents({"checked_vt": "true","certphisher_score": { "$gt": 140}})
    sites_high_count = mongo.db.sites.count_documents({"checked_vt": "true","certphisher_score": { "$gte" : 90, "$lt": 140}})
    sites_medium_count = mongo.db.sites.count_documents({"checked_vt": "true","certphisher_score": { "$gte" : 80, "$lt": 90}})
    return render_template("index.html",
        sites=sites, sites_count = sites_count, sites_critical_count = sites_critical_count, sites_high_count = sites_high_count, sites_medium_count = sites_medium_count)

@app.route('/alltime')
def alltime():
        sites = mongo.db.sites.find({"checked_vt": "true"}).sort("_id", -1)
        sites_count = mongo.db.sites.count_documents({"checked_vt": "true"})
        return render_template("alltime.html",
                sites=sites, sites_count = sites_count)

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    stats = {
        'total': mongo.db.sites.count_documents({"checked_vt": "true"}),
        'critical': mongo.db.sites.count_documents({"checked_vt": "true", "certphisher_score": {"$gt": 140}}),
        'high': mongo.db.sites.count_documents({"checked_vt": "true", "certphisher_score": {"$gte": 90, "$lt": 140}}),
        'medium': mongo.db.sites.count_documents({"checked_vt": "true", "certphisher_score": {"$gte": 80, "$lt": 90}}),
        'ca_stats': {}
    }

    # Get CA distribution
    pipeline = [
        {"$match": {"checked_vt": "true"}},
        {"$group": {"_id": "$certificate_authority", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    ca_results = list(mongo.db.sites.aggregate(pipeline))
    stats['ca_stats'] = {item['_id']: item['count'] for item in ca_results}

    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
