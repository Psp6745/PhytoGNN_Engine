# app.py
from flask import Flask, render_template
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure critical directories exist
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['MODEL_DIR'], exist_ok=True)

    # Register Blueprint Routes
    from routes.home import home_bp
    from routes.plants import plants_bp
    from routes.chemicals import chemicals_bp
    from routes.proteins import proteins_bp
    from routes.predictions import predictions_bp
    from routes.analytics import analytics_bp
    from routes.graph import graph_bp
    from routes.chatbot import chatbot_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(plants_bp)
    app.register_blueprint(chemicals_bp)
    app.register_blueprint(proteins_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(graph_bp)
    app.register_blueprint(chatbot_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', main_content="Page Not Found"), 404

    return app

# Create Flask app for Gunicorn / Render
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)