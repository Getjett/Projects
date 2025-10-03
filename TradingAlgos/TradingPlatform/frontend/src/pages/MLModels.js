import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as TrainIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Psychology as BrainIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import Plot from 'react-plotly.js';

// API services
import { mlApi } from '../services/api';

const MLModels = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [trainDialogOpen, setTrainDialogOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const [predictionResults, setPredictionResults] = useState(null);
  
  // Form states
  const [newModel, setNewModel] = useState({
    name: '',
    model_type: 'random_forest',
    symbol: 'RELIANCE',
    timeframe: '5minute',
    target: 'price_direction',
    features: []
  });

  const modelTypes = [
    { value: 'random_forest', label: 'Random Forest', icon: '🌳' },
    { value: 'xgboost', label: 'XGBoost', icon: '⚡' },
    { value: 'svm', label: 'Support Vector Machine', icon: '🎯' },
    { value: 'lstm', label: 'LSTM Neural Network', icon: '🧠' }
  ];

  const timeframes = [
    { value: '1minute', label: '1 Minute' },
    { value: '5minute', label: '5 Minutes' },
    { value: '15minute', label: '15 Minutes' },
    { value: '1hour', label: '1 Hour' },
    { value: 'day', label: 'Daily' }
  ];

  const symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'];

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await mlApi.getModels();
      setModels(response.data.models);
    } catch (error) {
      toast.error('Failed to load ML models');
      console.error('Error loading models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateModel = async () => {
    try {
      await mlApi.createModel(newModel);
      toast.success('ML model created successfully!');
      setCreateDialogOpen(false);
      setNewModel({
        name: '',
        model_type: 'random_forest',
        symbol: 'RELIANCE',
        timeframe: '5minute',
        target: 'price_direction',
        features: []
      });
      loadModels();
    } catch (error) {
      toast.error('Failed to create ML model');
      console.error('Error creating model:', error);
    }
  };

  const handleTrainModel = async (modelId) => {
    try {
      await mlApi.trainModel(modelId, {
        task_type: 'classification',
        n_estimators: 100,
        max_depth: 10
      });
      toast.success('Model training started! Check status for updates.');
      loadModels();
    } catch (error) {
      toast.error('Failed to start model training');
      console.error('Error training model:', error);
    }
  };

  const handlePredict = async (modelId) => {
    try {
      const response = await mlApi.predict(modelId);
      setPredictionResults(response.data);
      toast.success('Prediction generated successfully!');
    } catch (error) {
      toast.error('Failed to generate prediction');
      console.error('Error making prediction:', error);
    }
  };

  const handleDeleteModel = async (modelId) => {
    if (window.confirm('Are you sure you want to delete this model?')) {
      try {
        await mlApi.deleteModel(modelId);
        toast.success('Model deleted successfully!');
        loadModels();
      } catch (error) {
        toast.error('Failed to delete model');
        console.error('Error deleting model:', error);
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'trained': return 'success';
      case 'training': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 0.8) return 'success';
    if (accuracy >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BrainIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            Machine Learning Models
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Build, train, and deploy ML models for trading predictions
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          sx={{ height: 'fit-content' }}
        >
          Create Model
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <BrainIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h4">{models.length}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Models
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <TrendingUpIcon sx={{ fontSize: 32, color: 'success.main' }} />
                <Box>
                  <Typography variant="h4">
                    {models.filter(m => m.status === 'trained').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Trained Models
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <AssessmentIcon sx={{ fontSize: 32, color: 'warning.main' }} />
                <Box>
                  <Typography variant="h4">
                    {models.filter(m => m.status === 'training').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Training
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Typography variant="h2" sx={{ color: 'primary.main' }}>
                  {models.length > 0 ? 
                    (models.filter(m => m.accuracy).reduce((sum, m) => sum + m.accuracy, 0) / 
                     models.filter(m => m.accuracy).length * 100).toFixed(1) + '%' 
                    : 'N/A'}
                </Typography>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Avg Accuracy
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Models Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            ML Models
          </Typography>
          <TableContainer component={Paper} sx={{ backgroundColor: 'background.paper' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Symbol</TableCell>
                  <TableCell>Timeframe</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Accuracy</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8}>
                      <Box display="flex" justifyContent="center" p={2}>
                        <LinearProgress sx={{ width: '100%' }} />
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : models.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8}>
                      <Box textAlign="center" p={4}>
                        <Typography variant="body1" color="text.secondary">
                          No ML models found. Create your first model to get started!
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ) : (
                  models.map((model) => (
                    <TableRow key={model.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2">
                            {modelTypes.find(t => t.value === model.model_type)?.icon}
                          </Typography>
                          <Typography variant="body2">{model.name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={modelTypes.find(t => t.value === model.model_type)?.label || model.model_type}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{model.symbol}</TableCell>
                      <TableCell>{model.timeframe}</TableCell>
                      <TableCell>
                        <Chip 
                          label={model.status}
                          color={getStatusColor(model.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {model.accuracy ? (
                          <Chip 
                            label={`${(model.accuracy * 100).toFixed(1)}%`}
                            color={getAccuracyColor(model.accuracy)}
                            size="small"
                          />
                        ) : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {model.created_at ? new Date(model.created_at).toLocaleDateString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          {model.status === 'pending' && (
                            <Tooltip title="Train Model">
                              <IconButton 
                                size="small" 
                                onClick={() => handleTrainModel(model.id)}
                                color="primary"
                              >
                                <TrainIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          {model.status === 'trained' && (
                            <Tooltip title="Make Prediction">
                              <IconButton 
                                size="small" 
                                onClick={() => handlePredict(model.id)}
                                color="success"
                              >
                                <ViewIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title="Delete Model">
                            <IconButton 
                              size="small" 
                              onClick={() => handleDeleteModel(model.id)}
                              color="error"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Prediction Results */}
      {predictionResults && (
        <Box mt={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Latest Prediction Results
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box p={2} border={1} borderColor="divider" borderRadius={1}>
                    <Typography variant="body2" color="text.secondary">
                      Model ID: {predictionResults.model_id}
                    </Typography>
                    <Typography variant="h5" color="primary.main">
                      Prediction: {predictionResults.prediction[0]?.toFixed(4) || 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Confidence: {(predictionResults.confidence * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Generated: {new Date(predictionResults.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Create Model Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New ML Model</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Model Name"
                value={newModel.name}
                onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Model Type</InputLabel>
                <Select
                  value={newModel.model_type}
                  onChange={(e) => setNewModel({ ...newModel, model_type: e.target.value })}
                >
                  {modelTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Symbol</InputLabel>
                <Select
                  value={newModel.symbol}
                  onChange={(e) => setNewModel({ ...newModel, symbol: e.target.value })}
                >
                  {symbols.map((symbol) => (
                    <MenuItem key={symbol} value={symbol}>
                      {symbol}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Timeframe</InputLabel>
                <Select
                  value={newModel.timeframe}
                  onChange={(e) => setNewModel({ ...newModel, timeframe: e.target.value })}
                >
                  {timeframes.map((tf) => (
                    <MenuItem key={tf.value} value={tf.value}>
                      {tf.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Target Variable</InputLabel>
                <Select
                  value={newModel.target}
                  onChange={(e) => setNewModel({ ...newModel, target: e.target.value })}
                >
                  <MenuItem value="price_direction">Price Direction (Up/Down)</MenuItem>
                  <MenuItem value="price_change">Price Change (%)</MenuItem>
                  <MenuItem value="volatility">Volatility</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateModel} 
            variant="contained"
            disabled={!newModel.name}
          >
            Create Model
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MLModels;