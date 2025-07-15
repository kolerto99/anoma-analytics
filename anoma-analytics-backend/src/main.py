import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import logging

# Import models and services
from src.models.anoma_models import db
from src.routes.user import user_bp
from src.routes.analytics import analytics_bp
from src.services.data_simulator import AnomaDataSimulator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='production'):
    """Create Flask application with specified configuration"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load basic configuration
    app.config['SECRET_KEY'] = 'anoma-analytics-production-2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'anoma_analytics_production.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # SIMULATION MODE FOR DEPLOYMENT
    app.config['ENABLE_REAL_DATA'] = False
    app.config['SYNC_INTERVAL'] = 5  # 5 seconds for real-time updates
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=["*"])
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Create database tables
    with app.app_context():
        # Ensure database directory exists
        db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        os.makedirs(db_dir, exist_ok=True)
        
        # Create tables
        db.create_all()
        
        # Initialize with simulated data
        simulator = AnomaDataSimulator()
        simulator.populate_database()
        logger.info("Database initialized with simulated data")
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Anoma Analytics API',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

