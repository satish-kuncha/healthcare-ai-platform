# 1. Use a lightweight Node runtime to build the app
FROM node:20-alpine AS builder

WORKDIR /app

# 2. Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# 3. Copy frontend source files
COPY . .

# 4. Build the React app for production
RUN npm run build

# 5. Production Environment: Use Nginx to serve the static built files
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose Nginx standard port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]