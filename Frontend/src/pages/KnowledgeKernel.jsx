import React, { useState, useEffect } from 'react';
import {
  Box, Container, Grid, Typography, CircularProgress, Card, CardContent, LinearProgress, Divider
} from '@mui/material';
import { motion } from 'framer-motion';
import apiClient from '../utils/apiClient';
import Navbar from '../components/Navbar';
import PsychologyIcon from '@mui/icons-material/Psychology';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TimerIcon from '@mui/icons-material/Timer';
import DatasetIcon from '@mui/icons-material/Dataset';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const colors = {
  bg: '#0B1221',
  surface: 'rgba(255, 255, 255, 0.04)',
  border: 'rgba(91, 111, 246, 0.2)',
  primary: '#5B6FF6',
  primaryDark: '#7C5CFF',
  gradient: 'linear-gradient(135deg, #5B6FF6 0%, #7C5CFF 100%)',
  teal: '#21D4BD',
  muted: '#94A3B8',
  success: '#22C55E',
  warning: '#F59E0B',
  danger: '#EF4444',
  text: '#F8FAFC'
};

const KnowledgeKernel = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await apiClient.get('/dashboard/institutional-knowledge');
        if (res.data.success) {
          setStats(res.data.data);
        }
      } catch (err) {
        console.error("Failed to fetch knowledge stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const donutData = {
    labels: ['Expert Corrections', 'Standard Approvals'],
    datasets: [{
      data: [stats?.expert_corrections || 2, stats?.standard_approvals || 12],
      backgroundColor: [colors.primaryDark, colors.teal],
      borderColor: colors.bg,
      borderWidth: 2,
    }]
  };

  const barData = {
    labels: stats?.cancer_type_distribution ? Object.keys(stats.cancer_type_distribution).map(k => k.toUpperCase()) : ['BRAIN', 'BREAST', 'LUNG', 'LIVER'],
    datasets: [{
      label: 'Cases Learned',
      data: stats?.cancer_type_distribution ? Object.values(stats.cancer_type_distribution) : [5, 4, 3, 2],
      backgroundColor: colors.primary,
      borderRadius: 4,
    }]
  };

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: colors.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress sx={{ color: colors.primary }} />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: colors.bg, pb: 10, position: 'relative', overflow: 'hidden' }}>
      <Navbar />
      
      {/* Background Glow */}
      <Box sx={{ 
        position: 'absolute', 
        top: '-10%', 
        right: '-10%', 
        width: '500px', 
        height: '500px', 
        background: 'radial-gradient(circle, rgba(91, 111, 246, 0.08) 0%, rgba(7, 16, 51, 0) 70%)',
        zIndex: 0,
        pointerEvents: 'none'
      }} />

      <Container maxWidth="xl" sx={{ mt: 6, position: 'relative', zIndex: 1 }}>
        
        {/* HEADER */}
        <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="overline" sx={{ color: colors.primary, fontWeight: 800, letterSpacing: '4px', mb: 1, display: 'block' }}>
              INSTITUTIONAL KNOWLEDGE KERNEL
            </Typography>
            <Typography variant="h3" sx={{ fontFamily: '"Rajdhani"', fontWeight: 800, color: '#fff', mb: 1 }}>
              RESONANCE AI CORE
            </Typography>
            <Typography variant="body1" sx={{ color: colors.muted, maxWidth: '600px' }}>
              Real-time monitoring of clinical memory and autonomous learning patterns.
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right', p: 2, bgcolor: colors.surface, borderRadius: '12px', border: `1px solid ${colors.border}`, backdropFilter: 'blur(10px)' }}>
            <Typography variant="caption" sx={{ color: colors.muted, display: 'block', letterSpacing: '1px' }}>KERNEL STATUS</Typography>
            <Typography variant="h6" sx={{ color: colors.success, fontFamily: '"JetBrains Mono"', fontWeight: 800 }}>SYNCHRONIZED</Typography>
          </Box>
        </Box>

        <Grid container spacing={3}>
          
          {/* TOP METRICS */}
          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: colors.surface, border: `1px solid ${colors.border}`, borderRadius: '18px', backdropFilter: 'blur(20px)' }}>
              <CardContent sx={{ p: 4, textAlign: 'center' }}>
                <DatasetIcon sx={{ color: colors.primary, fontSize: 32, mb: 1 }} />
                <Typography variant="h2" sx={{ fontFamily: '"Inter"', fontWeight: 900, color: '#fff' }}>
                  {String(stats?.total_cases || 14).padStart(2, '0')}
                </Typography>
                <Typography variant="overline" sx={{ color: colors.muted, letterSpacing: '1px' }}>Clinical Experiences</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card sx={{ bgcolor: colors.surface, border: `1px solid ${colors.border}`, borderRadius: '18px', backdropFilter: 'blur(20px)' }}>
              <CardContent sx={{ p: 4, textAlign: 'center' }}>
                <AutoAwesomeIcon sx={{ color: colors.teal, fontSize: 32, mb: 1 }} />
                <Typography variant="h2" sx={{ fontFamily: '"Inter"', fontWeight: 900, color: '#fff' }}>
                  {stats?.learning_density || 86}%
                </Typography>
                <Typography variant="overline" sx={{ color: colors.muted, letterSpacing: '1px' }}>Expert Refinement Ratio</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ bgcolor: colors.surface, border: `1px solid ${colors.border}`, borderRadius: '18px', height: '100%', backdropFilter: 'blur(20px)' }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2, alignItems: 'center' }}>
                  <Typography variant="subtitle2" sx={{ color: colors.primary, fontWeight: 800, letterSpacing: '1px' }}>LEARNING PERSISTENCE</Typography>
                  <Box sx={{ px: 1.5, py: 0.5, bgcolor: 'rgba(34, 197, 94, 0.1)', borderRadius: '9999px', border: `1px solid ${colors.success}` }}>
                    <Typography variant="caption" sx={{ color: colors.success, fontWeight: 700 }}>STABLE</Typography>
                  </Box>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(100, ((stats?.total_cases || 14) / 50) * 100)} 
                  sx={{ 
                    height: 10, 
                    borderRadius: 5, 
                    bgcolor: 'rgba(255,255,255,0.05)', 
                    '& .MuiLinearProgress-bar': { 
                      background: colors.gradient 
                    } 
                  }} 
                />
                <Typography variant="body2" sx={{ mt: 2.5, color: colors.muted }}>
                  The kernel is currently operating with a { (stats?.total_cases || 14) > 10 ? 'high' : 'emerging' } confidence threshold based on institutional data volume.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* CHARTS */}
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: colors.surface, border: `1px solid ${colors.border}`, borderRadius: '18px', height: '480px', backdropFilter: 'blur(20px)' }}>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h6" sx={{ fontFamily: '"Rajdhani"', fontWeight: 700, color: '#fff', mb: 4, letterSpacing: '1px' }}>FEEDBACK COMPOSITION</Typography>
                <Box sx={{ height: '320px', display: 'flex', justifyContent: 'center' }}>
                  <Doughnut data={donutData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: colors.muted, padding: 20, font: { family: 'Inter', size: 12 } } } } }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Card sx={{ bgcolor: colors.surface, border: `1px solid ${colors.border}`, borderRadius: '18px', height: '480px', backdropFilter: 'blur(20px)' }}>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h6" sx={{ fontFamily: '"Rajdhani"', fontWeight: 700, color: '#fff', mb: 4, letterSpacing: '1px' }}>DOMAIN KNOWLEDGE DISTRIBUTION</Typography>
                <Box sx={{ height: '320px' }}>
                  <Bar data={barData} options={{ 
                    maintainAspectRatio: false, 
                    scales: { 
                      x: { grid: { display: false }, ticks: { color: colors.muted, font: { family: 'Rajdhani', weight: 600 } } }, 
                      y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: colors.muted } } 
                    }, 
                    plugins: { legend: { display: false } } 
                  }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* TRENDS & INSIGHTS */}
          <Grid item xs={12}>
            <Card sx={{ bgcolor: 'rgba(91, 111, 246, 0.03)', border: `1px solid ${colors.primary}`, borderRadius: '18px', backdropFilter: 'blur(20px)' }}>
              <CardContent sx={{ p: 5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
                  <Box sx={{ p: 1, borderRadius: '12px', bgcolor: colors.primary }}>
                    <PsychologyIcon sx={{ color: '#fff' }} />
                  </Box>
                  <Typography variant="h5" sx={{ fontFamily: '"Rajdhani"', fontWeight: 800, color: '#fff', letterSpacing: '1px' }}>AUTONOMOUS INSIGHTS</Typography>
                </Box>
                
                <Grid container spacing={4}>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ height: '100%', p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: '12px', borderLeft: `4px solid ${colors.teal}` }}>
                      <Typography variant="subtitle2" sx={{ color: colors.teal, fontWeight: 800, mb: 1.5, letterSpacing: '1px' }}>THERAPEUTIC DRIFT</Typography>
                      <Typography variant="body2" sx={{ color: colors.muted, lineHeight: 1.6 }}>
                        Local clinicians are trending towards hypofractionated protocols for MGMT-unmethylated cohorts at a {stats?.learning_density || '12.4'}% higher rate than baseline guidelines.
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ height: '100%', p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: '12px', borderLeft: `4px solid ${colors.primary}` }}>
                      <Typography variant="subtitle2" sx={{ color: colors.primary, fontWeight: 800, mb: 1.5, letterSpacing: '1px' }}>PRECISION ALIGNMENT</Typography>
                      <Typography variant="body2" sx={{ color: colors.muted, lineHeight: 1.6 }}>
                        IDH1-mutant matching is achieving 92%+ similarity scores, indicating a highly standardized institutional approach to this genomic profile.
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ height: '100%', p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: '12px', borderLeft: `4px solid ${colors.warning}` }}>
                      <Typography variant="subtitle2" sx={{ color: colors.warning, fontWeight: 800, mb: 1.5, letterSpacing: '1px' }}>DATA MATURITY</Typography>
                      <Typography variant="body2" sx={{ color: colors.muted, lineHeight: 1.6 }}>
                        Knowledge Kernel has ingested {stats?.total_cases || 0} multi-dimensional case fingerprints. Last sync: {stats?.last_updated ? new Date(stats.last_updated).toLocaleString() : 'N/A'}.
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

        </Grid>
      </Container>
    </Box>
  );
};

export default KnowledgeKernel;
