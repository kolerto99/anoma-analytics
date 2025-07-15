# Anoma Analytics Backend

Flask-based REST API backend for Anoma Protocol analytics dashboard.

## 🚀 Features

- **RESTful API** - Clean API endpoints for all data
- **Real-time Data** - Live data generation and updates
- **CORS Support** - Cross-origin requests enabled
- **Modular Architecture** - Organized service layer
- **Anoma Protocol** - Intent-centric data modeling

## 🛠️ Technology Stack

- **Python 3.11** - Modern Python features
- **Flask 2.3.3** - Lightweight web framework
- **Flask-CORS** - Cross-origin resource sharing
- **JSON** - Data serialization format

## 📁 Project Structure

```
src/
├── services/
│   └── data_simulator.py    # Data generation service
├── main.py                  # Main Flask application
└── main_namada.py          # Namada integration (alternative)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Start the server**
```bash
python src/main.py
```

3. **Server runs on**
```
http://localhost:5000
```

## 📊 API Endpoints

### Core Endpoints

#### Network Overview
```http
GET /api/overview
```
Returns general network statistics and metrics.

#### Network Statistics
```http
GET /api/network-stats
```
Returns real-time network performance data:
- Current TPS (Transactions Per Second)
- Average processing time
- Active resources count
- Pending intents
- Historical data points

#### Resources
```http
GET /api/resources
```
Returns paginated list of network resources:
- Resource types: TOKEN, NFT, INTENT, CUSTOM
- Resource metadata and status
- Filtering and pagination support

#### Transactions
```http
GET /api/transactions
```
Returns transaction history and details:
- Transaction metadata
- Processing status
- Timestamp information

#### Intents
```http
GET /api/intents
```
Returns intent tracking data:
- Intent types: stake, vote, swap, transfer
- Intent status and resolution
- Performance metrics

#### Blocks
```http
GET /api/blocks
```
Returns blockchain block information:
- Block metadata
- Transaction counts
- Block timestamps

### Response Format

All endpoints return JSON in the following format:

```json
{
  "status": "success",
  "data": {
    // Endpoint-specific data
  },
  "timestamp": "2025-07-15T23:30:00Z"
}
```

## 🔄 Real-time Data Generation

The backend implements a sophisticated data simulator that generates realistic Anoma Protocol data:

### Data Simulator Features
- **Realistic Metrics** - TPS, processing times, resource counts
- **Time-based Variation** - Natural fluctuations in network activity
- **Resource Types** - Proper Anoma resource modeling
- **Intent Processing** - Simulated intent lifecycle

### Resource Types

#### TOKEN Resources
```json
{
  "id": "resource_001",
  "type": "TOKEN",
  "data": {
    "amount": 1000,
    "token_id": "ANOMA",
    "decimals": 6
  }
}
```

#### NFT Resources
```json
{
  "id": "resource_002",
  "type": "NFT",
  "data": {
    "token_id": "NFT_001",
    "collection": "Anoma Genesis",
    "metadata_uri": "https://metadata.anoma.net/001"
  }
}
```

#### INTENT Resources
```json
{
  "id": "resource_003",
  "type": "INTENT",
  "data": {
    "intent_type": "swap",
    "status": "pending"
  }
}
```

## ⚙️ Configuration

### Environment Variables
```python
# Default configuration
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True
CORS_ORIGINS = '*'
```

### CORS Configuration
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')
```

## 🔧 Services

### Data Simulator Service

Located in `src/services/data_simulator.py`:

```python
class DataSimulator:
    def generate_network_stats(self):
        # Generate realistic network metrics
        
    def generate_resources(self, count=50):
        # Generate Anoma resources
        
    def generate_transactions(self, count=100):
        # Generate transaction data
```

### Key Features:
- **Realistic Data** - Based on actual blockchain patterns
- **Time Variation** - Natural fluctuations over time
- **Anoma Compliance** - Follows Anoma Protocol specifications
- **Performance Optimized** - Efficient data generation

## 🚀 Deployment

### Development
```bash
python src/main.py
# Runs on http://localhost:5000
```

### Production Considerations
- Use production WSGI server (Gunicorn, uWSGI)
- Configure proper CORS origins
- Set up environment variables
- Enable logging and monitoring

### Example Production Setup
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## 🧪 Testing

### Manual Testing
```bash
# Test API endpoints
curl http://localhost:5000/api/overview
curl http://localhost:5000/api/network-stats
curl http://localhost:5000/api/resources
```

### Health Check
```bash
curl http://localhost:5000/health
```

## 📊 Performance

### Optimization Features
- **Efficient Data Generation** - Optimized algorithms
- **Memory Management** - Proper resource cleanup
- **Response Caching** - Reduced computation overhead
- **CORS Optimization** - Minimal overhead

### Monitoring
- Request/response logging
- Performance metrics tracking
- Error handling and reporting

## 🔒 Security

### Current Implementation
- CORS enabled for development
- Basic error handling
- Input validation on endpoints

### Production Recommendations
- Implement authentication/authorization
- Rate limiting
- Input sanitization
- HTTPS enforcement
- Environment-specific CORS origins

## 🤝 Contributing

1. Follow Python PEP 8 style guidelines
2. Add proper docstrings to functions
3. Implement error handling
4. Add unit tests for new features
5. Update API documentation

## 📝 Dependencies

```txt
Flask==2.3.3
Flask-CORS==4.0.0
```

## 🔗 Integration

### Frontend Integration
The backend is designed to work seamlessly with the React frontend:
- RESTful API design
- JSON response format
- CORS support for cross-origin requests
- Real-time data updates

### Anoma Protocol Integration
- Resource modeling based on Anoma specifications
- Intent-centric architecture support
- Compatible with Anoma testnet data structures

