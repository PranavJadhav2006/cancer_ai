import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, createTheme, ThemeProvider, CssBaseline } from '@mui/material';
import Navbar from './components/Navbar';
import GlobalFooter from './components/GlobalFooter';
import Home from './pages/Home';
import About from './pages/About';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Tumor3DPage from './pages/Tumor3DPage';
import PatientIntake from './pages/PatientIntake';
import GenomicAnalysis from './pages/GenomicAnalysis';
import MRIAnalysis from './pages/MRIAnalysis';
import Histopathology from './pages/Histopathology';
import TreatmentPlan from './pages/TreatmentPlan';
import OutcomePrediction from './pages/OutcomePrediction';
import PathwaySimulator from './pages/PathwaySimulator';
import BlockchainAudit from './pages/BlockchainAudit';
import PatientProfile from './pages/PatientProfile';
import ClinicalBaselineDemo from './pages/ClinicalBaselineDemo';

// Create a global theme instance
const theme = createTheme({
  typography: {
    fontFamily: '"Space Grotesk", sans-serif', // Default for body/human text
    h1: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700, letterSpacing: '-0.02em' },
    h2: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700, letterSpacing: '-0.02em' },
    h3: { fontFamily: '"Rajdhani", sans-serif', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' },
    h4: { fontFamily: '"Rajdhani", sans-serif', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' },
    h5: { fontFamily: '"Rajdhani", sans-serif', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' },
    h6: { fontFamily: '"Rajdhani", sans-serif', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' },
    subtitle1: { fontFamily: '"Space Grotesk", sans-serif' },
    subtitle2: { fontFamily: '"Space Grotesk", sans-serif' },
    body1: { fontFamily: '"Space Grotesk", sans-serif', letterSpacing: '-0.02em' },
    body2: { fontFamily: '"Space Grotesk", sans-serif', letterSpacing: '-0.02em' },
    button: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 }, // Primary Button -> Space Grotesk
    overline: { fontFamily: '"Rajdhani", sans-serif', fontWeight: 600, letterSpacing: '0.1em' }, // Small labels
    caption: { fontFamily: '"Rajdhani", sans-serif', fontWeight: 500 }, // Small tech text
  },
  palette: {
    mode: 'dark',
    background: {
      default: '#0B1221', // Void Navy from your palette
      paper: 'rgba(22, 32, 50, 0.7)',
    },
    primary: {
      main: '#059789', // Clinical Teal
    },
    secondary: {
      main: '#00F0FF', // Cyber Cyan
    },
    text: {
      primary: '#F8FAFC',
      secondary: '#94A3B8',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Box sx={{ pt: { xs: 8, md: 10 }, minHeight: '100vh', display: 'flex', flexDirection: 'column', width: '100%' }}>
          <Box component="main" sx={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%' }}>
            <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tumor-3d" element={<Tumor3DPage />} />
            <Route path="/patients" element={<PatientIntake />} />
            <Route path="/genomic-analysis" element={<GenomicAnalysis />} />
            <Route path="/mri-analysis" element={<MRIAnalysis />} />
            <Route path="/histopathology" element={<Histopathology />} />
            <Route path="/treatment-plan" element={<TreatmentPlan />} />
            <Route path="/outcome-prediction" element={<OutcomePrediction />} />
            <Route path="/pathway-simulator" element={<PathwaySimulator />} />
            <Route path="/blockchain-audit" element={<BlockchainAudit />} />
            <Route path="/patient-profile" element={<PatientProfile />} />
            <Route path="/baseline-demo" element={<ClinicalBaselineDemo />} />
          </Routes>
          </Box>
        </Box>
        <GlobalFooter />
      </Router>
    </ThemeProvider>
  );
}

export default App;