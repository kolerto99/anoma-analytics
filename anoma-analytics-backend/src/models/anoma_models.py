from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class ResourceKind(Enum):
    TOKEN = "token"
    NFT = "nft"
    INTENT = "intent"
    CUSTOM = "custom"

class TransactionType(Enum):
    BALANCED = "balanced"
    UNBALANCED = "unbalanced"

class IntentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SOLVED = "solved"
    FAILED = "failed"

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.String(64), primary_key=True)  # Resource commitment hash
    kind = db.Column(db.Enum(ResourceKind), nullable=False)
    owner = db.Column(db.String(64), nullable=False)  # Owner address/identifier
    value = db.Column(db.String(255))  # Resource value (JSON string)
    resource_metadata = db.Column(db.Text)  # Additional metadata (JSON string)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    consumed_at = db.Column(db.DateTime, nullable=True)
    is_consumed = db.Column(db.Boolean, default=False)
    
    # Relationships
    created_in_transaction = db.Column(db.String(64), db.ForeignKey('transactions.id'))
    consumed_in_transaction = db.Column(db.String(64), db.ForeignKey('transactions.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'kind': self.kind.value,
            'owner': self.owner,
            'value': self.value,
            'resource_metadata': self.resource_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'consumed_at': self.consumed_at.isoformat() if self.consumed_at else None,
            'is_consumed': self.is_consumed,
            'created_in_transaction': self.created_in_transaction,
            'consumed_in_transaction': self.consumed_in_transaction
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(64), primary_key=True)  # Transaction hash
    type = db.Column(db.Enum(TransactionType), nullable=False)
    block_height = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    size_bytes = db.Column(db.Integer)
    gas_used = db.Column(db.Integer)
    status = db.Column(db.String(20), default='success')
    
    # Relationships
    created_resources = db.relationship('Resource', 
                                      foreign_keys=[Resource.created_in_transaction],
                                      backref='creation_transaction')
    consumed_resources = db.relationship('Resource', 
                                       foreign_keys=[Resource.consumed_in_transaction],
                                       backref='consumption_transaction')
    intents = db.relationship('Intent', backref='transaction')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'block_height': self.block_height,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'size_bytes': self.size_bytes,
            'gas_used': self.gas_used,
            'status': self.status,
            'created_resources_count': len(self.created_resources),
            'consumed_resources_count': len(self.consumed_resources),
            'intents_count': len(self.intents)
        }

class Intent(db.Model):
    __tablename__ = 'intents'
    
    id = db.Column(db.String(64), primary_key=True)  # Intent hash
    creator = db.Column(db.String(64), nullable=False)  # Intent creator address
    status = db.Column(db.Enum(IntentStatus), default=IntentStatus.PENDING)
    intent_data = db.Column(db.Text)  # Intent specification (JSON string)
    solver = db.Column(db.String(64), nullable=True)  # Solver that processed the intent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    
    # Foreign key to transaction
    transaction_id = db.Column(db.String(64), db.ForeignKey('transactions.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'creator': self.creator,
            'status': self.status.value,
            'intent_data': self.intent_data,
            'solver': self.solver,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processing_time_ms': self.processing_time_ms,
            'transaction_id': self.transaction_id
        }

class Block(db.Model):
    __tablename__ = 'blocks'
    
    height = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_count = db.Column(db.Integer, default=0)
    size_bytes = db.Column(db.Integer)
    proposer = db.Column(db.String(64))  # Block proposer
    
    def to_dict(self):
        return {
            'height': self.height,
            'hash': self.hash,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'transaction_count': self.transaction_count,
            'size_bytes': self.size_bytes,
            'proposer': self.proposer
        }

class NetworkStats(db.Model):
    __tablename__ = 'network_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_resources = db.Column(db.Integer, default=0)
    total_transactions = db.Column(db.Integer, default=0)
    total_intents = db.Column(db.Integer, default=0)
    active_resources = db.Column(db.Integer, default=0)  # Non-consumed resources
    pending_intents = db.Column(db.Integer, default=0)
    avg_processing_time_ms = db.Column(db.Float, default=0.0)
    tps = db.Column(db.Float, default=0.0)  # Transactions per second
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'total_resources': self.total_resources,
            'total_transactions': self.total_transactions,
            'total_intents': self.total_intents,
            'active_resources': self.active_resources,
            'pending_intents': self.pending_intents,
            'avg_processing_time_ms': self.avg_processing_time_ms,
            'tps': self.tps
        }

