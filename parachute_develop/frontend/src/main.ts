import './assets/main.css';

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';
import axios from 'axios';
import { OhVueIcon, addIcons } from 'oh-vue-icons';
import { CoHamburgerMenu, CoHome, BiBalloonHeart, CoInfo, CoCog } from 'oh-vue-icons/icons';

addIcons(CoHamburgerMenu, CoHome, BiBalloonHeart, CoInfo, CoCog);

const app = createApp(App);

// Configure Axios instance
const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',  // This ensures axios uses this URL for all requests
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
});

app.config.globalProperties.$axios = axiosInstance;

app.component('VIcon', OhVueIcon);

app.use(createPinia());
app.use(router);

app.mount('#app');
