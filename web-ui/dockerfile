# 1. Aşama: Derleme (Build) Aşaması
FROM node:20-alpine AS build
WORKDIR /app

# Paket dosyalarını kopyala ve bağımlılıkları kur
COPY package*.json ./
RUN npm install

# Proje dosyalarını kopyala ve production için derle
COPY . .
RUN npm run build

# 2. Aşama: Sunum (Serve) Aşaması
FROM nginx:alpine

# Nginx'in varsayılan HTML klasörüne derlenen React dosyalarını kopyala
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx'in yayın yapacağı port
EXPOSE 80

# Sunucuyu başlat
CMD ["nginx", "-g", "daemon off;"]