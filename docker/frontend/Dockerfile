FROM node:16-alpine AS build-stage

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy all files
COPY frontend/ .

# Build app - disable eslint during build to make it more resilient to linting issues
ENV DISABLE_ESLINT_PLUGIN=true
RUN npm run build

# Production stage
FROM nginx:stable-alpine AS production-stage

# Copy built files from the build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
