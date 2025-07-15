import asyncio
import json
import logging
from datetime import datetime
from flask import Flask
from flask_socketio import SocketIO, emit, disconnect
from typing import Dict, List, Any
from src.models.anoma_models import (
    db, Resource, Transaction, Intent, Block, NetworkStats
)

logger = logging.getLogger(__name__)

class WebSocketService:
    """WebSocket service for real-time data updates"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.socketio = None
        self.connected_clients = set()
        self.is_running = False
        
    def init_app(self, app: Flask):
        """Initialize WebSocket service with Flask app"""
        self.app = app
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
        
        # Register event handlers
        self.register_handlers()
        
    def register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid if 'request' in globals() else 'unknown'
            self.connected_clients.add(client_id)
            logger.info(f"Client connected: {client_id}")
            
            # Send initial data to new client
            self.send_initial_data(client_id)
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid if 'request' in globals() else 'unknown'
            self.connected_clients.discard(client_id)
            logger.info(f"Client disconnected: {client_id}")
            
        @self.socketio.on('subscribe')
        def handle_subscribe(data):
            """Handle subscription to specific data types"""
            client_id = request.sid if 'request' in globals() else 'unknown'
            data_types = data.get('types', [])
            logger.info(f"Client {client_id} subscribed to: {data_types}")
            
            # Store subscription preferences (could be enhanced with Redis)
            # For now, all clients get all updates
            
        @self.socketio.on('ping')
        def handle_ping():
            """Handle ping from client"""
            emit('pong', {'timestamp': datetime.utcnow().isoformat()})
            
    def send_initial_data(self, client_id: str = None):
        """Send initial data to client(s)"""
        try:
            # Get latest overview data
            overview_data = self.get_overview_data()
            
            # Get recent transactions
            recent_transactions = self.get_recent_transactions(limit=10)
            
            # Get recent resources
            recent_resources = self.get_recent_resources(limit=10)
            
            # Get recent intents
            recent_intents = self.get_recent_intents(limit=10)
            
            initial_data = {
                'type': 'initial_data',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'overview': overview_data,
                    'recent_transactions': recent_transactions,
                    'recent_resources': recent_resources,
                    'recent_intents': recent_intents
                }
            }
            
            if client_id:
                self.socketio.emit('data_update', initial_data, room=client_id)
            else:
                self.socketio.emit('data_update', initial_data)
                
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
            
    def broadcast_new_transaction(self, transaction_data: Dict[str, Any]):
        """Broadcast new transaction to all connected clients"""
        if not self.connected_clients:
            return
            
        try:
            update_data = {
                'type': 'new_transaction',
                'timestamp': datetime.utcnow().isoformat(),
                'data': transaction_data
            }
            
            self.socketio.emit('data_update', update_data)
            logger.info(f"Broadcasted new transaction: {transaction_data.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting transaction: {e}")
            
    def broadcast_new_resource(self, resource_data: Dict[str, Any]):
        """Broadcast new resource to all connected clients"""
        if not self.connected_clients:
            return
            
        try:
            update_data = {
                'type': 'new_resource',
                'timestamp': datetime.utcnow().isoformat(),
                'data': resource_data
            }
            
            self.socketio.emit('data_update', update_data)
            logger.info(f"Broadcasted new resource: {resource_data.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting resource: {e}")
            
    def broadcast_new_intent(self, intent_data: Dict[str, Any]):
        """Broadcast new intent to all connected clients"""
        if not self.connected_clients:
            return
            
        try:
            update_data = {
                'type': 'new_intent',
                'timestamp': datetime.utcnow().isoformat(),
                'data': intent_data
            }
            
            self.socketio.emit('data_update', update_data)
            logger.info(f"Broadcasted new intent: {intent_data.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting intent: {e}")
            
    def broadcast_new_block(self, block_data: Dict[str, Any]):
        """Broadcast new block to all connected clients"""
        if not self.connected_clients:
            return
            
        try:
            update_data = {
                'type': 'new_block',
                'timestamp': datetime.utcnow().isoformat(),
                'data': block_data
            }
            
            self.socketio.emit('data_update', update_data)
            logger.info(f"Broadcasted new block: {block_data.get('height', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting block: {e}")
            
    def broadcast_stats_update(self, stats_data: Dict[str, Any]):
        """Broadcast network stats update to all connected clients"""
        if not self.connected_clients:
            return
            
        try:
            update_data = {
                'type': 'stats_update',
                'timestamp': datetime.utcnow().isoformat(),
                'data': stats_data
            }
            
            self.socketio.emit('data_update', update_data)
            logger.info("Broadcasted stats update")
            
        except Exception as e:
            logger.error(f"Error broadcasting stats: {e}")
            
    def get_overview_data(self) -> Dict[str, Any]:
        """Get overview data for initial load"""
        try:
            latest_stats = NetworkStats.query.order_by(NetworkStats.timestamp.desc()).first()
            latest_block = Block.query.order_by(Block.height.desc()).first()
            
            return {
                'current_block_height': latest_block.height if latest_block else 0,
                'total_transactions': latest_stats.total_transactions if latest_stats else 0,
                'total_resources': latest_stats.total_resources if latest_stats else 0,
                'total_intents': latest_stats.total_intents if latest_stats else 0,
                'active_resources': latest_stats.active_resources if latest_stats else 0,
                'pending_intents': latest_stats.pending_intents if latest_stats else 0,
                'current_tps': latest_stats.tps if latest_stats else 0
            }
        except Exception as e:
            logger.error(f"Error getting overview data: {e}")
            return {}
            
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions"""
        try:
            transactions = Transaction.query.order_by(
                Transaction.timestamp.desc()
            ).limit(limit).all()
            
            return [tx.to_dict() for tx in transactions]
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []
            
    def get_recent_resources(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent resources"""
        try:
            resources = Resource.query.order_by(
                Resource.created_at.desc()
            ).limit(limit).all()
            
            return [res.to_dict() for res in resources]
        except Exception as e:
            logger.error(f"Error getting recent resources: {e}")
            return []
            
    def get_recent_intents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent intents"""
        try:
            intents = Intent.query.order_by(
                Intent.created_at.desc()
            ).limit(limit).all()
            
            return [intent.to_dict() for intent in intents]
        except Exception as e:
            logger.error(f"Error getting recent intents: {e}")
            return []
            
    def start_periodic_updates(self):
        """Start periodic updates for connected clients"""
        if self.is_running:
            return
            
        self.is_running = True
        
        def update_loop():
            while self.is_running:
                try:
                    if self.connected_clients:
                        # Send periodic stats updates
                        stats_data = self.get_overview_data()
                        self.broadcast_stats_update(stats_data)
                        
                    # Wait 30 seconds before next update
                    import time
                    time.sleep(30)
                    
                except Exception as e:
                    logger.error(f"Error in update loop: {e}")
                    
        # Start update loop in background thread
        import threading
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
    def stop_periodic_updates(self):
        """Stop periodic updates"""
        self.is_running = False

# Global WebSocket service instance
websocket_service = WebSocketService()

def init_websocket(app: Flask):
    """Initialize WebSocket service with Flask app"""
    websocket_service.init_app(app)
    websocket_service.start_periodic_updates()
    return websocket_service.socketio

