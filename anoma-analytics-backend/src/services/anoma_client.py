import asyncio
import aiohttp
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AnomaConfig:
    """Configuration for Anoma network connection"""
    rpc_url: str = "http://localhost:26657"  # Default Anoma RPC
    websocket_url: str = "ws://localhost:26657/websocket"  # Default WebSocket
    indexing_url: str = "http://localhost:8080"  # Anoma Indexing Service
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5

class AnomaClient:
    """Client for connecting to Anoma network and retrieving real-time data"""
    
    def __init__(self, config: AnomaConfig = None):
        self.config = config or AnomaConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        
    async def connect(self):
        """Establish connection to Anoma network"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test RPC connection
            await self._test_rpc_connection()
            self.is_connected = True
            logger.info("Successfully connected to Anoma network")
            
        except Exception as e:
            logger.error(f"Failed to connect to Anoma network: {e}")
            await self.disconnect()
            raise
            
    async def disconnect(self):
        """Close all connections"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        if self.session:
            await self.session.close()
            self.session = None
            
        self.is_connected = False
        logger.info("Disconnected from Anoma network")
        
    async def _test_rpc_connection(self):
        """Test RPC connection"""
        try:
            async with self.session.get(f"{self.config.rpc_url}/status") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Connected to Anoma node: {data.get('result', {}).get('node_info', {}).get('moniker', 'Unknown')}")
                else:
                    raise Exception(f"RPC connection failed with status {response.status}")
        except Exception as e:
            logger.error(f"RPC connection test failed: {e}")
            raise
            
    async def get_latest_block(self) -> Dict[str, Any]:
        """Get the latest block from Anoma"""
        if not self.is_connected:
            raise Exception("Not connected to Anoma network")
            
        try:
            async with self.session.get(f"{self.config.rpc_url}/block") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('result', {})
                else:
                    raise Exception(f"Failed to get latest block: {response.status}")
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            raise
            
    async def get_block_by_height(self, height: int) -> Dict[str, Any]:
        """Get block by height"""
        if not self.is_connected:
            raise Exception("Not connected to Anoma network")
            
        try:
            async with self.session.get(f"{self.config.rpc_url}/block?height={height}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('result', {})
                else:
                    raise Exception(f"Failed to get block {height}: {response.status}")
        except Exception as e:
            logger.error(f"Error getting block {height}: {e}")
            raise
            
    async def get_transactions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transactions from Anoma indexing service"""
        if not self.is_connected:
            raise Exception("Not connected to Anoma network")
            
        try:
            params = {'limit': limit, 'offset': offset}
            async with self.session.get(f"{self.config.indexing_url}/transactions", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('transactions', [])
                else:
                    raise Exception(f"Failed to get transactions: {response.status}")
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise
            
    async def get_resources(self, limit: int = 50, offset: int = 0, resource_type: str = None) -> List[Dict[str, Any]]:
        """Get resources from Anoma indexing service"""
        if not self.is_connected:
            raise Exception("Not connected to Anoma network")
            
        try:
            params = {'limit': limit, 'offset': offset}
            if resource_type:
                params['type'] = resource_type
                
            async with self.session.get(f"{self.config.indexing_url}/resources", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('resources', [])
                else:
                    raise Exception(f"Failed to get resources: {response.status}")
        except Exception as e:
            logger.error(f"Error getting resources: {e}")
            raise
            
    async def get_intents(self, limit: int = 50, offset: int = 0, status: str = None) -> List[Dict[str, Any]]:
        """Get intents from Anoma indexing service"""
        if not self.is_connected:
            raise Exception("Not connected to Anoma network")
            
        try:
            params = {'limit': limit, 'offset': offset}
            if status:
                params['status'] = status
                
            async with self.session.get(f"{self.config.indexing_url}/intents", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('intents', [])
                else:
                    raise Exception(f"Failed to get intents: {response.status}")
        except Exception as e:
            logger.error(f"Error getting intents: {e}")
            raise
            
    async def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        if not self.is_connected:
            raise Exception("Not connected to Anoma network")
            
        try:
            async with self.session.get(f"{self.config.indexing_url}/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    raise Exception(f"Failed to get network stats: {response.status}")
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            raise
            
    async def subscribe_to_blocks(self, callback):
        """Subscribe to new blocks via WebSocket"""
        try:
            self.websocket = await websockets.connect(self.config.websocket_url)
            
            # Subscribe to new blocks
            subscribe_msg = {
                "jsonrpc": "2.0",
                "method": "subscribe",
                "id": 1,
                "params": {
                    "query": "tm.event='NewBlock'"
                }
            }
            
            await self.websocket.send(json.dumps(subscribe_msg))
            
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    if 'result' in data and 'data' in data['result']:
                        await callback(data['result']['data'])
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse WebSocket message: {message}")
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    
        except Exception as e:
            logger.error(f"WebSocket subscription error: {e}")
            raise
            
    async def subscribe_to_transactions(self, callback):
        """Subscribe to new transactions via WebSocket"""
        try:
            if not self.websocket:
                self.websocket = await websockets.connect(self.config.websocket_url)
            
            # Subscribe to new transactions
            subscribe_msg = {
                "jsonrpc": "2.0",
                "method": "subscribe",
                "id": 2,
                "params": {
                    "query": "tm.event='Tx'"
                }
            }
            
            await self.websocket.send(json.dumps(subscribe_msg))
            
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    if 'result' in data and 'data' in data['result']:
                        await callback(data['result']['data'])
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse WebSocket message: {message}")
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    
        except Exception as e:
            logger.error(f"WebSocket subscription error: {e}")
            raise

# Singleton instance for global use
anoma_client = None

async def get_anoma_client(config: AnomaConfig = None) -> AnomaClient:
    """Get or create Anoma client instance"""
    global anoma_client
    
    if anoma_client is None or not anoma_client.is_connected:
        anoma_client = AnomaClient(config)
        await anoma_client.connect()
        
    return anoma_client

async def close_anoma_client():
    """Close global Anoma client"""
    global anoma_client
    
    if anoma_client:
        await anoma_client.disconnect()
        anoma_client = None

