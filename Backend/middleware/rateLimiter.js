const rateLimit = require('express-rate-limit');

// ─── Rate Limiting Middleware (DISABLED) ──────────────────────────────────────
// Limits have been effectively removed by setting them to a very high value.

/**
 * General API rate limiter.
 */
const generalLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, 
    max: 1000000, // Effectively disabled
    message: {
        success: false,
        message: 'Too many requests from this IP'
    },
    standardHeaders: true,
    legacyHeaders: false,
});

/**
 * Auth-specific rate limiter (login/register).
 */
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, 
    max: 1000000, // Effectively disabled
    message: {
        success: false,
        message: 'Too many authentication attempts'
    },
    standardHeaders: true,
    legacyHeaders: false,
});

/**
 * Sensitive operations rate limiter.
 */
const sensitiveLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 1000000, // Effectively disabled
    message: {
        success: false,
        message: 'Too many sensitive requests'
    },
    standardHeaders: true,
    legacyHeaders: false,
});

module.exports = { generalLimiter, authLimiter, sensitiveLimiter };
