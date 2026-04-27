const { Sequelize } = require('sequelize');
const dotenv = require('dotenv');

dotenv.config();

const rawUrl = process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/neuro_onco_ai';

// pg@8 does not support the `channel_binding` query param (Neon adds it by default)
// and Sequelize ignores `sslmode` in the URL — both must be handled via dialectOptions.
// Strip them here so the pg driver doesn't choke on unknown/unsupported params.
function sanitizeDbUrl(url) {
  try {
    const parsed = new URL(url);
    parsed.searchParams.delete('channel_binding');
    parsed.searchParams.delete('sslmode');
    return parsed.toString();
  } catch {
    return url;
  }
}

const dbUrl = sanitizeDbUrl(rawUrl);
const isCloudDb = rawUrl.includes('neon.tech') || rawUrl.includes('sslmode=require');

const sequelize = new Sequelize(dbUrl, {
  dialect: 'postgres',
  logging: false,
  dialectOptions: isCloudDb
    ? {
        ssl: {
          require: true,
          rejectUnauthorized: false, // Neon's CA is trusted; flip to true + provide ca cert for strict mode
        },
      }
    : {},
});

const connectDB = async () => {
  try {
    await sequelize.authenticate();
    console.log('🐘 PostgreSQL Connected Successfully');
  } catch (error) {
    console.error(`❌ Unable to connect to the database: ${error.message}`);
    process.exit(1);
  }
};

module.exports = { sequelize, connectDB };