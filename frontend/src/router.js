import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "./views/DashboardView.vue";
import QuestionOneView from "./views/QuestionOneView.vue";
import QuestionTwoView from "./views/QuestionTwoView.vue";

const routes = [
    { path: "/", name: "dashboard", component: DashboardView },
    { path: "/question1", name: "question1", component: QuestionOneView },
    { path: "/question2", name: "question2", component: QuestionTwoView },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior: () => ({ top: 0, left: 0 }),
});

export default router;
