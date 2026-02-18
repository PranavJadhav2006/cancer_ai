const express = require('express');
const router = express.Router();
const {
    getPatientAnalyses,
    getAnalysis,
    createAnalysis,
    processAnalysis,
    updateAnalysis,
    getSlice,
    get3DModel,
    getQRCode
} = require('../controllers/analysisController');
const { protect } = require('../middleware/auth');

router.route('/')
    .post(protect, createAnalysis);

router.route('/patient/:patientId')
    .get(protect, getPatientAnalyses);

router.route('/:id')
    .get(protect, getAnalysis)
    .put(protect, updateAnalysis);

router.route('/:id/process')
    .post(protect, processAnalysis);

router.route('/:id/slice/:index')
    .get(protect, getSlice);

router.route('/:id/model')
    .get(get3DModel);

router.route('/:id/qr')
    .get(getQRCode);

module.exports = router;
