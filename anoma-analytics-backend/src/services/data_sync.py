import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.exc import IntegrityError
from src.models.anoma_models import (
    db, Resource, Transaction, Intent, Block, NetworkStats,
    ResourceKind, TransactionType, IntentStatus
)
from src.services.anoma_client import get_anoma_client, AnomaConfig

logger = logging.getLogger(__name__)

class AnomaDataSync:
    """Service for synchronizing data from Anoma network to local database"""
    
    def __init__(self, config: AnomaConfig = None):
        self.config = config or AnomaConfig()
        self.client = None
        self.is_syncing = False
        self.sync_interval = 10  # seconds
        
    async def start_sync(self):
        """Start continuous data synchronization"""
        if self.is_syncing:
            logger.warning("Data sync already running")
            return
            
        self.is_syncing = True
        logger.info("Starting Anoma data synchronization")
        
        try:
            self.client = await get_anoma_client(self.config)
            
            # Start background tasks
            await asyncio.gather(
                self._sync_blocks(),
                self._sync_transactions(),
                self._sync_resources(),
                self._sync_intents(),
                self._update_network_stats(),
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"Error in data sync: {e}")
            self.is_syncing = False
            raise
            
    async def stop_sync(self):
        """Stop data synchronization"""
        self.is_syncing = False
        logger.info("Stopping Anoma data synchronization")
        
    async def _sync_blocks(self):
        """Continuously sync blocks from Anoma"""
        while self.is_syncing:
            try:
                # Get latest block from Anoma
                latest_anoma_block = await self.client.get_latest_block()
                
                if latest_anoma_block and 'block' in latest_anoma_block:
                    block_data = latest_anoma_block['block']
                    header = block_data.get('header', {})
                    
                    block_height = int(header.get('height', 0))
                    
                    # Check if we already have this block
                    existing_block = Block.query.filter_by(height=block_height).first()
                    
                    if not existing_block:
                        # Create new block record
                        new_block = Block(
                            height=block_height,
                            hash=header.get('app_hash', ''),
                            timestamp=datetime.fromisoformat(header.get('time', '').replace('Z', '+00:00')),
                            transaction_count=len(block_data.get('data', {}).get('txs', [])),
                            proposer=header.get('proposer_address', ''),
                            size_bytes=len(str(block_data).encode('utf-8'))
                        )
                        
                        db.session.add(new_block)
                        db.session.commit()
                        logger.info(f"Synced new block: {block_height}")
                        
            except Exception as e:
                logger.error(f"Error syncing blocks: {e}")
                
            await asyncio.sleep(self.sync_interval)
            
    async def _sync_transactions(self):
        """Continuously sync transactions from Anoma"""
        while self.is_syncing:
            try:
                # Get transactions from Anoma indexing service
                transactions = await self.client.get_transactions(limit=100)
                
                for tx_data in transactions:
                    tx_id = tx_data.get('id') or tx_data.get('hash')
                    
                    if not tx_id:
                        continue
                        
                    # Check if we already have this transaction
                    existing_tx = Transaction.query.filter_by(id=tx_id).first()
                    
                    if not existing_tx:
                        # Parse transaction data
                        new_tx = Transaction(
                            id=tx_id,
                            block_height=tx_data.get('block_height', 0),
                            timestamp=self._parse_timestamp(tx_data.get('timestamp')),
                            type=self._parse_transaction_type(tx_data.get('type', 'unknown')),
                            status='success' if tx_data.get('success', True) else 'failed',
                            gas_used=tx_data.get('gas_used', 0),
                            size_bytes=tx_data.get('size', 0),
                            created_resources_count=tx_data.get('created_resources', 0),
                            consumed_resources_count=tx_data.get('consumed_resources', 0),
                            intents_count=tx_data.get('intents', 0)
                        )
                        
                        db.session.add(new_tx)
                        
                try:
                    db.session.commit()
                    logger.info(f"Synced {len(transactions)} transactions")
                except IntegrityError:
                    db.session.rollback()
                    logger.warning("Some transactions already exist, skipping duplicates")
                    
            except Exception as e:
                logger.error(f"Error syncing transactions: {e}")
                
            await asyncio.sleep(self.sync_interval)
            
    async def _sync_resources(self):
        """Continuously sync resources from Anoma"""
        while self.is_syncing:
            try:
                # Get resources from Anoma indexing service
                resources = await self.client.get_resources(limit=100)
                
                for resource_data in resources:
                    resource_id = resource_data.get('id')
                    
                    if not resource_id:
                        continue
                        
                    # Check if we already have this resource
                    existing_resource = Resource.query.filter_by(id=resource_id).first()
                    
                    if not existing_resource:
                        # Parse resource data
                        new_resource = Resource(
                            id=resource_id,
                            kind=self._parse_resource_kind(resource_data.get('kind', 'unknown')),
                            owner=resource_data.get('owner', ''),
                            value=str(resource_data.get('value', {})),
                            resource_metadata=str(resource_data.get('metadata', {})),
                            created_at=self._parse_timestamp(resource_data.get('created_at')),
                            created_in_transaction=resource_data.get('created_in_tx'),
                            is_consumed=resource_data.get('is_consumed', False),
                            consumed_at=self._parse_timestamp(resource_data.get('consumed_at')),
                            consumed_in_transaction=resource_data.get('consumed_in_tx')
                        )
                        
                        db.session.add(new_resource)
                        
                try:
                    db.session.commit()
                    logger.info(f"Synced {len(resources)} resources")
                except IntegrityError:
                    db.session.rollback()
                    logger.warning("Some resources already exist, skipping duplicates")
                    
            except Exception as e:
                logger.error(f"Error syncing resources: {e}")
                
            await asyncio.sleep(self.sync_interval)
            
    async def _sync_intents(self):
        """Continuously sync intents from Anoma"""
        while self.is_syncing:
            try:
                # Get intents from Anoma indexing service
                intents = await self.client.get_intents(limit=100)
                
                for intent_data in intents:
                    intent_id = intent_data.get('id')
                    
                    if not intent_id:
                        continue
                        
                    # Check if we already have this intent
                    existing_intent = Intent.query.filter_by(id=intent_id).first()
                    
                    if existing_intent:
                        # Update status if changed
                        new_status = self._parse_intent_status(intent_data.get('status', 'pending'))
                        if existing_intent.status != new_status:
                            existing_intent.status = new_status
                            existing_intent.processed_at = self._parse_timestamp(intent_data.get('processed_at'))
                            existing_intent.solver = intent_data.get('solver')
                            existing_intent.transaction_id = intent_data.get('transaction_id')
                            
                            if intent_data.get('processing_time'):
                                existing_intent.processing_time_ms = intent_data['processing_time']
                    else:
                        # Create new intent
                        new_intent = Intent(
                            id=intent_id,
                            creator=intent_data.get('creator', ''),
                            intent_data=str(intent_data.get('data', {})),
                            status=self._parse_intent_status(intent_data.get('status', 'pending')),
                            created_at=self._parse_timestamp(intent_data.get('created_at')),
                            processed_at=self._parse_timestamp(intent_data.get('processed_at')),
                            processing_time_ms=intent_data.get('processing_time'),
                            solver=intent_data.get('solver'),
                            transaction_id=intent_data.get('transaction_id')
                        )
                        
                        db.session.add(new_intent)
                        
                try:
                    db.session.commit()
                    logger.info(f"Synced {len(intents)} intents")
                except IntegrityError:
                    db.session.rollback()
                    logger.warning("Some intents already exist, skipping duplicates")
                    
            except Exception as e:
                logger.error(f"Error syncing intents: {e}")
                
            await asyncio.sleep(self.sync_interval)
            
    async def _update_network_stats(self):
        """Update network statistics"""
        while self.is_syncing:
            try:
                # Get network stats from Anoma
                stats_data = await self.client.get_network_stats()
                
                # Calculate local stats
                total_transactions = Transaction.query.count()
                total_resources = Resource.query.count()
                total_intents = Intent.query.count()
                active_resources = Resource.query.filter_by(is_consumed=False).count()
                pending_intents = Intent.query.filter_by(status=IntentStatus.PENDING).count()
                
                # Calculate average processing time
                avg_processing_time = db.session.query(
                    db.func.avg(Intent.processing_time_ms)
                ).filter(Intent.processing_time_ms.isnot(None)).scalar() or 0
                
                # Calculate TPS (transactions per second in last minute)
                one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
                recent_transactions = Transaction.query.filter(
                    Transaction.timestamp >= one_minute_ago
                ).count()
                tps = recent_transactions / 60.0
                
                # Create new network stats record
                new_stats = NetworkStats(
                    timestamp=datetime.utcnow(),
                    total_transactions=total_transactions,
                    total_resources=total_resources,
                    total_intents=total_intents,
                    active_resources=active_resources,
                    pending_intents=pending_intents,
                    avg_processing_time_ms=avg_processing_time,
                    tps=tps
                )
                
                db.session.add(new_stats)
                db.session.commit()
                logger.info("Updated network statistics")
                
            except Exception as e:
                logger.error(f"Error updating network stats: {e}")
                
            await asyncio.sleep(30)  # Update stats every 30 seconds
            
    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime"""
        if not timestamp_str:
            return None
            
        try:
            # Handle different timestamp formats
            if 'T' in timestamp_str:
                if timestamp_str.endswith('Z'):
                    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(timestamp_str)
            else:
                return datetime.fromisoformat(timestamp_str)
        except Exception:
            return datetime.utcnow()
            
    def _parse_transaction_type(self, type_str):
        """Parse transaction type"""
        type_mapping = {
            'balanced': TransactionType.BALANCED,
            'unbalanced': TransactionType.UNBALANCED,
            'wrapper': TransactionType.WRAPPER
        }
        return type_mapping.get(type_str.lower(), TransactionType.UNBALANCED)
        
    def _parse_resource_kind(self, kind_str):
        """Parse resource kind"""
        kind_mapping = {
            'token': ResourceKind.TOKEN,
            'nft': ResourceKind.NFT,
            'intent': ResourceKind.INTENT,
            'custom': ResourceKind.CUSTOM
        }
        return kind_mapping.get(kind_str.lower(), ResourceKind.CUSTOM)
        
    def _parse_intent_status(self, status_str):
        """Parse intent status"""
        status_mapping = {
            'pending': IntentStatus.PENDING,
            'solved': IntentStatus.SOLVED,
            'failed': IntentStatus.FAILED,
            'expired': IntentStatus.EXPIRED
        }
        return status_mapping.get(status_str.lower(), IntentStatus.PENDING)

# Global sync service instance
data_sync_service = None

async def start_data_sync(config: AnomaConfig = None):
    """Start global data synchronization service"""
    global data_sync_service
    
    if data_sync_service and data_sync_service.is_syncing:
        logger.warning("Data sync service already running")
        return
        
    data_sync_service = AnomaDataSync(config)
    await data_sync_service.start_sync()

async def stop_data_sync():
    """Stop global data synchronization service"""
    global data_sync_service
    
    if data_sync_service:
        await data_sync_service.stop_sync()
        data_sync_service = None

