import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration for Anoma Analytics"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'anoma-analytics-production-key-2025')
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///anoma_analytics_production.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # CORS settings
    CORS_ORIGINS = ["*"]  # Allow all origins for now
    
    # Anoma network settings
    ANOMA_RPC_URL = os.environ.get('ANOMA_RPC_URL', 'http://localhost:26657')
    ANOMA_WEBSOCKET_URL = os.environ.get('ANOMA_WEBSOCKET_URL', 'ws://localhost:26657/websocket')
    ANOMA_INDEXING_URL = os.environ.get('ANOMA_INDEXING_URL', 'http://localhost:8080')
    
    # Data sync settings - REAL DATA BY DEFAULT
    ENABLE_REAL_DATA = os.environ.get('ENABLE_REAL_DATA', 'true').lower() == 'true'  # TRUE by default
    SYNC_INTERVAL = int(os.environ.get('SYNC_INTERVAL', '5'))  # 5 seconds for real-time updates
    
    # API settings
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '1000 per hour')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    @staticmethod
    def init_app(app):
        """Initialize app with production settings"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Setup logging
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/anoma_analytics.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Anoma Analytics startup')

class DevelopmentConfig:
    """Development configuration"""
    
    SECRET_KEY = 'dev-key'
    DEBUG = True
    TESTING = False
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///anoma_analytics_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    CORS_ORIGINS = ["*"]
    
    # Use simulated data in development
    ENABLE_REAL_DATA = False
    SYNC_INTERVAL = 5
    
    LOG_LEVEL = 'DEBUG'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

