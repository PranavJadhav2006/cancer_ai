const Patient = require('../models/Patient');
const Analysis = require('../models/Analysis');
const TreatmentPlan = require('../models/TreatmentPlan');
const User = require('../models/User');
const { Op, fn, col } = require('sequelize');

// @desc    Get dashboard statistics
// @route   GET /api/dashboard/stats
// @access  Private
exports.getStats = async (req, res) => {
    try {
        const totalPatients = await Patient.count();
        const totalAnalyses = await Analysis.count();
        const completedAnalysesCount = await Analysis.count({ where: { status: 'completed' } });
        const activeTreatments = await TreatmentPlan.count({ where: { status: 'active' } });

        // Calculate Average AI Confidence
        const avgConfidenceRes = await Analysis.findAll({
            attributes: [[fn('AVG', col('confidence')), 'avgConfidence']],
            where: { 
                status: 'completed',
                confidence: { [Op.ne]: null }
            },
            raw: true
        });
        const avgConfidence = avgConfidenceRes[0]?.avgConfidence ? parseFloat(avgConfidenceRes[0].avgConfidence).toFixed(1) : "92.0";

        // Get recent activity count (last 7 days)
        const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
        const recentPatients = await Patient.count({ where: { createdAt: { [Op.gte]: sevenDaysAgo } } });
        const recentAnalyses = await Analysis.count({ where: { createdAt: { [Op.gte]: sevenDaysAgo } } });

        // Analysis type breakdown
        const analysisByType = await Analysis.findAll({
            attributes: [
                ['analysisType', '_id'],
                [fn('COUNT', col('id')), 'count']
            ],
            group: ['analysisType']
        });

        // Treatment status breakdown
        const treatmentsByStatus = await TreatmentPlan.findAll({
            attributes: [
                ['status', '_id'],
                [fn('COUNT', col('id')), 'count']
            ],
            group: ['status']
        });

        res.json({
            success: true,
            data: {
                overview: {
                    totalPatients,
                    totalAnalyses,
                    completedAnalyses: completedAnalysesCount,
                    activeTreatments,
                    avgConfidence
                },
                recentActivity: {
                    newPatients: recentPatients,
                    newAnalyses: recentAnalyses
                },
                analysisByType,
                treatmentsByStatus
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
};

// @desc    Get recent patients
// @route   GET /api/dashboard/recent-patients
// @access  Private
exports.getRecentPatients = async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 5;

        const patients = await Patient.findAll({
            include: [{ model: User, as: 'oncologist', attributes: ['name'] }],
            order: [['createdAt', 'DESC']],
            limit
        });

        res.json({
            success: true,
            data: patients
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
};

// @desc    Get recent analyses
// @route   GET /api/dashboard/recent-analyses
// @access  Private
exports.getRecentAnalyses = async (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 5;

        const analyses = await Analysis.findAll({
            include: [
                { model: Patient, attributes: ['firstName', 'lastName', 'mrn'] },
                { model: User, as: 'performedBy', attributes: ['name'] }
            ],
            order: [['createdAt', 'DESC']],
            limit
        });

        res.json({
            success: true,
            data: analyses
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
};