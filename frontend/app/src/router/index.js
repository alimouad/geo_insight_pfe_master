import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/views/Auth/Login.vue';
import Register from '@/views/Auth/Register.vue';
import Dashboard from '@/views/Dashboard/Dashboard.vue';
import Project from '../views/Projects/Projects.vue';
import ProjectDetail from '@/views/Projects/ProjectDetail.vue';
import NewAnalysis from '@/views/Analysis/NewAnalysis.vue';
import AnalysisResult from '@/views/Analysis/AnalysisResult.vue';
import AnalysisCompare from '@/views/Analysis/AnalysisCompare.vue';
import Indicators from '@/views/Indicators/Indicators.vue';
import IndicatorDetail from '@/views/Indicators/IndicatorDetail.vue';
import Statistics from '@/views/Statistics/Statistics.vue';
import Exports from '@/views/Exports/Exports.vue';
import Favorites from '@/views/Favorites/Favorites.vue';
import Profile from '@/views/Profile/Profile.vue';
import Settings from '@/views/Settings/Settings.vue';
import Logout from '@/views/Auth/Logout.vue';



const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/login',
        },
        {
            path: '/login',
            name: 'login',
            component: Login,
        },
        {
            path: '/register',
            name: 'register',
            component: Register,
        },
        {
            path: '/dashboard',
            name: 'dashboard',
            component: Dashboard,

        },
        {
            path: '/projects',
            name: 'projects',
            component: Project,
        },
        {
            path: '/projects/:id',
            name: 'project-detail',
            component: ProjectDetail,
        },
        {
            path: '/analysis/new',
            name: 'new-analysis',
            component: NewAnalysis,
        },
        {
            path: '/projects/:projectId/analysis/compare',
            name: 'analysis-compare',
            component: AnalysisCompare,
        },
        {
            path: '/projects/:projectId/analysis/:analysisId',
            name: 'analysis-result',
            component: AnalysisResult,
        },
        {
            path: '/indicators',
            name: 'indicators',
            component: Indicators,
        },
        {
            path: '/indicators/:id',
            name: 'indicator-detail',
            component: IndicatorDetail,
        },
        {
            path: '/statistics',
            name: 'statistics',
            component: Statistics,
        },
        {
            path: '/exports',
            name: 'exports',
            component: Exports,
        },
        {
            path: '/favorites',
            name: 'favorites',
            component: Favorites,
        },
        {
            path: '/profile',
            name: 'profile',
            component: Profile,
        },
        {
            path: '/settings',
            name: 'settings',
            component: Settings,
        },
        {
            path: '/logout',
            name: 'logout',
            component: Logout,
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: '/login',
        },
    ]
      
});

// router.beforeEach((to) => {
//     const hasToken = Boolean(localStorage.getItem('token'));

//     if (to.meta.requiresAuth && !hasToken) {
//         return { name: 'login' };
//     }

//     if (to.name === 'login' && hasToken) {
//         return { name: 'dashboard' };
//     }

//     return true;
// });

export default router;
