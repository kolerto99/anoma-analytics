# Anoma Analytics Frontend

React-based frontend application for Anoma Protocol analytics dashboard.

## 🚀 Features

- **Real-time Dashboard** - Network overview with live metrics
- **Network Statistics** - TPS, processing times, resource tracking
- **Resource Management** - Browse and filter network resources
- **Transaction Explorer** - View transaction history and details
- **Intent Tracking** - Monitor intent creation and resolution
- **Block Explorer** - Browse blockchain blocks and statistics

## 🛠️ Technology Stack

- **React 18.2.0** - Modern React with hooks
- **JavaScript ES6+** - Modern JavaScript features
- **CSS3** - Responsive design with flexbox/grid
- **Fetch API** - HTTP requests to backend

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── Dashboard.jsx    # Main dashboard component
│   ├── NetworkStatsPageSimple.jsx
│   ├── ResourcesPageSimple.jsx
│   └── DashboardSimple.jsx
├── utils/
│   └── api.js          # API utility functions
├── App.jsx             # Main application component
└── index.js            # Application entry point
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies**
```bash
npm install
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your backend URL
```

3. **Start development server**
```bash
npm start
```

4. **Build for production**
```bash
npm run build
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
REACT_APP_API_URL=http://localhost:5000
```

For production:
```env
REACT_APP_API_URL=http://your-server-ip:5000
```

## 📊 Components

### Dashboard
- Network overview metrics
- Real-time performance indicators
- Resource and transaction summaries

### Network Stats
- Current TPS (Transactions Per Second)
- Average processing time
- Active resources count
- Pending intents tracking
- Historical data table

### Resources
- Resource listing with pagination
- Filter by resource type (TOKEN, NFT, INTENT, CUSTOM)
- Real-time resource status updates

### Transactions
- Transaction history browser
- Transaction details and metadata
- Real-time transaction monitoring

### Intents
- Intent tracking and status
- Intent type filtering
- Resolution time metrics

### Blocks
- Block explorer functionality
- Block details and statistics
- Real-time block updates

## 🔄 Real-time Updates

All components implement automatic data refresh:

```javascript
useEffect(() => {
  const interval = setInterval(() => {
    fetchData();
  }, 30000); // 30 seconds

  return () => clearInterval(interval);
}, []);
```

## 🎨 Styling

- **Responsive Design** - Mobile-first approach
- **Modern CSS** - Flexbox and Grid layouts
- **Color Scheme** - Professional blue/gray palette
- **Typography** - Clean, readable fonts

## 📱 Mobile Support

- Responsive breakpoints for all screen sizes
- Touch-friendly interface elements
- Optimized performance for mobile devices

## 🔧 API Integration

The frontend communicates with the Flask backend through RESTful APIs:

```javascript
// Example API call
const fetchNetworkStats = async () => {
  const response = await fetch(`${API_URL}/api/network-stats`);
  const data = await response.json();
  return data;
};
```

## 🚀 Deployment

### Development
```bash
npm start
# Runs on http://localhost:3000
```

### Production Build
```bash
npm run build
# Creates optimized build in /build directory
```

### Static Hosting
The built application can be deployed to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3
- Traditional web servers

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## 📦 Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App

## 🤝 Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Implement proper error handling
4. Ensure responsive design
5. Add appropriate comments

## 📝 Notes

- Built with Create React App
- Uses modern React patterns (hooks, functional components)
- Implements real-time data fetching
- Optimized for performance and user experience

