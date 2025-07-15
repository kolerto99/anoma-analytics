import random
import string
import json
import math
from datetime import datetime, timedelta
from src.models.anoma_models import (
    db, Resource, Transaction, Intent, Block, NetworkStats,
    ResourceKind, TransactionType, IntentStatus
)

class AnomaDataSimulator:
    """Simulator for generating realistic Anoma data"""
    
    def __init__(self):
        self.owners = self._generate_addresses(50)  # 50 unique addresses
        self.solvers = self._generate_addresses(10)  # 10 solver addresses
        self.current_block_height = 1000
        
    def _generate_addresses(self, count):
        """Generate realistic-looking addresses"""
        addresses = []
        for _ in range(count):
            # Generate address like: anoma1abc123def456...
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
            addresses.append(f"anoma1{suffix}")
        return addresses
    
    def _generate_hash(self, length=64):
        """Generate a random hash"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def _random_timestamp(self, days_back=30):
        """Generate a random timestamp within the last N days"""
        now = datetime.utcnow()
        start = now - timedelta(days=days_back)
        random_time = start + timedelta(
            seconds=random.randint(0, int((now - start).total_seconds()))
        )
        return random_time
    
    def generate_blocks(self, count=100):
        """Generate sample blocks"""
        blocks = []
        base_time = datetime.utcnow() - timedelta(days=7)
        
        for i in range(count):
            block = Block(
                height=self.current_block_height + i,
                hash=self._generate_hash(),
                timestamp=base_time + timedelta(minutes=i * 2),  # Block every 2 minutes
                transaction_count=random.randint(1, 20),
                size_bytes=random.randint(1024, 1024*1024),  # 1KB to 1MB
                proposer=random.choice(self.solvers)
            )
            blocks.append(block)
        
        return blocks
    
    def generate_transactions(self, count=500):
        """Generate sample transactions"""
        transactions = []
        
        for _ in range(count):
            tx = Transaction(
                id=self._generate_hash(),
                type=random.choice(list(TransactionType)),
                block_height=random.randint(self.current_block_height, self.current_block_height + 100),
                timestamp=self._random_timestamp(7),
                size_bytes=random.randint(256, 4096),
                gas_used=random.randint(21000, 500000),
                status=random.choices(['success', 'failed'], weights=[95, 5])[0]
            )
            transactions.append(tx)
        
        return transactions
    
    def generate_resources(self, count=1000):
        """Generate sample resources"""
        resources = []
        
        for _ in range(count):
            created_time = self._random_timestamp(7)
            is_consumed = random.choice([True, False])
            consumed_time = None
            
            if is_consumed:
                # Consumed sometime after creation
                consumed_time = created_time + timedelta(
                    hours=random.randint(1, 48)
                )
            
            # Generate resource value based on kind
            kind = random.choice(list(ResourceKind))
            value = self._generate_resource_value(kind)
            
            resource = Resource(
                id=self._generate_hash(),
                kind=kind,
                owner=random.choice(self.owners),
                value=json.dumps(value),
                resource_metadata=json.dumps(self._generate_resource_metadata(kind)),
                created_at=created_time,
                consumed_at=consumed_time,
                is_consumed=is_consumed,
                created_in_transaction=self._generate_hash(),
                consumed_in_transaction=self._generate_hash() if is_consumed else None
            )
            resources.append(resource)
        
        return resources
    
    def generate_intents(self, count=300):
        """Generate sample intents"""
        intents = []
        
        for _ in range(count):
            created_time = self._random_timestamp(7)
            status = random.choices(
                list(IntentStatus),
                weights=[10, 5, 70, 15]  # pending, processing, solved, failed
            )[0]
            
            processed_time = None
            processing_time_ms = None
            solver = None
            
            if status in [IntentStatus.SOLVED, IntentStatus.FAILED]:
                processing_time_ms = random.randint(50, 5000)
                processed_time = created_time + timedelta(milliseconds=processing_time_ms)
                solver = random.choice(self.solvers)
            elif status == IntentStatus.PROCESSING:
                solver = random.choice(self.solvers)
            
            intent = Intent(
                id=self._generate_hash(),
                creator=random.choice(self.owners),
                status=status,
                intent_data=json.dumps(self._generate_intent_data()),
                solver=solver,
                created_at=created_time,
                processed_at=processed_time,
                processing_time_ms=processing_time_ms,
                transaction_id=self._generate_hash()
            )
            intents.append(intent)
        
        return intents
    
    def generate_network_stats(self, count=168):  # 7 days of hourly stats
        """Generate network statistics"""
        stats = []
        base_time = datetime.utcnow() - timedelta(hours=count)
        
        # Base values that will fluctuate
        base_resources = 10000
        base_transactions = 5000
        base_intents = 3000
        
        for i in range(count):
            timestamp = base_time + timedelta(hours=i)
            
            # Add some realistic fluctuation
            hour = timestamp.hour
            day_factor = 1.0 + 0.3 * random.random()  # Daily variation
            hour_factor = 0.7 + 0.6 * (1 + math.sin(hour * 3.14159 / 12))  # Hourly pattern
            
            total_resources = int(base_resources * day_factor * hour_factor)
            total_transactions = int(base_transactions * day_factor * hour_factor)
            total_intents = int(base_intents * day_factor * hour_factor)
            
            stat = NetworkStats(
                timestamp=timestamp,
                total_resources=total_resources,
                total_transactions=total_transactions,
                total_intents=total_intents,
                active_resources=int(total_resources * 0.7),  # 70% active
                pending_intents=random.randint(10, 100),
                avg_processing_time_ms=random.uniform(200, 800),
                tps=random.uniform(5, 50)
            )
            stats.append(stat)
        
        return stats
    
    def _generate_resource_value(self, kind):
        """Generate realistic resource values based on kind"""
        if kind == ResourceKind.TOKEN:
            return {
                'amount': random.randint(1, 1000000),
                'token_id': f"token_{random.randint(1, 100)}",
                'decimals': 18
            }
        elif kind == ResourceKind.NFT:
            return {
                'token_id': random.randint(1, 10000),
                'collection': f"collection_{random.randint(1, 50)}",
                'metadata_uri': f"ipfs://Qm{self._generate_hash(32)}"
            }
        elif kind == ResourceKind.INTENT:
            return {
                'intent_type': random.choice(['swap', 'transfer', 'stake', 'vote']),
                'parameters': {
                    'amount': random.randint(1, 1000),
                    'target': random.choice(self.owners)
                }
            }
        else:  # CUSTOM
            return {
                'custom_type': f"type_{random.randint(1, 20)}",
                'data': f"custom_data_{random.randint(1, 1000)}"
            }
    
    def _generate_resource_metadata(self, kind):
        """Generate metadata for resources"""
        return {
            'created_by': 'anoma_simulator',
            'version': '1.0',
            'tags': random.sample(['defi', 'nft', 'gaming', 'dao', 'bridge'], k=random.randint(1, 3))
        }
    
    def _generate_intent_data(self):
        """Generate intent specification data"""
        intent_types = ['token_swap', 'nft_trade', 'liquidity_provision', 'governance_vote']
        intent_type = random.choice(intent_types)
        
        if intent_type == 'token_swap':
            return {
                'type': 'token_swap',
                'from_token': f"token_{random.randint(1, 100)}",
                'to_token': f"token_{random.randint(1, 100)}",
                'amount_in': random.randint(1, 1000),
                'min_amount_out': random.randint(1, 1000),
                'deadline': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        elif intent_type == 'nft_trade':
            return {
                'type': 'nft_trade',
                'collection': f"collection_{random.randint(1, 50)}",
                'token_id': random.randint(1, 10000),
                'price': random.randint(1, 100),
                'currency': f"token_{random.randint(1, 10)}"
            }
        elif intent_type == 'liquidity_provision':
            return {
                'type': 'liquidity_provision',
                'pool': f"pool_{random.randint(1, 20)}",
                'token_a': f"token_{random.randint(1, 100)}",
                'token_b': f"token_{random.randint(1, 100)}",
                'amount_a': random.randint(1, 1000),
                'amount_b': random.randint(1, 1000)
            }
        else:  # governance_vote
            return {
                'type': 'governance_vote',
                'proposal_id': random.randint(1, 100),
                'vote': random.choice(['yes', 'no', 'abstain']),
                'voting_power': random.randint(1, 10000)
            }
    
    def populate_database(self):
        """Populate database with simulated data"""
        try:
            print("Generating simulated Anoma data...")
            
            # Generate and save blocks
            print("Creating blocks...")
            blocks = self.generate_blocks(100)
            for block in blocks:
                db.session.add(block)
            
            # Generate and save transactions
            print("Creating transactions...")
            transactions = self.generate_transactions(500)
            for tx in transactions:
                db.session.add(tx)
            
            # Generate and save resources
            print("Creating resources...")
            resources = self.generate_resources(1000)
            for resource in resources:
                db.session.add(resource)
            
            # Generate and save intents
            print("Creating intents...")
            intents = self.generate_intents(300)
            for intent in intents:
                db.session.add(intent)
            
            # Generate and save network stats
            print("Creating network statistics...")
            stats = self.generate_network_stats(168)  # 7 days of hourly data
            for stat in stats:
                db.session.add(stat)
            
            # Commit all changes
            db.session.commit()
            print("✅ Database populated with simulated data!")
            
            return {
                'blocks': len(blocks),
                'transactions': len(transactions),
                'resources': len(resources),
                'intents': len(intents),
                'network_stats': len(stats)
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error populating database: {e}")
            raise e

