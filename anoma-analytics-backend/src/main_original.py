import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import asyncio
import threading
import logging

# Import models and services
from src.models.anoma_models import db
from src.routes.user import user_bp
from src.routes.analytics import analytics_bp
from src.services.data_simulator import AnomaDataSimulator
from src.services.anoma_client import AnomaConfig
from src.services.data_sync import start_data_sync
from src.config.production import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='production'):
    """Create Flask application with specified configuration"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Override with environment-specific settings
    app.config['SECRET_KEY'] = 'anoma-analytics-production-2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'anoma_analytics_production.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # REAL DATA BY DEFAULT - NO SIMULATION
    app.config['ENABLE_REAL_DATA'] = True
    app.config['SYNC_INTERVAL'] = 5  # 5 seconds for real-time updates
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=["*"])
    
    # Initialize SocketIO for real-time updates
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        logger=True,
        engineio_logger=False
    )
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
    return app, socketio

app, socketio = create_app()

# Global variables for real-time data sync
data_sync_thread = None
is_syncing = False

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket client connection"""
    logger.info(f"Client connected for real-time updates")
    
@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket client disconnection"""
    logger.info(f"Client disconnected from real-time updates")

@app.route('/api/init-data', methods=['POST'])
def init_data():
    """Initialize database with REAL Anoma data (not simulation)"""
    global data_sync_thread, is_syncing
    
    try:
        enable_real_data = app.config.get('ENABLE_REAL_DATA', True)
        
        if enable_real_data and not is_syncing:
            # Start real-time data synchronization with Anoma network
            logger.info("🚀 Starting REAL-TIME data sync with Anoma network...")
            
            # Create Anoma configuration
            anoma_config = AnomaConfig(
                rpc_url=app.config.get('ANOMA_RPC_URL', 'http://localhost:26657'),
                websocket_url=app.config.get('ANOMA_WEBSOCKET_URL', 'ws://localhost:26657/websocket'),
                indexing_url=app.config.get('ANOMA_INDEXING_URL', 'http://localhost:8080')
            )
            
            # Start data sync in background thread
            def start_sync():
                global is_syncing
                is_syncing = True
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    logger.info("🔄 Connecting to Anoma network for real-time data...")
                    loop.run_until_complete(start_data_sync(anoma_config))
                except Exception as e:
                    logger.error(f"❌ Error in real-time data sync: {e}")
                    # Fallback to simulation if real data fails
                    logger.info("⚠️ Falling back to simulated data...")
                    with app.app_context():
                        simulator = AnomaDataSimulator()
                        simulator.populate_database()
                finally:
                    loop.close()
                    is_syncing = False
                    
            data_sync_thread = threading.Thread(target=start_sync, daemon=True)
            data_sync_thread.start()
            
            return jsonify({
                'success': True,
                'message': '🚀 REAL-TIME data sync with Anoma network started!',
                'data_source': 'anoma_network_realtime',
                'config': {
                    'rpc_url': anoma_config.rpc_url,
                    'indexing_url': anoma_config.indexing_url,
                    'sync_interval': app.config.get('SYNC_INTERVAL', 5),
                    'websocket_enabled': True
                }
            })
        elif is_syncing:
            return jsonify({
                'success': True,
                'message': '✅ Real-time data sync already running',
                'data_source': 'anoma_network_realtime'
            })
        else:
            # Fallback to simulated data only for development/testing
            logger.warning("⚠️ Using simulated data (development mode only)")
            simulator = AnomaDataSimulator()
            result = simulator.populate_database()
            
            return jsonify({
                'success': True,
                'message': '⚠️ Using simulated data (development mode)',
                'data_source': 'simulation',
                'data': result
            })
            
    except Exception as e:
        logger.error(f"❌ Error initializing data: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '❌ Failed to initialize real-time data. Check Anoma network connection.'
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current application configuration"""
    return jsonify({
        'data_source': 'anoma_network_realtime' if app.config.get('ENABLE_REAL_DATA', True) else 'simulation',
        'real_time_enabled': True,
        'sync_interval': app.config.get('SYNC_INTERVAL', 5),
        'websocket_enabled': True,
        'anoma_config': {
            'rpc_url': app.config.get('ANOMA_RPC_URL', 'http://localhost:26657'),
            'indexing_url': app.config.get('ANOMA_INDEXING_URL', 'http://localhost:8080')
        },
        'status': 'syncing' if is_syncing else 'ready'
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get real-time sync status"""
    return jsonify({
        'is_syncing': is_syncing,
        'data_source': 'anoma_network_realtime' if is_syncing else 'simulation',
        'message': '🔄 Syncing real-time data from Anoma network' if is_syncing else '⏸️ Not syncing'
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    logger.info("🚀 Starting Anoma Analytics with REAL-TIME data support")
    
    # Auto-initialize with real data on startup
    with app.app_context():
        try:
            # Trigger real-time data initialization
            import requests
            import time
            time.sleep(2)  # Wait for server to start
            requests.post('http://localhost:5000/api/init-data', timeout=5)
            logger.info("✅ Auto-initialized with real-time Anoma data")
        except Exception as e:
            logger.warning(f"⚠️ Could not auto-initialize data: {e}")
    
    # Run with SocketIO support for real-time updates
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

