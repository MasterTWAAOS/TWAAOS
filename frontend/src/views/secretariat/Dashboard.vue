<template>
  <div class="secretariat-dashboard">
    <h1>Dashboard Secretariat</h1>
    
    <div class="p-grid p-mt-3">
      <!-- Summary Stats Cards -->
      <div class="p-col-12 p-md-4">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-book"></i>
              <span>Discipline</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalSubjects }}</div>
              <div class="stats-description">Total discipline</div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="p-col-12 p-md-4">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-calendar-check"></i>
              <span>Examene Programate</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.scheduledExams }}</div>
              <div class="stats-description">{{ scheduledExamsPercentage }}% din total</div>
              <ProgressBar :value="scheduledExamsPercentage" />
            </div>
          </template>
        </Card>
      </div>
      
      <div class="p-col-12 p-md-4">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-users"></i>
              <span>Studenți</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalGroups }}</div>
              <div class="stats-description">Grupe înregistrate</div>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="p-mt-4">
      <h2>Acțiuni Rapide</h2>
      <div class="p-grid">
        <div class="p-col-12 p-md-4 p-lg-3">
          <Card class="action-card">
            <template #content>
              <router-link :to="{ name: 'UploadData' }" class="action-link">
                <i class="pi pi-upload"></i>
                <span>Încărcare Date</span>
              </router-link>
            </template>
          </Card>
        </div>
        
        <div class="p-col-12 p-md-4 p-lg-3">
          <Card class="action-card">
            <template #content>
              <router-link :to="{ name: 'ManageExams' }" class="action-link">
                <i class="pi pi-list"></i>
                <span>Gestionare Examene</span>
              </router-link>
            </template>
          </Card>
        </div>
        
        <div class="p-col-12 p-md-4 p-lg-3">
          <Card class="action-card">
            <template #content>
              <router-link :to="{ name: 'ConfigurePeriods' }" class="action-link">
                <i class="pi pi-calendar"></i>
                <span>Configurare Perioade</span>
              </router-link>
            </template>
          </Card>
        </div>
        
        <div class="p-col-12 p-md-4 p-lg-3">
          <Card class="action-card">
            <template #content>
              <a href="#" @click.prevent="syncData" class="action-link">
                <i class="pi pi-sync"></i>
                <span>Sincronizare Date USV</span>
              </a>
            </template>
          </Card>
        </div>
      </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="p-mt-4">
      <h2>Activitate Recentă</h2>
      <DataTable :value="recentActivity" :paginator="true" :rows="5" class="p-datatable-sm">
        <Column field="date" header="Data" :sortable="true"></Column>
        <Column field="type" header="Tip">
          <template #body="slotProps">
            <Badge :value="slotProps.data.type" :severity="getActivitySeverity(slotProps.data.type)" />
          </template>
        </Column>
        <Column field="description" header="Descriere"></Column>
        <Column field="user" header="Utilizator"></Column>
      </DataTable>
    </div>
    
    <!-- Exam Status Overview -->
    <div class="p-mt-4">
      <h2>Status Examene</h2>
      <div class="p-grid">
        <div class="p-col-12 p-md-6">
          <h3>Status examene per grupă</h3>
          <Chart type="bar" :data="groupStatusData" :options="chartOptions" />
        </div>
        <div class="p-col-12 p-md-6">
          <h3>Status examene per disciplină</h3>
          <Chart type="doughnut" :data="subjectStatusData" :options="pieOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import ProgressBar from 'primevue/progressbar'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Badge from 'primevue/badge'
import Chart from 'primevue/chart'

export default {
  name: 'SecretariatDashboard',
  components: {
    ProgressBar,
    DataTable,
    Column,
    Badge,
    Chart
  },
  setup() {
    const store = useStore()
    
    // Dashboard stats
    const stats = ref({
      totalSubjects: 47,
      scheduledExams: 35,
      totalSubjectsCount: 47,
      totalGroups: 21
    })
    
    // Computed percentage
    const scheduledExamsPercentage = computed(() => {
      return Math.round((stats.value.scheduledExams / stats.value.totalSubjectsCount) * 100)
    })
    
    // Recent activity data
    const recentActivity = ref([
      { date: '2025-05-11 14:30', type: 'sync', description: 'Sincronizare date cu USV', user: 'Secretariat FIESC' },
      { date: '2025-05-11 11:15', type: 'approve', description: 'Aprobare examen Matematică Aplicată - CTI2', user: 'Prof. Ionescu' },
      { date: '2025-05-10 16:45', type: 'propose', description: 'Propunere dată examen Programare Web - AITC3', user: 'Popescu Andrei' },
      { date: '2025-05-10 09:20', type: 'upload', description: 'Încărcare listă șefi de grupă', user: 'Secretariat FIESC' },
      { date: '2025-05-09 15:30', type: 'config', description: 'Configurare perioadă examene sesiune vară', user: 'Secretariat FIESC' },
      { date: '2025-05-09 10:45', type: 'reject', description: 'Respingere examen Analiza Datelor - CTI3', user: 'Prof. Georgescu' },
      { date: '2025-05-08 13:15', type: 'confirm', description: 'Confirmare sală R408 - Examen Rețele', user: 'Secretariat FIESC' },
    ])
    
    // Chart data for group status
    const groupStatusData = ref({
      labels: ['CTI1', 'CTI2', 'CTI3', 'CTI4', 'AITC1', 'AITC2', 'AITC3'],
      datasets: [
        {
          label: 'Programate',
          backgroundColor: '#42A5F5',
          data: [5, 6, 4, 7, 4, 5, 4]
        },
        {
          label: 'În așteptare',
          backgroundColor: '#FFA726',
          data: [1, 0, 2, 0, 2, 1, 3]
        },
        {
          label: 'Neprogramate',
          backgroundColor: '#EF5350',
          data: [0, 1, 0, 0, 1, 0, 0]
        }
      ]
    })
    
    // Chart data for subject status
    const subjectStatusData = ref({
      labels: ['Programate', 'În așteptare', 'Neprogramate'],
      datasets: [
        {
          data: [35, 9, 3],
          backgroundColor: ['#42A5F5', '#FFA726', '#EF5350'],
          hoverBackgroundColor: ['#64B5F6', '#FFB74D', '#EF5350']
        }
      ]
    })
    
    // Chart options
    const chartOptions = ref({
      plugins: {
        legend: {
          position: 'bottom'
        }
      },
      scales: {
        x: {
          stacked: true
        },
        y: {
          stacked: true
        }
      }
    })
    
    const pieOptions = ref({
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    })
    
    // Function to get badge severity based on activity type
    const getActivitySeverity = (type) => {
      switch (type) {
        case 'sync': return 'info'
        case 'approve': return 'success'
        case 'propose': return 'info'
        case 'upload': return 'info'
        case 'config': return 'info'
        case 'reject': return 'danger'
        case 'confirm': return 'success'
        default: return 'info'
      }
    }
    
    // Function to trigger data synchronization
    const syncData = async () => {
      try {
        // Send notification that sync is starting
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Sincronizare',
          detail: 'Se sincronizează datele cu USV...',
          life: 3000
        })
        
        // Call API endpoint to sync data - this would connect to the Flask synchronization service
        await store.dispatch('sync/fetchAndSyncData')
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare',
          detail: 'Datele au fost sincronizate cu succes!',
          life: 3000
        })
        
        // Update dashboard data
        fetchDashboardData()
      } catch (error) {
        // Show error notification
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Eroare la sincronizarea datelor: ' + (error.message || 'Eroare necunoscută'),
          life: 5000
        })
      }
    }
    
    // Function to fetch dashboard data
    const fetchDashboardData = async () => {
      try {
        // In a real implementation, this would fetch data from API
        // For now, we're using mock data
        console.log('Fetching dashboard data...')
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }
    
    onMounted(() => {
      fetchDashboardData()
    })
    
    return {
      stats,
      scheduledExamsPercentage,
      recentActivity,
      groupStatusData,
      subjectStatusData,
      chartOptions,
      pieOptions,
      getActivitySeverity,
      syncData
    }
  }
}
</script>

<style lang="scss" scoped>
.secretariat-dashboard {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  h2 {
    color: #2c3e50;
    font-size: 1.25rem;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e9ecef;
  }
  
  h3 {
    color: #2c3e50;
    font-size: 1.1rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
  }
  
  .stats-card {
    height: 100%;
    
    :deep(.p-card-title) {
      .card-title {
        display: flex;
        align-items: center;
        
        i {
          margin-right: 0.5rem;
          font-size: 1.25rem;
          color: #1E88E5;
        }
      }
    }
    
    .stats-content {
      text-align: center;
      
      .stats-number {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
      }
      
      .stats-description {
        color: #6c757d;
        margin-bottom: 0.75rem;
      }
    }
  }
  
  .action-card {
    height: 100%;
    
    .action-link {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      color: #495057;
      padding: 1.5rem;
      transition: all 0.2s ease;
      height: 100%;
      
      i {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        color: #1E88E5;
      }
      
      span {
        font-size: 1rem;
        text-align: center;
      }
      
      &:hover {
        background-color: #f8f9fa;
        color: #1E88E5;
      }
    }
  }
}
</style>
