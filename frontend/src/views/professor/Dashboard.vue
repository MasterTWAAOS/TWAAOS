<template>
  <div class="professor-dashboard">
    <h1>Dashboard Cadru Didactic</h1>
    
    <div class="p-grid p-mt-3">
      <!-- Summary Stats Cards -->
      <div class="p-col-12 p-md-3">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-inbox"></i>
              <span>Propuneri în Așteptare</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.pendingProposals || 0 }}</div>
              <div class="stats-description">Propuneri care așteaptă validare</div>
              <router-link :to="{ name: 'ReviewProposals' }" class="stats-link">
                <Button label="Vezi propunerile" class="p-button-sm p-button-outlined" />
              </router-link>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="p-col-12 p-md-3">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-exclamation-circle"></i>
              <span>Examene Neprogramate</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.pendingExams || 0 }}</div>
              <div class="stats-description">Fără dată propusă</div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="p-col-12 p-md-3">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-calendar-check"></i>
              <span>Examene Programate</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.scheduledExams || 0 }}</div>
              <div class="stats-description">din {{ stats.totalSubjects }} discipline</div>
              <ProgressBar :value="scheduledExamsPercentage" class="mt-2" />
            </div>
          </template>
        </Card>
      </div>
      
      <div class="p-col-12 p-md-3">
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
              <div class="next-exam-location">
                <template v-if="Array.isArray(nextExam.roomNames) && nextExam.roomNames.length">
                  Săli: {{ formatRoomsList(nextExam.roomNames) }}
                </template>
                <template v-else-if="nextExam.room">
                  Sala: {{ nextExam.room }}
                </template>
                <template v-else>
                  Sală: Nespecificată
                </template>
              </div>
            </div>
            <div class="stats-content no-exam" v-else>
              <div class="no-exam-message">Nu aveți examene programate în perioada imediat următoare.</div>
            </div>
          </template>
        </Card>
      </div>
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
            <p>Nu aveți examene programate în perioada următoare.</p>
          </div>
          <div v-else>
            <DataTable 
              :value="scheduledExams" 
              :paginator="scheduledExams.length > 5" 
              :rows="5" 
              sortField="date" 
              :sortOrder="1" 
              stripedRows
              dataKey="id"
              responsiveLayout="scroll"
              class="p-datatable-sm"
            >
              <Column field="subject" header="Disciplina" style="width: 25%"></Column>
              <Column field="groupName" header="Grupa" style="width: 15%"></Column>
              <Column field="date" header="Data" style="width: 15%">
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.date) }}
                </template>
              </Column>
              <Column field="startTime" header="Interval" style="width: 15%">
                <template #body="slotProps">
                  {{ slotProps.data.startTime }} - {{ slotProps.data.endTime }}
                </template>
              </Column>
              <Column field="roomNames" header="Săli" style="width: 15%">
                <template #body="slotProps">
                  <div>
                    <!-- Handle different room data formats -->
                    <template v-if="Array.isArray(slotProps.data.roomNames) && slotProps.data.roomNames.length">
                      <!-- Display all room names joined by commas -->
                      {{ formatRoomsList(slotProps.data.roomNames) }}
                    </template>
                    <template v-else-if="slotProps.data.room">
                      <!-- Legacy format with single room -->
                      {{ slotProps.data.room }}
                    </template>
                    <template v-else>
                      <!-- No room data -->
                      Nespecificată
                    </template>
                  </div>
                </template>
              </Column>
            </DataTable>
          </div>
        </template>
      </Card>
    </div>

    <!-- Rejected exams section -->
    <div class="p-mt-4">
      <Card v-if="rejectedExams.length > 0">
        <template #title>
          <h2>Propuneri Respinse</h2>
        </template>
        <template #content>
          <div v-if="loading.rejectedExams" class="loading-container">
            <ProgressSpinner />
          </div>
          <div v-else>
            <DataTable 
              :value="rejectedExams" 
              :paginator="rejectedExams.length > 5" 
              :rows="5" 
              stripedRows
              dataKey="id"
              responsiveLayout="scroll"
              class="p-datatable-sm"
            >
              <Column field="subject" header="Disciplina" style="width: 40%"></Column>
              <Column field="groupName" header="Grupa" style="width: 40%"></Column>
              <Column field="status" header="Status" style="width: 20%">
                <template #body>
                  <span class="status-badge status-rejected">respins</span>
                </template>
              </Column>
            </DataTable>
          </div>
        </template>
      </Card>
    </div>

    <!-- Pending Exams (Unprogrammed) -->
    <div class="p-mt-4">
      <Card v-if="pendingExams.length > 0">
        <template #title>
          <h2>Examene Neprogramate</h2>
        </template>
        <template #content>
          <div v-if="loading.pendingExams" class="loading-container">
            <ProgressSpinner />
          </div>
          <div v-else>
            <DataTable 
              :value="pendingExams" 
              :paginator="pendingExams.length > 5" 
              :rows="5" 
              stripedRows
              dataKey="id"
              responsiveLayout="scroll"
              class="p-datatable-sm"
            >
              <Column field="subject" header="Disciplina" style="width: 50%"></Column>
              <Column field="groupName" header="Grupa" style="width: 30%"></Column>
              <Column field="status" header="Status" style="width: 20%">
                <template #body>
                  <span class="status-badge status-pending">în așteptare</span>
                </template>
              </Column>
            </DataTable>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import examService from '@/services/exam.service'

export default {
  name: 'ProfessorDashboard',
  components: {
    Card,
    DataTable,
    Column,
    Button,
    ProgressBar,
    ProgressSpinner
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // Dashboard stats
    const stats = ref({
      scheduledExams: 0,
      totalSubjects: 0,
      pendingExams: 0,
      pendingProposals: 0,
      rejectedExams: 0
    })
    
    // Loading states
    const loading = reactive({
      scheduledExams: false,
      pendingExams: false,
      pendingProposals: false,
      nextExam: false,
      rejectedExams: false
    })
    
    // Exams data
    const scheduledExams = ref([])
    const pendingExams = ref([])
    const pendingProposals = ref([])
    const rejectedExams = ref([])
    
    // Next exam
    const nextExam = ref(null)
    
    // Calculate percentage of scheduled exams with 2 decimals
    const scheduledExamsPercentage = computed(() => {
      if (!stats.value.totalSubjects) return 0
      return parseFloat(((stats.value.scheduledExams / stats.value.totalSubjects) * 100).toFixed(2))
    })
    
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
    
    // Format multiple rooms list
    const formatRoomsList = (rooms) => {
      if (!rooms || !Array.isArray(rooms) || rooms.length === 0) {
        return 'Nespecificată'
      }
      
      return rooms.join(', ')
    }
    
    // Get only the day part from a date
    const getDayOfMonth = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.getDate()
    }
    
    // Get month name from date
    const getMonthName = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { month: 'long' }).format(date)
    }
    
    const viewExamDetails = (exam) => {
      router.push({ name: 'SetupExams' })
    }
    
    // Fetch data
    const fetchDashboardData = async () => {
      try {
        const user = store.getters['auth/currentUser']
        if (!user || !user.id) {
          console.error('User not logged in or missing ID')
          return
        }
        
        const teacherId = user.id
        loading.scheduledExams = true
        loading.pendingExams = true
        loading.pendingProposals = true
        loading.rejectedExams = true
        loading.nextExam = true
        
        console.log(`Fetching dashboard data for teacher ID: ${teacherId}`)
        const response = await examService.getTeacherDashboard(teacherId)
        const dashboardData = response.data
        
        // Process exam data helper function
        const processExamData = (exam) => ({
          id: exam.id,
          subject: exam.subjectName || 'Necunoscut',
          subjectId: exam.subjectId,
          subjectCode: exam.subjectShortName,
          groupName: exam.groupName || 'Necunoscut',
          groupId: exam.groupId,
          date: exam.date,
          startTime: exam.startTime || '00:00',
          endTime: exam.endTime || '00:00',
          roomIds: exam.roomIds || [],
          roomNames: exam.roomNames || [],
          room: exam.roomName,
          status: exam.status
        })
        
        // Update scheduled exams (approved)
        if (dashboardData.scheduledExams && Array.isArray(dashboardData.scheduledExams)) {
          scheduledExams.value = dashboardData.scheduledExams.map(processExamData)
        } else {
          scheduledExams.value = []
        }
        
        // Update pending exams
        if (dashboardData.pendingExams && Array.isArray(dashboardData.pendingExams)) {
          pendingExams.value = dashboardData.pendingExams.map(processExamData)
        } else {
          pendingExams.value = []
        }
        
        // Update pending proposals
        if (dashboardData.pendingProposals && Array.isArray(dashboardData.pendingProposals)) {
          pendingProposals.value = dashboardData.pendingProposals.map(processExamData)
        } else {
          pendingProposals.value = []
        }
        
        // Update rejected exams
        if (dashboardData.rejectedExams && Array.isArray(dashboardData.rejectedExams)) {
          rejectedExams.value = dashboardData.rejectedExams.map(processExamData)
        } else {
          rejectedExams.value = []
        }
        
        // Update next exam
        if (dashboardData.nextExam) {
          nextExam.value = processExamData(dashboardData.nextExam)
        } else {
          nextExam.value = null
        }
        
        // Update stats
        if (dashboardData.stats) {
          stats.value = {
            scheduledExams: dashboardData.stats.scheduledExams || 0,
            totalSubjects: dashboardData.stats.totalSubjects || 0,
            pendingExams: dashboardData.stats.pendingExams || 0,
            pendingProposals: dashboardData.stats.pendingProposals || 0,
            rejectedExams: dashboardData.stats.rejectedExams || 0
          }
        }
        
        console.log('Dashboard data loaded successfully:', {
          scheduledExams: scheduledExams.value.length,
          hasNextExam: !!nextExam.value
        })
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca datele pentru dashboard',
          life: 5000
        })
      } finally {
        loading.scheduledExams = false
        loading.pendingExams = false
        loading.pendingProposals = false
        loading.rejectedExams = false
        loading.nextExam = false
      }
    }
    
    // Initialize
    onMounted(() => {
      fetchDashboardData()
    })
    
    return {
      stats,
      loading,
      scheduledExams,
      pendingExams,
      pendingProposals,
      rejectedExams,
      nextExam,
      scheduledExamsPercentage,
      formatDate,
      formatDatetime,
      formatRoomsList,
      getDayOfMonth,
      getMonthName,
      viewExamDetails
    }
  }
}
</script>

<style lang="scss" scoped>
.professor-dashboard {
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
  
  .subject-name {
    font-weight: 500;
  }
  
  .subject-code {
    font-size: 0.875rem;
    color: #6c757d;
    margin-top: 0.25rem;
  }
  
  .proposed-date {
    .date {
      font-weight: 500;
    }
    
    .time {
      font-size: 0.875rem;
      color: #6c757d;
      margin-top: 0.25rem;
    }
  }
  
  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    text-align: center;
    
    &.status-pending {
      background-color: #FFF3CD;
      color: #856404;
    }
    
    &.status-approved {
      background-color: #D1E7DD;
      color: #0F5132;
    }
    
    &.status-proposed {
      background-color: #CCE5FF;
      color: #084298;
    }
    
    &.status-rejected {
      background-color: #F8D7DA;
      color: #842029;
    }
  }
  
  .progress-value {
    font-size: 0.8rem;
    margin-top: 0.25rem;
    color: #007bff;
    font-weight: 500;
  }
}
</style>
