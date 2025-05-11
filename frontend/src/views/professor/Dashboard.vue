<template>
  <div class="professor-dashboard">
    <h1>Dashboard Cadru Didactic</h1>
    
    <div class="p-grid p-mt-3">
      <!-- Summary Stats Cards -->
      <div class="p-col-12 p-md-4">
        <Card class="stats-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-inbox"></i>
              <span>Propuneri în Așteptare</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.pendingProposals }}</div>
              <div class="stats-description">Propuneri de validat</div>
              <router-link :to="{ name: 'ReviewProposals' }" class="stats-link">
                <Button 
                  label="Validare Propuneri" 
                  class="p-button-sm p-button-outlined" 
                  v-if="stats.pendingProposals > 0"
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
              <span>Examene Programate</span>
            </div>
          </template>
          <template #content>
            <div class="stats-content">
              <div class="stats-number">{{ stats.scheduledExams }}</div>
              <div class="stats-description">Din {{ stats.totalSubjects }} discipline</div>
              <ProgressBar :value="scheduledExamsPercentage" />
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
    
    <!-- Pending Proposals Preview -->
    <div class="p-mt-4">
      <Card>
        <template #title>
          <h2>Propuneri în Așteptare</h2>
        </template>
        <template #content>
          <div v-if="loading.pendingProposals" class="loading-container">
            <ProgressSpinner />
          </div>
          <div v-else-if="pendingProposals.length === 0" class="empty-state">
            <i class="pi pi-check-circle"></i>
            <p>Nu aveți propuneri în așteptare de validat.</p>
          </div>
          <div v-else>
            <DataTable 
              :value="pendingProposals" 
              :rows="5" 
              :paginator="true"
              class="p-datatable-sm" 
              responsiveLayout="scroll"
            >
              <Column field="subject.name" header="Disciplină">
                <template #body="slotProps">
                  <div>
                    <div class="subject-name">{{ slotProps.data.subject.name }}</div>
                    <div class="subject-code">{{ slotProps.data.subject.code }}</div>
                  </div>
                </template>
              </Column>
              <Column field="group.name" header="Grupă" style="width: 10%">
                <template #body="slotProps">
                  <Chip :label="slotProps.data.group.name" />
                </template>
              </Column>
              <Column field="proposedDate" header="Dată Propusă" style="width: 15%">
                <template #body="slotProps">
                  <div class="proposed-date">
                    <div class="date">{{ formatDate(slotProps.data.proposedDate) }}</div>
                    <div class="time">{{ slotProps.data.proposedTimeStart }} - {{ slotProps.data.proposedTimeEnd }}</div>
                  </div>
                </template>
              </Column>
              <Column field="submittedDate" header="Trimis la" style="width: 15%">
                <template #body="slotProps">
                  {{ formatDatetime(slotProps.data.submittedDate) }}
                </template>
              </Column>
              <Column header="Acțiuni" style="width: 15%">
                <template #body="slotProps">
                  <Button 
                    icon="pi pi-check" 
                    class="p-button-success p-button-sm p-mr-1" 
                    v-tooltip.top="'Aprobă propunerea'"
                    @click="approveProposal(slotProps.data)"
                  />
                  <Button 
                    icon="pi pi-times" 
                    class="p-button-danger p-button-sm" 
                    v-tooltip.top="'Respinge propunerea'"
                    @click="rejectProposal(slotProps.data)"
                  />
                </template>
              </Column>
            </DataTable>
            
            <div class="p-mt-2 p-d-flex p-jc-end">
              <router-link :to="{ name: 'ReviewProposals' }">
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
              <Column field="group" header="Grupă" :sortable="true" style="width: 10%">
                <template #body="slotProps">
                  <Chip :label="slotProps.data.group" />
                </template>
              </Column>
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
              <Column header="Acțiuni" style="width: 15%">
                <template #body="slotProps">
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-secondary p-button-sm" 
                    v-tooltip.top="'Vizualizează detalii'"
                    @click="viewExamDetails(slotProps.data)"
                  />
                </template>
              </Column>
            </DataTable>
            
            <div class="p-mt-2 p-d-flex p-jc-end">
              <router-link :to="{ name: 'SetupExams' }">
                <Button 
                  label="Configurare Examene" 
                  icon="pi pi-cog" 
                  class="p-button-outlined p-button-sm"
                />
              </router-link>
            </div>
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
    Chip,
    ProgressBar,
    ProgressSpinner
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // Dashboard stats
    const stats = ref({
      pendingProposals: 0,
      scheduledExams: 0,
      totalSubjects: 0
    })
    
    // Loading states
    const loading = reactive({
      pendingProposals: false,
      scheduledExams: false
    })
    
    // Data
    const pendingProposals = ref([])
    const scheduledExams = ref([])
    const nextExam = ref(null)
    
    // Computed percentage
    const scheduledExamsPercentage = computed(() => {
      return stats.value.totalSubjects ? (stats.value.scheduledExams / stats.value.totalSubjects) * 100 : 0
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
    
    // Actions
    const approveProposal = (proposal) => {
      router.push({ name: 'ReviewProposals' })
    }
    
    const rejectProposal = (proposal) => {
      router.push({ name: 'ReviewProposals' })
    }
    
    const viewExamDetails = (exam) => {
      router.push({ name: 'SetupExams' })
    }
    
    // Fetch data
    const fetchDashboardData = async () => {
      try {
        // Fetch pending proposals
        await fetchPendingProposals()
        
        // Fetch scheduled exams
        await fetchScheduledExams()
        
        // Get dashboard stats
        stats.value = {
          pendingProposals: pendingProposals.value.length,
          scheduledExams: scheduledExams.value.length,
          totalSubjects: scheduledExams.value.length + pendingProposals.value.length + 3 // Some not yet proposed
        }
        
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
    
    const fetchPendingProposals = async () => {
      try {
        loading.pendingProposals = true
        
        // In a real implementation, we would call the API
        // const response = await examService.getPendingProposals()
        // pendingProposals.value = response.data
        
        // For demo purposes, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        pendingProposals.value = [
          {
            id: 1,
            subject: { name: 'Programare Orientată pe Obiecte', code: 'POO23' },
            group: { name: 'CTI2', program: 'Calculatoare și Tehnologia Informației', year: 2 },
            proposedDate: '2025-06-10',
            proposedTimeStart: '09:00',
            proposedTimeEnd: '11:00',
            status: 'pending',
            submittedBy: { name: 'Popescu Ion', email: 'ion.popescu@student.usv.ro' },
            submittedDate: '2025-05-05T14:30:00',
            reviewedBy: null,
            reviewDate: null,
            comments: null,
            rejectionReason: null
          },
          {
            id: 4,
            subject: { name: 'Baze de Date', code: 'BD32' },
            group: { name: 'AITC2', program: 'Automatică și Informatică Aplicată', year: 2 },
            proposedDate: '2025-06-18',
            proposedTimeStart: '10:00',
            proposedTimeEnd: '12:00',
            status: 'pending',
            submittedBy: { name: 'Dumitrescu Elena', email: 'elena.dumitrescu@student.usv.ro' },
            submittedDate: '2025-05-08T09:15:00',
            reviewedBy: null,
            reviewDate: null,
            comments: null,
            rejectionReason: null
          },
          {
            id: 5,
            subject: { name: 'Sisteme de Operare', code: 'SO24' },
            group: { name: 'CTI2', program: 'Calculatoare și Tehnologia Informației', year: 2 },
            proposedDate: '2025-06-20',
            proposedTimeStart: '12:00',
            proposedTimeEnd: '14:00',
            status: 'pending',
            submittedBy: { name: 'Popescu Ion', email: 'ion.popescu@student.usv.ro' },
            submittedDate: '2025-05-09T11:30:00',
            reviewedBy: null,
            reviewDate: null,
            comments: null,
            rejectionReason: null
          }
        ]
      } catch (error) {
        console.error('Error fetching pending proposals:', error)
      } finally {
        loading.pendingProposals = false
      }
    }
    
    const fetchScheduledExams = async () => {
      try {
        loading.scheduledExams = true
        
        // In a real implementation, we would call the API
        // const response = await examService.getScheduledExams()
        // scheduledExams.value = response.data
        
        // For demo purposes, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        scheduledExams.value = [
          {
            id: 201,
            subject: 'Rețele de Calculatoare',
            group: 'CTI3',
            date: '2025-06-15',
            startTime: '12:00',
            endTime: '14:00',
            room: 'C3'
          },
          {
            id: 202,
            subject: 'Inteligență Artificială',
            group: 'CTI4',
            date: '2025-06-18',
            startTime: '10:00',
            endTime: '12:00',
            room: 'A2'
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
      pendingProposals,
      scheduledExams,
      nextExam,
      scheduledExamsPercentage,
      formatDate,
      formatDatetime,
      approveProposal,
      rejectProposal,
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
}
</style>
