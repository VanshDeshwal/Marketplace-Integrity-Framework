# Marketplace Integrity Framework - React Frontend

A modern React application for marketplace product analysis using machine learning models.

## Features

- **Duplicate Detection**: Find duplicate products using image embeddings and FAISS vector search
- **Semantic Search**: Search products by meaning using text embeddings and OpenCLIP models
- **Fraud Analysis**: Detect potential fraud indicators in product images using ML models
- **Dark/Light Theme**: Toggle between dark and light themes
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18.2.0**: Modern React with hooks and functional components
- **Lucide React**: Beautiful icons
- **Custom Hooks**: Theme management, toast notifications, API status
- **CSS3**: Modern styling with gradients, animations, and responsive design

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Project Structure

```
src/
├── components/           # React components
│   ├── TabNavigation.js     # Tab navigation component
│   ├── DuplicateDetection.js # Duplicate detection feature
│   ├── SemanticSearch.js    # Semantic search feature
│   ├── FraudAnalysis.js     # Fraud analysis feature
│   ├── ResultsContainer.js  # Results display component
│   └── Toast.js             # Toast notification component
├── hooks/                # Custom React hooks
│   ├── useTheme.js          # Theme management hook
│   ├── useToast.js          # Toast notifications hook
│   └── useApi.js            # API status monitoring hook
├── utils/                # Utility functions
│   ├── api.js               # API configuration and request helpers
│   └── helpers.js           # General helper functions
├── App.js                # Main application component
├── App.css               # Application styles
├── index.js              # React entry point
└── index.css             # Global styles
```

## Backend Integration

The frontend communicates with a FastAPI backend that provides:

- **Duplicate Detection API**: `/find-duplicates` endpoint
- **Semantic Search APIs**: `/search-text` and `/search-image` endpoints  
- **Fraud Analysis API**: `/analyze-fraud` endpoint
- **Health Check**: `/health` endpoint for API status monitoring

### API Configuration

The app automatically detects the environment:
- **Local Development**: Uses `http://localhost:8000`
- **Production**: Uses `https://api.marketplace.vanshdeshwal.dev`

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm run build`: Builds the app for production
- `npm test`: Launches the test runner
- `npm run eject`: Ejects from Create React App (irreversible)

## Features in Detail

### Theme System
- Light and dark themes with smooth transitions
- Persistent theme preference using localStorage
- Theme toggle button with icon animation

### File Upload
- Drag and drop image upload
- File validation and preview
- Progress indicators during upload

### Search Functionality
- Real-time search for text queries
- Debounced input to reduce API calls
- Search type switching (text vs image description)

### Results Display
- Grid layout for search and duplicate results
- Detailed fraud analysis with risk indicators
- Image fallbacks and error handling

### Toast Notifications
- Success, error, warning, and info notifications
- Auto-dismiss with configurable timeout
- Slide-in animations and manual dismiss

## Styling

The application uses modern CSS features:
- CSS Custom Properties for theming
- Flexbox and Grid layouts
- Backdrop filters for glass-morphism effects
- Smooth transitions and animations
- Responsive design with mobile-first approach

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is part of the Marketplace Integrity Framework.
