<template>
  <div class="main-layout">
    <header class="main-header">
      <div class="container">
        <div class="header-content p-d-flex p-jc-between p-ai-center">
          <div class="logo">
            <picture>
              <!-- Use SVG as primary format (better for scaling) -->
              <source srcset="@/assets/images/logo.svg" type="image/svg+xml">
              <!-- Fallback to PNG if SVG not supported -->
              <img src="@/assets/images/logo.png" alt="FIESC Logo" class="header-logo" onerror="this.onerror=null; this.src='/logo.png';" />
            </picture>
            <h1>FIESC - Planificarea Examenelor</h1>
          </div>
          <div class="user-menu">
            <div v-if="currentUser" class="p-d-flex p-ai-center">
              <span class="p-mr-2">{{ currentUser.firstName }} {{ currentUser.lastName }}</span>
              <Button 
                icon="pi pi-sign-out" 
                class="p-button-text p-button-rounded" 
                @click="logout" 
                tooltip="Deconectare"
              />
            </div>
          </div>
        </div>
      </div>
    </header>
    
    <div class="main-content">
      <div class="container">
        <div class="p-grid">
          <div class="p-col-12 p-md-3">
            <div class="sidebar">
              <!-- Different navigation based on user role -->
              <div v-if="userRole === 'SEC'">
                <SidebarSecretariat />
              </div>
              <div v-else-if="userRole === 'SG'">
                <SidebarStudent />
              </div>
              <div v-else-if="userRole === 'CD'">
                <SidebarProfessor />
              </div>
              <div v-else-if="userRole === 'ADM'">
                <SidebarAdmin />
              </div>
            </div>
          </div>
          
          <div class="p-col-12 p-md-9">
            <div class="content-wrapper">
              <router-view />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <footer class="main-footer">
      <div class="container">
        <p>&copy; {{ currentYear }} Universitatea Ștefan cel Mare din Suceava. Toate drepturile rezervate.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

// Sidebar components for different user roles
import SidebarSecretariat from '@/components/navigation/SidebarSecretariat.vue'
import SidebarStudent from '@/components/navigation/SidebarStudent.vue'
import SidebarProfessor from '@/components/navigation/SidebarProfessor.vue'
import SidebarAdmin from '@/components/navigation/SidebarAdmin.vue'

export default {
  name: 'MainLayout',
  components: {
    SidebarSecretariat,
    SidebarStudent,
    SidebarProfessor,
    SidebarAdmin
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const currentYear = ref(new Date().getFullYear())
    
    // Computed properties
    const currentUser = computed(() => store.getters['auth/currentUser'])
    const userRole = computed(() => store.getters['auth/userRole'])
    
    // Methods
    const logout = () => {
      store.dispatch('auth/logout')
    }
    
    onMounted(() => {
      // Check if user is authenticated
      if (!store.getters['auth/isAuthenticated']) {
        router.push('/auth/login')
      }
    })
    
    return {
      currentYear,
      currentUser,
      userRole,
      logout
    }
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-header {
  background-color: #1E88E5;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .logo {
    display: flex;
    align-items: center;
    
    .header-logo {
      height: 40px;
      margin-right: 1rem;
      object-fit: contain;
      max-width: 100%;
    }
    
    picture {
      display: inline-block;
      line-height: 0;
    }
    
    h1 {
      font-size: 1.5rem;
      margin: 0;
      font-weight: 500;
    }
  }
}

.main-content {
  flex: 1;
  padding: 2rem 0;
  
  .sidebar {
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .content-wrapper {
    background-color: white;
    border-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    padding: 1.5rem;
    min-height: 400px;
  }
}

.main-footer {
  background-color: #f8f9fa;
  padding: 1.5rem 0;
  border-top: 1px solid #e9ecef;
  text-align: center;
  color: #6c757d;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
</style>
