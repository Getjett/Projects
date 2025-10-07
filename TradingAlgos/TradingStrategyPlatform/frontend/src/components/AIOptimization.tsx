import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableRow,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AutoAwesome as AIIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface AIOptimizationProps {
  open: boolean;
  onClose: () => void;
  backtestResult: any;
  strategyConfig: any;
  onApplyOptimization: (optimizedParams: any) => void;
}

const AIOptimization: React.FC<AIOptimizationProps> = ({
  open,
  onClose,
  backtestResult,
  strategyConfig,
  onApplyOptimization,
}) => {
  const [loading, setLoading] = useState(false);
  const [optimization, setOptimization] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeStrategy = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/ai/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          backtest_id: backtestResult.id,
          trades: backtestResult.trades,
          strategy_config: {
            ...strategyConfig,
            asset_class: strategyConfig.assetClass,
            breakout_direction: strategyConfig.breakoutDirection,
            entry_time_start: strategyConfig.entryTimeStart,
            target_value: strategyConfig.targetValue,
            stop_loss_value: strategyConfig.stopLossValue,
            risk_reward_ratio: strategyConfig.riskRewardRatio,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze strategy');
      }

      const data = await response.json();
      setOptimization(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (open && !optimization) {
      analyzeStrategy();
    }
  }, [open]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <ErrorIcon />;
      case 'medium':
        return <WarningIcon />;
      case 'low':
        return <InfoIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const handleApplyOptimization = () => {
    if (optimization?.optimized_parameters?.optimized) {
      onApplyOptimization(optimization.optimized_parameters.optimized);
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <AIIcon color="primary" />
          <Typography variant="h6">🤖 AI Strategy Optimizer</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading && (
          <Box sx={{ width: '100%', my: 2 }}>
            <Typography variant="body2" gutterBottom>
              Analyzing your strategy...
            </Typography>
            <LinearProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {optimization && (
          <Box>
            {/* Confidence Score */}
            <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  AI Confidence Score: {optimization.confidence_score}/100
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={optimization.confidence_score}
                  sx={{ height: 10, borderRadius: 5 }}
                />
                <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                  Based on {backtestResult.trades.length} trades analyzed
                </Typography>
              </CardContent>
            </Card>

            {/* Key Analysis Summary */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Win Rate
                    </Typography>
                    <Typography variant="h4">
                      {optimization.analysis.win_rate.win_rate}%
                    </Typography>
                    <Chip
                      label={optimization.analysis.win_rate.assessment.toUpperCase()}
                      size="small"
                      color={
                        optimization.analysis.win_rate.assessment === 'excellent'
                          ? 'success'
                          : optimization.analysis.win_rate.assessment === 'good'
                          ? 'primary'
                          : 'warning'
                      }
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Profit Factor
                    </Typography>
                    <Typography variant="h4">
                      {optimization.analysis.win_rate.profit_factor}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Target: &gt; 1.5
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Best Direction
                    </Typography>
                    <Typography variant="h4">
                      {optimization.analysis.direction.best_direction}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {optimization.analysis.direction.best_direction === 'BULLISH' ? '🟢' : '🔴'}{' '}
                      ₹
                      {Math.max(
                        optimization.analysis.direction.bullish_profit,
                        optimization.analysis.direction.bearish_profit
                      ).toFixed(0)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Recommendations */}
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              🎯 AI Recommendations
            </Typography>

            {optimization.recommendations.map((rec: any, index: number) => (
              <Accordion key={index} defaultExpanded={index === 0}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={1} width="100%">
                    <Chip
                      icon={getPriorityIcon(rec.priority)}
                      label={rec.priority.toUpperCase()}
                      size="small"
                      color={getPriorityColor(rec.priority) as any}
                    />
                    <Typography>{rec.title}</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Alert severity={getPriorityColor(rec.priority) as any} sx={{ mb: 2 }}>
                      <strong>Issue:</strong> {rec.issue}
                    </Alert>
                    <Typography variant="body2" gutterBottom>
                      <strong>Suggestion:</strong> {rec.suggestion}
                    </Typography>
                    <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                      <strong>Action:</strong> {rec.action}
                    </Typography>
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}

            {/* Optimized Parameters */}
            <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
              ⚙️ Optimized Parameters
            </Typography>

            <Card variant="outlined">
              <CardContent>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell><strong>Parameter</strong></TableCell>
                      <TableCell><strong>Current</strong></TableCell>
                      <TableCell><strong>Optimized</strong></TableCell>
                      <TableCell><strong>Change</strong></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Target Value</TableCell>
                      <TableCell>{optimization.optimized_parameters.current.target_value}%</TableCell>
                      <TableCell>{optimization.optimized_parameters.optimized.target_value}%</TableCell>
                      <TableCell>
                        {optimization.optimized_parameters.optimized.target_value >
                        optimization.optimized_parameters.current.target_value ? (
                          <Chip icon={<TrendingUpIcon />} label="Increase" color="success" size="small" />
                        ) : (
                          <Chip icon={<TrendingDownIcon />} label="Decrease" color="error" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Stop Loss Value</TableCell>
                      <TableCell>{optimization.optimized_parameters.current.stop_loss_value}%</TableCell>
                      <TableCell>{optimization.optimized_parameters.optimized.stop_loss_value}%</TableCell>
                      <TableCell>
                        {optimization.optimized_parameters.optimized.stop_loss_value >
                        optimization.optimized_parameters.current.stop_loss_value ? (
                          <Chip icon={<TrendingUpIcon />} label="Increase" color="warning" size="small" />
                        ) : (
                          <Chip icon={<TrendingDownIcon />} label="Decrease" color="success" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Entry Time Start</TableCell>
                      <TableCell>{optimization.optimized_parameters.current.entry_time_start}</TableCell>
                      <TableCell>{optimization.optimized_parameters.optimized.entry_time_start}</TableCell>
                      <TableCell>
                        <Chip label="Adjusted" color="info" size="small" />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Breakout Direction</TableCell>
                      <TableCell>{optimization.optimized_parameters.current.breakout_direction}</TableCell>
                      <TableCell>{optimization.optimized_parameters.optimized.breakout_direction}</TableCell>
                      <TableCell>
                        <Chip label="Optimized" color="primary" size="small" />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>

                {/* Expected Improvement */}
                <Alert severity="success" sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    <strong>Expected Improvement:</strong>
                  </Typography>
                  <Typography variant="body2">
                    Current Profit: ₹
                    {optimization.optimized_parameters.expected_improvement.current_profit.toFixed(2)}
                  </Typography>
                  <Typography variant="body2">
                    Estimated Profit: ₹
                    {optimization.optimized_parameters.expected_improvement.estimated_profit.toFixed(2)}{' '}
                    (+{optimization.optimized_parameters.expected_improvement.improvement_percentage}%)
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        {optimization && (
          <>
            <Tooltip title="Re-run analysis">
              <IconButton onClick={analyzeStrategy} color="primary">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              startIcon={<CheckIcon />}
              onClick={handleApplyOptimization}
              disabled={!optimization}
            >
              Apply Optimizations
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default AIOptimization;
