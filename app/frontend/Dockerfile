FROM node:22-slim

WORKDIR /app

# Install dependencies first so this layer is cached until the package files change
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

# Copy config files and source code
COPY . .

# Expose pot 5173 and start the Vite dev server
EXPOSE 5173
CMD ["npm", "run", "dev"]