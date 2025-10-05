import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  isEntry?: boolean;
  isExit?: boolean;
}

interface TradingViewChartProps {
  data: CandleData[];
  entryPrice: number;
  exitPrice: number;
  width?: number;
  height?: number;
}

const TradingViewChart: React.FC<TradingViewChartProps> = ({ 
  data, 
  entryPrice, 
  exitPrice,
  width = 900,
  height = 400 
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candlestickSeriesRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('TradingViewChart useEffect triggered');
    console.log('chartContainerRef.current:', chartContainerRef.current);
    console.log('data length:', data.length);
    
    if (!chartContainerRef.current) {
      console.log('No chart container ref, returning');
      return;
    }

    // Dynamically import the library to avoid module resolution issues
    let isMounted = true;

    console.log('Starting dynamic import of lightweight-charts');
    
    // Try-catch around the entire import and setup
    (async () => {
      try {
        const LightweightCharts = await import('lightweight-charts');
        console.log('Lightweight charts loaded successfully', LightweightCharts);
        
        if (!isMounted || !chartContainerRef.current) {
          console.log('Component unmounted or no ref');
          return;
        }

        // Create chart
        const chart = LightweightCharts.createChart(chartContainerRef.current, {
          width,
          height,
          layout: {
            textColor: '#333',
            background: { color: '#ffffff' },
          },
          grid: {
            vertLines: { color: '#e1e1e1' },
            horzLines: { color: '#e1e1e1' },
          },
          crosshair: {
            mode: 1 as any,
          },
          rightPriceScale: {
            borderColor: '#cccccc',
          },
          timeScale: {
            borderColor: '#cccccc',
            timeVisible: true,
            secondsVisible: false,
          },
        });

        chartRef.current = chart;

        // Add candlestick series
        const candlestickSeries = (chart as any).addCandlestickSeries({
          upColor: '#26a69a',
          downColor: '#ef5350',
          borderUpColor: '#26a69a',
          borderDownColor: '#ef5350',
          wickUpColor: '#26a69a',
          wickDownColor: '#ef5350',
        });

        candlestickSeriesRef.current = candlestickSeries;

        // Convert data to TradingView format (timestamps to seconds)
        const chartData = data.map(candle => {
          // Parse the time string and convert to timestamp
          const [datePart, timePart] = candle.time.split(' ');
          const [day, month, year] = datePart.split('/');
          const [hours, minutes] = timePart.split(':');
          const date = new Date(
            parseInt('20' + year), 
            parseInt(month) - 1, 
            parseInt(day), 
            parseInt(hours), 
            parseInt(minutes)
          );
          
          return {
            time: Math.floor(date.getTime() / 1000) as any, // Convert to seconds
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close,
          };
        });

        candlestickSeries.setData(chartData);

        // Add entry price line
        (candlestickSeries as any).createPriceLine({
          price: entryPrice,
          color: '#2196f3',
          lineWidth: 2,
          lineStyle: 2, // Dashed
          axisLabelVisible: true,
          title: 'Entry',
        });

        // Add exit price line
        (candlestickSeries as any).createPriceLine({
          price: exitPrice,
          color: exitPrice >= entryPrice ? '#4caf50' : '#f44336',
          lineWidth: 2,
          lineStyle: 2, // Dashed
          axisLabelVisible: true,
          title: 'Exit',
        });

        // Find entry and exit candles and add markers
        const markers: any[] = [];
        
        data.forEach((candle, index) => {
          if (candle.isEntry) {
            markers.push({
              time: chartData[index].time,
              position: 'belowBar',
              color: '#2196f3',
              shape: 'arrowUp',
              text: 'Entry',
            });
          }
          if (candle.isExit) {
            markers.push({
              time: chartData[index].time,
              position: 'aboveBar',
              color: '#ff9800',
              shape: 'arrowDown',
              text: 'Exit',
            });
          }
        });

        if (markers.length > 0) {
          (candlestickSeries as any).setMarkers(markers);
        }

        // Fit content
        chart.timeScale().fitContent();

        // Handle resize
        const handleResize = () => {
          if (chartContainerRef.current) {
            chart.applyOptions({
              width: chartContainerRef.current.clientWidth,
            });
          }
        };

        window.addEventListener('resize', handleResize);

        chartRef.current = chart;
        console.log('Chart setup complete, setting isLoading to false');
        setIsLoading(false);
      } catch (err) {
        console.error('Failed to load chart library:', err);
        setError('Failed to load chart library: ' + (err as Error).message);
        setIsLoading(false);
      }
    })();

    // Cleanup function
    return () => {
      isMounted = false;
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [data, entryPrice, exitPrice, width, height]);

  return (
    <Box 
      sx={{ 
        width: '100%', 
        height: height,
        position: 'relative',
      }}
    >
      {/* Chart container - always rendered so ref is available */}
      <Box 
        ref={chartContainerRef} 
        sx={{ 
          width: '100%', 
          height: '100%',
          position: 'relative',
        }} 
      />
      
      {/* Loading overlay */}
      {isLoading && (
        <Box 
          sx={{ 
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            zIndex: 1000,
          }}
        >
          <CircularProgress />
        </Box>
      )}

      {/* Error overlay */}
      {error && (
        <Box 
          sx={{ 
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            zIndex: 1000,
          }}
        >
          <Typography color="error">{error}</Typography>
        </Box>
      )}
    </Box>
  );
};

export default TradingViewChart;
