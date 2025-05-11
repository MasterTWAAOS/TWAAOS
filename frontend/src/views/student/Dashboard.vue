<template>
  <div class="student-dashboard">
    <h1>Dashboard Șef de Grupă</h1>
    
    <div class="p-grid p-mt-3">
      <!-- Summary Stats Cards -->
      <div class="p-col-12 p-md-4">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-calendar-plus"></i>
              <span>Discipline Nepropuse</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.pendingSubjects }}</div>
              <div class="stats-description">Discipline fără dată propusă</div>
              <router-link :to="{ name: 'SGProposeDates' }" class="stats-link">
                <Button 
                  label="Propune Date" 
                  class="p-button-sm p-button-outlined" 
                  v-if="stats.pendingSubjects > 0"
                />
              </router-link>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="p-col-12 p-md-4">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-check-circle"></i>
              <span>Status Propuneri</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="status-item">
                <div class="status-label">
                  <span class="status-dot pending"></span>
                  <span>În așteptare: {{ stats.pendingProposals }}</span>
                </div>
              </div>
              <div class="status-item">
                <div class="status-label">
                  <span class="status-dot approved"></span>
                  <span>Aprobate: {{ stats.approvedProposals }}</span>
                </div>
              </div>
              <div class="status-item">
                <div class="status-label">
                  <span class="status-dot rejected"></span>
                  <span>Respinse: {{ stats.rejectedProposals }}</span>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="p-col-12 p-md-4">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-calendar"></i>
              <span>Următorul Examen</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content" v-if="nextExam">
              <div class="next-exam-subject">{{ nextExam.subject }}</div>
              <div class="next-exam-date">{{ formatDate(nextExam.date) }}</div>
              <div class="next-exam-time">{{ nextExam.startTime }} - {{ nextExam.endTime }}</div>
              <div class="next-exam-location">Sala {{ nextExam.room }}</div>
            </div>
            <div class="stats-content no-exam" v-else>
              <div class="no-exam-message">Nu aveți examene programate în perioada imediat următoare.</div>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Recent Proposals -->
    <div class="p-mt-4">
      <Card>
        <template #title>
          <h2>Propuneri Recente</h2>
        </template>
        <template #content>
          <div v-if="loading.recentProposals" class="loading-container">
            <ProgressSpinner />
          </div>
          <div v-else-if="recentProposals.length === 0" class="empty-state">
            <i class="pi pi-info-circle"></i>
            <p>Nu aveți propuneri recente.</p>
            <router-link :to="{ name: 'SGProposeDates' }">
              <Button label="Propune Date Examene" class="p-mt-2" />
            </router-link>
          </div>
          <div v-else>
            <DataTable 
              :value="recentProposals" 
              :rows="5" 
              :paginator="true"
              class="p-datatable-sm" 
              responsiveLayout="scroll"
            >
              <Column field="subject" header="Disciplină" :sortable="true"></Column>
              <Column field="date" header="Dată Propusă" :sortable="true">
                <template #body="slotProps">
                  <div>
                    <div>{{ formatDate(slotProps.data.date) }}</div>
                    <div class="time-display">{{ slotProps.data.startTime }} - {{ slotProps.data.endTime }}</div>
                  </div>
                </template>
              </Column>
              <Column field="status" header="Status" :sortable="true" style="width: 15%">
                <template #body="slotProps">
                  <Tag :value="slotProps.data.statusLabel" :severity="getStatusSeverity(slotProps.data.status)" />
                </template>
              </Column>
              <Column field="submittedDate" header="Trimis la" :sortable="true" style="width: 20%">
                <template #body="slotProps">
                  {{ formatDatetime(slotProps.data.submittedDate) }}
                </template>
              </Column>
              <Column field="comment" header="Comentarii" style="width: 20%">
                <template #body="slotProps">
                  <div v-if="slotProps.data.comment" class="proposal-comment">
                    {{ slotProps.data.comment }}
                  </div>
                  <div v-else-if="slotProps.data.rejectionReason" class="proposal-rejection">
                    {{ slotProps.data.rejectionReason }}
                  </div>
                  <div v-else>-</div>
                </template>
              </Column>
            </DataTable>
            
            <div class="p-mt-2 p-d-flex p-jc-end">
              <router-link :to="{ name: 'SGProposeDates' }">
                <Button 
                  label="Vezi toate propunerile" 
                  icon="pi pi-arrow-right" 
                  class="p-button-outlined p-button-sm"
                />
              </router-link>
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <!-- Scheduled Exams -->
    <div class="p-mt-4">
      <Card>
        <template #title>
          <h2>Examene Programate</h2>
        </template>
        <template #content>
          <div v-if="loading.scheduledExams" class="loading-container">
            <ProgressSpinner />
          </div>
          <div v-else-if="scheduledExams.length === 0" class="empty-state">
            <i class="pi pi-calendar-times"></i>
            <p>Nu aveți examene programate momentan.</p>
          </div>
          <div v-else>
            <DataTable 
              :value="scheduledExams" 
              :rows="5" 
              :paginator="true"
              class="p-datatable-sm" 
              responsiveLayout="scroll"
            >
              <Column field="subject" header="Disciplină" :sortable="true"></Column>
              <Column field="date" header="Data" :sortable="true" style="width: 15%">
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.date) }}
                </template>
              </Column>
              <Column field="time" header="Interval Orar" style="width: 15%">
                <template #body="slotProps">
                  {{ slotProps.data.startTime }} - {{ slotProps.data.endTime }}
                </template>
              </Column>
              <Column field="room" header="Sala" style="width: 10%"></Column>
              <Column field="professor" header="Cadru Didactic" style="width: 20%"></Column>
            </DataTable>
          </div>
        </template>
      </Card>
    </div>
    
    <!-- Calendar Preview -->
    <div class="p-mt-4">
      <Card>
        <template #title>
          <h2>Calendar Examene</h2>
        </template>
        <template #content>
          <div class="p-text-center p-my-3">
            <Button 
              label="Descarcă Calendar Examene" 
              icon="pi pi-download" 
              class="p-button-outlined"
              @click="downloadCalendar"
            />
          </div>
          
          <div class="calendar-info p-mt-3">
            <i class="pi pi-info-circle"></i>
            <span>Calendarul complet al examenelor poate fi descărcat și importat în aplicații precum Google Calendar, Microsoft Outlook sau Apple Calendar.</span>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import examService from '@/services/exam.service'

export default {
  name: 'StudentDashboard',
  components: {
    Card,
    DataTable,
    Column,
    Button,
    Tag,
    ProgressSpinner
  },
  setup() {
    const store = useStore()
    
    // Dashboard stats
    const stats = ref({
      pendingSubjects: 3,
      pendingProposals: 1,
      approvedProposals: 1,
      rejectedProposals: 1
    })
    
    // Loading states
    const loading = reactive({
      recentProposals: false,
      scheduledExams: false
    })
    
    // Data
    const recentProposals = ref([])
    const scheduledExams = ref([])
    const nextExam = ref(null)
    
    // Format functions
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric' 
      }).format(date)
    }
    
    const formatDatetime = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
    
    // Get status severity
    const getStatusSeverity = (status) => {
      switch (status) {
        case 'pending': return 'warning'
        case 'approved': return 'success'
        case 'rejected': return 'danger'
        default: return 'info'
      }
    }
    
    // Actions
    const downloadCalendar = () => {
      store.dispatch('notifications/showNotification', {
        severity: 'info',
        summary: 'Descărcare Calendar',
        detail: 'Calendarul examenelor a fost descărcat.',
        life: 3000
      })
    }
    
    // Fetch data
    const fetchDashboardData = async () => {
      try {
        // Fetch recent proposals
        await fetchRecentProposals()
        
        // Fetch scheduled exams
        await fetchScheduledExams()
        
        // Get next exam
        if (scheduledExams.value.length > 0) {
          nextExam.value = scheduledExams.value[0]
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca datele pentru dashboard',
          life: 5000
        })
      }
    }
    
    const fetchRecentProposals = async () => {
      try {
        loading.recentProposals = true
        
        // In a real implementation, we would call the API
        // const response = await examService.getMyProposals(5) // Get most recent 5
        // recentProposals.value = response.data
        
        // For demo purposes, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        recentProposals.value = [
          {
            id: 101,
            subject: 'Metode Numerice',
            date: '2025-06-10',
            startTime: '10:00',
            endTime: '12:00',
            status: 'approved',
            statusLabel: 'Aprobat',
            submittedDate: '2025-05-01T14:30:00',
            comment: 'Sala C2 rezervată pentru examen.',
            rejectionReason: null
          },
          {
            id: 102,
            subject: 'Baze de Date',
            date: '2025-06-15',
            startTime: '12:00',
            endTime: '14:00',
            status: 'pending',
            statusLabel: 'În așteptare',
            submittedDate: '2025-05-05T09:15:00',
            comment: null,
            rejectionReason: null
          },
          {
            id: 103,
            subject: 'Inteligență Artificială',
            date: '2025-06-12',
            startTime: '14:00',
            endTime: '16:00',
            status: 'rejected',
            statusLabel: 'Respins',
            submittedDate: '2025-05-03T16:45:00',
            comment: null,
            rejectionReason: 'Data propusă se suprapune cu un alt examen. Vă rog să propuneți o altă dată.'
          }
        ]
      } catch (error) {
        console.error('Error fetching recent proposals:', error)
      } finally {
        loading.recentProposals = false
      }
    }
    
    const fetchScheduledExams = async () => {
      try {
        loading.scheduledExams = true
        
        // In a real implementation, we would call the API
        // const response = await examService.getScheduledExams('CTI3') // Get exams for current group
        // scheduledExams.value = response.data
        
        // For demo purposes, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        scheduledExams.value = [
          {
            id: 201,
            subject: 'Metode Numerice',
            date: '2025-06-10',
            startTime: '10:00',
            endTime: '12:00',
            room: 'C2',
            professor: 'Prof. Dr. Ionescu Maria'
          }
        ]
      } catch (error) {
        console.error('Error fetching scheduled exams:', error)
      } finally {
        loading.scheduledExams = false
      }
    }
    
    // Initialize
    onMounted(() => {
      fetchDashboardData()
    })
    
    return {
      stats,
      loading,
      recentProposals,
      scheduledExams,
      nextExam,
      formatDate,
      formatDatetime,
      getStatusSeverity,
      downloadCalendar
    }
  }
}
</script>

<style lang="scss" scoped>
.student-dashboard {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  h2 {
    font-size: 1.25rem;
    color: #2c3e50;
    margin: 0;
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
      
      .stats-link {
        display: inline-block;
        margin-top: 0.75rem;
      }
      
      .status-item {
        margin-bottom: 0.75rem;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .status-label {
          display: flex;
          align-items: center;
          justify-content: center;
          
          .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 0.5rem;
            
            &.pending {
              background-color: #FFC107;
            }
            
            &.approved {
              background-color: #4CAF50;
            }
            
            &.rejected {
              background-color: #F44336;
            }
          }
        }
      }
      
      &.no-exam {
        .no-exam-message {
          color: #6c757d;
          font-style: italic;
        }
      }
      
      .next-exam-subject {
        font-weight: 600;
        font-size: 1.25rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
      }
      
      .next-exam-date {
        font-weight: 500;
        color: #2c3e50;
        margin-bottom: 0.25rem;
      }
      
      .next-exam-time, .next-exam-location {
        color: #6c757d;
      }
    }
  }
  
  .loading-container {
    display: flex;
    justify-content: center;
    padding: 2rem;
  }
  
  .empty-state {
    text-align: center;
    padding: 2rem 0;
    
    i {
      font-size: 2rem;
      color: #6c757d;
      margin-bottom: 0.5rem;
    }
    
    p {
      color: #6c757d;
      margin-bottom: 0;
    }
  }
  
  .time-display {
    font-size: 0.875rem;
    color: #6c757d;
  }
  
  .proposal-comment {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
  }
  
  .proposal-rejection {
    color: #f44336;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
  }
  
  .calendar-info {
    display: flex;
    align-items: flex-start;
    padding: 0.75rem;
    background-color: #e3f2fd;
    border-radius: 4px;
    
    i {
      font-size: 1.25rem;
      color: #1E88E5;
      margin-right: 0.75rem;
      margin-top: 0.1rem;
    }
    
    span {
      color: #2c3e50;
    }
  }
}
</style>
