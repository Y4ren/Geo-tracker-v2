import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import 'flag-icons/css/flag-icons.min.css';

createApp(App)
    .use(router)
    .mount('#app')
