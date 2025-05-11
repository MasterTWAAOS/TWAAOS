<template>
  <div class="propose-dates">
    <h1>Propunere Date Examene</h1>
    
    <div class="p-grid">
      <!-- Subjects pending proposals -->
      <div class="p-col-12 p-lg-8">
        <Card>
          <template #title>
            <h2>Discipline fără dată de examen propusă</h2>
          </template>
          <template #content>
            <div v-if="loading.subjects" class="loading-container">
              <ProgressSpinner />
            </div>
            <div v-else-if="pendingSubjects.length === 0" class="empty-state">
              <i class="pi pi-check-circle"></i>
              <h3>Toate propunerile au fost trimise</h3>
              <p>Toate disciplinele din acest semestru au deja o dată de examen propusă sau aprobată.</p>
            </div>
            <div v-else class="subjects-list">
              <DataTable 
                :value="pendingSubjects" 
                class="p-datatable-sm" 
                responsiveLayout="scroll"
                v-model:selection="selectedSubject"
                selectionMode="single"
                dataKey="id"
                @row-select="onSubjectSelect"
              >
                <Column field="name" header="Denumire">
                  <template #body="slotProps">
                    <div>
                      <div class="subject-name">{{ slotProps.data.name }}</div>
                      <div class="subject-code">{{ slotProps.data.code }}</div>
                    </div>
                  </template>
                </Column>
                <Column field="professor" header="Cadru Didactic" style="width: 25%"></Column>
                <Column field="semester" header="Semestru" style="width: 15%">
                  <template #body="slotProps">
                    <Tag :value="slotProps.data.semester"></Tag>
                  </template>
                </Column>
                <Column header="Acțiuni" style="width: 15%">
                  <template #body="slotProps">
                    <Button 
                      icon="pi pi-calendar-plus" 
                      class="p-button-primary p-button-sm" 
                      v-tooltip.top="'Propune dată examen'"
                      @click="openProposeDialog(slotProps.data)"
                    />
                  </template>
                </Column>
              </DataTable>
            </div>
          </template>
        </Card>
      </div>
      
      <!-- Status and upcoming exams -->
      <div class="p-col-12 p-lg-4">
        <Card class="p-mb-3">
          <template #title>
            <h2>Status Propuneri</h2>
          </template>
          <template #content>
            <div class="status-summary">
              <div class="status-item">
                <div class="status-number">{{ proposalStats.pending }}</div>
                <div class="status-label">În așteptare</div>
                <ProgressBar :value="proposalStats.pendingPercentage" class="status-progress" severity="warning" />
              </div>
              
              <div class="status-item">
                <div class="status-number">{{ proposalStats.approved }}</div>
                <div class="status-label">Aprobate</div>
                <ProgressBar :value="proposalStats.approvedPercentage" class="status-progress" severity="success" />
              </div>
              
              <div class="status-item">
                <div class="status-number">{{ proposalStats.rejected }}</div>
                <div class="status-label">Respinse</div>
                <ProgressBar :value="proposalStats.rejectedPercentage" class="status-progress" severity="danger" />
              </div>
              
              <div class="status-item">
                <div class="status-number">{{ proposalStats.notProposed }}</div>
                <div class="status-label">Nepropuse</div>
                <ProgressBar :value="proposalStats.notProposedPercentage" class="status-progress" severity="info" />
              </div>
            </div>
          </template>
        </Card>
        
        <Card>
          <template #title>
            <h2>Următoarele Examene</h2>
          </template>
          <template #content>
            <div v-if="loading.upcomingExams" class="loading-container">
              <ProgressSpinner />
            </div>
            <div v-else-if="upcomingExams.length === 0" class="empty-state">
              <i class="pi pi-calendar"></i>
              <p>Nu există examene programate în perioada imediat următoare.</p>
            </div>
            <div v-else class="upcoming-exams">
              <ul class="exam-list">
                <li v-for="exam in upcomingExams" :key="exam.id" class="exam-item">
                  <div class="exam-date">
                    <div class="date">{{ formatDate(exam.date) }}</div>
                    <div class="time">{{ exam.startTime }} - {{ exam.endTime }}</div>
                  </div>
                  <div class="exam-details">
                    <div class="exam-subject">{{ exam.subject }}</div>
                    <div class="exam-info">
                      <span class="location">Sala {{ exam.room }}</span>
                      <Tag :value="exam.status" :severity="getStatusSeverity(exam.status)" />
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Propose Date Dialog -->
    <Dialog 
      v-model:visible="proposeDialog.visible" 
      :header="'Propune dată pentru ' + (proposeDialog.subject?.name || '')" 
      :style="{width: '500px'}"
      :modal="true"
    >
      <div class="p-fluid">
        <div class="p-field p-mb-3">
          <label for="examDate">Data Examen <span class="required-field">*</span></label>
          <Calendar 
            id="examDate" 
            v-model="proposeDialog.date" 
            dateFormat="dd/mm/yy"
            :showIcon="true"
            :minDate="minExamDate"
            :maxDate="maxExamDate"
            class="w-full"
            :disabled="proposeDialog.loading"
          />
          <small v-if="examPeriod" class="helper-text">
            Perioada de examinare: {{ formatDate(examPeriod.startDate) }} - {{ formatDate(examPeriod.endDate) }}
          </small>
        </div>
        
        <div class="p-formgrid p-grid">
          <div class="p-field p-col-6">
            <label for="startTime">Ora începere <span class="required-field">*</span></label>
            <Dropdown 
              id="startTime" 
              v-model="proposeDialog.startTime" 
              :options="startTimeOptions" 
              optionLabel="label"
              optionValue="value"
              placeholder="Selectați ora"
              class="w-full"
              :disabled="proposeDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-6">
            <label for="endTime">Ora terminare <span class="required-field">*</span></label>
            <Dropdown 
              id="endTime" 
              v-model="proposeDialog.endTime" 
              :options="endTimeOptions" 
              optionLabel="label"
              optionValue="value"
              placeholder="Selectați ora"
              class="w-full"
              :disabled="proposeDialog.loading || !proposeDialog.startTime"
            />
          </div>
        </div>
        
        <div class="p-field">
          <label for="notes">Observații (opțional)</label>
          <Textarea 
            id="notes" 
            v-model="proposeDialog.notes" 
            rows="3" 
            placeholder="Adăugați observații sau preferințe pentru acest examen"
            :disabled="proposeDialog.loading"
          />
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="proposeDialog.visible = false"
          :disabled="proposeDialog.loading"
        />
        <Button 
          label="Trimite Propunere" 
          icon="pi pi-send" 
          class="p-button-primary" 
          @click="submitProposal"
          :loading="proposeDialog.loading"
          :disabled="!isProposalValid"
        />
      </template>
    </Dialog>
    
    <!-- My Proposals Table -->
    <div class="my-proposals p-mt-4">
      <h2>Propunerile Mele</h2>
      
      <DataTable 
        :value="myProposals" 
        :paginator="true" 
        :rows="5"
        :rowsPerPageOptions="[5, 10, 20]"
        responsiveLayout="scroll"
        class="p-datatable-striped"
        :loading="loading.myProposals"
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
import Dialog from 'primevue/dialog'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'

export default {
  name: 'ProposeDatesView',
  components: {
    Card,
    DataTable,
    Column,
    Button,
    Dialog,
    Calendar,
    Dropdown,
    Textarea,
    ProgressBar,
    ProgressSpinner,
    Tag
  },
  setup() {
    const store = useStore()
    
    // Loading states
    const loading = reactive({
      subjects: false,
      myProposals: false,
      upcomingExams: false
    })
    
    // Subjects data
    const pendingSubjects = ref([])
    const selectedSubject = ref(null)
    
    // My proposals data
    const myProposals = ref([])
    
    // Upcoming exams
    const upcomingExams = ref([])
    
    // Exam period from server/store
    const examPeriod = ref({
      startDate: new Date('2025-06-05'),
      endDate: new Date('2025-06-25')
    })
    
    // Min and max exam dates
    const minExamDate = computed(() => examPeriod.value?.startDate || new Date())
    const maxExamDate = computed(() => examPeriod.value?.endDate || new Date())
    
    // Propose dialog
    const proposeDialog = reactive({
      visible: false,
      subject: null,
      date: null,
      startTime: null,
      endTime: null,
      notes: '',
      loading: false
    })
    
    // Time options
    const startTimeOptions = ref([
      { label: '08:00', value: '08:00' },
      { label: '09:00', value: '09:00' },
      { label: '10:00', value: '10:00' },
      { label: '11:00', value: '11:00' },
      { label: '12:00', value: '12:00' },
      { label: '13:00', value: '13:00' },
      { label: '14:00', value: '14:00' },
      { label: '15:00', value: '15:00' },
      { label: '16:00', value: '16:00' },
      { label: '17:00', value: '17:00' }
    ])
    
    // End time options based on start time
    const endTimeOptions = computed(() => {
      if (!proposeDialog.startTime) return []
      
      const startTimeIndex = startTimeOptions.value.findIndex(
        option => option.value === proposeDialog.startTime
      )
      
      // Only show end times that are at least 2 hours after start time
      return startTimeOptions.value
        .filter((_, index) => index >= startTimeIndex + 2)
        .map(option => ({ label: option.value, value: option.value }))
    })
    
    // Proposal stats
    const proposalStats = computed(() => {
      const totalSubjects = pendingSubjects.value.length + myProposals.value.length
      const pending = myProposals.value.filter(p => p.status === 'pending').length
      const approved = myProposals.value.filter(p => p.status === 'approved').length
      const rejected = myProposals.value.filter(p => p.status === 'rejected').length
      const notProposed = pendingSubjects.value.length
      
      return {
        totalSubjects,
        pending,
        approved,
        rejected,
        notProposed,
        pendingPercentage: totalSubjects ? (pending / totalSubjects) * 100 : 0,
        approvedPercentage: totalSubjects ? (approved / totalSubjects) * 100 : 0,
        rejectedPercentage: totalSubjects ? (rejected / totalSubjects) * 100 : 0,
        notProposedPercentage: totalSubjects ? (notProposed / totalSubjects) * 100 : 0
      }
    })
    
    // Check if proposal is valid
    const isProposalValid = computed(() => {
      return proposeDialog.date && proposeDialog.startTime && proposeDialog.endTime
    })
    
    // Format dates
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
    
    // Subject select handler
    const onSubjectSelect = (event) => {
      openProposeDialog(event.data)
    }
    
    // Open propose dialog
    const openProposeDialog = (subject) => {
      proposeDialog.subject = subject
      proposeDialog.date = null
      proposeDialog.startTime = null
      proposeDialog.endTime = null
      proposeDialog.notes = ''
      proposeDialog.visible = true
    }
    
    // Submit proposal
    const submitProposal = async () => {
      if (!isProposalValid.value) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Completați toate câmpurile obligatorii',
          life: 3000
        })
        return
      }
      
      try {
        proposeDialog.loading = true
        
        // In a real implementation, call the API
        // await examService.proposeExamDate({
        //   subjectId: proposeDialog.subject.id,
        //   date: proposeDialog.date,
        //   startTime: proposeDialog.startTime,
        //   endTime: proposeDialog.endTime,
        //   notes: proposeDialog.notes
        // })
        
        // For demo purposes, simulate the API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Add to my proposals
        const newProposal = {
          id: Date.now(),
          subject: proposeDialog.subject.name,
          date: proposeDialog.date.toISOString(),
          startTime: proposeDialog.startTime,
          endTime: proposeDialog.endTime,
          status: 'pending',
          statusLabel: 'În așteptare',
          submittedDate: new Date().toISOString(),
          comment: null,
          rejectionReason: null
        }
        
        myProposals.value.unshift(newProposal)
        
        // Remove from pending subjects
        pendingSubjects.value = pendingSubjects.value.filter(
          subject => subject.id !== proposeDialog.subject.id
        )
        
        // Close dialog
        proposeDialog.visible = false
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere Trimisă',
          detail: 'Propunerea a fost trimisă cu succes.',
          life: 3000
        })
      } catch (error) {
        console.error('Error submitting proposal:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la trimiterea propunerii.',
          life: 5000
        })
      } finally {
        proposeDialog.loading = false
      }
    }
    
    // Load subjects
    const loadSubjects = async () => {
      try {
        loading.subjects = true
        
        // In a real implementation, call the API
        // const response = await subjectService.getPendingSubjects()
        // pendingSubjects.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        pendingSubjects.value = [
          {
            id: 1,
            name: 'Programare Web',
            code: 'PW32',
            professor: 'Prof. Dr. Ionescu Maria',
            semester: 'Semestrul 2'
          },
          {
            id: 2,
            name: 'Algoritmi și Structuri de Date',
            code: 'ASD21',
            professor: 'Prof. Dr. Popescu Ion',
            semester: 'Semestrul 2'
          },
          {
            id: 3,
            name: 'Ingineria Programării',
            code: 'IP34',
            professor: 'Prof. Dr. Georgescu Andrei',
            semester: 'Semestrul 2'
          }
        ]
      } catch (error) {
        console.error('Error loading subjects:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca disciplinele.',
          life: 5000
        })
      } finally {
        loading.subjects = false
      }
    }
    
    // Load my proposals
    const loadMyProposals = async () => {
      try {
        loading.myProposals = true
        
        // In a real implementation, call the API
        // const response = await examService.getMyProposals()
        // myProposals.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        myProposals.value = [
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
        console.error('Error loading proposals:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca propunerile.',
          life: 5000
        })
      } finally {
        loading.myProposals = false
      }
    }
    
    // Load upcoming exams
    const loadUpcomingExams = async () => {
      try {
        loading.upcomingExams = true
        
        // In a real implementation, call the API
        // const response = await examService.getUpcomingExams()
        // upcomingExams.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        upcomingExams.value = [
          {
            id: 201,
            subject: 'Metode Numerice',
            date: '2025-06-10',
            startTime: '10:00',
            endTime: '12:00',
            room: 'C2',
            status: 'approved'
          }
        ]
      } catch (error) {
        console.error('Error loading upcoming exams:', error)
      } finally {
        loading.upcomingExams = false
      }
    }
    
    // Initialize
    onMounted(() => {
      loadSubjects()
      loadMyProposals()
      loadUpcomingExams()
    })
    
    return {
      loading,
      pendingSubjects,
      selectedSubject,
      myProposals,
      upcomingExams,
      examPeriod,
      minExamDate,
      maxExamDate,
      proposeDialog,
      startTimeOptions,
      endTimeOptions,
      proposalStats,
      isProposalValid,
      formatDate,
      formatDatetime,
      getStatusSeverity,
      onSubjectSelect,
      openProposeDialog,
      submitProposal
    }
  }
}
</script>

<style lang="scss" scoped>
.propose-dates {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  h2 {
    color: #2c3e50;
    font-size: 1.25rem;
    margin-top: 0;
    margin-bottom: 0;
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
      font-size: 2.5rem;
      color: #4caf50;
      margin-bottom: 1rem;
    }
    
    h3 {
      color: #2c3e50;
      margin-top: 0;
      margin-bottom: 0.5rem;
      font-size: 1.25rem;
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
  
  .status-summary {
    .status-item {
      margin-bottom: 1.5rem;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .status-number {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
      }
      
      .status-label {
        font-size: 0.875rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
      }
      
      .status-progress {
        height: 0.5rem;
      }
    }
  }
  
  .upcoming-exams {
    .exam-list {
      list-style: none;
      padding: 0;
      margin: 0;
      
      .exam-item {
        display: flex;
        align-items: flex-start;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e9ecef;
        
        &:last-child {
          border-bottom: none;
        }
        
        .exam-date {
          flex: 0 0 auto;
          width: 30%;
          
          .date {
            font-weight: 500;
            color: #2c3e50;
          }
          
          .time {
            font-size: 0.875rem;
            color: #6c757d;
            margin-top: 0.25rem;
          }
        }
        
        .exam-details {
          flex: 1 1 auto;
          
          .exam-subject {
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 0.25rem;
          }
          
          .exam-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .location {
              font-size: 0.875rem;
              color: #6c757d;
            }
          }
        }
      }
    }
  }
  
  .my-proposals {
    h2 {
      margin-bottom: 1rem;
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
  }
  
  .helper-text {
    display: block;
    color: #6c757d;
    margin-top: 0.25rem;
  }
  
  .required-field {
    color: #f44336;
  }
  
  .w-full {
    width: 100%;
  }
}
</style>
