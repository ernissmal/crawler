from flask import Blueprint, request, jsonify
from app.controllers.crawl_controller import CrawlController

routes = Blueprint("routes", __name__)

@routes.route("/crawl/domain", methods=["GET"])
def crawl_domain():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    result = CrawlController.crawl_domain(url)
    return jsonify(result)
