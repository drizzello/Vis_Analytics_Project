import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./assets/base.css";
import "./assets/main.css";
import "./assets/question-layout.css";

import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";

const app = createApp(App);

app.use(router);

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: ".p-dark",
        },
    },
});

app.mount("#app");
