import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
      host: '0.0.0.0', // Bind to all network interfaces
      port: 5173, // Optional: Explicitly set the port if needed
      proxy: {
        '/api': 'http://127.0.0.1:8000', // Proxy API requests to Django backend
      },
  },
});


