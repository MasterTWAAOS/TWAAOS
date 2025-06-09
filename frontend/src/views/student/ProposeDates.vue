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
                <Column field="professor" header="Cadru Didactic" style="width: 30%">
                  <template #body="slotProps">
                    <div class="professor-name">{{ slotProps.data.professor || 'Indisponibil' }}</div>
                  </template>
                </Column>
                <Column header="Acțiuni" style="width: 20%">
                  <template #body="slotProps">
                    <Button 
                      label="Stabilește data" 
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
                <div class="status-number">{{ proposalStats.proposed }}</div>
                <div class="status-label">Propuse</div>
                <ProgressBar :value="proposalStats.proposedPercentage" class="status-progress" severity="info" />
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
              
              <!-- Removed 'Nepropuse' category as it's not one of the standardized statuses -->
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
          <small class="helper-text info-text">
            <i class="pi pi-info-circle"></i> Ca reprezentant al grupei, trebuie să propui doar data examenului. Ora și alte detalii vor fi stabilite de profesor.
          </small>
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
        <Column field="submittedDate" header="Trimis la" :sortable="true" style="width: 15%">
          <template #body="slotProps">
            {{ formatDatetime(slotProps.data.submittedDate) }}
          </template>
        </Column>
        <Column header="Acțiuni" style="width: 15%">
          <template #body="slotProps">
            <div class="action-buttons">
              <Button 
                v-if="slotProps.data.status === 'rejected'"
                icon="pi pi-refresh" 
                class="p-button-warning p-button-sm"
                @click="resubmitRejectedProposal(slotProps.data)"
                v-tooltip.top="'Propune o nouă dată'"
              />
              <Button 
                v-if="slotProps.data.status === 'approved'"
                icon="pi pi-check-circle" 
                class="p-button-success p-button-sm"
                disabled
                v-tooltip.top="'Propunere aprobată de profesor'"
              />
            </div>
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
import apiClient from '../../services/api.service';
import examService from '../../services/exam.service';
import subjectService from '../../services/subject.service';
import configService from '../../services/config.service';

export default {
  name: 'ProposeDatesView',
  components: {
    Card,
    DataTable,
    Column,
    Button,
    Dialog,
    Calendar,
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
    
    // Exam period from server
    const examPeriod = ref(null)
    
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
    
    // Proposal stats - using only the standardized statuses: pending, proposed, approved, rejected
    const proposalStats = computed(() => {
      // Total subjects includes both pending subjects and existing proposals
      const totalSubjects = pendingSubjects.value.length + myProposals.value.length
      
      // Count subjects for each standardized status
      const pending = myProposals.value.filter(p => p.status === 'pending').length
      const proposed = myProposals.value.filter(p => p.status === 'proposed').length
      const approved = myProposals.value.filter(p => p.status === 'approved').length
      const rejected = myProposals.value.filter(p => p.status === 'rejected').length
      
      // Calculate total and percentages
      return {
        totalSubjects,
        pending,
        proposed,
        approved,
        rejected,
        pendingPercentage: totalSubjects ? (pending / totalSubjects) * 100 : 0,
        proposedPercentage: totalSubjects ? (proposed / totalSubjects) * 100 : 0,
        approvedPercentage: totalSubjects ? (approved / totalSubjects) * 100 : 0,
        rejectedPercentage: totalSubjects ? (rejected / totalSubjects) * 100 : 0
      }
    })
    
    // Computed property to check if date is filled
    const isProposalValid = computed(() => {
      return !!proposeDialog.date
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
      if (!proposeDialog.date) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Selectați o dată pentru examen',
          life: 3000
        })
        return
      }
      
      try {
        proposeDialog.loading = true
        
        // Set default start and end times (as SG only sets date)
        const defaultStartTime = "09:00:00"
        const defaultEndTime = "11:00:00"
        
        // Prepare the proposal data
        // Fix date offset by using local date formatting instead of UTC
        let formattedDate
        if (proposeDialog.date instanceof Date) {
          // Format as YYYY-MM-DD without timezone adjustments
          const year = proposeDialog.date.getFullYear()
          // getMonth() is 0-indexed, so add 1
          const month = String(proposeDialog.date.getMonth() + 1).padStart(2, '0')
          const day = String(proposeDialog.date.getDate()).padStart(2, '0')
          formattedDate = `${year}-${month}-${day}`
        } else {
          formattedDate = proposeDialog.date
        }
        
        const proposalData = {
          subjectId: proposeDialog.subject.id,
          date: formattedDate,
          startTime: defaultStartTime, // Using default time
          endTime: defaultEndTime, // Using default time
          notes: proposeDialog.notes,
          groupId: store.getters['auth/currentUser'].groupId // Make sure groupId is sent
        }
        
        console.log('Sending exam date proposal:', proposalData)
        
        // Call the API to submit the proposal
        const response = await examService.proposeDate(proposalData)
        
        // Get the newly created proposal from the response
        const newProposal = {
          id: response.data.id,
          subject: proposeDialog.subject.name,
          date: proposeDialog.date instanceof Date ? 
            proposeDialog.date.toISOString() : 
            proposeDialog.date,
          startTime: defaultStartTime,
          endTime: defaultEndTime,
          status: 'pending',
          statusLabel: 'În așteptare',
          submittedDate: new Date().toISOString(),
          notes: proposeDialog.notes || null,
          rejectionReason: null,
          professorName: proposeDialog.subject.professor
        }
        
        // Add to my proposals
        myProposals.value.unshift(newProposal)
        
        // Remove from pending subjects
        pendingSubjects.value = pendingSubjects.value.filter(
          subject => subject.id !== proposeDialog.subject.id
        )
        
        // Close dialog
        proposeDialog.visible = false
        
        // Refresh upcoming exams to include the new proposal
        await loadUpcomingExams()
        
        // Refresh my proposals to update statuses
        await loadMyProposals()
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere Trimisă',
          detail: 'Propunerea a fost trimisă cu succes și profesorul a fost notificat prin email.',
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
    
    // Load subjects that need dates proposed (pending or rejected exams)
    const loadSubjects = async () => {
      try {
        loading.subjects = true
        
        // Get the current group ID from the user object
        const currentUser = store.getters['auth/currentUser']
        const groupId = currentUser?.groupId
        
        if (!groupId) {
          console.error('User has no group ID assigned')
          store.dispatch('notifications/showNotification', {
            severity: 'error',
            summary: 'Eroare',
            detail: 'Nu s-a putut determina grupa. Verificați autentificarea.',
            life: 5000
          })
          loading.subjects = false
          return
        }
        
        console.log('Loading pending subjects for group ID:', groupId)
        
        // Get all subjects that need exam dates proposed for this group
        const response = await apiClient.get(`/subjects/group/${groupId}/pending`)
        
        // Debug what's coming from the API
        console.log('API Response for pending subjects:', response)
        console.log('Number of subjects returned:', response.data.length)
        
        // The backend now properly returns subjects that need proposals
        // This includes:
        // 1. Subjects without any exam proposals yet
        // 2. Subjects with only rejected exam proposals
        // 3. Subjects with only pending exam proposals (from SEC)
        const pendingData = response.data
        
        console.log('Processing pending subjects:', pendingData)
        
        // Map the subjects to the format needed for the UI
        pendingSubjects.value = pendingData.map(subject => ({
          id: subject.id,
          name: subject.name,
          code: subject.code,
          professor: subject.professorName, 
          professorId: subject.professorId,
          semester: `Semestrul ${subject.semester}`,
          // If the subject has an exam status, use it, otherwise treat as pending
          status: subject.examStatus?.toLowerCase() || 'pending',
          // Add debug info
          needsProposal: subject.needsProposal || true
        }))
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
        
        // Get the current group ID from the user object
        const currentUser = store.getters['auth/currentUser']
        const groupId = currentUser?.groupId
        
        if (!groupId) {
          console.error('User has no group ID assigned')
          store.dispatch('notifications/showNotification', {
            severity: 'error',
            summary: 'Eroare',
            detail: 'Nu s-a putut determina grupa. Verificați autentificarea.',
            life: 5000
          })
          loading.myProposals = false
          return
        }
        
        console.log('Loading proposals for group ID:', groupId)
        
        // Call the API to get my proposals
        const response = await examService.getByGroup(groupId)
        
        // Process the response data
        myProposals.value = response.data.map(proposal => {
          // Determine status and status label
          let status, statusLabel;
          
          // Normalize the status to lowercase for comparison
          const rawStatus = proposal.approvalStatus || proposal.status || '';
          const normalizedStatus = rawStatus.toLowerCase();
          
          // Map backend status (now standardized to English) to frontend display values
          // Using only English status values internally with Romanian translations for display
          switch(normalizedStatus) {
            case 'approved':
              status = 'approved';
              statusLabel = 'Aprobat';
              break;
            case 'rejected':
              status = 'rejected';
              statusLabel = 'Respins';
              break;
            case 'proposed':
              status = 'proposed';
              statusLabel = 'Propus';
              break;
            case 'pending':
            default:
              status = 'pending';
              statusLabel = 'În așteptare';
              break;
          }
          
          console.log(`Exam ${proposal.id} original status: ${rawStatus}, mapped to: ${status}, ${statusLabel}`)

          // Map the proposal data to our format
          return {
            id: proposal.id,
            subject: proposal.subjectName,
            date: proposal.date,
            startTime: proposal.startTime,
            endTime: proposal.endTime,
            status: status,
            statusLabel: statusLabel,
            submittedDate: proposal.submittedAt || new Date().toISOString(),
            comment: proposal.notes,
            rejectionReason: proposal.rejectionReason,
            professorName: proposal.professorName,
            subjectId: proposal.subjectId,
            professorId: proposal.professorId
          };
        });
        
        // Check for recently rejected proposals and show notifications
        const lastCheckTime = localStorage.getItem('lastRejectionCheck');
        const now = new Date().toISOString();
        
        if (lastCheckTime) {
          const recentRejections = myProposals.value.filter(p => 
            p.status === 'rejected' && 
            new Date(p.updatedAt || p.submittedDate) > new Date(lastCheckTime)
          );
          
          // Notify for each recent rejection
          recentRejections.forEach(rejection => {
            store.dispatch('notifications/showNotification', {
              severity: 'warn',
              summary: 'Propunere Respinsă',
              detail: `Propunerea pentru ${rejection.subject} a fost respinsă: ${rejection.rejectionReason || 'Niciun motiv specificat.'}`,
              life: 10000,
              sticky: true
            });
          });
        }
        
        // Update last check time
        localStorage.setItem('lastRejectionCheck', now);
      } catch (error) {
        console.error('Error loading proposals:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca propunerile de examene.',
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
        
        // Get the current group ID from the user object
        const currentUser = store.getters['auth/currentUser']
        const groupId = currentUser?.groupId
        
        if (!groupId) {
          console.error('User has no group ID assigned')
          store.dispatch('notifications/showNotification', {
            severity: 'error',
            summary: 'Eroare',
            detail: 'Nu s-a putut determina grupa. Verificați autentificarea.',
            life: 5000
          })
          loading.upcomingExams = false
          return
        }
        
        console.log('Loading upcoming exams for group ID:', groupId)
        
        // Get upcoming exams for this group
        const response = await examService.getByGroup(groupId)
        
        // Filter to show only approved upcoming exams (those in the future)
        const now = new Date()
        const sortedExams = response.data
          .filter(exam => {
            // Only include approved exams
            const examStatus = (exam.approvalStatus || exam.status || '').toLowerCase();
            if (examStatus !== 'approved') {
              return false;
            }
            
            // Only include future exams or today's exams
            const examDate = new Date(exam.date)
            return examDate >= now || (
              examDate.getDate() === now.getDate() &&
              examDate.getMonth() === now.getMonth() &&
              examDate.getFullYear() === now.getFullYear()
            )
          })
          // Sort by date (closest first)
          .sort((a, b) => new Date(a.date) - new Date(b.date))
          // Take only the first 5
          .slice(0, 5)
        
        // Map to the format needed by the view
        upcomingExams.value = sortedExams.map(exam => ({
          id: exam.id,
          subject: exam.subjectName,
          date: exam.date,
          startTime: exam.startTime,
          endTime: exam.endTime,
          room: exam.roomName || 'TBA',
          status: exam.approvalStatus?.toLowerCase() || 'pending'
        }))
      } catch (error) {
        console.error('Error loading upcoming exams:', error)
      } finally {
        loading.upcomingExams = false
      }
    }
    
    // Resubmit a rejected proposal
    const resubmitRejectedProposal = (proposal) => {
      // Find subject data from the rejected proposal
      const subjectData = {
        id: proposal.subjectId || 0,
        name: proposal.subject,
        professor: proposal.professorName,
        professorId: proposal.professorId,
        code: proposal.code || '',
        semester: proposal.semester || 'Semestrul X'
      }
      
      // Open the proposal dialog with prefilled data
      proposeDialog.subject = subjectData
      proposeDialog.date = null
      proposeDialog.startTime = null
      proposeDialog.endTime = null
      proposeDialog.notes = `Resubmitere după respingere. Motiv anterior: ${proposal.rejectionReason}`
      proposeDialog.visible = true
      
      // Show the rejection reason in a notification to remind the student
      store.dispatch('notifications/showNotification', {
        severity: 'info',
        summary: 'Motivul respingerii anterioare',
        detail: proposal.rejectionReason || 'Niciun motiv specificat.',
        life: 7000
      })
    }
    
    // Load exam period configuration
    const loadExamPeriod = async () => {
      try {
        const response = await configService.getCurrentConfig()
        console.log('Config API response:', response.data)
        
        if (response.data) {
          // Check the format of the dates coming from backend
          const startDate = response.data.start_date || response.data.startDate
          const endDate = response.data.end_date || response.data.endDate
          
          // Create a fallback exam period if the API doesn't return valid dates
          if (!startDate || !endDate) {
            // Fallback to a reasonable exam period (2 weeks from now)
            const today = new Date()
            const twoWeeksLater = new Date()
            twoWeeksLater.setDate(today.getDate() + 14)
            
            examPeriod.value = {
              startDate: today,
              endDate: twoWeeksLater
            }
            console.log('Using fallback exam period:', examPeriod.value)
          } else {
            // Parse dates properly
            examPeriod.value = {
              startDate: new Date(startDate),
              endDate: new Date(endDate)
            }
            console.log('Loaded exam period successfully:', examPeriod.value)
          }
        } else {
          // Fallback to current date + 2 weeks if no config
          const today = new Date()
          const twoWeeksLater = new Date()
          twoWeeksLater.setDate(today.getDate() + 14)
          
          examPeriod.value = {
            startDate: today,
            endDate: twoWeeksLater
          }
          console.log('No config found, using fallback period:', examPeriod.value)
          
          store.dispatch('notifications/showNotification', {
            severity: 'warn',
            summary: 'Atenție',
            detail: 'Nu s-a găsit o perioadă de examinare configurată. Contactați secretariatul.',
            life: 5000
          })
        }
      } catch (error) {
        console.error('Error loading exam period:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut încărca perioada de examinare.',
          life: 5000
        })
        
        // Create a default exam period in case of error
        const today = new Date()
        const twoWeeksLater = new Date()
        twoWeeksLater.setDate(today.getDate() + 14)
        
        examPeriod.value = {
          startDate: today,
          endDate: twoWeeksLater
        }
      }
    }

    // Initialize
    onMounted(() => {
      loadExamPeriod()
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
      submitProposal,
      loadExamPeriod
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
