from flask import Flask
from routes.donor_routes import donor_bp
from routes.request_routes import request_bp
from routes.ai_routes import ai_bp

app = Flask(__name__)

app.register_blueprint(donor_bp)
app.register_blueprint(request_bp)
app.register_blueprint(ai_bp)

if __name__ == "__main__":
    app.run(debug=True)