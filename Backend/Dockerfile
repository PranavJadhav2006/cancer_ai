# ─── Stage 1: Build the React/Vite Frontend ──────────────────────────────────
# Build context is the project ROOT (set in docker-compose.yml)
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Install frontend dependencies
COPY Frontend/package.json Frontend/package-lock.json ./
RUN npm ci

# Copy frontend source and build
COPY Frontend/ .
RUN npm run build
# Output: /frontend/dist

# ─── Stage 2: Run the Node.js Backend ────────────────────────────────────────
FROM node:20-alpine AS backend

WORKDIR /app

# Install backend production dependencies
COPY Backend/package.json Backend/package-lock.json ./
RUN npm ci --omit=dev

# Copy backend source
COPY Backend/ .

# Copy the built frontend into the path server.js expects:
#   server.js: path.join(__dirname, '../Frontend/dist')
#   __dirname = /app  →  resolved path = /Frontend/dist
COPY --from=frontend-builder /frontend/dist /Frontend/dist

EXPOSE 8000

ENV NODE_ENV=production

CMD ["node", "server.js"]
