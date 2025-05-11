<template>
  <div class="admin-dashboard">
    <h1>Panou de Control Administrator</h1>
    
    <div class="p-grid">
      <!-- System Statistics -->
      <div class="p-col-12 p-lg-6">
        <Card>
          <template #title>
            <div class="card-title">
              <i class="pi pi-chart-line p-mr-2"></i>
              Statistici Sistem
            </div>
          </template>
          <template #content>
            <div v-if="loading.stats" class="p-d-flex p-jc-center">
              <ProgressSpinner />
            </div>
            <div v-else class="stats-grid p-grid">
              <div class="p-col-12 p-md-6 p-mb-3">
                <div class="stat-card users">
                  <div class="stat-icon">
                    <i class="pi pi-users"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ stats.totalUsers }}</span>
                    <span class="stat-label">Utilizatori</span>
                  </div>
                </div>
              </div>
              
              <div class="p-col-12 p-md-6 p-mb-3">
                <div class="stat-card exams">
                  <div class="stat-icon">
                    <i class="pi pi-calendar"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ stats.totalExams }}</span>
                    <span class="stat-label">Examene Planificate</span>
                  </div>
                </div>
              </div>
              
              <div class="p-col-12 p-md-6 p-mb-3">
                <div class="stat-card groups">
                  <div class="stat-icon">
                    <i class="pi pi-th-large"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ stats.totalGroups }}</span>
                    <span class="stat-label">Grupe</span>
                  </div>
                </div>
              </div>
              
              <div class="p-col-12 p-md-6 p-mb-3">
                <div class="stat-card rooms">
                  <div class="stat-icon">
                    <i class="pi pi-building"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-value">{{ stats.totalRooms }}</span>
                    <span class="stat-label">Săli</span>
                  </div>
                </div>
              </div>
              
              <div class="p-col-12">
                <div class="system-status">
                  <h3>Status Sistem</h3>
                  <div class="status-items p-grid">
                    <div class="p-col-12 p-md-6">
                      <div class="status-item">
                        <span class="status-label">API:</span>
                        <Tag 
                          :value="stats.apiStatus ? 'Operațional' : 'Probleme'" 
                          :severity="stats.apiStatus ? 'success' : 'danger'"
                        />
                      </div>
                    </div>
                    <div class="p-col-12 p-md-6">
                      <div class="status-item">
                        <span class="status-label">Sincronizare:</span>
                        <Tag 
                          :value="stats.syncStatus ? 'Actualizat' : 'Neactualizat'" 
                          :severity="stats.syncStatus ? 'success' : 'warning'"
                        />
                      </div>
                    </div>
                    <div class="p-col-12 p-md-6">
                      <div class="status-item">
                        <span class="status-label">Bază de Date:</span>
                        <Tag 
                          :value="stats.dbStatus ? 'Online' : 'Probleme'" 
                          :severity="stats.dbStatus ? 'success' : 'danger'"
                        />
                      </div>
                    </div>
                    <div class="p-col-12 p-md-6">
                      <div class="status-item">
                        <span class="status-label">Stocarea Rapoartelor:</span>
                        <Tag 
                          :value="stats.storageStatus ? 'Disponibil' : 'Aproape Plin'" 
                          :severity="stats.storageStatus ? 'success' : 'warning'"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <!-- Recent Activity -->
      <div class="p-col-12 p-lg-6">
        <Card>
          <template #title>
            <div class="card-title">
              <i class="pi pi-history p-mr-2"></i>
              Activitate Recentă
            </div>
          </template>
          <template #content>
            <div v-if="loading.activity" class="p-d-flex p-jc-center">
              <ProgressSpinner />
            </div>
            <DataTable 
              v-else
              :value="recentActivity" 
              :paginator="true" 
              :rows="5"
              class="p-datatable-sm"
              emptyMessage="Nu există activitate recentă"
            >
              <Column field="timestamp" header="Data" style="width: 30%">
                <template #body="slotProps">
                  <span>{{ formatDate(slotProps.data.timestamp) }}</span>
                </template>
              </Column>
              <Column field="action" header="Acțiune" style="width: 25%">
                <template #body="slotProps">
                  <Tag :value="slotProps.data.action" :severity="getActivitySeverity(slotProps.data.action)" />
                </template>
              </Column>
              <Column field="user" header="Utilizator" style="width: 25%"></Column>
              <Column field="details" header="Detalii"></Column>
            </DataTable>
          </template>
        </Card>
        
        <Card class="p-mt-3">
          <template #title>
            <div class="card-title">
              <i class="pi pi-exclamation-circle p-mr-2"></i>
              Alerte Sistem
            </div>
          </template>
          <template #content>
            <div v-if="loading.alerts" class="p-d-flex p-jc-center">
              <ProgressSpinner />
            </div>
            <div v-else-if="systemAlerts.length === 0" class="empty-alerts">
              <i class="pi pi-check-circle"></i>
              <p>Nu există alerte în sistem</p>
            </div>
            <ul v-else class="alerts-list">
              <li v-for="alert in systemAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
                <i :class="'pi ' + getAlertIcon(alert.severity)"></i>
                <div class="alert-content">
                  <div class="alert-title">{{ alert.title }}</div>
                  <div class="alert-message">{{ alert.message }}</div>
                  <div class="alert-time">{{ formatDate(alert.timestamp) }}</div>
                </div>
                <Button 
                  icon="pi pi-times" 
                  class="p-button-rounded p-button-text" 
                  @click="dismissAlert(alert.id)"
                />
              </li>
            </ul>
          </template>
        </Card>
      </div>
      
      <!-- Quick Actions -->
      <div class="p-col-12">
        <Card>
          <template #title>
            <div class="card-title">
              <i class="pi pi-bolt p-mr-2"></i>
              Acțiuni Rapide
            </div>
          </template>
          <template #content>
            <div class="quick-actions p-grid">
              <div class="p-col-6 p-sm-4 p-md-3 p-xl-2">
                <div class="action-card" @click="navigateTo('/admin/manage-users')">
                  <i class="pi pi-users"></i>
                  <span>Gestionare Utilizatori</span>
                </div>
              </div>
              <div class="p-col-6 p-sm-4 p-md-3 p-xl-2">
                <div class="action-card" @click="navigateTo('/admin/manage-faculties')">
                  <i class="pi pi-building"></i>
                  <span>Gestionare Facultăți</span>
                </div>
              </div>
              <div class="p-col-6 p-sm-4 p-md-3 p-xl-2">
                <div class="action-card" @click="runSyncJob">
                  <i class="pi pi-sync"></i>
                  <span>Sincronizare Date</span>
                </div>
              </div>
              <div class="p-col-6 p-sm-4 p-md-3 p-xl-2">
                <div class="action-card" @click="navigateTo('/exam-schedule')">
                  <i class="pi pi-calendar"></i>
                  <span>Vizualizare Calendar</span>
                </div>
              </div>
              <div class="p-col-6 p-sm-4 p-md-3 p-xl-2">
                <div class="action-card" @click="openBackupDialog">
                  <i class="pi pi-database"></i>
                  <span>Backup Sistem</span>
                </div>
              </div>
              <div class="p-col-6 p-sm-4 p-md-3 p-xl-2">
                <div class="action-card" @click="navigateTo('/admin/system-logs')">
                  <i class="pi pi-list"></i>
                  <span>Vizualizare Logs</span>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Backup Dialog -->
    <Dialog 
      v-model:visible="backupDialog.visible" 
      header="Backup Sistem" 
      :style="{width: '450px'}" 
      :modal="true"
    >
      <div class="p-fluid">
        <div class="p-field">
          <label for="backupName">Denumire Backup</label>
          <InputText 
            id="backupName" 
            v-model="backupDialog.name" 
            placeholder="ex: backup_sesiune_vara_2025"
          />
        </div>
        <div class="p-field">
          <label for="backupType">Ce doriți să includeți?</label>
          <div class="p-mt-2">
            <div class="p-field-checkbox">
              <Checkbox id="backupDb" v-model="backupDialog.includeDb" :binary="true" />
              <label for="backupDb">Bază de date</label>
            </div>
            <div class="p-field-checkbox">
              <Checkbox id="backupFiles" v-model="backupDialog.includeFiles" :binary="true" />
              <label for="backupFiles">Fișiere încărcate</label>
            </div>
            <div class="p-field-checkbox">
              <Checkbox id="backupReports" v-model="backupDialog.includeReports" :binary="true" />
              <label for="backupReports">Rapoarte generate</label>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="backupDialog.visible = false"
          :disabled="backupDialog.loading"
        />
        <Button 
          label="Creare Backup" 
          icon="pi pi-check" 
          @click="createBackup"
          :loading="backupDialog.loading"
          :disabled="!isBackupFormValid"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import AdminService from '@/services/admin.service'

export default {
  name: 'AdminDashboardView',
  components: {
    Card,
    DataTable,
    Column,
    Dialog,
    Button,
    InputText,
    Checkbox,
    Tag,
    ProgressSpinner
  },
  setup() {
    const router = useRouter()
    const store = useStore()
    
    // Loading states
    const loading = reactive({
      stats: true,
      activity: true,
      alerts: true
    })
    
    // System statistics
    const stats = reactive({
      totalUsers: 0,
      totalExams: 0,
      totalGroups: 0,
      totalRooms: 0,
      apiStatus: true,
      syncStatus: true,
      dbStatus: true,
      storageStatus: true
    })
    
    // Recent activity
    const recentActivity = ref([])
    
    // System alerts
    const systemAlerts = ref([])
    
    // Backup dialog
    const backupDialog = reactive({
      visible: false,
      name: '',
      includeDb: true,
      includeFiles: true,
      includeReports: true,
      loading: false
    })
    
    // Computed property to check if backup form is valid
    const isBackupFormValid = computed(() => {
      return backupDialog.name.trim() && 
        (backupDialog.includeDb || backupDialog.includeFiles || backupDialog.includeReports)
    })
    
    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
    
    // Get activity severity
    const getActivitySeverity = (action) => {
      switch(action) {
        case 'LOGIN':
        case 'SYNC':
        case 'VIEW':
          return 'info'
        case 'CREATE':
        case 'UPDATE':
          return 'success'
        case 'DELETE':
          return 'danger'
        case 'WARN':
          return 'warning'
        default:
          return 'info'
      }
    }
    
    // Get alert icon
    const getAlertIcon = (severity) => {
      switch(severity) {
        case 'error':
          return 'pi-times-circle'
        case 'warning':
          return 'pi-exclamation-triangle'
        case 'info':
          return 'pi-info-circle'
        default:
          return 'pi-info-circle'
      }
    }
    
    // Navigate to a page
    const navigateTo = (path) => {
      router.push(path)
    }
    
    // Open backup dialog
    const openBackupDialog = () => {
      backupDialog.name = `backup_${new Date().toISOString().split('T')[0]}`
      backupDialog.visible = true
    }
    
    // Create backup
    const createBackup = async () => {
      if (!isBackupFormValid.value) {
        store.dispatch('notifications/showNotification', {
          severity: 'warn',
          summary: 'Validare',
          detail: 'Completați denumirea backup-ului și selectați cel puțin o opțiune',
          life: 3000
        })
        return
      }
      
      try {
        backupDialog.loading = true
        
        // Create request data
        const backupData = {
          name: backupDialog.name,
          includeDb: backupDialog.includeDb,
          includeFiles: backupDialog.includeFiles,
          includeReports: backupDialog.includeReports
        }
        
        // In a real implementation, call the API
        // await AdminService.createBackup(backupData)
        
        // For demo purposes, simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Backup Creat',
          detail: 'Backup-ul a fost creat cu succes',
          life: 3000
        })
        
        // Close dialog
        backupDialog.visible = false
      } catch (error) {
        console.error('Error creating backup:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut crea backup-ul',
          life: 5000
        })
      } finally {
        backupDialog.loading = false
      }
    }
    
    // Run sync job
    const runSyncJob = async () => {
      try {
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Sincronizare',
          detail: 'Sincronizarea datelor a început...',
          life: 3000
        })
        
        // In a real implementation, call the API
        // await store.dispatch('sync/fetchAndSyncData')
        
        // For demo purposes, simulate API call
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        // Update sync status
        stats.syncStatus = true
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare',
          detail: 'Datele au fost sincronizate cu succes',
          life: 3000
        })
      } catch (error) {
        console.error('Error syncing data:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut sincroniza datele',
          life: 5000
        })
      }
    }
    
    // Dismiss alert
    const dismissAlert = async (alertId) => {
      try {
        // In a real implementation, call the API
        // await AdminService.dismissAlert(alertId)
        
        // For demo purposes, remove from local state
        systemAlerts.value = systemAlerts.value.filter(alert => alert.id !== alertId)
      } catch (error) {
        console.error('Error dismissing alert:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut șterge alerta',
          life: 5000
        })
      }
    }
    
    // Load dashboard data
    const loadDashboardData = async () => {
      try {
        // Load stats
        loading.stats = true
        
        // In a real implementation, call the API
        // const statsResponse = await AdminService.getSystemStats()
        // Object.assign(stats, statsResponse.data)
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        Object.assign(stats, {
          totalUsers: 152,
          totalExams: 78,
          totalGroups: 35,
          totalRooms: 24,
          apiStatus: true,
          syncStatus: true,
          dbStatus: true,
          storageStatus: true
        })
      } catch (error) {
        console.error('Error loading stats:', error)
      } finally {
        loading.stats = false
      }
      
      try {
        // Load recent activity
        loading.activity = true
        
        // In a real implementation, call the API
        // const activityResponse = await AdminService.getRecentActivity()
        // recentActivity.value = activityResponse.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 800))
        
        recentActivity.value = [
          {
            id: 1,
            timestamp: new Date(2025, 4, 11, 15, 30),
            action: 'LOGIN',
            user: 'admin@example.com',
            details: 'Autentificare reușită'
          },
          {
            id: 2,
            timestamp: new Date(2025, 4, 11, 14, 45),
            action: 'CREATE',
            user: 'secretariat@example.com',
            details: 'Creare examen nou: Programare Web'
          },
          {
            id: 3,
            timestamp: new Date(2025, 4, 11, 13, 20),
            action: 'UPDATE',
            user: 'prof.ionescu@example.com',
            details: 'Actualizare configurație examen: Algoritmi'
          },
          {
            id: 4,
            timestamp: new Date(2025, 4, 11, 12, 15),
            action: 'SYNC',
            user: 'sistem',
            details: 'Sincronizare date USV reușită'
          },
          {
            id: 5,
            timestamp: new Date(2025, 4, 11, 10, 5),
            action: 'DELETE',
            user: 'admin@example.com',
            details: 'Ștergere utilizator: user123@example.com'
          }
        ]
      } catch (error) {
        console.error('Error loading activity:', error)
      } finally {
        loading.activity = false
      }
      
      try {
        // Load system alerts
        loading.alerts = true
        
        // In a real implementation, call the API
        // const alertsResponse = await AdminService.getSystemAlerts()
        // systemAlerts.value = alertsResponse.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 600))
        
        systemAlerts.value = [
          {
            id: 1,
            severity: 'warning',
            title: 'Spațiu de stocare limitat',
            message: 'Spațiul de stocare pentru rapoarte este aproape plin (85%). Considerați ștergerea rapoartelor vechi.',
            timestamp: new Date(2025, 4, 11, 9, 0)
          },
          {
            id: 2,
            severity: 'info',
            title: 'Sesiune de examinare activă',
            message: 'Sesiunea de vară 2025 este activă în prezent. 78 de examene programate.',
            timestamp: new Date(2025, 4, 10, 8, 30)
          }
        ]
      } catch (error) {
        console.error('Error loading alerts:', error)
      } finally {
        loading.alerts = false
      }
    }
    
    // Initialize
    onMounted(() => {
      loadDashboardData()
    })
    
    return {
      loading,
      stats,
      recentActivity,
      systemAlerts,
      backupDialog,
      isBackupFormValid,
      formatDate,
      getActivitySeverity,
      getAlertIcon,
      navigateTo,
      openBackupDialog,
      createBackup,
      runSyncJob,
      dismissAlert
    }
  }
}
</script>

<style lang="scss" scoped>
.admin-dashboard {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  .card-title {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
    
    i {
      margin-right: 0.5rem;
      color: #3f51b5;
    }
  }
  
  .stats-grid {
    .stat-card {
      display: flex;
      align-items: center;
      padding: 1rem;
      border-radius: 8px;
      background-color: #fff;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      
      .stat-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin-right: 1rem;
        
        i {
          font-size: 1.5rem;
          color: #fff;
        }
      }
      
      .stat-content {
        display: flex;
        flex-direction: column;
        
        .stat-value {
          font-size: 1.75rem;
          font-weight: 700;
          color: #2c3e50;
        }
        
        .stat-label {
          font-size: 0.875rem;
          color: #6c757d;
        }
      }
      
      &.users {
        .stat-icon {
          background-color: #3f51b5;
        }
      }
      
      &.exams {
        .stat-icon {
          background-color: #f44336;
        }
      }
      
      &.groups {
        .stat-icon {
          background-color: #4caf50;
        }
      }
      
      &.rooms {
        .stat-icon {
          background-color: #ff9800;
        }
      }
    }
    
    .system-status {
      margin-top: 1rem;
      
      h3 {
        font-size: 1.1rem;
        margin-top: 0;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e9ecef;
      }
      
      .status-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
        
        .status-label {
          font-weight: 500;
          margin-right: 0.5rem;
          min-width: 90px;
        }
      }
    }
  }
  
  .alerts-list {
    list-style: none;
    padding: 0;
    margin: 0;
    
    .alert-item {
      display: flex;
      align-items: flex-start;
      padding: 1rem;
      margin-bottom: 0.75rem;
      border-radius: 6px;
      background-color: #f8f9fa;
      
      i {
        font-size: 1.25rem;
        margin-right: 0.75rem;
        margin-top: 0.125rem;
      }
      
      .alert-content {
        flex: 1;
        
        .alert-title {
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 0.25rem;
        }
        
        .alert-message {
          color: #495057;
          margin-bottom: 0.5rem;
        }
        
        .alert-time {
          font-size: 0.75rem;
          color: #6c757d;
        }
      }
      
      &.error {
        background-color: #ffebee;
        
        i {
          color: #f44336;
        }
        
        .alert-title {
          color: #d32f2f;
        }
      }
      
      &.warning {
        background-color: #fff8e1;
        
        i {
          color: #ff9800;
        }
        
        .alert-title {
          color: #ef6c00;
        }
      }
      
      &.info {
        background-color: #e3f2fd;
        
        i {
          color: #2196f3;
        }
        
        .alert-title {
          color: #1976d2;
        }
      }
    }
  }
  
  .empty-alerts {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 0;
    
    i {
      font-size: 2.5rem;
      color: #4caf50;
      margin-bottom: 0.5rem;
    }
    
    p {
      color: #6c757d;
      margin: 0;
    }
  }
  
  .quick-actions {
    .action-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 1.5rem 0.5rem;
      border-radius: 8px;
      background-color: #f8f9fa;
      cursor: pointer;
      transition: all 0.2s ease-in-out;
      height: 100%;
      min-height: 120px;
      
      i {
        font-size: 2rem;
        color: #3f51b5;
        margin-bottom: 0.75rem;
      }
      
      span {
        text-align: center;
        color: #2c3e50;
        font-weight: 500;
      }
      
      &:hover {
        background-color: #e9ecef;
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }
    }
  }
}
</style>
