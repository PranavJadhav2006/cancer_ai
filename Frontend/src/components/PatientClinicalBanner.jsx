import React from 'react';
import { motion } from 'framer-motion';
import { 
  Person as PersonIcon, 
  CalendarMonth as CalendarIcon, 
  Wc as GenderIcon, 
  Phone as PhoneIcon,
  MonitorHeart as HeartIcon,
  Assignment as DiagnosisIcon,
  Timeline as KpsIcon,
  Psychology as EcoIcon
} from '@mui/icons-material';
import './PatientClinicalBanner.css';

const PatientClinicalBanner = ({ patientData }) => {
  // Default data if none provided (for development/preview)
  const defaultData = {
    fullName: "hogit gkiridv",
    dob: "6/9/1967",
    gender: "FEMALE",
    contact: "9786054123",
    diagnosis: "Brain",
    cancerType: "Brain",
    kps: "70%",
    ecog: "3"
  };

  const data = patientData || defaultData;

  const containerVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration: 0.6, 
        ease: [0.2, 0.9, 0.25, 1],
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { opacity: 1, x: 0 }
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase();
  };

  return (
    <motion.div 
      className="patient-clinical-banner"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <div className="banner-container">
        
        {/* Patient Identity */}
        <motion.div className="patient-identity" variants={itemVariants}>
          <div className="patient-avatar">
            {getInitials(data.fullName)}
          </div>
          <div className="identity-text">
            <h2 className="patient-name">{data.fullName}</h2>
            <div className="patient-meta">
              <span className="meta-item" style={{ color: '#00F0FF', fontWeight: 700 }}>MRN: {data.mrn || 'N/A'}</span>
              <span className="meta-item"><CalendarIcon sx={{ fontSize: 14 }} /> {data.dob}</span>
              <span className="meta-item"><GenderIcon sx={{ fontSize: 14 }} /> {data.gender}</span>
              <span className="meta-item"><PhoneIcon sx={{ fontSize: 14 }} /> {data.contact}</span>
            </div>
          </div>
        </motion.div>

        {/* Clinical Info: Diagnosis */}
        <motion.div className="clinical-group" variants={itemVariants}>
          <span className="group-label">Primary Diagnosis</span>
          <div className="group-value">
            <span className="status-badge badge-teal">
              <DiagnosisIcon sx={{ fontSize: 16, verticalAlign: 'middle', mr: 1 }} />
              {data.diagnosis}
            </span>
          </div>
        </motion.div>

        {/* Clinical Info: Cancer Type */}
        <motion.div className="clinical-group" variants={itemVariants}>
          <span className="group-label">Cancer Type</span>
          <div className="group-value">
            <span className="status-badge badge-cyan">
              <HeartIcon sx={{ fontSize: 16, verticalAlign: 'middle', mr: 1 }} />
              {data.cancerType}
            </span>
          </div>
        </motion.div>

        {/* Performance Metrics */}
        <motion.div className="clinical-group" variants={itemVariants}>
          <span className="group-label">Performance Metrics</span>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <div className="clinical-score">
              <KpsIcon sx={{ fontSize: 16, color: '#64748B' }} />
              <span className="score-value">{data.kps}</span>
              <span className="score-unit">KPS</span>
            </div>
            <div className="clinical-score">
              <EcoIcon sx={{ fontSize: 16, color: '#64748B' }} />
              <span className="score-value">{data.ecog}</span>
              <span className="score-unit">ECOG</span>
            </div>
          </div>
        </motion.div>

      </div>
    </motion.div>
  );
};

export default PatientClinicalBanner;
