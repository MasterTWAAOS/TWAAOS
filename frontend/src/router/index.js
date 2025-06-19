import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Layouts
import MainLayout from '@/layouts/MainLayout.vue'

// Views
import ExamSchedule from '@/views/common/ExamSchedule.vue'
import Unauthorized from '@/views/error/Unauthorized.vue'
import NotFound from '@/views/error/NotFound.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

// Public Pages
import Login from '@/views/auth/Login.vue'

// Secretariat Views
import SecretariatDashboard from '@/views/secretariat/Dashboard.vue'
import ConfigurePeriods from '@/views/secretariat/ConfigurePeriods.vue'
import ManageExams from '@/views/secretariat/ManageExams.vue'
import DownloadReports from '@/views/secretariat/DownloadReports.vue'
import UploadData from '@/views/secretariat/UploadData.vue'

// Student Group Leader Views
import SGProposeDates from '@/views/student/ProposeDates.vue'

// Professor Views
import ProfessorDashboard from '@/views/professor/Dashboard.vue'
import ReviewProposals from '@/views/professor/ReviewProposals.vue'
import SetupExams from '@/views/professor/SetupExams.vue'

// Admin Views
import AdminDashboard from '@/views/admin/Dashboard.vue'
import ManageFaculties from '@/views/admin/ManageFaculties.vue'
import ManageUsers from '@/views/admin/ManageUsers.vue'

const routes = [
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login
      }
    ]
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      // Secretariat Routes
      {
        path: 'secretariat',
        meta: { role: 'SEC' },
        children: [
          {
            path: '',
            name: 'SecretariatDashboard',
            component: SecretariatDashboard
          },
          {
            path: 'configure-periods',
            name: 'ConfigurePeriods',
            component: ConfigurePeriods
          },
          {
            path: 'manage-exams',
            name: 'ManageExams',
            component: ManageExams
          },
          {
            path: 'download-reports',
            name: 'DownloadReports',
            component: DownloadReports
          },
          {
            path: 'upload-data',
            name: 'UploadData',
            component: UploadData
          }
        ]
      },
      
      // Student Group Leader Routes
      {
        path: 'student',
        meta: { role: 'SG' },
        children: [
          {
            path: '',
            name: 'SGProposeDates',
            component: SGProposeDates
          }
        ]
      },
      
      // Professor Routes
      {
        path: 'professor',
        meta: { role: 'CD' },
        children: [
          {
            path: '',
            name: 'ProfessorDashboard',
            component: ProfessorDashboard
          },
          {
            path: 'review-proposals',
            name: 'ReviewProposals',
            component: ReviewProposals
          },
          {
            path: 'setup-exams',
            name: 'SetupExams',
            component: SetupExams
          }
        ]
      },
      
      // Admin Routes
      {
        path: 'admin',
        meta: { role: 'ADM' },
        children: [
          {
            path: '',
            name: 'AdminDashboard',
            component: AdminDashboard
          },
          {
            path: 'manage-faculties',
            name: 'ManageFaculties',
            component: ManageFaculties
          },
          {
            path: 'manage-users',
            name: 'ManageUsers',
            component: ManageUsers
          }
        ]
      },
      
      // Common Routes
      {
        path: 'exam-schedule',
        name: 'ExamSchedule',
        component: ExamSchedule
      },
      
      // Redirect to role-specific dashboard based on user role
      {
        path: '',
        redirect: to => {
          const role = store.getters['auth/userRole']
          if (role === 'SG') return '/student'
          if (role === 'CD') return '/professor'
          if (role === 'SEC') return '/secretariat'
          if (role === 'ADM') return '/admin'
          return '/auth/login'
        }
      }
    ]
  },
  
  // Error Routes
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: Unauthorized
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const userRole = store.getters['auth/userRole']
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'Login' })
    } else if (to.matched.some(record => record.meta.role && record.meta.role !== userRole)) {
      // Redirect to appropriate dashboard if trying to access route for another role
      if (userRole === 'SG') next({ path: '/student' })
      else if (userRole === 'CD') next({ path: '/professor' })
      else if (userRole === 'SEC') next({ path: '/secretariat' })
      else if (userRole === 'ADM') next({ path: '/admin' })
      else next({ name: 'Login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
