#!/usr/bin/env python3
"""
Namada API Client - Клиент для получения реальных данных из блокчейна Namada
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NamadaAPIClient:
    """Клиент для работы с Namada RPC API"""
    
    def __init__(self, rpc_url: str = "https://namada-mainnet-rpc.itrocket.net"):
        self.rpc_url = rpc_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Anoma-Analytics/1.0'
        })
        
    def _make_rpc_call(self, method: str, params: List[Any] = None) -> Dict:
        """Выполняет RPC вызов к Namada ноде"""
        if params is None:
            params = []
            
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        try:
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                logger.error(f"RPC Error: {data['error']}")
                return None
                
            return data.get('result')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    
    def get_status(self) -> Optional[Dict]:
        """Получает статус ноды"""
        return self._make_rpc_call("status")
    
    def get_block(self, height: Optional[int] = None) -> Optional[Dict]:
        """Получает блок по высоте (если не указана - последний)"""
        if height is None:
            # Сначала получаем статус для определения последней высоты
            status = self.get_status()
            if not status:
                return None
            height = int(status['sync_info']['latest_block_height'])
            
        return self._make_rpc_call("block", [str(height)])
    
    def get_block_results(self, height: int) -> Optional[Dict]:
        """Получает результаты выполнения блока"""
        return self._make_rpc_call("block_results", [str(height)])
    
    def get_validators(self, height: Optional[int] = None) -> Optional[Dict]:
        """Получает список валидаторов"""
        params = [str(height)] if height else []
        return self._make_rpc_call("validators", params)
    
    def get_tx(self, tx_hash: str) -> Optional[Dict]:
        """Получает транзакцию по хешу"""
        return self._make_rpc_call("tx", [tx_hash, True])  # True для включения proof
    
    def get_blockchain_info(self, min_height: int, max_height: int) -> Optional[Dict]:
        """Получает информацию о блокчейне в диапазоне высот"""
        return self._make_rpc_call("blockchain", [str(min_height), str(max_height)])

class NamadaDataProcessor:
    """Обработчик данных Namada для преобразования в формат аналитики"""
    
    def __init__(self, api_client: NamadaAPIClient):
        self.api = api_client
        
    def process_block_to_analytics(self, block_data: Dict) -> Dict:
        """Преобразует данные блока в формат для аналитики"""
        if not block_data or 'block' not in block_data:
            return None
            
        block = block_data['block']
        header = block['header']
        
        # Парсим время блока
        block_time = datetime.fromisoformat(header['time'].replace('Z', '+00:00'))
        
        # Подсчитываем транзакции
        transactions = block['data'].get('txs', [])
        tx_count = len(transactions)
        
        # Анализируем транзакции
        tx_analysis = self._analyze_transactions(transactions)
        
        return {
            'block_height': int(header['height']),
            'block_hash': header['last_block_id']['hash'] if header.get('last_block_id') else '',
            'timestamp': block_time.isoformat(),
            'proposer_address': header.get('proposer_address', ''),
            'transaction_count': tx_count,
            'transactions': tx_analysis,
            'validators_count': len(block_data.get('last_commit', {}).get('signatures', [])),
            'chain_id': header.get('chain_id', ''),
            'app_hash': header.get('app_hash', ''),
            'data_hash': header.get('data_hash', '')
        }
    
    def _analyze_transactions(self, transactions: List[str]) -> List[Dict]:
        """Анализирует транзакции в блоке"""
        analyzed_txs = []
        
        for i, tx_data in enumerate(transactions):
            # Базовый анализ транзакции (в реальности нужно декодировать)
            tx_hash = f"tx_{i}_{hash(tx_data) % 1000000}"
            
            # Определяем тип транзакции (упрощенно)
            tx_type = self._determine_tx_type(tx_data)
            
            analyzed_txs.append({
                'hash': tx_hash,
                'type': tx_type,
                'size': len(tx_data),
                'index': i
            })
            
        return analyzed_txs
    
    def _determine_tx_type(self, tx_data: str) -> str:
        """Определяет тип транзакции (упрощенная логика)"""
        # В реальности нужно декодировать транзакцию
        # Пока используем простую эвристику
        if len(tx_data) < 100:
            return "transfer"
        elif len(tx_data) < 500:
            return "stake"
        elif len(tx_data) < 1000:
            return "governance"
        else:
            return "complex"
    
    def get_network_stats(self) -> Dict:
        """Получает статистику сети"""
        status = self.api.get_status()
        if not status:
            return {}
            
        sync_info = status['sync_info']
        latest_height = int(sync_info['latest_block_height'])
        
        # Получаем несколько последних блоков для анализа
        recent_blocks = []
        for i in range(5):  # Последние 5 блоков
            height = latest_height - i
            if height > 0:
                block = self.api.get_block(height)
                if block:
                    recent_blocks.append(self.process_block_to_analytics(block))
        
        # Вычисляем статистику
        if recent_blocks:
            total_txs = sum(b['transaction_count'] for b in recent_blocks if b)
            avg_block_time = self._calculate_avg_block_time(recent_blocks)
            
            return {
                'current_height': latest_height,
                'latest_block_time': sync_info['latest_block_time'],
                'total_recent_transactions': total_txs,
                'average_block_time': avg_block_time,
                'tps': total_txs / (5 * avg_block_time) if avg_block_time > 0 else 0,
                'chain_id': status['node_info']['network'],
                'node_version': status['node_info']['version'],
                'catching_up': sync_info['catching_up']
            }
        
        return {}
    
    def _calculate_avg_block_time(self, blocks: List[Dict]) -> float:
        """Вычисляет среднее время между блоками"""
        if len(blocks) < 2:
            return 6.0  # Примерное время блока в Namada
            
        times = []
        for i in range(len(blocks) - 1):
            if blocks[i] and blocks[i+1]:
                t1 = datetime.fromisoformat(blocks[i]['timestamp'])
                t2 = datetime.fromisoformat(blocks[i+1]['timestamp'])
                diff = abs((t1 - t2).total_seconds())
                times.append(diff)
        
        return sum(times) / len(times) if times else 6.0
    
    def get_recent_transactions(self, limit: int = 50) -> List[Dict]:
        """Получает последние транзакции"""
        status = self.api.get_status()
        if not status:
            return []
            
        latest_height = int(status['sync_info']['latest_block_height'])
        transactions = []
        
        # Ищем транзакции в последних блоках
        for height in range(latest_height, max(latest_height - 20, 1), -1):
            if len(transactions) >= limit:
                break
                
            block = self.api.get_block(height)
            if block:
                block_data = self.process_block_to_analytics(block)
                if block_data and block_data['transactions']:
                    for tx in block_data['transactions']:
                        tx['block_height'] = height
                        tx['timestamp'] = block_data['timestamp']
                        transactions.append(tx)
                        
                        if len(transactions) >= limit:
                            break
        
        return transactions[:limit]

def test_namada_client():
    """Тестирует Namada API клиент"""
    print("🧪 Тестирование Namada API клиента...")
    
    client = NamadaAPIClient()
    processor = NamadaDataProcessor(client)
    
    # Тест статуса
    print("\n📊 Получение статуса сети...")
    status = client.get_status()
    if status:
        print(f"✅ Высота блока: {status['sync_info']['latest_block_height']}")
        print(f"✅ Chain ID: {status['node_info']['network']}")
        print(f"✅ Версия ноды: {status['node_info']['version']}")
    
    # Тест получения блока
    print("\n🧱 Получение последнего блока...")
    block = client.get_block()
    if block:
        block_data = processor.process_block_to_analytics(block)
        if block_data:
            print(f"✅ Блок #{block_data['block_height']}")
            print(f"✅ Транзакций: {block_data['transaction_count']}")
            print(f"✅ Время: {block_data['timestamp']}")
    
    # Тест статистики сети
    print("\n📈 Получение статистики сети...")
    stats = processor.get_network_stats()
    if stats:
        print(f"✅ TPS: {stats.get('tps', 0):.2f}")
        print(f"✅ Среднее время блока: {stats.get('average_block_time', 0):.1f}s")
        print(f"✅ Последние транзакции: {stats.get('total_recent_transactions', 0)}")
    
    # Тест последних транзакций
    print("\n💸 Получение последних транзакций...")
    transactions = processor.get_recent_transactions(10)
    print(f"✅ Найдено транзакций: {len(transactions)}")
    
    for i, tx in enumerate(transactions[:3]):
        print(f"  {i+1}. {tx['type']} - {tx['hash'][:16]}...")
    
    print("\n🎉 Тестирование завершено!")
    return True

if __name__ == "__main__":
    test_namada_client()

