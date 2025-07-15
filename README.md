# Anoma Analytics

Real-time analytics dashboard for Anoma Protocol - monitoring resources, transactions, intents and network performance.

![Anoma Analytics Dashboard](https://img.shields.io/badge/Status-Live-brightgreen)
![React](https://img.shields.io/badge/React-18.2.0-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Python](https://img.shields.io/badge/Python-3.11-yellow)

## 🚀 Live Demo

**Frontend:** [Live Demo](http://your-server-ip) (Replace with your deployment URL)

## 📊 Features

### Real-time Monitoring
- **Dashboard** - Overview of network metrics and performance
- **Network Stats** - TPS, processing times, active resources
- **Resources** - Resource management and filtering
- **Transactions** - Transaction history and analysis
- **Intents** - Intent tracking and resolution
- **Blocks** - Block explorer and statistics

### Key Capabilities
- ✅ **Real-time updates** every 30 seconds
- ✅ **Intent-centric architecture** support
- ✅ **Resource tracking** (TOKEN, NFT, INTENT, CUSTOM)
- ✅ **Performance metrics** monitoring
- ✅ **Responsive design** for desktop and mobile
- ✅ **Live data indicators**

## 🏗️ Architecture

### Frontend (React)
- Modern React 18 with functional components
- Real-time data fetching with automatic refresh
- Responsive UI with mobile support
- Component-based architecture

### Backend (Flask)
- RESTful API endpoints
- Real-time data simulation
- CORS support for cross-origin requests
- Modular service architecture

## 🛠️ Technology Stack

**Frontend:**
- React 18.2.0
- JavaScript ES6+
- CSS3 with responsive design
- Fetch API for HTTP requests

**Backend:**
- Python 3.11
- Flask 2.3.3
- Flask-CORS for cross-origin support
- JSON data handling

**Deployment:**
- Frontend: Static file serving
- Backend: Flask development server
- Real-time updates via polling

## 📁 Project Structure

```
anoma-analytics/
├── anoma-analytics-frontend/     # React frontend application
│   ├── public/                   # Static assets
│   ├── src/                      # Source code
│   │   ├── components/           # React components
│   │   ├── utils/               # Utility functions
│   │   └── App.jsx              # Main application
│   └── package.json             # Frontend dependencies
├── anoma-analytics-backend/      # Flask backend API
│   ├── src/                     # Source code
│   │   ├── services/            # Business logic
│   │   └── main.py              # Main application
│   └── requirements.txt         # Backend dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kolerto99/anoma-analytics.git
cd anoma-analytics
```

2. **Setup Backend**
```bash
cd anoma-analytics-backend
pip install -r requirements.txt
python src/main.py
```

3. **Setup Frontend**
```bash
cd ../anoma-analytics-frontend
npm install
npm start
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📊 API Endpoints

### Core Endpoints
- `GET /api/overview` - Network overview statistics
- `GET /api/network-stats` - Real-time network performance
- `GET /api/resources` - Resource management data
- `GET /api/transactions` - Transaction history
- `GET /api/intents` - Intent tracking data
- `GET /api/blocks` - Block information

### Data Format
All endpoints return JSON with real-time generated data following Anoma Protocol specifications.

## 🔧 Configuration

### Environment Variables

**Frontend (.env.production):**
```
REACT_APP_API_URL=http://193.58.121.166:5000
```

**Backend:**
- Default port: 5000
- CORS enabled for all origins
- Real-time data generation every 30 seconds

## 🎯 Anoma Protocol Integration

This dashboard is designed specifically for Anoma Protocol's intent-centric architecture:

### Resource Types
- **TOKEN** - Fungible tokens with amount and decimals
- **NFT** - Non-fungible tokens with metadata
- **INTENT** - User intentions (stake, vote, swap, transfer)
- **CUSTOM** - Custom resource types

### Intent Processing
- Intent creation and resolution tracking
- Performance metrics for intent processing
- Real-time intent status updates

## 🔄 Real-time Updates

The application implements automatic data refresh:
- **Interval:** 30 seconds
- **Components:** All dashboard pages
- **Indicators:** Live data status display
- **Performance:** Optimized polling with error handling

## 🚀 Deployment

### Production Deployment
The application can be deployed to any server:
- **Frontend:** Static file hosting
- **Backend:** Flask server with CORS enabled

### Deployment Process
1. Frontend built and served as static files
2. Backend running on Flask development server
3. Real-time data generation active
4. CORS configured for cross-origin access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Links

- **Live Application:** [Your Deployment URL]
- **Anoma Protocol:** https://anoma.net
- **Documentation:** https://specs.anoma.net

## 📞 Contact

For questions or support, please open an issue in this repository.

---

**Built with ❤️ for the Anoma ecosystem**

