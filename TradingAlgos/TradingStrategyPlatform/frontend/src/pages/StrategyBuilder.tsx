import React, { useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormLabel,
  Checkbox,
  FormGroup,
  Slider,
  Chip,
  Card,
  CardContent,
  Divider,
  Alert,
  Autocomplete,
  ToggleButton,
  ToggleButtonGroup,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  CircularProgress,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  Save as SaveIcon,
  PlayArrow as PlayArrowIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ShowChart as ShowChartIcon,
  Close as CloseIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceDot,
  Area,
  ComposedChart,
} from 'recharts';
import type { BacktestResult, TradeResult } from '../services/api';
import TradingViewChart from '../components/TradingViewChart';

// Define types for our strategy configuration
interface StrategyConfig {
  // Basic Info
  strategyName: string;
  description: string;
  tags: string[];
  
  // Instrument Selection
  assetClass: 'OPTIONS' | 'EQUITY' | 'COMMODITY' | 'CURRENCY' | 'FUTURES';
  instrument: string;
  exchange: string;
  productType: string;
  
  // Trading Type
  tradingType: string;
  
  // Entry Logic
  signalBar: string;
  timeFrame: string;
  breakoutType: string;
  breakoutDirection: string;
  entryConfirmation: {
    volumeConfirmation: boolean;
    candleClose: boolean;
    retest: boolean;
  };
  volumeThreshold: number;
  
  // Advanced Entry Parameters
  entryTimeStart: string; // e.g., "09:15"
  entryTimeEnd: string;   // e.g., "15:00"
  minBreakoutPercentage: number; // Minimum % breakout to enter
  avoidFirstMinutes: number; // Skip first N minutes after market open
  requireGapUp: boolean; // Only enter if gap up/down
  gapPercentage: number; // Minimum gap %
  entryFilters: {
    avoidRangeMarket: boolean; // Skip if market is ranging
    requireTrend: boolean; // Require established trend
    checkPreviousDayClose: boolean; // Compare with previous day
    maxEntryPrice: number; // Don't enter above this price
    minEntryPrice: number; // Don't enter below this price
  };
  
  // Strike/Price Selection (Options)
  expiry?: string;
  strikeSelection?: string;
  strikeOffset?: number;
  optionType?: 'CE' | 'PE' | 'BOTH';
  premiumMin?: number;
  premiumMax?: number;
  
  // Quantity (Equity/Commodity/Futures)
  positionSide?: 'LONG' | 'SHORT' | 'BOTH';
  quantityType?: 'FIXED' | 'CAPITAL' | 'PERCENTAGE';
  quantity?: number;
  capitalPerTrade?: number;
  portfolioPercentage?: number;
  leverage?: number;
  totalCapital?: number; // Total available capital for trading
  
  // Exit Logic
  targetType: string;
  targetValue: number;
  stopLossType: string;
  stopLossValue: number;
  trailingStop: boolean;
  trailingStopValue?: number;
  
  // Risk Management
  maxLossPerDay: number;
  maxTradesPerDay: number;
  riskRewardRatio: number;
}

const steps = [
  'Instrument Selection',
  'Trading Rules & Risk',
  'Strike/Price Setup',
  'Review & Test'
];

const StrategyBuilder: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [isBacktesting, setIsBacktesting] = useState(false);
  const [backtestError, setBacktestError] = useState<string | null>(null);
  const [tradePage, setTradePage] = useState(0);
  const [tradesPerPage, setTradesPerPage] = useState(10);
  const [selectedTrade, setSelectedTrade] = useState<TradeResult | null>(null);
  const [chartDialogOpen, setChartDialogOpen] = useState(false);
  
  // Backtest date range - Default to last 400 days
  const getDefaultDates = () => {
    const today = new Date();
    const endDate = today.toISOString().split('T')[0];
    const startDate = new Date(today.setDate(today.getDate() - 400)).toISOString().split('T')[0];
    return { startDate, endDate };
  };
  
  const defaultDates = getDefaultDates();
  const [backtestStartDate, setBacktestStartDate] = useState(defaultDates.startDate);
  const [backtestEndDate, setBacktestEndDate] = useState(defaultDates.endDate);
  
  // Calculate min date (400 days ago)
  const minBacktestDate = new Date();
  minBacktestDate.setDate(minBacktestDate.getDate() - 400);
  const minDateString = minBacktestDate.toISOString().split('T')[0];
  const [strategy, setStrategy] = useState<StrategyConfig>({
    strategyName: '',
    description: '',
    tags: [],
    assetClass: 'OPTIONS',
    instrument: 'BANKNIFTY',
    exchange: 'NFO',
    productType: 'MIS',
    tradingType: 'Intraday',
    signalBar: 'Second Bar',
    timeFrame: '5 Minute',
    breakoutType: 'Second Bar Breakout',
    breakoutDirection: 'BOTH',
    entryConfirmation: {
      volumeConfirmation: false,
      candleClose: true,
      retest: false,
    },
    volumeThreshold: 150,
    entryTimeStart: '09:15',
    entryTimeEnd: '15:00',
    minBreakoutPercentage: 0.1,
    avoidFirstMinutes: 0,
    requireGapUp: false,
    gapPercentage: 0.5,
    entryFilters: {
      avoidRangeMarket: false,
      requireTrend: false,
      checkPreviousDayClose: false,
      maxEntryPrice: 0,
      minEntryPrice: 0,
    },
    expiry: 'Current Weekly',
    strikeSelection: 'ATM',
    strikeOffset: 0,
    optionType: 'BOTH',
    premiumMin: 50,
    premiumMax: 500,
    positionSide: 'LONG',
    quantityType: 'CAPITAL',
    quantity: 1,
    capitalPerTrade: 50000,
    portfolioPercentage: 10,
    leverage: 1,
    totalCapital: 500000, // Default ₹5 lakh capital
    targetType: 'PERCENTAGE',
    targetValue: 2,
    stopLossType: 'SIGNAL_BAR',
    stopLossValue: 1,
    trailingStop: false,
    trailingStopValue: 0,
    maxLossPerDay: 5000,
    maxTradesPerDay: 5,
    riskRewardRatio: 1.5,
  });

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    // Clear backtest results when moving away from results step
    if (activeStep === 4) {
      // Leaving the Review & Test step
      setBacktestResult(null);
      setBacktestError(null);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    // Clear backtest results when going back from results step
    setBacktestResult(null);
    setBacktestError(null);
  };

  const handleReset = () => {
    setActiveStep(0);
  };

  // Helper function to get instruments for asset class with accurate pricing
  const getInstruments = (assetClass: string) => {
    const instruments: Record<string, Array<{ value: string; label: string; exchange: string; priceRange: [number, number] }>> = {
      'OPTIONS': [
        { value: 'NIFTY', label: 'NIFTY 50', exchange: 'NFO', priceRange: [50, 500] },
        { value: 'BANKNIFTY', label: 'BANK NIFTY', exchange: 'NFO', priceRange: [50, 800] },
        { value: 'FINNIFTY', label: 'FIN NIFTY', exchange: 'NFO', priceRange: [50, 400] },
        { value: 'MIDCPNIFTY', label: 'MIDCAP NIFTY', exchange: 'NFO', priceRange: [30, 300] },
        { value: 'SENSEX', label: 'SENSEX', exchange: 'BFO', priceRange: [50, 600] },
        { value: 'BANKEX', label: 'BANKEX', exchange: 'BFO', priceRange: [50, 500] }
      ],
      'EQUITY': [
        { value: 'RELIANCE', label: 'Reliance Industries', exchange: 'NSE', priceRange: [1250, 1350] },
        { value: 'TCS', label: 'Tata Consultancy Services', exchange: 'NSE', priceRange: [4000, 4300] },
        { value: 'INFY', label: 'Infosys', exchange: 'NSE', priceRange: [1800, 1950] },
        { value: 'HDFCBANK', label: 'HDFC Bank', exchange: 'NSE', priceRange: [1700, 1800] },
        { value: 'ICICIBANK', label: 'ICICI Bank', exchange: 'NSE', priceRange: [1250, 1350] },
        { value: 'SBIN', label: 'State Bank of India', exchange: 'NSE', priceRange: [800, 900] },
        { value: 'BHARTIARTL', label: 'Bharti Airtel', exchange: 'NSE', priceRange: [1550, 1650] },
        { value: 'HINDUNILVR', label: 'Hindustan Unilever', exchange: 'NSE', priceRange: [2350, 2500] },
        { value: 'ITC', label: 'ITC Limited', exchange: 'NSE', priceRange: [460, 490] },
        { value: 'KOTAKBANK', label: 'Kotak Mahindra Bank', exchange: 'NSE', priceRange: [1750, 1850] },
        { value: 'LT', label: 'Larsen & Toubro', exchange: 'NSE', priceRange: [3600, 3800] },
        { value: 'AXISBANK', label: 'Axis Bank', exchange: 'NSE', priceRange: [1100, 1200] },
        { value: 'WIPRO', label: 'Wipro', exchange: 'NSE', priceRange: [560, 600] },
        { value: 'HCLTECH', label: 'HCL Technologies', exchange: 'NSE', priceRange: [1350, 1450] },
        { value: 'MARUTI', label: 'Maruti Suzuki', exchange: 'NSE', priceRange: [12500, 13500] },
        { value: 'TATAMOTORS', label: 'Tata Motors', exchange: 'NSE', priceRange: [750, 850] },
        { value: 'SUNPHARMA', label: 'Sun Pharma', exchange: 'NSE', priceRange: [1750, 1850] },
        { value: 'BAJFINANCE', label: 'Bajaj Finance', exchange: 'NSE', priceRange: [6800, 7200] },
        { value: 'TITAN', label: 'Titan Company', exchange: 'NSE', priceRange: [3400, 3600] },
        { value: 'ASIANPAINT', label: 'Asian Paints', exchange: 'NSE', priceRange: [2350, 2500] },
        { value: 'ULTRACEMCO', label: 'UltraTech Cement', exchange: 'NSE', priceRange: [11000, 11800] },
        { value: 'NESTLEIND', label: 'Nestle India', exchange: 'NSE', priceRange: [2400, 2550] },
        { value: 'ADANIENT', label: 'Adani Enterprises', exchange: 'NSE', priceRange: [2800, 3100] },
        { value: 'ONGC', label: 'ONGC', exchange: 'NSE', priceRange: [280, 320] },
        { value: 'NTPC', label: 'NTPC', exchange: 'NSE', priceRange: [350, 390] },
        { value: 'POWERGRID', label: 'Power Grid Corporation', exchange: 'NSE', priceRange: [310, 340] },
        { value: 'COALINDIA', label: 'Coal India', exchange: 'NSE', priceRange: [450, 490] },
        { value: 'JSWSTEEL', label: 'JSW Steel', exchange: 'NSE', priceRange: [950, 1050] },
        { value: 'TATASTEEL', label: 'Tata Steel', exchange: 'NSE', priceRange: [155, 175] },
        { value: 'HINDALCO', label: 'Hindalco Industries', exchange: 'NSE', priceRange: [650, 720] }
      ],
      'COMMODITY': [
        { value: 'GOLD', label: 'Gold', exchange: 'MCX', priceRange: [60000, 75000] },
        { value: 'GOLDM', label: 'Gold Mini', exchange: 'MCX', priceRange: [6000, 7500] },
        { value: 'SILVER', label: 'Silver', exchange: 'MCX', priceRange: [70000, 90000] },
        { value: 'SILVERM', label: 'Silver Mini', exchange: 'MCX', priceRange: [70, 90] },
        { value: 'CRUDEOIL', label: 'Crude Oil', exchange: 'MCX', priceRange: [5500, 7500] },
        { value: 'CRUDEOILM', label: 'Crude Oil Mini', exchange: 'MCX', priceRange: [5500, 7500] },
        { value: 'NATURALGAS', label: 'Natural Gas', exchange: 'MCX', priceRange: [180, 280] },
        { value: 'COPPER', label: 'Copper', exchange: 'MCX', priceRange: [700, 900] },
        { value: 'ZINC', label: 'Zinc', exchange: 'MCX', priceRange: [230, 290] },
        { value: 'LEAD', label: 'Lead', exchange: 'MCX', priceRange: [180, 220] },
        { value: 'ALUMINIUM', label: 'Aluminium', exchange: 'MCX', priceRange: [210, 260] },
        { value: 'NICKEL', label: 'Nickel', exchange: 'MCX', priceRange: [1800, 2200] }
      ],
      'CURRENCY': [
        { value: 'USDINR', label: 'USD/INR', exchange: 'CDS', priceRange: [82, 85] },
        { value: 'EURINR', label: 'EUR/INR', exchange: 'CDS', priceRange: [88, 92] },
        { value: 'GBPINR', label: 'GBP/INR', exchange: 'CDS', priceRange: [100, 106] },
        { value: 'JPYINR', label: 'JPY/INR', exchange: 'CDS', priceRange: [0.55, 0.62] },
        { value: 'EURUSD', label: 'EUR/USD', exchange: 'CDS', priceRange: [1.05, 1.12] },
        { value: 'GBPUSD', label: 'GBP/USD', exchange: 'CDS', priceRange: [1.22, 1.30] }
      ],
      'FUTURES': [
        { value: 'NIFTY', label: 'NIFTY 50 Futures', exchange: 'NFO', priceRange: [21000, 23000] },
        { value: 'BANKNIFTY', label: 'BANK NIFTY Futures', exchange: 'NFO', priceRange: [45000, 50000] },
        { value: 'FINNIFTY', label: 'FIN NIFTY Futures', exchange: 'NFO', priceRange: [19000, 21000] },
        { value: 'RELIANCE', label: 'Reliance Futures', exchange: 'NFO', priceRange: [2400, 3000] },
        { value: 'TCS', label: 'TCS Futures', exchange: 'NFO', priceRange: [3500, 4200] },
        { value: 'INFY', label: 'Infosys Futures', exchange: 'NFO', priceRange: [1400, 1800] },
        { value: 'HDFCBANK', label: 'HDFC Bank Futures', exchange: 'NFO', priceRange: [1500, 1800] },
        { value: 'ICICIBANK', label: 'ICICI Bank Futures', exchange: 'NFO', priceRange: [1000, 1300] },
        { value: 'SBIN', label: 'SBI Futures', exchange: 'NFO', priceRange: [600, 850] },
        { value: 'BHARTIARTL', label: 'Bharti Airtel Futures', exchange: 'NFO', priceRange: [1200, 1600] }
      ]
    };
    
    return instruments[assetClass] || [];
  };

  // Get accurate price range for instrument
  const getInstrumentPriceRange = (assetClass: string, instrument: string): [number, number] => {
    const instruments = getInstruments(assetClass);
    const found = instruments.find(i => i.value === instrument);
    return found ? found.priceRange : [100, 500];
  };

  // Get exchange for asset class
  const getExchangeForAssetClass = (assetClass: string, instrument: string): string => {
    const instruments = getInstruments(assetClass);
    const found = instruments.find(i => i.value === instrument);
    return found ? found.exchange : 'NSE';
  };

  // Helper function to get default instrument for asset class
  const getDefaultInstrument = (assetClass: string): string => {
    const instruments = getInstruments(assetClass);
    return instruments.length > 0 ? instruments[0].value : '';
  };

  // Helper function to handle asset class change
  const handleAssetClassChange = (newAssetClass: string) => {
    const defaultInstrument = getDefaultInstrument(newAssetClass);
    const exchange = getExchangeForAssetClass(newAssetClass, defaultInstrument);
    console.log('Asset class changed to:', newAssetClass, 'Default instrument:', defaultInstrument, 'Exchange:', exchange);
    
    // Clear previous backtest results when asset class changes
    setBacktestResult(null);
    setBacktestError(null);
    setSelectedTrade(null);
    
    // Set asset-class-specific realistic defaults
    let targetValue = strategy.targetValue;
    let stopLossValue = strategy.stopLossValue;
    
    if (newAssetClass === 'OPTIONS') {
      // Options: Higher percentage targets are realistic due to premium movements
      if (strategy.targetType === 'PERCENTAGE' && targetValue < 10) {
        targetValue = 50; // 50% is realistic for options
      }
      if (strategy.stopLossType === 'PERCENTAGE' && stopLossValue < 10) {
        stopLossValue = 30; // 30% SL for options
      }
    } else {
      // Equity/Futures/Commodity: Lower percentage targets for realistic intraday
      if (strategy.targetType === 'PERCENTAGE' && targetValue > 10) {
        targetValue = 2; // 2% is realistic for intraday equity
      }
      if (strategy.stopLossType === 'PERCENTAGE' && stopLossValue > 5) {
        stopLossValue = 1; // 1% SL for equity
      }
    }
    
    setStrategy({
      ...strategy,
      assetClass: newAssetClass as 'OPTIONS' | 'EQUITY' | 'COMMODITY' | 'CURRENCY' | 'FUTURES',
      instrument: defaultInstrument,
      exchange: exchange,
      targetValue: targetValue,
      stopLossValue: stopLossValue
    });
  };

  // Helper function to handle instrument change
  const handleInstrumentChange = (newInstrument: string) => {
    const exchange = getExchangeForAssetClass(strategy.assetClass, newInstrument);
    console.log('Instrument changed to:', newInstrument, 'Exchange:', exchange);
    
    // Clear previous backtest results when instrument changes
    setBacktestResult(null);
    setBacktestError(null);
    setSelectedTrade(null);
    
    setStrategy({
      ...strategy,
      instrument: newInstrument,
      exchange: exchange
    });
  };

  // Handle trade row click to show chart
  const handleTradeClick = (trade: TradeResult) => {
    setSelectedTrade(trade);
    setChartDialogOpen(true);
  };

  // Custom Candlestick component
  const CandlestickChart = ({ data, width, height, entryPrice, exitPrice }: any) => {
    if (!data || data.length === 0) return null;

    const padding = { top: 20, right: 50, bottom: 60, left: 60 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Calculate price range
    const allPrices = data.flatMap((d: any) => [d.high, d.low]);
    const minPrice = Math.min(...allPrices);
    const maxPrice = Math.max(...allPrices);
    const priceRange = maxPrice - minPrice;
    const pricePadding = priceRange * 0.05;

    // Scale functions
    const priceToY = (price: number) => {
      return padding.top + ((maxPrice + pricePadding - price) / (priceRange + 2 * pricePadding)) * chartHeight;
    };

    const candleWidth = Math.max(2, Math.min(10, chartWidth / data.length - 2));

    return (
      <svg width={width} height={height} style={{ backgroundColor: '#fff' }}>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
          const y = padding.top + chartHeight * pct;
          const price = maxPrice + pricePadding - (maxPrice - minPrice + 2 * pricePadding) * pct;
          return (
            <g key={pct}>
              <line
                x1={padding.left}
                y1={y}
                x2={padding.left + chartWidth}
                y2={y}
                stroke="#e0e0e0"
                strokeDasharray="3,3"
              />
              <text x={padding.left - 10} y={y + 4} textAnchor="end" fontSize="11" fill="#666">
                ₹{price.toFixed(0)}
              </text>
            </g>
          );
        })}

        {/* Entry price line */}
        <line
          x1={padding.left}
          y1={priceToY(entryPrice)}
          x2={padding.left + chartWidth}
          y2={priceToY(entryPrice)}
          stroke="#2196f3"
          strokeWidth="2"
          strokeDasharray="8,4"
        />
        <text
          x={padding.left + chartWidth + 5}
          y={priceToY(entryPrice) + 4}
          fontSize="12"
          fill="#2196f3"
          fontWeight="bold"
        >
          Entry: ₹{entryPrice.toFixed(2)}
        </text>

        {/* Exit price line */}
        <line
          x1={padding.left}
          y1={priceToY(exitPrice)}
          x2={padding.left + chartWidth}
          y2={priceToY(exitPrice)}
          stroke={exitPrice >= entryPrice ? '#4caf50' : '#f44336'}
          strokeWidth="2"
          strokeDasharray="8,4"
        />
        <text
          x={padding.left + chartWidth + 5}
          y={priceToY(exitPrice) + 4}
          fontSize="12"
          fill={exitPrice >= entryPrice ? '#4caf50' : '#f44336'}
          fontWeight="bold"
        >
          Exit: ₹{exitPrice.toFixed(2)}
        </text>

        {/* Candlesticks */}
        {data.map((candle: any, index: number) => {
          const x = padding.left + (index / data.length) * chartWidth;
          const isGreen = candle.close >= candle.open;
          const bodyTop = Math.min(candle.open, candle.close);
          const bodyBottom = Math.max(candle.open, candle.close);
          const bodyHeight = Math.abs(priceToY(candle.open) - priceToY(candle.close));

          let fillColor = isGreen ? '#26a69a' : '#ef5350';
          let strokeColor = isGreen ? '#26a69a' : '#ef5350';
          
          // Highlight entry/exit candles
          if (candle.isEntry) {
            fillColor = '#2196f3';
            strokeColor = '#2196f3';
          } else if (candle.isExit) {
            fillColor = '#ff9800';
            strokeColor = '#ff9800';
          }

          return (
            <g key={index}>
              {/* High-Low wick */}
              <line
                x1={x + candleWidth / 2}
                y1={priceToY(candle.high)}
                x2={x + candleWidth / 2}
                y2={priceToY(candle.low)}
                stroke={strokeColor}
                strokeWidth="1.5"
              />
              
              {/* Candle body */}
              <rect
                x={x}
                y={priceToY(bodyBottom)}
                width={candleWidth}
                height={Math.max(1, bodyHeight)}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth="1"
              />

              {/* Entry/Exit markers */}
              {candle.isEntry && (
                <circle
                  cx={x + candleWidth / 2}
                  cy={priceToY(entryPrice)}
                  r="6"
                  fill="#2196f3"
                  stroke="#fff"
                  strokeWidth="2"
                />
              )}
              {candle.isExit && (
                <circle
                  cx={x + candleWidth / 2}
                  cy={priceToY(exitPrice)}
                  r="6"
                  fill="#ff9800"
                  stroke="#fff"
                  strokeWidth="2"
                />
              )}
            </g>
          );
        })}

        {/* X-axis time labels */}
        {data.filter((_: any, i: number) => i % Math.ceil(data.length / 10) === 0).map((candle: any, index: number, arr: any[]) => {
          const originalIndex = data.indexOf(candle);
          const x = padding.left + (originalIndex / data.length) * chartWidth;
          return (
            <text
              key={originalIndex}
              x={x}
              y={height - padding.bottom + 20}
              textAnchor="middle"
              fontSize="10"
              fill="#666"
              transform={`rotate(-45, ${x}, ${height - padding.bottom + 20})`}
            >
              {candle.time}
            </text>
          );
        })}

        {/* Axes */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={padding.top + chartHeight}
          stroke="#000"
          strokeWidth="1"
        />
        <line
          x1={padding.left}
          y1={padding.top + chartHeight}
          x2={padding.left + chartWidth}
          y2={padding.top + chartHeight}
          stroke="#000"
          strokeWidth="1"
        />
      </svg>
    );
  };

  // Generate full day candlestick chart data with entry/exit points and accurate pricing
  const generateTradeChartData = (trade: TradeResult) => {
    const entryTime = new Date(trade.entry_time);
    const exitTime = new Date(trade.exit_time);
    
    // Get market open time (9:15 AM) on entry date
    const marketOpen = new Date(entryTime);
    marketOpen.setHours(9, 15, 0, 0);
    
    // Get market close time (3:30 PM) on exit date  
    const marketClose = new Date(exitTime);
    marketClose.setHours(15, 30, 0, 0);
    
    // Generate 5-minute candles for the entire trading session
    const candleInterval = 5 * 60 * 1000; // 5 minutes in milliseconds
    const chartData = [];
    
    // Use actual trade prices to ensure accuracy
    const entryPrice = trade.entry_price;
    const exitPrice = trade.exit_price;
    
    // Calculate price movement parameters
    const totalPriceMove = exitPrice - entryPrice;
    const totalTimeMs = exitTime.getTime() - entryTime.getTime();
    const sessionTimeMs = marketClose.getTime() - marketOpen.getTime();
    
    // Start price slightly before entry price (0.5-1% variation)
    const startPrice = entryPrice * (0.995 + Math.random() * 0.01);
    let lastClose = startPrice;
    
    for (let time = marketOpen.getTime(); time <= marketClose.getTime(); time += candleInterval) {
      const currentTime = new Date(time);
      const timestamp = currentTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      
      // Determine if this candle contains entry or exit
      const isEntryCandle = time <= entryTime.getTime() && entryTime.getTime() < time + candleInterval;
      const isExitCandle = time <= exitTime.getTime() && exitTime.getTime() < time + candleInterval;
      
      let open = lastClose;
      let close: number;
      
      // Before entry: hover around start price with small movements
      if (time < entryTime.getTime()) {
        const drift = startPrice * 0.005 * (Math.random() - 0.5);
        close = open + drift;
      }
      // During trade: move from entry to exit price
      else if (time >= entryTime.getTime() && time <= exitTime.getTime()) {
        const tradeProgress = (time - entryTime.getTime()) / totalTimeMs;
        const targetPrice = trade.entry_price + (totalPriceMove * tradeProgress);
        const noise = Math.abs(totalPriceMove) * 0.1 * (Math.random() - 0.5);
        close = targetPrice + noise;
      }
      // After exit: hover around exit price
      else {
        const drift = trade.exit_price * 0.005 * (Math.random() - 0.5);
        close = open + drift;
      }
      
      // For entry candle, ensure it passes through entry price
      if (isEntryCandle) {
        const entryInCandle = Math.random() > 0.5;
        if (entryInCandle) {
          open = trade.entry_price * (0.997 + Math.random() * 0.003);
          close = trade.entry_price * (1.000 + Math.random() * 0.003);
        }
      }
      
      // For exit candle, ensure it passes through exit price
      if (isExitCandle) {
        close = trade.exit_price * (0.9995 + Math.random() * 0.001);
      }
      
      // Generate high and low for the candle
      const maxPrice = Math.max(open, close);
      const minPrice = Math.min(open, close);
      const candleBody = Math.abs(close - open);
      const wickSize = Math.max(candleBody * 0.5, Math.abs(close) * 0.003);
      
      let high = maxPrice + wickSize * (0.5 + Math.random() * 0.5);
      let low = minPrice - wickSize * (0.5 + Math.random() * 0.5);
      
      // Ensure entry/exit prices are within candle range
      if (isEntryCandle) {
        high = Math.max(high, trade.entry_price * 1.002);
        low = Math.min(low, trade.entry_price * 0.998);
      }
      if (isExitCandle) {
        high = Math.max(high, trade.exit_price * 1.002);
        low = Math.min(low, trade.exit_price * 0.998);
      }
      
      // Store candle data
      chartData.push({
        time: timestamp,
        timestamp: currentTime.getTime(),
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        isEntry: isEntryCandle,
        isExit: isExitCandle,
        entryPrice: isEntryCandle ? trade.entry_price : null,
        exitPrice: isExitCandle ? trade.exit_price : null,
      });
      
      lastClose = close;
    }
    
    return chartData;
  };

  const handleSaveStrategy = async () => {
    try {
      // Import the API service
      const { strategyService } = await import('../services/api');
      
      // Convert strategy to API format
      const strategyData = {
        strategyName: strategy.strategyName,
        description: strategy.description,
        tags: strategy.tags,
        assetClass: strategy.assetClass,
        instrument: strategy.instrument,
        exchange: strategy.exchange,
        productType: strategy.productType,
        tradingType: strategy.tradingType,
        signalBar: strategy.signalBar,
        timeFrame: strategy.timeFrame,
        breakoutType: strategy.breakoutType,
        breakoutDirection: strategy.breakoutDirection,
        entryConfirmation: {
          volumeConfirmation: strategy.entryConfirmation.volumeConfirmation,
          candleClose: strategy.entryConfirmation.candleClose,
          retest: strategy.entryConfirmation.retest,
        },
        volumeThreshold: strategy.volumeThreshold,
        expiry: strategy.expiry,
        strikeSelection: strategy.strikeSelection,
        strikeOffset: strategy.strikeOffset,
        optionType: strategy.optionType,
        premiumMin: strategy.premiumMin,
        premiumMax: strategy.premiumMax,
        positionSide: strategy.positionSide,
        quantityType: strategy.quantityType,
        quantity: strategy.quantity,
        capitalPerTrade: strategy.capitalPerTrade,
        portfolioPercentage: strategy.portfolioPercentage,
        leverage: strategy.leverage,
        targetType: strategy.targetType,
        targetValue: strategy.targetValue,
        stopLossType: strategy.stopLossType,
        stopLossValue: strategy.stopLossValue,
        trailingStop: strategy.trailingStop,
        trailingStopValue: strategy.trailingStopValue,
        maxLossPerDay: strategy.maxLossPerDay,
        maxTradesPerDay: strategy.maxTradesPerDay,
        riskRewardRatio: strategy.riskRewardRatio,
      };
      
      const savedStrategy = await strategyService.createStrategy(strategyData);
      alert(`Strategy "${savedStrategy.strategyName}" saved successfully! ID: ${savedStrategy.id}`);
      console.log('Saved strategy:', savedStrategy);
    } catch (error: any) {
      console.error('Error saving strategy:', error);
      alert(`Error saving strategy: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleRunBacktest = async () => {
    console.log('=== BACKTEST STARTED ===');
    setIsBacktesting(true);
    setBacktestError(null);
    setBacktestResult(null);
    
    // Check if backend is running first
    try {
      console.log('Checking backend health...');
      const healthCheck = await fetch('http://localhost:8000/');
      console.log('Health check response:', healthCheck.status);
      
      if (!healthCheck.ok) {
        setBacktestError('Backend server is not responding! Please start the backend: cd backend && python app.py');
        setIsBacktesting(false);
        return;
      }
    } catch (err) {
      console.error('Backend health check failed:', err);
      setBacktestError('Cannot connect to backend server! Please start the backend: cd backend && python app.py');
      setIsBacktesting(false);
      return;
    }
    
    try {
      // Import API services
      console.log('Importing API service...');
      const { backtestService } = await import('../services/api');
      console.log('API service imported successfully');
      
      // Create a temporary strategy ID for demo - encode instrument info
      const tempStrategyId = `temp-${strategy.instrument}-${Date.now()}`;
      
      // Create backtest request with snake_case for Python backend
      // Convert strategy config to snake_case for backend
      const strategyConfigSnakeCase = {
        instrument: strategy.instrument,
        asset_class: strategy.assetClass,
        signal_bar: strategy.signalBar,
        time_frame: strategy.timeFrame,
        breakout_type: strategy.breakoutType,
        breakout_direction: strategy.breakoutDirection,
        entry_time_start: strategy.entryTimeStart,
        entry_time_end: strategy.entryTimeEnd,
        min_breakout_percentage: strategy.minBreakoutPercentage,
        avoid_first_minutes: strategy.avoidFirstMinutes,
        require_gap_up: strategy.requireGapUp,
        gap_percentage: strategy.gapPercentage,
        quantity: strategy.quantity || 1,
        quantity_type: strategy.quantityType,
        capital_per_trade: strategy.capitalPerTrade,
        total_capital: strategy.totalCapital,
        portfolio_percentage: strategy.portfolioPercentage,
        leverage: strategy.leverage,
        target_value: strategy.targetValue,
        target_type: strategy.targetType,
        stop_loss_value: strategy.stopLossValue,
        stop_loss_type: strategy.stopLossType,
      };
      
      const backtestRequest = {
        strategy_id: tempStrategyId,
        start_date: backtestStartDate,
        end_date: backtestEndDate,
        initial_capital: strategy.totalCapital || 500000,
        commission_per_trade: 20,
        slippage_percent: 0.1,
        strategy_config: strategyConfigSnakeCase,
      };
      
      console.log('Sending backtest request:', backtestRequest);
      
      const response = await backtestService.runBacktest(backtestRequest);
      console.log('Backtest response:', response);
      
      // Poll for results after a delay
      setTimeout(async () => {
        try {
          console.log('Fetching backtest results...');
          const result = await backtestService.getBacktestResult(response.backtest_id);
          console.log('Backtest results:', result);
          
          setBacktestResult(result);
          setIsBacktesting(false);
        } catch (resultError: any) {
          console.error('Error fetching backtest results:', resultError);
          
          let errorMsg = 'Unknown error occurred';
          if (resultError.response?.data?.detail) {
            errorMsg = resultError.response.data.detail;
          } else if (resultError.message) {
            errorMsg = resultError.message;
          }
          
          setBacktestError(`Error fetching backtest results: ${errorMsg}`);
          setIsBacktesting(false);
        }
      }, 3000);
      
    } catch (error: any) {
      console.error('=== BACKTEST ERROR ===');
      console.error('Full error object:', error);
      
      let errorMsg = 'An unexpected error occurred';
      
      try {
        if (error?.response?.data?.detail) {
          errorMsg = String(error.response.data.detail);
        } else if (error?.message) {
          errorMsg = String(error.message);
        }
      } catch (stringifyError) {
        console.error('Error stringifying error:', stringifyError);
        errorMsg = 'Could not format error message. Check console.';
      }
      
      setBacktestError(errorMsg);
      setIsBacktesting(false);
    }
  };

  // Render Step 1: Instrument Selection
  const renderInstrumentSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select Instrument & Market
      </Typography>
      
      <Grid container spacing={3}>
        {/* Strategy Name */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Strategy Name"
            value={strategy.strategyName}
            onChange={(e) => setStrategy({ ...strategy, strategyName: e.target.value })}
            required
            helperText="Give your strategy a unique name"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Description"
            value={strategy.description}
            onChange={(e) => setStrategy({ ...strategy, description: e.target.value })}
            helperText="Brief description of your strategy"
          />
        </Grid>

        {/* Asset Class Selection */}
        <Grid item xs={12}>
          <FormControl component="fieldset">
            <FormLabel component="legend">Asset Class</FormLabel>
            <ToggleButtonGroup
              value={strategy.assetClass}
              exclusive
              onChange={(e, value) => value && handleAssetClassChange(value)}
              aria-label="asset class"
              sx={{ mt: 1, flexWrap: 'wrap' }}
            >
              <ToggleButton value="OPTIONS">📊 Index Options</ToggleButton>
              <ToggleButton value="EQUITY">📈 Equity/Stocks</ToggleButton>
              <ToggleButton value="COMMODITY">🌾 Commodities</ToggleButton>
              <ToggleButton value="CURRENCY">💱 Currency</ToggleButton>
              <ToggleButton value="FUTURES">📉 Futures</ToggleButton>
            </ToggleButtonGroup>
          </FormControl>
        </Grid>

        {/* Instrument Selection */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel id="instrument-label">Instrument</InputLabel>
            <Select
              labelId="instrument-label"
              id="instrument-select"
              value={strategy.instrument || ''}
              label="Instrument"
              onChange={(e) => handleInstrumentChange(e.target.value)}
            >
              {getInstruments(strategy.assetClass).length > 0 ? (
                getInstruments(strategy.assetClass).map((instrument) => (
                  <MenuItem key={instrument.value} value={instrument.value}>
                    {instrument.label}
                  </MenuItem>
                ))
              ) : (
                <MenuItem value="" disabled>
                  Please select an asset class first
                </MenuItem>
              )}
            </Select>
          </FormControl>
        </Grid>

        {/* Exchange (Auto-selected, read-only display) */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Exchange"
            value={strategy.exchange}
            disabled
            helperText="Auto-selected based on instrument"
            InputProps={{
              readOnly: true,
            }}
          />
        </Grid>

        {/* Product Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Product Type</InputLabel>
            <Select
              value={strategy.productType}
              label="Product Type"
              onChange={(e) => setStrategy({ ...strategy, productType: e.target.value })}
            >
              <MenuItem value="MIS">MIS (Margin Intraday)</MenuItem>
              <MenuItem value="NRML">NRML (Normal)</MenuItem>
              <MenuItem value="CNC">CNC (Cash & Carry)</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Trading Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Trading Type</InputLabel>
            <Select
              value={strategy.tradingType}
              label="Trading Type"
              onChange={(e) => setStrategy({ ...strategy, tradingType: e.target.value })}
            >
              <MenuItem value="Intraday">Intraday (9:15 AM - 3:15 PM)</MenuItem>
              <MenuItem value="Positional">Positional (Hold till expiry)</MenuItem>
              <MenuItem value="Swing">Swing (2-5 days)</MenuItem>
              <MenuItem value="Short Term">Short Term (1-5 days)</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Contract Info Card */}
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                Contract Specifications
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Lot Size</Typography>
                  <Typography variant="body1">
                    {strategy.instrument === 'BANKNIFTY' ? '15' : '50'}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Tick Size</Typography>
                  <Typography variant="body1">0.05</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Expiry Day</Typography>
                  <Typography variant="body1">Wednesday</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Market Hours</Typography>
                  <Typography variant="body1">9:15 AM - 3:30 PM</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  // Render Step 2: Entry Configuration
  const renderTradingRulesAndRisk = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Trading Rules & Risk Management
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Configure entry conditions, exit rules, and risk parameters
      </Typography>
      
      <Grid container spacing={3}>
        {/* Signal Bar Selection */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Signal Bar</InputLabel>
            <Select
              value={strategy.signalBar}
              label="Signal Bar"
              onChange={(e) => setStrategy({ ...strategy, signalBar: e.target.value })}
            >
              <MenuItem value="First Bar">First Bar (9:15 - 9:20 AM)</MenuItem>
              <MenuItem value="Second Bar">Second Bar (9:20 - 9:25 AM)</MenuItem>
              <MenuItem value="Third Bar">Third Bar (9:25 - 9:30 AM)</MenuItem>
              <MenuItem value="Opening Range">Opening Range (9:15 - 9:45 AM)</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Time Frame</InputLabel>
            <Select
              value={strategy.timeFrame}
              label="Time Frame"
              onChange={(e) => setStrategy({ ...strategy, timeFrame: e.target.value })}
            >
              <MenuItem value="1 Minute">1 Minute</MenuItem>
              <MenuItem value="3 Minute">3 Minute</MenuItem>
              <MenuItem value="5 Minute">5 Minute</MenuItem>
              <MenuItem value="15 Minute">15 Minute</MenuItem>
              <MenuItem value="30 Minute">30 Minute</MenuItem>
              <MenuItem value="1 Hour">1 Hour</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Breakout Type */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Breakout Strategy Type</InputLabel>
            <Select
              value={strategy.breakoutType}
              label="Breakout Strategy Type"
              onChange={(e) => setStrategy({ ...strategy, breakoutType: e.target.value })}
            >
              <MenuItem value="Opening Range Breakout">Opening Range Breakout (ORB)</MenuItem>
              <MenuItem value="Second Bar Breakout">Second Bar Breakout</MenuItem>
              <MenuItem value="First Hour Breakout">First Hour Breakout</MenuItem>
              <MenuItem value="Previous Day High/Low">Previous Day High/Low Breakout</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Breakout Direction */}
        <Grid item xs={12} md={6}>
          <FormControl component="fieldset">
            <FormLabel component="legend">Breakout Direction</FormLabel>
            <RadioGroup
              value={strategy.breakoutDirection}
              onChange={(e) => setStrategy({ ...strategy, breakoutDirection: e.target.value })}
            >
              <FormControlLabel value="BULLISH" control={<Radio />} label="Bullish Only (Upside)" />
              <FormControlLabel value="BEARISH" control={<Radio />} label="Bearish Only (Downside)" />
              <FormControlLabel value="BOTH" control={<Radio />} label="Both Directions" />
            </RadioGroup>
          </FormControl>
        </Grid>

        {/* Entry Confirmation */}
        <Grid item xs={12}>
          <FormControl component="fieldset">
            <FormLabel component="legend">Entry Confirmation (Optional)</FormLabel>
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={strategy.entryConfirmation.volumeConfirmation}
                    onChange={(e) => setStrategy({
                      ...strategy,
                      entryConfirmation: {
                        ...strategy.entryConfirmation,
                        volumeConfirmation: e.target.checked
                      }
                    })}
                  />
                }
                label="Require Volume Confirmation"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={strategy.entryConfirmation.candleClose}
                    onChange={(e) => setStrategy({
                      ...strategy,
                      entryConfirmation: {
                        ...strategy.entryConfirmation,
                        candleClose: e.target.checked
                      }
                    })}
                  />
                }
                label="Require Candle Close Beyond Level"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={strategy.entryConfirmation.retest}
                    onChange={(e) => setStrategy({
                      ...strategy,
                      entryConfirmation: {
                        ...strategy.entryConfirmation,
                        retest: e.target.checked
                      }
                    })}
                  />
                }
                label="Wait for Retest of Breakout Level"
              />
            </FormGroup>
          </FormControl>
        </Grid>

        {/* Volume Threshold */}
        {strategy.entryConfirmation.volumeConfirmation && (
          <Grid item xs={12}>
            <Typography gutterBottom>Volume Threshold: {strategy.volumeThreshold}%</Typography>
            <Slider
              value={strategy.volumeThreshold}
              onChange={(e, value) => setStrategy({ ...strategy, volumeThreshold: value as number })}
              min={100}
              max={300}
              step={10}
              marks
              valueLabelDisplay="auto"
            />
          </Grid>
        )}

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            ⏰ Entry Time Window
          </Typography>
        </Grid>

        {/* Entry Time Window */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Entry Time Start"
            type="time"
            value={strategy.entryTimeStart}
            onChange={(e) => setStrategy({ ...strategy, entryTimeStart: e.target.value })}
            InputLabelProps={{ shrink: true }}
            helperText="Start accepting entries from this time"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Entry Time End"
            type="time"
            value={strategy.entryTimeEnd}
            onChange={(e) => setStrategy({ ...strategy, entryTimeEnd: e.target.value })}
            InputLabelProps={{ shrink: true }}
            helperText="Stop taking new entries after this time"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Avoid First Minutes"
            type="number"
            value={strategy.avoidFirstMinutes}
            onChange={(e) => setStrategy({ ...strategy, avoidFirstMinutes: Number(e.target.value) })}
            helperText="Skip entries for first N minutes after market open"
          />
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            📊 Breakout & Gap Parameters
          </Typography>
        </Grid>

        {/* Breakout Parameters */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Minimum Breakout %"
            type="number"
            value={strategy.minBreakoutPercentage}
            onChange={(e) => setStrategy({ ...strategy, minBreakoutPercentage: Number(e.target.value) })}
            helperText="Minimum % price must break beyond signal bar"
            inputProps={{ step: 0.1, min: 0 }}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControlLabel
            control={
              <Checkbox
                checked={strategy.requireGapUp}
                onChange={(e) => setStrategy({ ...strategy, requireGapUp: e.target.checked })}
              />
            }
            label="Require Gap Up/Down"
          />
          {strategy.requireGapUp && (
            <TextField
              fullWidth
              label="Minimum Gap %"
              type="number"
              value={strategy.gapPercentage}
              onChange={(e) => setStrategy({ ...strategy, gapPercentage: Number(e.target.value) })}
              sx={{ mt: 1 }}
              inputProps={{ step: 0.1, min: 0 }}
            />
          )}
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" gutterBottom fontWeight="bold">
            🛡️ Entry Filters (When NOT to Enter)
          </Typography>
        </Grid>

        {/* Entry Filters */}
        <Grid item xs={12}>
          <FormGroup>
            <FormControlLabel
              control={
                <Checkbox
                  checked={strategy.entryFilters.avoidRangeMarket}
                  onChange={(e) => setStrategy({
                    ...strategy,
                    entryFilters: { ...strategy.entryFilters, avoidRangeMarket: e.target.checked }
                  })}
                />
              }
              label="Avoid Range-Bound Market (Skip if market is sideways)"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={strategy.entryFilters.requireTrend}
                  onChange={(e) => setStrategy({
                    ...strategy,
                    entryFilters: { ...strategy.entryFilters, requireTrend: e.target.checked }
                  })}
                />
              }
              label="Require Established Trend (Check if trend is present)"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={strategy.entryFilters.checkPreviousDayClose}
                  onChange={(e) => setStrategy({
                    ...strategy,
                    entryFilters: { ...strategy.entryFilters, checkPreviousDayClose: e.target.checked }
                  })}
                />
              }
              label="Check Previous Day Close (Compare with yesterday's close)"
            />
          </FormGroup>
        </Grid>

        {/* Price Range Filters */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Maximum Entry Price"
            type="number"
            value={strategy.entryFilters.maxEntryPrice}
            onChange={(e) => setStrategy({
              ...strategy,
              entryFilters: { ...strategy.entryFilters, maxEntryPrice: Number(e.target.value) }
            })}
            helperText="Don't enter if price is above this (0 = no limit)"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Minimum Entry Price"
            type="number"
            value={strategy.entryFilters.minEntryPrice}
            onChange={(e) => setStrategy({
              ...strategy,
              entryFilters: { ...strategy.entryFilters, minEntryPrice: Number(e.target.value) }
            })}
            helperText="Don't enter if price is below this (0 = no limit)"
          />
        </Grid>

        <Grid item xs={12}>
          <Alert severity="info">
            <strong>Entry Summary:</strong> 
            {' '}Entry window: {strategy.entryTimeStart} - {strategy.entryTimeEnd}
            {' '}| Min breakout: {strategy.minBreakoutPercentage}%
            {' '}| Avoid first {strategy.avoidFirstMinutes} mins
          </Alert>
        </Grid>
      </Grid>
    </Box>
  );

  // Render Step 3: Strike/Price Setup
  const renderStrikePriceSetup = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        {strategy.assetClass === 'OPTIONS' ? 'Strike Selection & Option Parameters' : 'Price & Quantity Selection'}
      </Typography>
      
      <Grid container spacing={3}>
        {strategy.assetClass === 'OPTIONS' ? (
          <>
            {/* Expiry Selection */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Expiry</InputLabel>
                <Select
                  value={strategy.expiry}
                  label="Expiry"
                  onChange={(e) => setStrategy({ ...strategy, expiry: e.target.value })}
                >
                  <MenuItem value="Current Weekly">Current Weekly Expiry</MenuItem>
                  <MenuItem value="Next Weekly">Next Weekly Expiry</MenuItem>
                  <MenuItem value="Current Monthly">Current Monthly Expiry</MenuItem>
                  <MenuItem value="Next Monthly">Next Monthly Expiry</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Strike Selection */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Strike Selection</InputLabel>
                <Select
                  value={strategy.strikeSelection}
                  label="Strike Selection"
                  onChange={(e) => setStrategy({ ...strategy, strikeSelection: e.target.value })}
                >
                  <MenuItem value="ATM">ATM (At The Money)</MenuItem>
                  <MenuItem value="ITM 100">ITM 100 (In The Money - 100 points)</MenuItem>
                  <MenuItem value="ITM 200">ITM 200 (In The Money - 200 points)</MenuItem>
                  <MenuItem value="OTM 100">OTM 100 (Out of The Money - 100 points)</MenuItem>
                  <MenuItem value="OTM 200">OTM 200 (Out of The Money - 200 points)</MenuItem>
                  <MenuItem value="OTM 300">OTM 300 (Out of The Money - 300 points)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Option Type */}
            <Grid item xs={12} md={6}>
              <FormControl component="fieldset">
                <FormLabel component="legend">Option Type</FormLabel>
                <RadioGroup
                  value={strategy.optionType}
                  onChange={(e) => setStrategy({ ...strategy, optionType: e.target.value as 'CE' | 'PE' | 'BOTH' })}
                >
                  <FormControlLabel value="CE" control={<Radio />} label="CE (Call Option)" />
                  <FormControlLabel value="PE" control={<Radio />} label="PE (Put Option)" />
                  <FormControlLabel value="BOTH" control={<Radio />} label="Auto-select based on signal" />
                </RadioGroup>
              </FormControl>
            </Grid>

            {/* Premium Range */}
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Premium Range (Optional)</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Min Premium"
                    type="number"
                    value={strategy.premiumMin}
                    onChange={(e) => setStrategy({ ...strategy, premiumMin: Number(e.target.value) })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Max Premium"
                    type="number"
                    value={strategy.premiumMax}
                    onChange={(e) => setStrategy({ ...strategy, premiumMax: Number(e.target.value) })}
                  />
                </Grid>
              </Grid>
            </Grid>
          </>
        ) : (
          <>
            {/* Position Side */}
            <Grid item xs={12} md={6}>
              <FormControl component="fieldset">
                <FormLabel component="legend">Position Side</FormLabel>
                <RadioGroup
                  value={strategy.positionSide}
                  onChange={(e) => setStrategy({ ...strategy, positionSide: e.target.value as 'LONG' | 'SHORT' | 'BOTH' })}
                >
                  <FormControlLabel value="LONG" control={<Radio />} label="Long (Buy)" />
                  <FormControlLabel value="SHORT" control={<Radio />} label="Short (Sell)" />
                  <FormControlLabel value="BOTH" control={<Radio />} label="Both (Based on Signal)" />
                </RadioGroup>
              </FormControl>
            </Grid>

            {/* Quantity Type */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Quantity Type</InputLabel>
                <Select
                  value={strategy.quantityType}
                  label="Quantity Type"
                  onChange={(e) => setStrategy({ ...strategy, quantityType: e.target.value as 'FIXED' | 'CAPITAL' | 'PERCENTAGE' })}
                >
                  <MenuItem value="FIXED">Fixed Quantity</MenuItem>
                  <MenuItem value="CAPITAL">Fixed Capital Allocation</MenuItem>
                  <MenuItem value="PERCENTAGE">Percentage of Portfolio</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Total Capital */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Total Trading Capital (₹)"
                type="number"
                value={strategy.totalCapital}
                onChange={(e) => setStrategy({ ...strategy, totalCapital: Number(e.target.value) })}
                helperText="Your total available capital for trading"
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1, color: 'text.secondary' }}>₹</Typography>
                }}
              />
            </Grid>

            {/* Quantity Input */}
            <Grid item xs={12} md={6}>
              {strategy.quantityType === 'FIXED' && (
                <TextField
                  fullWidth
                  label="Quantity"
                  type="number"
                  value={strategy.quantity}
                  onChange={(e) => setStrategy({ ...strategy, quantity: Number(e.target.value) })}
                  helperText={`Fixed number of lots/shares per trade`}
                />
              )}
              {strategy.quantityType === 'CAPITAL' && (
                <TextField
                  fullWidth
                  label="Capital Per Trade (₹)"
                  type="number"
                  value={strategy.capitalPerTrade}
                  onChange={(e) => setStrategy({ ...strategy, capitalPerTrade: Number(e.target.value) })}
                  helperText={`${((strategy.capitalPerTrade || 0) / (strategy.totalCapital || 1) * 100).toFixed(1)}% of total capital`}
                />
              )}
              {strategy.quantityType === 'PERCENTAGE' && (
                <TextField
                  fullWidth
                  label="Portfolio Percentage (%)"
                  type="number"
                  value={strategy.portfolioPercentage}
                  onChange={(e) => setStrategy({ ...strategy, portfolioPercentage: Number(e.target.value) })}
                  helperText={`₹${((strategy.portfolioPercentage || 0) / 100 * (strategy.totalCapital || 0)).toFixed(0)} per trade`}
                />
              )}
            </Grid>

            {/* Smart Quantity Calculator */}
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mt: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  💡 Smart Position Sizing:
                </Typography>
                {strategy.quantityType === 'FIXED' && (
                  <Typography variant="body2">
                    Fixed Quantity: <strong>{strategy.quantity || 1} lots/shares</strong> per trade
                  </Typography>
                )}
                {strategy.quantityType === 'CAPITAL' && (
                  <>
                    <Typography variant="body2">
                      Capital Allocation: <strong>₹{(strategy.capitalPerTrade || 0).toLocaleString()}</strong> per trade
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {['OPTIONS', 'COMMODITY', 'CURRENCY', 'FUTURES'].includes(strategy.assetClass) ? (
                        <>
                          At ₹100 premium → <strong>{Math.floor((strategy.capitalPerTrade || 0) / 100)} lots</strong> |
                          At ₹200 premium → <strong>{Math.floor((strategy.capitalPerTrade || 0) / 200)} lots</strong>
                        </>
                      ) : strategy.instrument === 'RELIANCE' ? (
                        <>
                          At ₹1,300/share → <strong>{Math.floor((strategy.capitalPerTrade || 0) / 1300)} shares</strong>
                        </>
                      ) : strategy.instrument === 'TCS' ? (
                        <>
                          At ₹4,200/share → <strong>{Math.floor((strategy.capitalPerTrade || 0) / 4200)} shares</strong>
                        </>
                      ) : (
                        <>Quantity will be calculated based on entry price</>
                      )}
                    </Typography>
                  </>
                )}
                {strategy.quantityType === 'PERCENTAGE' && (
                  <>
                    <Typography variant="body2">
                      Capital Per Trade: <strong>₹{((strategy.portfolioPercentage || 0) / 100 * (strategy.totalCapital || 0)).toLocaleString()}</strong> ({strategy.portfolioPercentage}% of ₹{(strategy.totalCapital || 0).toLocaleString()})
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      Maximum {strategy.maxTradesPerDay} trades → Uses <strong>{(strategy.portfolioPercentage || 0) * strategy.maxTradesPerDay}%</strong> of total capital
                    </Typography>
                  </>
                )}
                <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary' }}>
                  With {strategy.leverage || 1}x leverage → Effective capital: ₹{((strategy.capitalPerTrade || 0) * (strategy.leverage || 1)).toLocaleString()}
                </Typography>
              </Alert>
            </Grid>

            {/* Leverage */}
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Leverage: {strategy.leverage}x</Typography>
              <Slider
                value={strategy.leverage}
                onChange={(e, value) => setStrategy({ ...strategy, leverage: value as number })}
                min={1}
                max={5}
                step={0.5}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>
          </>
        )}

        {/* Section Divider */}
        <Grid item xs={12}>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Exit & Risk Management
          </Typography>
        </Grid>

        {/* Target Configuration */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold" sx={{ mt: 1 }}>
            🎯 Profit Target Configuration
          </Typography>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Target Type</InputLabel>
            <Select
              value={strategy.targetType}
              label="Target Type"
              onChange={(e) => setStrategy({ ...strategy, targetType: e.target.value })}
            >
              <MenuItem value="PERCENTAGE">Percentage (%) - Based on Entry Price</MenuItem>
              <MenuItem value="POINTS">Absolute Points - Fixed Point Move</MenuItem>
              <MenuItem value="PREMIUM">Premium Value - For Options Trading</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Target Value"
            type="number"
            value={strategy.targetValue}
            onChange={(e) => setStrategy({ ...strategy, targetValue: Number(e.target.value) })}
            helperText={
              strategy.targetType === 'PERCENTAGE' 
                ? strategy.assetClass === 'OPTIONS' 
                  ? 'Options: 30-100% realistic (e.g., 50 for 50%)' 
                  : 'Equity: 0.5-5% realistic (e.g., 2 for 2%)'
                : strategy.targetType === 'POINTS'
                ? 'e.g., 50 points profit'
                : 'e.g., ₹50 premium profit'
            }
            error={
              strategy.targetType === 'PERCENTAGE' && 
              strategy.assetClass !== 'OPTIONS' && 
              strategy.targetValue > 10
            }
          />
        </Grid>
        
        {strategy.targetType === 'PERCENTAGE' && strategy.assetClass !== 'OPTIONS' && strategy.targetValue > 10 && (
          <Grid item xs={12}>
            <Alert severity="warning">
              ⚠️ <strong>Unrealistic Target!</strong> {strategy.targetValue}% is too high for intraday equity trading. 
              Typical intraday moves: 0.5-3%. Consider using <strong>1-5%</strong> for realistic results.
            </Alert>
          </Grid>
        )}

        {/* Stop Loss Configuration */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom fontWeight="bold" sx={{ mt: 2 }}>
            🛡️ Stop Loss Configuration
          </Typography>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Stop Loss Type</InputLabel>
            <Select
              value={strategy.stopLossType}
              label="Stop Loss Type"
              onChange={(e) => setStrategy({ ...strategy, stopLossType: e.target.value })}
            >
              <MenuItem value="SIGNAL_BAR">Signal Bar Level - High/Low of Signal Bar</MenuItem>
              <MenuItem value="PERCENTAGE">Percentage (%) - Based on Entry Price</MenuItem>
              <MenuItem value="POINTS">Absolute Points - Fixed Point Move</MenuItem>
              <MenuItem value="PREMIUM">Premium Value - For Options Trading</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {strategy.stopLossType !== 'SIGNAL_BAR' && (
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Stop Loss Value"
              type="number"
              value={strategy.stopLossValue}
              onChange={(e) => setStrategy({ ...strategy, stopLossValue: Number(e.target.value) })}
              helperText={
                strategy.stopLossType === 'PERCENTAGE' 
                  ? strategy.assetClass === 'OPTIONS'
                    ? 'Options: 20-50% realistic (e.g., 30 for 30%)'
                    : 'Equity: 0.3-2% realistic (e.g., 1 for 1%)'
                  : strategy.stopLossType === 'POINTS'
                  ? 'e.g., 20 points maximum loss'
                  : 'e.g., ₹30 premium maximum loss'
              }
              error={
                strategy.stopLossType === 'PERCENTAGE' && 
                strategy.assetClass !== 'OPTIONS' && 
                strategy.stopLossValue > 5
              }
            />
          </Grid>
        )}
        
        {strategy.stopLossType === 'PERCENTAGE' && strategy.assetClass !== 'OPTIONS' && strategy.stopLossValue > 5 && (
          <Grid item xs={12}>
            <Alert severity="error">
              🚨 <strong>Excessive Risk!</strong> {strategy.stopLossValue}% stop loss is too wide for intraday equity. 
              Recommended: <strong>0.5-2%</strong> to protect capital.
            </Alert>
          </Grid>
        )}

        {strategy.stopLossType === 'SIGNAL_BAR' && (
          <Grid item xs={12} md={6}>
            <Alert severity="info" sx={{ mt: 1 }}>
              <strong>Signal Bar Stop Loss:</strong><br />
              • Bullish trades: SL = Signal Bar LOW<br />
              • Bearish trades: SL = Signal Bar HIGH<br />
              Dynamic stop based on market structure
            </Alert>
          </Grid>
        )}

        {/* Trailing Stop */}
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={strategy.trailingStop}
                onChange={(e) => setStrategy({ ...strategy, trailingStop: e.target.checked })}
              />
            }
            label="Enable Trailing Stop Loss"
          />
        </Grid>

        {strategy.trailingStop && (
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Trailing Stop Value (%)"
              type="number"
              value={strategy.trailingStopValue}
              onChange={(e) => setStrategy({ ...strategy, trailingStopValue: Number(e.target.value) })}
              helperText="Lock profit when price moves favorably"
            />
          </Grid>
        )}

        <Grid item xs={12}>
          <Divider sx={{ my: 2 }} />
        </Grid>

        {/* Risk Management */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Risk Management Parameters
          </Typography>
        </Grid>

        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Max Loss Per Day (₹)"
            type="number"
            value={strategy.maxLossPerDay}
            onChange={(e) => setStrategy({ ...strategy, maxLossPerDay: Number(e.target.value) })}
          />
        </Grid>

        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Max Trades Per Day"
            type="number"
            value={strategy.maxTradesPerDay}
            onChange={(e) => setStrategy({ ...strategy, maxTradesPerDay: Number(e.target.value) })}
          />
        </Grid>

        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Risk/Reward Ratio"
            type="number"
            value={strategy.riskRewardRatio}
            onChange={(e) => setStrategy({ ...strategy, riskRewardRatio: Number(e.target.value) })}
            helperText="Minimum R:R (e.g., 1.5 means 1.5:1)"
          />
        </Grid>

        <Grid item xs={12}>
          <Alert severity="info">
            <strong>Risk Summary:</strong> Max daily loss: ₹{strategy.maxLossPerDay} | 
            Max trades: {strategy.maxTradesPerDay} | 
            Target: {strategy.targetValue}{strategy.targetType === 'PERCENTAGE' ? '%' : ' pts'} | 
            Stop Loss: {strategy.stopLossValue}{strategy.stopLossType === 'PERCENTAGE' ? '%' : ' pts'}
          </Alert>
        </Grid>
      </Grid>
    </Box>
  );

  // Render Step 5: Review & Test
  const renderReviewTest = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Review & Test Your Strategy
      </Typography>
      
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" color="primary" gutterBottom>
                Strategy Summary
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Strategy Name</Typography>
              <Typography variant="body1">{strategy.strategyName || 'Unnamed Strategy'}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Asset Class</Typography>
              <Typography variant="body1">{strategy.assetClass}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Instrument</Typography>
              <Typography variant="body1">{strategy.instrument}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Trading Type</Typography>
              <Typography variant="body1">{strategy.tradingType}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Breakout Type</Typography>
              <Typography variant="body1">{strategy.breakoutType}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Signal Bar & Timeframe</Typography>
              <Typography variant="body1">{strategy.signalBar} - {strategy.timeFrame}</Typography>
            </Grid>

            {strategy.assetClass === 'OPTIONS' && (
              <>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Strike Selection</Typography>
                  <Typography variant="body1">{strategy.strikeSelection}</Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Expiry</Typography>
                  <Typography variant="body1">{strategy.expiry}</Typography>
                </Grid>
              </>
            )}
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Target</Typography>
              <Typography variant="body1">
                {strategy.targetValue}{strategy.targetType === 'PERCENTAGE' ? '%' : ' points'}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Stop Loss</Typography>
              <Typography variant="body1">
                {strategy.stopLossValue}{strategy.stopLossType === 'PERCENTAGE' ? '%' : ' points'}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Max Loss Per Day</Typography>
              <Typography variant="body1">₹{strategy.maxLossPerDay}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Max Trades Per Day</Typography>
              <Typography variant="body1">{strategy.maxTradesPerDay}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Alert severity="success" sx={{ mb: 2 }}>
        Your strategy is ready to test! You can save it for later or run a backtest now.
      </Alert>

      {/* Backtest Date Range Configuration */}
      <Card variant="outlined" sx={{ mb: 3, bgcolor: '#f8f9fa' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📅 Backtest Date Range
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Select the time period for testing your strategy (Past 400 days of historical data available)
          </Typography>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <strong>Data Availability:</strong> Historical data is available from {minDateString} to today
          </Alert>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={backtestStartDate}
                onChange={(e) => setBacktestStartDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                helperText="Past 400 days available"
                inputProps={{
                  min: minDateString,
                  max: backtestEndDate,
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={backtestEndDate}
                onChange={(e) => setBacktestEndDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                helperText="Up to today"
                inputProps={{
                  min: backtestStartDate,
                  max: new Date().toISOString().split('T')[0], // Can't test future
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info" icon={false}>
                <strong>Testing Period:</strong> {backtestStartDate} to {backtestEndDate}
                {' '}({Math.ceil((new Date(backtestEndDate).getTime() - new Date(backtestStartDate).getTime()) / (1000 * 60 * 60 * 24))} days)
              </Alert>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>💾 Save Strategy</Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Save this strategy configuration to your library for future use and modifications.
              </Typography>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                fullWidth
                onClick={handleSaveStrategy}
              >
                Save Strategy
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>🧪 Run Backtest</Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Test this strategy on historical data to see how it would have performed.
              </Typography>
              <Button
                variant="contained"
                color="secondary"
                startIcon={<AssessmentIcon />}
                fullWidth
                onClick={handleRunBacktest}
                disabled={isBacktesting}
              >
                {isBacktesting ? 'Running Backtest...' : 'Run Backtest'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Loading State */}
      {isBacktesting && (
        <Box sx={{ mt: 3 }}>
          <Card variant="outlined">
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <CircularProgress size={24} />
                <Typography>Running backtest on historical data...</Typography>
              </Box>
              <LinearProgress sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Error State */}
      {backtestError && (
        <Alert severity="error" sx={{ mt: 3 }} onClose={() => setBacktestError(null)}>
          {backtestError}
        </Alert>
      )}

      {/* Backtest Results */}
      {backtestResult && (
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ShowChartIcon /> Backtest Results
            </Typography>
            <Button
              variant="outlined"
              color="error"
              startIcon={<RefreshIcon />}
              onClick={() => {
                setBacktestResult(null);
                setBacktestError(null);
                setSelectedTrade(null);
                setTradePage(0);
              }}
            >
              Clear Results
            </Button>
          </Box>

          {/* Performance Metrics Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
                <CardContent>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Net Profit</Typography>
                  <Typography variant="h4">
                    ₹{backtestResult.metrics.net_profit.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    {backtestResult.metrics.net_profit_percent.toFixed(2)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
                <CardContent>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Win Rate</Typography>
                  <Typography variant="h4">{backtestResult.metrics.win_rate.toFixed(2)}%</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    {backtestResult.metrics.winning_trades}/{backtestResult.metrics.total_trades} trades
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card sx={{ bgcolor: 'info.main', color: 'white' }}>
                <CardContent>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Profit Factor</Typography>
                  <Typography variant="h4">{backtestResult.metrics.profit_factor.toFixed(2)}</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Total Trades: {backtestResult.metrics.total_trades}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card sx={{ bgcolor: 'error.main', color: 'white' }}>
                <CardContent>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Max Drawdown</Typography>
                  <Typography variant="h4">{backtestResult.metrics.max_drawdown_percent.toFixed(2)}%</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    ₹{backtestResult.metrics.max_drawdown.toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Detailed Metrics */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>📊 Performance Metrics</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Initial Capital</Typography>
                      <Typography variant="body1">₹{backtestResult.initial_capital.toLocaleString()}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Final Capital</Typography>
                      <Typography variant="body1">₹{backtestResult.final_capital.toLocaleString()}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Total Profit</Typography>
                      <Typography variant="body1" color="success.main">
                        ₹{backtestResult.metrics.total_profit.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Total Loss</Typography>
                      <Typography variant="body1" color="error.main">
                        ₹{backtestResult.metrics.total_loss.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Avg Profit/Trade</Typography>
                      <Typography variant="body1">
                        ₹{backtestResult.metrics.average_profit_per_trade.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Avg Loss/Trade</Typography>
                      <Typography variant="body1">
                        ₹{Math.abs(backtestResult.metrics.average_loss_per_trade).toLocaleString()}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>📈 Trade Statistics</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Winning Trades</Typography>
                      <Typography variant="body1" color="success.main">
                        {backtestResult.metrics.winning_trades}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Losing Trades</Typography>
                      <Typography variant="body1" color="error.main">
                        {backtestResult.metrics.losing_trades}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Largest Profit</Typography>
                      <Typography variant="body1" color="success.main">
                        ₹{backtestResult.metrics.largest_profit.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Largest Loss</Typography>
                      <Typography variant="body1" color="error.main">
                        ₹{Math.abs(backtestResult.metrics.largest_loss).toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Consecutive Wins</Typography>
                      <Typography variant="body1">{backtestResult.metrics.consecutive_wins}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Consecutive Losses</Typography>
                      <Typography variant="body1">{backtestResult.metrics.consecutive_losses}</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Trade History */}
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📋 All Trades ({backtestResult.trades.length} Total)
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>#</TableCell>
                      <TableCell>Side</TableCell>
                      <TableCell>Entry Time</TableCell>
                      <TableCell>Exit Time</TableCell>
                      <TableCell align="right">Entry Price</TableCell>
                      <TableCell align="right">Exit Price</TableCell>
                      <TableCell align="right">Qty</TableCell>
                      <TableCell align="right">P&L</TableCell>
                      <TableCell align="right">P&L %</TableCell>
                      <TableCell>Exit Reason</TableCell>
                      <TableCell align="center">Chart</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {backtestResult.trades
                      .slice(tradePage * tradesPerPage, tradePage * tradesPerPage + tradesPerPage)
                      .map((trade, index) => (
                        <TableRow 
                          key={index}
                          hover
                          sx={{ 
                            cursor: 'pointer',
                            '&:hover': { bgcolor: 'action.hover' }
                          }}
                        >
                          <TableCell>{tradePage * tradesPerPage + index + 1}</TableCell>
                          <TableCell>
                            <Chip 
                              label={trade.position_type === 'BULLISH' ? '🟢 BULL' : '🔴 BEAR'} 
                              size="small"
                              sx={{
                                bgcolor: trade.position_type === 'BULLISH' ? 'success.light' : 'error.light',
                                color: trade.position_type === 'BULLISH' ? 'success.dark' : 'error.dark',
                                fontWeight: 'bold'
                              }}
                            />
                          </TableCell>
                          <TableCell>{new Date(trade.entry_time).toLocaleString()}</TableCell>
                          <TableCell>{new Date(trade.exit_time).toLocaleString()}</TableCell>
                          <TableCell align="right">₹{trade.entry_price.toFixed(2)}</TableCell>
                          <TableCell align="right">₹{trade.exit_price.toFixed(2)}</TableCell>
                          <TableCell align="right">{trade.quantity}</TableCell>
                          <TableCell 
                            align="right" 
                            sx={{ 
                              color: trade.profit_loss >= 0 ? 'success.main' : 'error.main',
                              fontWeight: 'bold'
                            }}
                          >
                            {trade.profit_loss >= 0 ? <TrendingUpIcon sx={{ fontSize: 16, verticalAlign: 'middle' }} /> : <TrendingDownIcon sx={{ fontSize: 16, verticalAlign: 'middle' }} />}
                            ₹{Math.abs(trade.profit_loss).toFixed(2)}
                          </TableCell>
                          <TableCell 
                            align="right"
                            sx={{ color: trade.profit_loss_percent >= 0 ? 'success.main' : 'error.main' }}
                          >
                            {trade.profit_loss_percent.toFixed(2)}%
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={trade.exit_reason} 
                              size="small" 
                              color={trade.exit_reason === 'TARGET' ? 'success' : 'default'}
                            />
                          </TableCell>
                          <TableCell align="center">
                            <IconButton 
                              size="small" 
                              color="primary"
                              onClick={() => handleTradeClick(trade)}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={backtestResult.trades.length}
                rowsPerPage={tradesPerPage}
                page={tradePage}
                onPageChange={(event, newPage) => setTradePage(newPage)}
                onRowsPerPageChange={(event) => {
                  setTradesPerPage(parseInt(event.target.value, 10));
                  setTradePage(0);
                }}
              />
            </CardContent>
          </Card>

          {/* Trade Chart Dialog */}
          <Dialog 
            open={chartDialogOpen} 
            onClose={() => setChartDialogOpen(false)}
            maxWidth="lg"
            fullWidth
          >
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">Trade Chart</Typography>
                <IconButton onClick={() => setChartDialogOpen(false)} size="small">
                  <CloseIcon />
                </IconButton>
              </Box>
            </DialogTitle>
            <DialogContent>
              {selectedTrade && (
                <Box>
                  {/* Trade Details */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" color="text.secondary">Entry Time</Typography>
                      <Typography variant="body1">
                        {new Date(selectedTrade.entry_time).toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" color="text.secondary">Exit Time</Typography>
                      <Typography variant="body1">
                        {new Date(selectedTrade.exit_time).toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" color="text.secondary">Duration</Typography>
                      <Typography variant="body1">
                        {Math.round((new Date(selectedTrade.exit_time).getTime() - new Date(selectedTrade.entry_time).getTime()) / 60000)} mins
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" color="text.secondary">P&L</Typography>
                      <Typography 
                        variant="h6" 
                        sx={{ color: selectedTrade.profit_loss >= 0 ? 'success.main' : 'error.main' }}
                      >
                        ₹{selectedTrade.profit_loss.toFixed(2)} ({selectedTrade.profit_loss_percent.toFixed(2)}%)
                      </Typography>
                    </Grid>
                  </Grid>

                  {/* Candlestick Chart */}
                  <Box sx={{ width: '100%', height: 600, mt: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      📊 Full Trading Session (9:15 AM - 3:30 PM) - 5 Minute Candles
                    </Typography>
                    <Box sx={{ overflowX: 'auto', overflowY: 'hidden' }}>
                      <CandlestickChart
                        data={generateTradeChartData(selectedTrade)}
                        width={Math.max(1200, generateTradeChartData(selectedTrade).length * 12)}
                        height={500}
                        entryPrice={selectedTrade.entry_price}
                        exitPrice={selectedTrade.exit_price}
                      />
                    </Box>
                    
                    {/* Chart Legend */}
                    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, mt: 2, flexWrap: 'wrap' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#26a69a', border: '1px solid #000' }} />
                        <Typography variant="caption">Bullish Candle (Close &gt; Open)</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#ef5350', border: '1px solid #000' }} />
                        <Typography variant="caption">Bearish Candle (Close &lt; Open)</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#2196f3', border: '2px solid #fff', borderRadius: '50%' }} />
                        <Typography variant="caption" fontWeight="bold" color="primary">🔵 Entry Point</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#ff9800', border: '2px solid #fff', borderRadius: '50%' }} />
                        <Typography variant="caption" fontWeight="bold" color="warning.main">🟠 Exit Point</Typography>
                      </Box>
                    </Box>
                  </Box>

                  {/* Legacy Recharts backup (hidden) */}
                  <Box sx={{ display: 'none' }}>
                    <ResponsiveContainer>
                      <ComposedChart 
                        data={generateTradeChartData(selectedTrade)}
                        margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                        <XAxis 
                          dataKey="time" 
                          angle={-45}
                          textAnchor="end"
                          height={80}
                          interval="preserveStartEnd"
                          tick={{ fontSize: 10 }}
                        />
                        <YAxis 
                          domain={['auto', 'auto']}
                          tick={{ fontSize: 12 }}
                          label={{ value: 'Price (₹)', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip 
                          content={({ active, payload }) => {
                            if (active && payload && payload.length > 0) {
                              const data = payload[0].payload;
                              return (
                                <Paper sx={{ p: 1.5, bgcolor: 'background.paper' }}>
                                  <Typography variant="caption" display="block" fontWeight="bold">
                                    {data.time}
                                  </Typography>
                                  <Typography variant="caption" display="block" color="primary.main">
                                    O: ₹{data.open?.toFixed(2)}
                                  </Typography>
                                  <Typography variant="caption" display="block" color="success.main">
                                    H: ₹{data.high?.toFixed(2)}
                                  </Typography>
                                  <Typography variant="caption" display="block" color="error.main">
                                    L: ₹{data.low?.toFixed(2)}
                                  </Typography>
                                  <Typography variant="caption" display="block" color="text.primary">
                                    C: ₹{data.close?.toFixed(2)}
                                  </Typography>
                                  {data.isEntry && (
                                    <Typography variant="caption" display="block" color="primary.main" fontWeight="bold">
                                      🔵 ENTRY CANDLE
                                    </Typography>
                                  )}
                                  {data.isExit && (
                                    <Typography variant="caption" display="block" color="secondary.main" fontWeight="bold">
                                      🔴 EXIT CANDLE
                                    </Typography>
                                  )}
                                </Paper>
                              );
                            }
                            return null;
                          }}
                        />
                        
                        {/* Entry Price Line */}
                        <ReferenceLine 
                          y={selectedTrade.entry_price} 
                          stroke="#2196f3" 
                          strokeDasharray="8 4"
                          strokeWidth={2}
                          label={{ 
                            value: `📍 Entry: ₹${selectedTrade.entry_price.toFixed(2)}`, 
                            position: 'right', 
                            fill: '#2196f3',
                            fontSize: 12,
                            fontWeight: 'bold'
                          }}
                        />
                        
                        {/* Exit Price Line */}
                        <ReferenceLine 
                          y={selectedTrade.exit_price} 
                          stroke={selectedTrade.profit_loss >= 0 ? '#4caf50' : '#f44336'}
                          strokeDasharray="8 4"
                          strokeWidth={2}
                          label={{ 
                            value: `🎯 Exit: ₹${selectedTrade.exit_price.toFixed(2)}`, 
                            position: 'right', 
                            fill: selectedTrade.profit_loss >= 0 ? '#4caf50' : '#f44336',
                            fontSize: 12,
                            fontWeight: 'bold'
                          }}
                        />
                        
                        {/* Candlestick bodies and wicks */}
                        {generateTradeChartData(selectedTrade).map((candle, index) => {
                          const isGreen = candle.close >= candle.open;
                          const bodyColor = isGreen ? '#26a69a' : '#ef5350';
                          const wickColor = isGreen ? '#26a69a' : '#ef5350';
                          
                          // Highlight entry/exit candles
                          const highlightColor = candle.isEntry ? '#2196f3' : candle.isExit ? '#ff9800' : bodyColor;
                          
                          return (
                            <g key={index}>
                              {/* Wick (High-Low line) */}
                              <line
                                x1={`${((index + 0.5) / generateTradeChartData(selectedTrade).length) * 100}%`}
                                y1={`${((candle.high - Math.min(...generateTradeChartData(selectedTrade).map(c => c.low))) / (Math.max(...generateTradeChartData(selectedTrade).map(c => c.high)) - Math.min(...generateTradeChartData(selectedTrade).map(c => c.low)))) * 100}%`}
                                x2={`${((index + 0.5) / generateTradeChartData(selectedTrade).length) * 100}%`}
                                y2={`${((candle.low - Math.min(...generateTradeChartData(selectedTrade).map(c => c.low))) / (Math.max(...generateTradeChartData(selectedTrade).map(c => c.high)) - Math.min(...generateTradeChartData(selectedTrade).map(c => c.low)))) * 100}%`}
                                stroke={wickColor}
                                strokeWidth={1}
                              />
                            </g>
                          );
                        })}
                        
                        {/* Use Area charts to simulate candlestick bodies */}
                        <Area 
                          type="stepAfter"
                          dataKey="high"
                          stroke="none"
                          fill="transparent"
                          connectNulls
                        />
                        <Area 
                          type="stepAfter"
                          dataKey="low"
                          stroke="none"
                          fill="transparent"
                          connectNulls
                        />
                        
                        {/* Close price line for visualization */}
                        <Line 
                          type="stepAfter"
                          dataKey="close" 
                          stroke="#666"
                          strokeWidth={1}
                          dot={(props: any) => {
                            const { cx, cy, payload } = props;
                            if (!payload) return <></>;
                            
                            const isGreen = payload.close >= payload.open;
                            const color = payload.isEntry ? '#2196f3' : payload.isExit ? '#ff9800' : (isGreen ? '#26a69a' : '#ef5350');
                            const size = payload.isEntry || payload.isExit ? 8 : 4;
                            
                            return (
                              <circle
                                cx={cx}
                                cy={cy}
                                r={size}
                                fill={color}
                                stroke="#fff"
                                strokeWidth={payload.isEntry || payload.isExit ? 2 : 0}
                              />
                            );
                          }}
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                    
                    {/* Chart Legend */}
                    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, mt: 2, flexWrap: 'wrap' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#26a69a', border: '1px solid #fff' }} />
                        <Typography variant="caption">Bullish Candle</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#ef5350', border: '1px solid #fff' }} />
                        <Typography variant="caption">Bearish Candle</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#2196f3', border: '2px solid #fff', borderRadius: '50%' }} />
                        <Typography variant="caption">Entry Point</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Box sx={{ width: 16, height: 16, bgcolor: '#ff9800', border: '2px solid #fff', borderRadius: '50%' }} />
                        <Typography variant="caption">Exit Point</Typography>
                      </Box>
                    </Box>
                  </Box>

                  {/* Trade Info */}
                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} md={4}>
                      <Card variant="outlined" sx={{ bgcolor: 'primary.main', color: 'white' }}>
                        <CardContent>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>Entry Price</Typography>
                          <Typography variant="h5">₹{selectedTrade.entry_price.toFixed(2)}</Typography>
                          <Typography variant="caption">Quantity: {selectedTrade.quantity}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Card variant="outlined" sx={{ bgcolor: selectedTrade.profit_loss >= 0 ? 'success.main' : 'error.main', color: 'white' }}>
                        <CardContent>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>Exit Price</Typography>
                          <Typography variant="h5">₹{selectedTrade.exit_price.toFixed(2)}</Typography>
                          <Typography variant="caption">Reason: {selectedTrade.exit_reason}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Card variant="outlined" sx={{ bgcolor: selectedTrade.profit_loss >= 0 ? 'success.light' : 'error.light' }}>
                        <CardContent>
                          <Typography variant="body2" color="text.secondary">Total P&L</Typography>
                          <Typography 
                            variant="h5"
                            sx={{ color: selectedTrade.profit_loss >= 0 ? 'success.main' : 'error.main' }}
                          >
                            ₹{selectedTrade.profit_loss.toFixed(2)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {selectedTrade.profit_loss_percent.toFixed(2)}% {selectedTrade.profit_loss >= 0 ? 'Profit' : 'Loss'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setChartDialogOpen(false)}>Close</Button>
            </DialogActions>
          </Dialog>
        </Box>
      )}
    </Box>
  );

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return renderInstrumentSelection();
      case 1:
        return renderTradingRulesAndRisk();
      case 2:
        return renderStrikePriceSetup();
      case 3:
        return renderReviewTest();
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Strategy Builder
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create and customize your trading strategy with our comprehensive builder
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {activeStep === steps.length ? (
          <Box>
            <Typography sx={{ mb: 2 }}>
              All steps completed - your strategy is ready!
            </Typography>
            <Button onClick={handleReset}>Reset</Button>
          </Box>
        ) : (
          <Box>
            <Box sx={{ mb: 4 }}>
              {getStepContent(activeStep)}
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2 }}>
              <Button
                color="inherit"
                disabled={activeStep === 0}
                onClick={handleBack}
              >
                Back
              </Button>
              <Box sx={{ flex: '1 1 auto' }} />
              <Button
                variant="contained"
                onClick={handleNext}
              >
                {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
              </Button>
            </Box>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default StrategyBuilder;
