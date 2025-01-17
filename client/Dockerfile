# Step 1: Use an official Node.js image to build the app
FROM node:16 AS build

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Step 4: Install dependencies
RUN npm install

# Step 5: Copy the rest of the app's source code
COPY . .

# Step 6: Build the React app for production
RUN npm run build

# Step 7: Use a lightweight Nginx image to serve the React app
FROM nginx:alpine

# Step 8: Copy the build files from the previous build stage to Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Step 9: Expose port 80 to access the app
EXPOSE 80

# Step 10: Run the Nginx server to serve the app
CMD ["nginx", "-g", "daemon off;"]
