<template>
  <div class="sidebar-secretariat">
    <h2>Secretariat</h2>
    <div class="menu">
      <ul>
        <li>
          <router-link :to="{ name: 'SecretariatDashboard' }" class="menu-item">
            <i class="pi pi-home"></i>
            <span>Dashboard</span>
          </router-link>
        </li>
        <li>
          <router-link :to="{ name: 'UploadData' }" class="menu-item">
            <i class="pi pi-upload"></i>
            <span>Încărcare Date</span>
          </router-link>
        </li>
        <li>
          <router-link :to="{ name: 'ConfigurePeriods' }" class="menu-item">
            <i class="pi pi-calendar"></i>
            <span>Configurare Perioade</span>
          </router-link>
        </li>
        <li>
          <router-link :to="{ name: 'ManageExams' }" class="menu-item">
            <i class="pi pi-list"></i>
            <span>Gestionare Examene</span>
          </router-link>
        </li>
        <li>
          <router-link :to="{ name: 'DownloadReports' }" class="menu-item">
            <i class="pi pi-download"></i>
            <span>Descărcare Rapoarte</span>
          </router-link>
        </li>
        <li>
          <a href="#" @click.prevent="fetchAndSyncData" class="menu-item">
            <i class="pi pi-sync"></i>
            <span>Sincronizare Date</span>
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { useStore } from 'vuex'

export default {
  name: 'SidebarSecretariat',
  setup() {
    const store = useStore()
    
    // Function to trigger data synchronization from USV APIs
    const fetchAndSyncData = async () => {
      try {
        // Use a toast to show progress
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Sincronizare date',
          detail: 'Sincronizare date în curs...',
          life: 3000
        })
        
        // Call API to trigger sync
        await store.dispatch('sync/fetchAndSyncData')
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare date',
          detail: 'Datele au fost sincronizate cu succes!',
          life: 3000
        })
      } catch (error) {
        // Show error notification
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare sincronizare',
          detail: error.message || 'A apărut o eroare la sincronizarea datelor',
          life: 5000
        })
      }
    }
    
    return {
      fetchAndSyncData
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar-secretariat {
  h2 {
    font-size: 1.25rem;
    color: #2c3e50;
    margin-top: 0;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e9ecef;
  }
  
  .menu {
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        margin-bottom: 0.5rem;
        
        .menu-item {
          display: flex;
          align-items: center;
          padding: 0.75rem;
          border-radius: 4px;
          text-decoration: none;
          color: #495057;
          transition: all 0.2s ease;
          
          i {
            margin-right: 0.75rem;
            font-size: 1.1rem;
          }
          
          &:hover, &.router-link-active {
            background-color: #e3f2fd;
            color: #1E88E5;
          }
        }
      }
    }
  }
}
</style>
