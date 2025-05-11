<template>
  <div class="dashboard">
    <!-- Dynamic dashboard based on user role -->
    <component :is="dashboardComponent" v-if="isAuthenticated" />
    
    <!-- Not authenticated message -->
    <Card v-else>
      <template #content>
        <div class="p-d-flex p-flex-column p-ai-center">
          <i class="pi pi-lock error-icon"></i>
          <h2>Acces restricționat</h2>
          <p>Trebuie să vă autentificați pentru a accesa această pagină.</p>
          <Button 
            label="Autentificare" 
            icon="pi pi-sign-in" 
            class="p-button-primary" 
            @click="navigateToLogin"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import { computed, defineAsyncComponent } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'

// Lazy load role-specific dashboards
const SecretariatDashboard = defineAsyncComponent(() => 
  import('@/views/secretariat/Dashboard.vue')
)
const ProfessorDashboard = defineAsyncComponent(() => 
  import('@/views/professor/Dashboard.vue')
)
const StudentDashboard = defineAsyncComponent(() => 
  import('@/views/student/Dashboard.vue')
)
const AdminDashboard = defineAsyncComponent(() => 
  import('@/views/admin/Dashboard.vue')
)

export default {
  name: 'DashboardView',
  components: {
    Card,
    Button,
    SecretariatDashboard,
    ProfessorDashboard,
    StudentDashboard,
    AdminDashboard
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // Get authentication state
    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    const userRole = computed(() => store.getters['auth/userRole'])
    
    // Determine which dashboard component to show based on user role
    const dashboardComponent = computed(() => {
      if (!isAuthenticated.value) return null
      
      switch (userRole.value) {
        case 'ADMIN':
          return AdminDashboard
        case 'SECRETARIAT':
          return SecretariatDashboard
        case 'PROFESSOR':
          return ProfessorDashboard
        case 'STUDENT':
          return StudentDashboard
        default:
          return null
      }
    })
    
    // Navigation
    const navigateToLogin = () => {
      router.push('/login')
    }
    
    return {
      isAuthenticated,
      userRole,
      dashboardComponent,
      navigateToLogin
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  .error-icon {
    font-size: 3rem;
    color: #f44336;
    margin-bottom: 1rem;
  }
  
  h2 {
    color: #2c3e50;
    margin-top: 0;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #6c757d;
    margin-bottom: 1.5rem;
  }
}
</style>
