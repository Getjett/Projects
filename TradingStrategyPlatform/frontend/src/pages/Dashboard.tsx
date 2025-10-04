import React from 'react';
import { Container, Typography, Grid, Card, CardContent, Box, Button } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import AssessmentIcon from '@mui/icons-material/Assessment';

const Dashboard: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Welcome Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                🎉 Welcome to Universal Trading Strategy Platform!
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Your platform is up and running! Both backend and frontend are active.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="success.main">
                  ✅ Backend API: Running on http://localhost:8000
                </Typography>
                <Typography variant="body2" color="success.main">
                  ✅ Frontend: Running on http://localhost:3000
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Strategies</Typography>
              </Box>
              <Typography variant="h3">0</Typography>
              <Typography variant="body2" color="text.secondary">
                Create your first strategy
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ShowChartIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Backtests Run</Typography>
              </Box>
              <Typography variant="h3">0</Typography>
              <Typography variant="body2" color="text.secondary">
                No backtests yet
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssessmentIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Win Rate</Typography>
              </Box>
              <Typography variant="h3">-</Typography>
              <Typography variant="body2" color="text.secondary">
                Start trading to see stats
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <Button variant="contained" color="primary" href="/strategy-builder">
                  Create Strategy
                </Button>
                <Button variant="outlined" color="primary" href="http://localhost:8000/api/docs" target="_blank">
                  View API Docs
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Supported Instruments */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎯 Supported Instruments
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Box sx={{ p: 2, bgcolor: 'primary.light', borderRadius: 1, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="primary.contrastText">
                      Index Options
                    </Typography>
                    <Typography variant="caption" color="primary.contrastText">
                      Nifty, Bank Nifty, Fin Nifty
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Box sx={{ p: 2, bgcolor: 'success.light', borderRadius: 1, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="success.contrastText">
                      Equity
                    </Typography>
                    <Typography variant="caption" color="success.contrastText">
                      NSE, BSE Stocks
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Box sx={{ p: 2, bgcolor: 'warning.light', borderRadius: 1, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="warning.contrastText">
                      Commodities
                    </Typography>
                    <Typography variant="caption" color="warning.contrastText">
                      Gold, Silver, Crude Oil
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Box sx={{ p: 2, bgcolor: 'error.light', borderRadius: 1, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="error.contrastText">
                      Currency
                    </Typography>
                    <Typography variant="caption" color="error.contrastText">
                      USD/INR, EUR/INR
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2.4}>
                  <Box sx={{ p: 2, bgcolor: 'info.light', borderRadius: 1, textAlign: 'center' }}>
                    <Typography variant="subtitle2" color="info.contrastText">
                      Futures
                    </Typography>
                    <Typography variant="caption" color="info.contrastText">
                      Index & Stock Futures
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
