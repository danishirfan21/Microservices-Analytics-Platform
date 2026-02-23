# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Set build arguments for React environment variables
ARG REACT_APP_USER_SERVICE_URL
ARG REACT_APP_ANALYTICS_SERVICE_URL

# Set environment variables for the build process
ENV REACT_APP_USER_SERVICE_URL=$REACT_APP_USER_SERVICE_URL
ENV REACT_APP_ANALYTICS_SERVICE_URL=$REACT_APP_ANALYTICS_SERVICE_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration (optional)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
