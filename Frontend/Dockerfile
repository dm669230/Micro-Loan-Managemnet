# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock if using yarn)
COPY package*.json ./

# Install dependencies using npm install (or yarn install)
RUN npm install

# Copy the rest of the code
COPY . .

# Build the app using Vite
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the built assets from the build stage to the nginx directory
COPY --from=build /app/dist /usr/share/nginx/html

# Expose the port nginx will run on
EXPOSE 80

# Start nginx to serve the app
CMD ["nginx", "-g", "daemon off;"]
