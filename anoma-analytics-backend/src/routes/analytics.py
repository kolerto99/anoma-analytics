from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from src.models.anoma_models import (
    db, Resource, Transaction, Intent, Block, NetworkStats,
    ResourceKind, TransactionType, IntentStatus
)

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@analytics_bp.route('/overview', methods=['GET'])
def get_overview():
    """Get overview statistics"""
    try:
        # Count data directly from tables
        total_transactions = Transaction.query.count()
        total_resources = Resource.query.count()
        total_intents = Intent.query.count()
        
        # Count active/pending items
        active_resources = Resource.query.filter(Resource.is_consumed == False).count()
        pending_intents = Intent.query.filter(Intent.status == IntentStatus.PENDING).count()
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_transactions = Transaction.query.filter(Transaction.timestamp >= yesterday).count()
        recent_intents = Intent.query.filter(Intent.created_at >= yesterday).count()
        recent_resources = Resource.query.filter(Resource.created_at >= yesterday).count()
        
        # Get current block height
        latest_block = Block.query.order_by(desc(Block.height)).first()
        current_height = latest_block.height if latest_block else 0
        
        # Calculate average processing time for intents
        avg_processing_time = db.session.query(func.avg(Intent.processing_time_ms)).scalar() or 0
        
        # Calculate current TPS (transactions in last minute)
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_tx_count = Transaction.query.filter(Transaction.timestamp >= one_minute_ago).count()
        current_tps = recent_tx_count / 60.0  # transactions per second
        
        overview = {
            'current_block_height': current_height,
            'total_transactions': total_transactions,
            'total_resources': total_resources,
            'total_intents': total_intents,
            'active_resources': active_resources,
            'pending_intents': pending_intents,
            'avg_processing_time_ms': float(avg_processing_time),
            'current_tps': round(current_tps, 2),
            'recent_activity': {
                'transactions_24h': recent_transactions,
                'intents_24h': recent_intents,
                'resources_24h': recent_resources
            }
        }
        
        return jsonify(overview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/resources', methods=['GET'])
def get_resources():
    """Get resources with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        kind = request.args.get('kind')
        owner = request.args.get('owner')
        is_consumed = request.args.get('is_consumed')
        
        # Build query
        query = Resource.query
        
        if kind:
            query = query.filter(Resource.kind == ResourceKind(kind))
        if owner:
            query = query.filter(Resource.owner == owner)
        if is_consumed is not None:
            query = query.filter(Resource.is_consumed == (is_consumed.lower() == 'true'))
        
        # Order by creation time (newest first)
        query = query.order_by(desc(Resource.created_at))
        
        # Paginate
        resources = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'resources': [resource.to_dict() for resource in resources.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': resources.total,
                'pages': resources.pages,
                'has_next': resources.has_next,
                'has_prev': resources.has_prev
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Get transactions with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        tx_type = request.args.get('type')
        status = request.args.get('status')
        
        # Build query
        query = Transaction.query
        
        if tx_type:
            query = query.filter(Transaction.type == TransactionType(tx_type))
        if status:
            query = query.filter(Transaction.status == status)
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(Transaction.timestamp))
        
        # Paginate
        transactions = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [tx.to_dict() for tx in transactions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': transactions.total,
                'pages': transactions.pages,
                'has_next': transactions.has_next,
                'has_prev': transactions.has_prev
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/intents', methods=['GET'])
def get_intents():
    """Get intents with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        status = request.args.get('status')
        creator = request.args.get('creator')
        solver = request.args.get('solver')
        
        # Build query
        query = Intent.query
        
        if status:
            query = query.filter(Intent.status == IntentStatus(status))
        if creator:
            query = query.filter(Intent.creator == creator)
        if solver:
            query = query.filter(Intent.solver == solver)
        
        # Order by creation time (newest first)
        query = query.order_by(desc(Intent.created_at))
        
        # Paginate
        intents = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'intents': [intent.to_dict() for intent in intents.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': intents.total,
                'pages': intents.pages,
                'has_next': intents.has_next,
                'has_prev': intents.has_prev
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/blocks', methods=['GET'])
def get_blocks():
    """Get blocks with pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Order by height (newest first)
        blocks = Block.query.order_by(desc(Block.height)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'blocks': [block.to_dict() for block in blocks.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': blocks.total,
                'pages': blocks.pages,
                'has_next': blocks.has_next,
                'has_prev': blocks.has_prev
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/stats/resources', methods=['GET'])
def get_resource_stats():
    """Get resource statistics"""
    try:
        # Resource distribution by kind
        resource_by_kind = db.session.query(
            Resource.kind,
            func.count(Resource.id).label('count')
        ).group_by(Resource.kind).all()
        
        # Resource consumption stats
        consumption_stats = db.session.query(
            func.count(Resource.id).label('total'),
            func.sum(func.cast(Resource.is_consumed, db.Integer)).label('consumed'),
            func.sum(func.cast(~Resource.is_consumed, db.Integer)).label('active')
        ).first()
        
        # Top resource owners
        top_owners = db.session.query(
            Resource.owner,
            func.count(Resource.id).label('count')
        ).group_by(Resource.owner).order_by(desc('count')).limit(10).all()
        
        return jsonify({
            'distribution_by_kind': [
                {'kind': kind.value, 'count': count} 
                for kind, count in resource_by_kind
            ],
            'consumption_stats': {
                'total': consumption_stats.total or 0,
                'consumed': consumption_stats.consumed or 0,
                'active': consumption_stats.active or 0
            },
            'top_owners': [
                {'owner': owner, 'count': count}
                for owner, count in top_owners
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/stats/transactions', methods=['GET'])
def get_transaction_stats():
    """Get transaction statistics"""
    try:
        # Transaction distribution by type
        tx_by_type = db.session.query(
            Transaction.type,
            func.count(Transaction.id).label('count')
        ).group_by(Transaction.type).all()
        
        # Transaction volume over time (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        daily_volume = db.session.query(
            func.date(Transaction.timestamp).label('date'),
            func.count(Transaction.id).label('count')
        ).filter(Transaction.timestamp >= week_ago).group_by(
            func.date(Transaction.timestamp)
        ).order_by('date').all()
        
        # Average transaction size and gas usage
        avg_stats = db.session.query(
            func.avg(Transaction.size_bytes).label('avg_size'),
            func.avg(Transaction.gas_used).label('avg_gas')
        ).first()
        
        return jsonify({
            'distribution_by_type': [
                {'type': tx_type.value, 'count': count}
                for tx_type, count in tx_by_type
            ],
            'daily_volume': [
                {'date': str(date), 'count': count}
                for date, count in daily_volume
            ],
            'averages': {
                'size_bytes': float(avg_stats.avg_size or 0),
                'gas_used': float(avg_stats.avg_gas or 0)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/stats/intents', methods=['GET'])
def get_intent_stats():
    """Get intent statistics"""
    try:
        # Intent distribution by status
        intent_by_status = db.session.query(
            Intent.status,
            func.count(Intent.id).label('count')
        ).group_by(Intent.status).all()
        
        # Average processing time
        avg_processing_time = db.session.query(
            func.avg(Intent.processing_time_ms)
        ).filter(Intent.processing_time_ms.isnot(None)).scalar()
        
        # Top solvers
        top_solvers = db.session.query(
            Intent.solver,
            func.count(Intent.id).label('count'),
            func.avg(Intent.processing_time_ms).label('avg_time')
        ).filter(Intent.solver.isnot(None)).group_by(
            Intent.solver
        ).order_by(desc('count')).limit(10).all()
        
        # Intent processing time distribution (simplified)
        processing_time_ranges = [
            {'range': '< 100ms', 'count': 0},
            {'range': '100-500ms', 'count': 0},
            {'range': '500ms-1s', 'count': 0},
            {'range': '1-5s', 'count': 0},
            {'range': '> 5s', 'count': 0}
        ]
        
        return jsonify({
            'distribution_by_status': [
                {'status': status.value, 'count': count}
                for status, count in intent_by_status
            ],
            'avg_processing_time_ms': float(avg_processing_time or 0),
            'top_solvers': [
                {
                    'solver': solver,
                    'count': count,
                    'avg_processing_time_ms': float(avg_time or 0)
                }
                for solver, count, avg_time in top_solvers
            ],
            'processing_time_distribution': processing_time_ranges
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/stats/network', methods=['GET'])
def get_network_stats():
    """Get network statistics over time"""
    try:
        # Query parameters
        hours = request.args.get('hours', 24, type=int)
        
        # Get network stats for the specified time period
        time_ago = datetime.utcnow() - timedelta(hours=hours)
        stats = NetworkStats.query.filter(
            NetworkStats.timestamp >= time_ago
        ).order_by(NetworkStats.timestamp).all()
        
        return jsonify({
            'stats': [stat.to_dict() for stat in stats],
            'time_range_hours': hours
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

