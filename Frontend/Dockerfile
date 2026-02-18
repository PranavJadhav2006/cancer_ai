# ─── Stage 1: Build the React/Vite app ───────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer cache)
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# The built output is in /app/dist
# This image is used as a build stage by the Backend Dockerfile.
# It is not run as a standalone container.
