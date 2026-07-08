import './style.css'
import 'leaflet/dist/leaflet.css'

import router from './router';
import { createPinia } from 'pinia';

import { createApp } from 'vue';
import App from './App.vue';



const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
// app.use(Toast);

app.mount('#app');