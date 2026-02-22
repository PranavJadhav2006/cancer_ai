const express = require('express');
const router = express.Router();
const {
    getPatientOutcomes,
    getOutcome,
    createOutcome,
    generateFormattedOutcomes,
    downloadReport
} = require('../controllers/outcomeController');
const { protect } = require('../middleware/auth');

router.route('/predict-formatted')
    .post(protect, generateFormattedOutcomes);

router.route('/download-report')
    .post(protect, downloadReport);

router.route('/')
    .post(protect, createOutcome);

router.route('/patient/:patientId')
    .get(protect, getPatientOutcomes);

router.route('/:id')
    .get(protect, getOutcome);

module.exports = router;