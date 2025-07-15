#!/usr/bin/env python3
"""
Anoma Analytics Backend with Real Namada Data Integration
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import threading
import time
import logging
from datetime import datetime, timezone, timedelta
import sys
import os

# Добавляем путь к нашим модулям
sys.path.append('/home/ubuntu')
from namada_integration_layer import NamadaAnalyticsAdapter

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Глобальный адаптер Namada
namada_adapter = None

def init_namada_adapter():
    """Инициализирует адаптер Namada"""
    global namada_adapter
    try:
        namada_adapter = NamadaAnalyticsAdapter("namada_analytics.db")
        logger.info("✅ Namada адаптер инициализирован")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации Namada адаптера: {e}")
        return False

def sync_namada_data():
    """Фоновая синхронизация с Namada"""
    global namada_adapter
    while True:
        try:
            if namada_adapter:
                logger.info("🔄 Синхронизация с Namada...")
                namada_adapter.sync_with_namada()
                logger.info("✅ Синхронизация завершена")
            time.sleep(30)  # Синхронизация каждые 30 секунд
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации: {e}")
            time.sleep(60)  # При ошибке ждем дольше

@app.route('/api/analytics/overview', methods=['GET'])
def get_overview():
    """Получает общую статистику (Dashboard)"""
    try:
        if not namada_adapter:
            return jsonify({"error": "Namada adapter not initialized"}), 500
            
        data = namada_adapter.get_dashboard_data()
        
        return jsonify({
            "total_resources": data.get('total_resources', 0),
            "total_transactions": data.get('total_transactions', 0),
            "active_intents": data.get('active_intents', 0),
            "current_block": data.get('current_block', 0),
            "network_stats": {
                "tps": data.get('tps', 0),
                "avg_processing_time": data.get('avg_processing_time', 0),
                "active_resources": data.get('active_resources', 0),
                "pending_intents": data.get('pending_intents', 0)
            }
        })
    except Exception as e:
        logger.error(f"Error in get_overview: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/stats/network', methods=['GET'])
def get_network_stats():
    """Получает статистику сети"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        conn = sqlite3.connect(namada_adapter.db_path)
        cursor = conn.cursor()
        
        # Получаем статистику за указанный период
        since_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT timestamp, tps, avg_processing_time, active_resources, pending_intents, block_height
            FROM network_stats 
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        ''', (since_time.isoformat(),))
        
        stats = cursor.fetchall()
        conn.close()
        
        # Форматируем данные
        formatted_stats = []
        for stat in stats:
            formatted_stats.append({
                "timestamp": stat[0],
                "tps": stat[1],
                "avg_processing_time": stat[2],
                "active_resources": stat[3],
                "pending_intents": stat[4],
                "block_height": stat[5]
            })
        
        # Получаем текущие значения
        current = formatted_stats[0] if formatted_stats else {
            "tps": 0, "avg_processing_time": 0, 
            "active_resources": 0, "pending_intents": 0
        }
        
        return jsonify({
            "current_tps": current["tps"],
            "avg_processing_time": current["avg_processing_time"],
            "active_resources": current["active_resources"],
            "pending_intents": current["pending_intents"],
            "historical_data": formatted_stats,
            "summary": {
                "data_points": len(formatted_stats),
                "time_range_hours": hours,
                "avg_tps": sum(s["tps"] for s in formatted_stats) / len(formatted_stats) if formatted_stats else 0
            }
        })
    except Exception as e:
        logger.error(f"Error in get_network_stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/resources', methods=['GET'])
def get_resources():
    """Получает список ресурсов"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        kind_filter = request.args.get('kind')
        status_filter = request.args.get('status')
        owner_filter = request.args.get('owner')
        
        conn = sqlite3.connect(namada_adapter.db_path)
        cursor = conn.cursor()
        
        # Строим запрос с фильтрами
        where_conditions = []
        params = []
        
        if kind_filter:
            where_conditions.append("kind = ?")
            params.append(kind_filter)
        if status_filter:
            where_conditions.append("status = ?")
            params.append(status_filter)
        if owner_filter:
            where_conditions.append("owner LIKE ?")
            params.append(f"%{owner_filter}%")
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Получаем общее количество
        cursor.execute(f"SELECT COUNT(*) FROM resources{where_clause}", params)
        total_count = cursor.fetchone()[0]
        
        # Получаем данные с пагинацией
        offset = (page - 1) * per_page
        cursor.execute(f'''
            SELECT resource_id, kind, owner, status, amount, token_id, decimals,
                   collection, metadata_uri, intent_type, custom_type, created_at, updated_at
            FROM resources{where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', params + [per_page, offset])
        
        resources = cursor.fetchall()
        conn.close()
        
        # Форматируем данные
        formatted_resources = []
        for resource in resources:
            formatted_resources.append({
                "id": resource[0],
                "kind": resource[1],
                "owner": resource[2],
                "status": resource[3],
                "amount": resource[4],
                "token_id": resource[5],
                "decimals": resource[6],
                "collection": resource[7],
                "metadata_uri": resource[8],
                "intent_type": resource[9],
                "custom_type": resource[10],
                "created_at": resource[11],
                "updated_at": resource[12]
            })
        
        return jsonify({
            "resources": formatted_resources,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        logger.error(f"Error in get_resources: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/transactions', methods=['GET'])
def get_transactions():
    """Получает список транзакций"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        conn = sqlite3.connect(namada_adapter.db_path)
        cursor = conn.cursor()
        
        # Получаем общее количество
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_count = cursor.fetchone()[0]
        
        # Получаем данные с пагинацией
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT tx_hash, block_height, timestamp, tx_type, from_address, to_address,
                   amount, fee, status, gas_used
            FROM transactions
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        transactions = cursor.fetchall()
        conn.close()
        
        # Форматируем данные
        formatted_transactions = []
        for tx in transactions:
            formatted_transactions.append({
                "hash": tx[0],
                "block_height": tx[1],
                "timestamp": tx[2],
                "type": tx[3],
                "from": tx[4],
                "to": tx[5],
                "amount": tx[6],
                "fee": tx[7],
                "status": tx[8],
                "gas_used": tx[9]
            })
        
        return jsonify({
            "transactions": formatted_transactions,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        logger.error(f"Error in get_transactions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/intents', methods=['GET'])
def get_intents():
    """Получает список интентов"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        conn = sqlite3.connect(namada_adapter.db_path)
        cursor = conn.cursor()
        
        # Получаем общее количество
        cursor.execute("SELECT COUNT(*) FROM intents")
        total_count = cursor.fetchone()[0]
        
        # Получаем данные с пагинацией
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT intent_id, intent_type, creator, status, target_amount, current_amount,
                   deadline, created_at, updated_at, metadata
            FROM intents
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        intents = cursor.fetchall()
        conn.close()
        
        # Форматируем данные
        formatted_intents = []
        for intent in intents:
            formatted_intents.append({
                "id": intent[0],
                "type": intent[1],
                "creator": intent[2],
                "status": intent[3],
                "target_amount": intent[4],
                "current_amount": intent[5],
                "deadline": intent[6],
                "created_at": intent[7],
                "updated_at": intent[8],
                "metadata": json.loads(intent[9]) if intent[9] else {}
            })
        
        return jsonify({
            "intents": formatted_intents,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        logger.error(f"Error in get_intents: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/blocks', methods=['GET'])
def get_blocks():
    """Получает список блоков"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        conn = sqlite3.connect(namada_adapter.db_path)
        cursor = conn.cursor()
        
        # Получаем общее количество
        cursor.execute("SELECT COUNT(*) FROM blocks")
        total_count = cursor.fetchone()[0]
        
        # Получаем данные с пагинацией
        offset = (page - 1) * per_page
        cursor.execute('''
            SELECT block_height, block_hash, timestamp, proposer, transaction_count, size
            FROM blocks
            ORDER BY block_height DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        blocks = cursor.fetchall()
        conn.close()
        
        # Форматируем данные
        formatted_blocks = []
        for block in blocks:
            formatted_blocks.append({
                "height": block[0],
                "hash": block[1],
                "timestamp": block[2],
                "proposer": block[3],
                "transaction_count": block[4],
                "size": block[5]
            })
        
        return jsonify({
            "blocks": formatted_blocks,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        logger.error(f"Error in get_blocks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({
        "status": "healthy",
        "namada_adapter": "connected" if namada_adapter else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

def main():
    """Главная функция"""
    logger.info("🚀 Запуск Anoma Analytics Backend с интеграцией Namada...")
    
    # Инициализируем адаптер Namada
    if not init_namada_adapter():
        logger.error("❌ Не удалось инициализировать Namada адаптер")
        return
    
    # Запускаем фоновую синхронизацию
    sync_thread = threading.Thread(target=sync_namada_data, daemon=True)
    sync_thread.start()
    logger.info("🔄 Фоновая синхронизация запущена")
    
    # Запускаем Flask приложение
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"🌐 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()

