<template>
  <div class="review-proposals">
    <h1>Validare Propuneri Examene</h1>
    
    <div class="filter-section p-card p-mb-3">
      <div class="p-grid">
        <!-- Removed status filter as all exams here should be in 'proposed' status -->
        
        <div class="p-col-12 p-md-6">
          <div class="p-field">
            <label for="groupFilter">Grupă</label>
            <Dropdown 
              id="groupFilter" 
              v-model="filters.group" 
              :options="groupOptions" 
              optionLabel="name" 
              placeholder="Toate grupele"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="p-col-12 p-md-6">
          <div class="p-field">
            <label for="search">Căutare</label>
            <InputText 
              id="search" 
              v-model="filters.search" 
              placeholder="Caută după codul disciplinei"
              class="w-full"
            />
          </div>
        </div>
      </div>
    </div>
    
    <div class="proposals-table">
      <DataTable 
        :value="filteredProposals" 
        :paginator="true" 
        :rows="10"
        :rowsPerPageOptions="[5, 10, 20]"
        responsiveLayout="scroll"
        class="p-datatable-striped"
        :loading="loading"
      >
        <Column field="subject.name" header="Disciplină" :sortable="true">
          <template #body="slotProps">
            <div>
              <div class="subject-name">{{ slotProps.data.subject.name }}</div>
              <div class="subject-code">{{ slotProps.data.subject.code }}</div>
            </div>
          </template>
        </Column>
        <Column field="group.name" header="Grupă" :sortable="true" style="width: 10%">
          <template #body="slotProps">
            <!-- Debug the group data -->
            <div style="display: none;">{{ console.log('[UI Debug] Group data:', slotProps.data) }}</div>
            <div>{{ slotProps.data.group.name }}</div>
          </template>
        </Column>
        <Column field="proposedDate" header="Dată Propusă" :sortable="true" style="width: 15%">
          <template #body="slotProps">
            <!-- Debug date fields -->
            <div style="display: none;">{{ console.log('[Date Debug]', slotProps.data) }}</div>
            <div class="proposed-date">
              <div class="date">{{ formatDate(slotProps.data.proposedDate || slotProps.data.date || slotProps.data.examDate) }}</div>
            </div>
          </template>
        </Column>
        <Column field="status" header="Status" :sortable="true" style="width: 10%">
          <template #body="slotProps">
            <Tag :value="getStatusLabel(slotProps.data.status)" :severity="getStatusSeverity(slotProps.data.status)" />
          </template>
        </Column>
        <Column header="Acțiuni" style="width: 15%">
          <template #body="slotProps">
            <div class="action-buttons">
              <Button 
                icon="pi pi-check" 
                class="p-button-success p-button-sm p-mr-1" 
                v-tooltip.top="'Aprobă propunerea'"
                v-if="slotProps.data.status === 'proposed'"
                @click="openApproveDialog(slotProps.data)"
              />
              <Button 
                icon="pi pi-times" 
                class="p-button-danger p-button-sm p-mr-1" 
                v-tooltip.top="'Respinge propunerea'"
                v-if="slotProps.data.status === 'proposed'"
                @click="openRejectDialog(slotProps.data)"
              />
              <Button 
                icon="pi pi-eye" 
                class="p-button-secondary p-button-sm" 
                v-tooltip.top="'Vizualizează detalii'"
                @click="openDetailsDialog(slotProps.data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
    
    <!-- Approve Dialog -->
    <Dialog 
      v-model:visible="dialogs.approve.visible" 
      header="Aprobare Propunere" 
      :style="{width: '650px'}"
      :modal="true"
      :closable="false"
    >
      <div class="p-fluid">
        <div class="p-grid">
          <!-- Sala/Săli -->
          <div class="p-col-12 p-md-6">
            <div class="p-field p-mb-3">
              <label for="approveRoom">Sală/Săli de Examen <span class="required-field">*</span></label>
              <MultiSelect 
                id="approveRoom" 
                v-model="dialogs.approve.rooms" 
                :options="roomOptions" 
                optionLabel="name" 
                placeholder="Selectați sala/sălile"
                display="chip"
                class="w-full"
              />
              <small v-if="dialogs.approve.validationErrors.rooms" class="p-error">{{ dialogs.approve.validationErrors.rooms }}</small>
            </div>
          </div>

          <!-- Interval de timp -->
          <div class="p-col-12 p-md-6">
            <div class="p-field p-mb-3">
              <label>Interval de timp <span class="required-field">*</span></label>
              <div class="p-d-flex p-ai-center">
                <div class="p-mr-2" style="flex: 1">
                  <Dropdown 
                    v-model="dialogs.approve.startTime" 
                    :options="timeOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="Ora început"
                    class="w-full"
                    @change="validateTimeInterval"
                  />
                </div>
                <span class="p-mx-2">-</span>
                <div style="flex: 1">
                  <Dropdown 
                    v-model="dialogs.approve.endTime" 
                    :options="timeOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    placeholder="Ora sfârșit"
                    class="w-full"
                    @change="validateTimeInterval"
                  />
                </div>
              </div>
              <small v-if="dialogs.approve.validationErrors.timeInterval" class="p-error">{{ dialogs.approve.validationErrors.timeInterval }}</small>
            </div>
          </div>

          <!-- Asistenți -->
          <div class="p-col-12">
            <div class="p-field p-mb-3">
              <label for="assistants">Asistent/Asistenți de Examen <span class="required-field">*</span></label>
              <MultiSelect 
                id="assistants" 
                v-model="dialogs.approve.assistants" 
                :options="assistantOptions" 
                optionLabel="name" 
                placeholder="Selectați asistenții"
                :filter="false"
                display="chip"
                class="w-full"
              />
              <small v-if="dialogs.approve.validationErrors.assistants" class="p-error">{{ dialogs.approve.validationErrors.assistants }}</small>
            </div>
          </div>

          <!-- Removed Comments field as per request -->

          <!-- Conflict warnings -->
          <div class="p-col-12" v-if="dialogs.approve.conflicts.length > 0">
            <Message severity="warn" :closable="false">
              <template #header>
                <i class="pi pi-exclamation-triangle p-mr-2"></i>
                <span>Atenție! Există posibile conflicte:</span>
              </template>
              <ul class="p-ml-2 p-mb-0">
                <li v-for="(conflict, index) in dialogs.approve.conflicts" :key="index">
                  {{ conflict }}
                </li>
              </ul>
            </Message>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="dialogs.approve.visible = false"
        />
        <Button 
          label="Confirmare" 
          icon="pi pi-check" 
          class="p-button-success" 
          @click="approveProposal"
          :loading="dialogs.approve.loading"
          :disabled="!isApproveFormValid"
        />
      </template>
    </Dialog>
    
    <!-- Reject Dialog -->
    <Dialog 
      v-model:visible="dialogs.reject.visible" 
      header="Respingere Propunere" 
      :style="{width: '450px'}"
      :modal="true"
    >
      <div class="p-fluid">
        <div class="p-field p-mb-3">
          <label for="rejectReason">Motivul Respingerii <span class="required-field">*</span></label>
          <Textarea 
            id="rejectReason" 
            v-model="dialogs.reject.reason" 
            rows="3" 
            placeholder="Specificați motivul respingerii propunerii"
            required
          />
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="dialogs.reject.visible = false"
        />
        <Button 
          label="Confirmare" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="rejectProposal"
          :loading="dialogs.reject.loading"
          :disabled="!dialogs.reject.reason"
        />
      </template>
    </Dialog>
    
    <!-- Details Dialog -->
    <Dialog 
      v-model:visible="dialogs.details.visible" 
      header="Detalii Propunere" 
      :style="{width: '650px'}"
      :modal="true"
    >
      <div v-if="dialogs.details.proposal" class="proposal-details">
        <div class="p-grid">
          <div class="p-col-12 p-md-6">
            <h3>Detalii Propunere</h3>
            <div class="detail-item">
              <span class="detail-label">Disciplină:</span>
              <span class="detail-value">{{ dialogs.details.proposal.subject.name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Cod Disciplină:</span>
              <span class="detail-value">{{ dialogs.details.proposal.subject.code }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Grupă:</span>
              <span class="detail-value">{{ dialogs.details.proposal.group.name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Dată Propusă:</span>
              <span class="detail-value">{{ formatDate(dialogs.details.proposal.proposedDate) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Interval Orar:</span>
              <span class="detail-value">{{ formatTime(dialogs.details.proposal.proposedTimeStart) }} - {{ formatTime(dialogs.details.proposal.proposedTimeEnd) }}</span>
            </div>
          </div>
          <div class="p-col-12 p-md-6">
            <h3>Informații Suplimentare</h3>
            <div class="detail-item">
              <span class="detail-label">Propus de:</span>
              <span class="detail-value">{{ dialogs.details.proposal.submittedBy?.name || 'Student Group Leader' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Data Propunerii:</span>
              <span class="detail-value">{{ formatDatetime(dialogs.details.proposal.submittedDate) }}</span>
            </div>
            <div class="detail-item" v-if="dialogs.details.proposal.reviewedBy">
              <span class="detail-label">Verificat de:</span>
              <span class="detail-value">{{ dialogs.details.proposal.reviewedBy.name }}</span>
            </div>
            <div class="detail-item" v-if="dialogs.details.proposal.comments">
              <span class="detail-label">Comentarii:</span>
              <span class="detail-value">{{ dialogs.details.proposal.comments }}</span>
            </div>
            <div class="detail-item" v-if="dialogs.details.proposal.rejectionReason">
              <span class="detail-label">Motivul Respingerii:</span>
              <span class="detail-value">{{ dialogs.details.proposal.rejectionReason }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Închide" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="dialogs.details.visible = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

// Import services instead of direct API calls
import RoomService from '../../services/room.service'
import ScheduleService from '../../services/schedule.service'
import UserService from '../../services/user.service'
import SubjectService from '../../services/subject.service'
import GroupService from '../../services/group.service'
import apiClient from '@/services/api.service.js'

// PrimeVue components
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import MultiSelect from 'primevue/multiselect'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import Message from 'primevue/message'

export default {
  name: 'ReviewProposalsView',
  components: {
    DataTable,
    Column,
    Dropdown,
    InputText,
    Button,
    Dialog,
    MultiSelect,
    Textarea,
    Tag,
    Message
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const proposals = ref([])
    const scheduledExams = ref([])
    
    // Caches for reducing API calls
    const subjectsCache = ref({}) // Cache by ID
    const groupsCache = ref({})   // Cache by ID
    const roomsCache = ref({})    // Cache by ID
    const usersCache = ref({})    // Cache by role and ID
    
    // Filters
    const filters = reactive({
      status: null,
      group: null,
      search: ''
    })
    
    // Filter options
    const statusOptions = ref([
      { name: 'Propuse', value: 'proposed' },
      { name: 'Aprobate', value: 'approved' },
      { name: 'Respinse', value: 'rejected' }
    ])
    
    const groupOptions = ref([])
    const roomOptions = ref([])
    const availableRooms = ref([])
    const roomsLoading = ref(false)
    
    const assistantOptions = ref([])
    const availableAssistants = ref([])
    const assistantsLoading = ref(false)
    
    // Time options in 1-hour increments (as per requirement)
    const timeOptions = ref([
      { label: '08:00', value: '08:00' },
      { label: '09:00', value: '09:00' },
      { label: '10:00', value: '10:00' },
      { label: '11:00', value: '11:00' },
      { label: '12:00', value: '12:00' },
      { label: '13:00', value: '13:00' },
      { label: '14:00', value: '14:00' },
      { label: '15:00', value: '15:00' },
      { label: '16:00', value: '16:00' },
      { label: '17:00', value: '17:00' },
      { label: '18:00', value: '18:00' },
      { label: '19:00', value: '19:00' },
      { label: '20:00', value: '20:00' }
    ])
    
    // Dialog states
    const dialogs = reactive({
      approve: {
        visible: false,
        proposal: null,
        rooms: [],  // Multiple rooms can be selected
        startTime: null,
        endTime: null,
        assistants: [], // Multiple assistants can be selected
        comments: '',
        loading: false,
        validationErrors: {
          rooms: null,
          timeInterval: null,
          assistants: null
        },
        conflicts: []
      },
      reject: {
        visible: false,
        proposal: null,
        reason: '',
        loading: false
      },
      details: {
        visible: false,
        proposal: null
      }
    })
    
    // Filtered proposals based on filters
    const filteredProposals = computed(() => {
      return proposals.value.filter(proposal => {
        // Filter by status
        if (filters.status && proposal.status !== filters.status.value) {
          return false
        }
        
        // Filter by group
        if (filters.group && proposal.group.name !== filters.group.value) {
          return false
        }
        
        // Filter by search term - only search by subject code/shortName
        if (filters.search) {
          const searchTerm = filters.search.toLowerCase()
          const subject = subjectsCache.value[proposal.subject.id]
          
          // Only search in subject code (stored as "code" in the subjectsCache)
          const subjectCode = subject?.code?.toLowerCase() || ''
          
          if (!subjectCode.includes(searchTerm)) {
            return false
          }
        }
        
        return true
      })
    })
    
    // Check if approve form is valid
    const isApproveFormValid = computed(() => {
      const { rooms, startTime, endTime, validationErrors } = dialogs.approve
      
      // Debug values to help identify the issue
      console.log('[Debug] Form validation values:', {
        hasRooms: rooms && rooms.length > 0,
        hasTime: Boolean(startTime && endTime),
        validationErrors,
        rooms,
        startTime,
        endTime
      })
      
      // Modified to NOT require assistants - only rooms and time intervals are required
      return (
        rooms && rooms.length > 0 &&
        startTime && endTime &&
        !validationErrors.rooms &&
        !validationErrors.timeInterval
      )
    })
    
    // Format functions with more robust error handling
    const formatDate = (dateString) => {
      // If no date, show a placeholder
      if (!dateString) {
        return 'Dată neprecizată'
      }
      
      try {
        const date = new Date(dateString)
        // Check if date is valid
        if (isNaN(date.getTime())) {
          console.warn('Invalid date value:', dateString)
          return 'Dată invalidă'
        }
        
        return new Intl.DateTimeFormat('ro-RO', { 
          day: '2-digit', 
          month: 'long', 
          year: 'numeric' 
        }).format(date)
      } catch (error) {
        console.error('Error formatting date:', dateString, error)
        return 'Eroare formatare dată'
      }
    }
    
    const formatTime = (timeString) => {
      // Return the time string as is but with a placeholder for missing values
      return timeString || '--:--'
    }
    
    const formatDatetime = (dateString) => {
      if (!dateString) return 'N/A'
      
      try {
        const date = new Date(dateString)
        if (isNaN(date.getTime())) return 'N/A' // Check if date is invalid
        
        return new Intl.DateTimeFormat('ro-RO', { 
          day: '2-digit', 
          month: 'short', 
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date)
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'N/A'
      }
    }
    
    // Status helpers - matching ProposeDates.vue implementation
    const getStatusLabel = (status) => {
      switch (status) {
        case 'pending': return 'În așteptare'
        case 'proposed': return 'Propus'
        case 'approved': return 'Aprobat'
        case 'rejected': return 'Respins'
        default: return status
      }
    }
    
    const getStatusSeverity = (status) => {
      switch (status) {
        case 'pending': return 'warning'
        case 'proposed': return 'info'
        case 'approved': return 'success'
        case 'rejected': return 'danger'
        default: return 'info'
      }
    }
    
    // Validation methods
    const validateTimeInterval = () => {
      const { startTime, endTime } = dialogs.approve
      dialogs.approve.validationErrors.timeInterval = null
      
      // Reset validation error if both fields are not yet set
      if (!startTime || !endTime) return
      
      // Check if start time is before end time
      if (startTime >= endTime) {
        dialogs.approve.validationErrors.timeInterval = 'Ora de început trebuie să fie înainte de ora de sfârșit'
        return
      }
      
      // Check if time interval is valid (1 hour increments)
      const startHour = parseInt(startTime.split(':')[0])
      const endHour = parseInt(endTime.split(':')[0])
      
      if (endHour - startHour < 1) {
        dialogs.approve.validationErrors.timeInterval = 'Durata examenului trebuie să fie de minim 1 oră'
      } else {
        // Clear the error if the interval is now valid
        dialogs.approve.validationErrors.timeInterval = null
      }
      
      // After validation passes, check for conflicts
      checkForTimeConflicts()
    }
    
    const closeDialogs = () => {
      dialogs.approve.visible = false
      dialogs.reject.visible = false
      dialogs.details.visible = false
    }
    
    // Get scheduled exam for conflict check
    const getScheduledExam = (scheduleId) => {
      return scheduledExams.value.find(exam => exam.id === scheduleId)
    }
    
    // Integrated conflict check that calls the backend API to verify conflicts
    const checkForConflicts = async () => {
      const { rooms, assistants, startTime, endTime, proposal } = dialogs.approve
      const conflicts = []
      
      // Check if we have all required data before checking conflicts
      if (!rooms || rooms.length === 0 || !assistants || assistants.length === 0 || !startTime || !endTime || !proposal) {
        return conflicts
      }
      
      try {
        // Prepare conflict check data
        const conflictCheckData = {
          date: proposal.proposedDate,
          startTime: startTime,
          endTime: endTime,
          roomIds: rooms.map(r => r.value),
          assistantIds: assistants.map(a => a.value),
          scheduleId: proposal.id  // To exclude the current schedule from conflict checks
        }
        
        // Call backend through store to check for conflicts
        const conflictData = await store.dispatch('schedules/checkConflicts', conflictCheckData)
        
        // Process room conflicts
        if (conflictData.roomConflicts && conflictData.roomConflicts.length > 0) {
          for (const conflict of conflictData.roomConflicts) {
            // Try to get subject name from cache if available
            let subjectName = conflict.subjectName
            if (!subjectName && conflict.subjectId && subjectsCache.value[conflict.subjectId]) {
              subjectName = subjectsCache.value[conflict.subjectId].name
            }
            conflicts.push(`Sala ${conflict.roomName} este deja rezervată între ${conflict.startTime} - ${conflict.endTime} pentru ${subjectName}`)
          }
        }
        
        // Process assistant conflicts
        if (conflictData.assistantConflicts && conflictData.assistantConflicts.length > 0) {
          for (const conflict of conflictData.assistantConflicts) {
            // Try to get subject name from cache if available
            let subjectName = conflict.subjectName
            if (!subjectName && conflict.subjectId && subjectsCache.value[conflict.subjectId]) {
              subjectName = subjectsCache.value[conflict.subjectId].name
            }
            conflicts.push(`Asistentul ${conflict.assistantName} este deja alocat între ${conflict.startTime} - ${conflict.endTime} pentru ${subjectName}`)
          }
        }
        
        // Process teacher conflicts
        if (conflictData.teacherConflicts && conflictData.teacherConflicts.length > 0) {
          for (const conflict of conflictData.teacherConflicts) {
            // Try to get subject name from cache if available
            let subjectName = conflict.subjectName
            if (!subjectName && conflict.subjectId && subjectsCache.value[conflict.subjectId]) {
              subjectName = subjectsCache.value[conflict.subjectId].name
            }
            conflicts.push(`Dvs. aveți deja programat un examen între ${conflict.startTime} - ${conflict.endTime} pentru ${subjectName}`)
          }
        }
      } catch (error) {
        console.error('Error checking for conflicts:', error)
        // Add a generic error in case of backend failure
        conflicts.push('Nu s-a putut verifica existența potențialelor conflicte. Verificați manual programarea.')
      }
      
      return conflicts
    }
    
    const checkForTimeConflicts = async () => {
      // Clear existing conflicts
      dialogs.approve.conflicts = []
      
      // Get all conflicts from the backend
      const conflicts = await checkForConflicts()
      
      // Update the conflicts in the dialog
      if (conflicts && conflicts.length > 0) {
        dialogs.approve.conflicts = conflicts
      }
    }

    // Dialog actions
    const openApproveDialog = async (proposal) => {
      // Reset dialog state
      dialogs.approve.proposal = { ...proposal }
      dialogs.approve.rooms = []
      dialogs.approve.assistants = []
      dialogs.approve.startTime = null
      dialogs.approve.endTime = null
      dialogs.approve.comments = ''
      dialogs.approve.loading = false
      dialogs.approve.validationErrors = {
        rooms: null,
        timeInterval: null,
        assistants: null
      }
      dialogs.approve.conflicts = []
      
      try {
        // If proposal has room requirements, pre-select rooms that match
        if (proposal.roomRequirements) {
          // Ensure rooms are loaded
          if (availableRooms.value.length === 0 && Object.keys(roomsCache.value).length === 0) {
            await loadRooms()
          }
          
          // Use cached rooms when possible
          const roomsToFilter = availableRooms.value.length > 0 ? 
            availableRooms.value : Object.values(roomsCache.value)
            
          // Find rooms that match the requirements
          const matchingRooms = roomsToFilter.filter(room => 
            // For example, if requirement includes 'computers', filter rooms with computers
            (proposal.roomRequirements.toLowerCase().includes('calculatoare') && room.computers) ||
            // If capacity is mentioned, filter by capacity
            (proposal.roomRequirements.match(/\d+/) && room.capacity >= parseInt(proposal.roomRequirements.match(/\d+/)[0]))
          )
          
          if (matchingRooms.length > 0) {
            dialogs.approve.rooms = [matchingRooms[0]] // Pre-select the first matching room
          }
        }
        
        // Use the more efficient subject-specific assistants loading
        if (proposal.subject && proposal.subject.id) {
          // Load assistants specific to this subject instead of all CD users
          await loadAssistantsBySubject(proposal.subject.id)
        } else if (availableAssistants.value.length === 0) {
          // Fallback to loading all assistants if no subject ID available
          await loadAssistants()
        }
        
        // Check if subject has previous assigned assistants and pre-select them
        if (proposal.subject && proposal.subject.id) {
          try {
            // Use the cached subject data when possible
            const subjectData = await getSubjectById(proposal.subject.id)
            
            if (subjectData && subjectData.assistantIds && subjectData.assistantIds.length > 0) {
              // Find matching assistants from our available list
              const preSelectedAssistants = availableAssistants.value.filter(assistant => 
                subjectData.assistantIds.includes(assistant.value)
              )
              
              if (preSelectedAssistants.length > 0) {
                dialogs.approve.assistants = preSelectedAssistants
              }
            }
          } catch (error) {
            console.error('Error loading subject assistants:', error)
          }
        }
      } catch (error) {
        console.error('Error preparing approval dialog:', error)
      } finally {
        // Show dialog
        dialogs.approve.visible = true
      }
    }
    
    const openRejectDialog = (proposal) => {
      dialogs.reject.proposal = proposal
      dialogs.reject.reason = ''
      dialogs.reject.visible = true
    }
    
    const openDetailsDialog = (proposal) => {
      dialogs.details.proposal = proposal
      dialogs.details.visible = true
    }
    
    const approveProposal = async () => {
      // Reset validation errors
      dialogs.approve.validationErrors = {
        rooms: null,
        timeInterval: null,
        assistants: null
      }
      
      // Validate required fields
      let hasErrors = false
      
      if (!dialogs.approve.rooms || dialogs.approve.rooms.length === 0) {
        dialogs.approve.validationErrors.rooms = 'Selectați cel puțin o sală pentru examen'
        hasErrors = true
      }
      
      if (!dialogs.approve.assistants || dialogs.approve.assistants.length === 0) {
        dialogs.approve.validationErrors.assistants = 'Selectați cel puțin un asistent pentru examen'
        hasErrors = true
      }
      
      if (!dialogs.approve.startTime || !dialogs.approve.endTime) {
        dialogs.approve.validationErrors.timeInterval = 'Selectați intervalul de timp pentru examen'
        hasErrors = true
      } else {
        validateTimeInterval()
        if (dialogs.approve.validationErrors.timeInterval) {
          hasErrors = true
        }
      }
      
      if (hasErrors) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Vă rugăm să completați toate câmpurile obligatorii',
          life: 3000
        })
        return
      }
      
      // Check for conflicts
      await checkForConflicts()
      if (dialogs.approve.conflicts && dialogs.approve.conflicts.length > 0) {
        // Show warning but allow to proceed
        store.dispatch('notifications/showNotification', {
          severity: 'warn',
          summary: 'Atenție',
          detail: 'Există posibile conflicte de programare. Verificați detaliile înainte de confirmare.',
          life: 5000
        })
      }
      
      try {
        dialogs.approve.loading = true
        
        // Prepare approval data for the store action
        const approvalData = {
          status: 'approved', // Explicitly set status to approved from proposed
          roomId: dialogs.approve.rooms[0].value, // Primary room
          additionalRoomIds: dialogs.approve.rooms.length > 1 
            ? dialogs.approve.rooms.slice(1).map(r => r.value) 
            : [],
          assistantIds: dialogs.approve.assistants.map(a => a.value),
          startTime: dialogs.approve.startTime,
          endTime: dialogs.approve.endTime,
          comments: '',  // Removed comments as per request
          sendEmail: true // Enable email notification for approval
        }
        
        console.log('Approving proposal with data:', approvalData)
        
        // Use store module to approve the proposal
        const updatedSchedule = await store.dispatch('schedules/approveProposal', {
          scheduleId: dialogs.approve.proposal.id,
          approvalData: approvalData
        })
        
        // Get current user from store
        const currentUser = store.getters['auth/user'] || {}
        
        // Update local data
        const index = proposals.value.findIndex(p => p.id === dialogs.approve.proposal.id)
        if (index !== -1) {
          // Use the updated schedule data returned from the API
          const primaryRoom = {
            value: updatedSchedule.roomId,
            name: dialogs.approve.rooms[0].name
          }
          
          // Create reviewer info safely even if currentUser is undefined
          const reviewerName = currentUser.firstName && currentUser.lastName ? 
            `${currentUser.firstName} ${currentUser.lastName}` : 'Administrator'
          
          // Update the local proposal with the new data
          proposals.value[index] = {
            ...proposals.value[index],
            status: 'approved',
            reviewedBy: { 
              name: reviewerName, 
              email: currentUser.email || ''
            },
            reviewDate: new Date().toISOString(),
            comments: updatedSchedule.comments || dialogs.approve.comments || '',
            room: primaryRoom,
            startTime: updatedSchedule.startTime || dialogs.approve.startTime,
            endTime: updatedSchedule.endTime || dialogs.approve.endTime,
            assistants: dialogs.approve.assistants
          }
          
          // Also add to scheduled exams
          scheduledExams.value.push({
            id: dialogs.approve.proposal.id,
            subject: proposals.value[index].subject,
            group: proposals.value[index].group,
            date: proposals.value[index].proposedDate,
            startTime: updatedSchedule.startTime || dialogs.approve.startTime,
            endTime: updatedSchedule.endTime || dialogs.approve.endTime,
            room: primaryRoom,
            assistants: dialogs.approve.assistants
          })
        }
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere Aprobată',
          detail: 'Propunerea a fost aprobată și examenul a fost programat cu succes',
          life: 3000
        })
        
        // Reset the dialog state first
        dialogs.approve.proposal = null;
        dialogs.approve.rooms = [];
        dialogs.approve.startTime = null;
        dialogs.approve.endTime = null;
        dialogs.approve.assistants = [];
        dialogs.approve.conflicts = [];
        
        // Close dialog - make sure this really happens
        dialogs.approve.visible = false;
        
        // Refresh proposals list to ensure we have the latest data
        // Use setTimeout to ensure dialog closing completes first
        setTimeout(() => {
          loadProposals();
        }, 100);
      } catch (error) {
        console.error('Error approving proposal:', error);
        // Show error notification
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la aprobarea propunerii',
          life: 5000
        })
      } finally {
        dialogs.approve.loading = false
      }
    }
    
    const rejectProposal = async () => {
      if (!dialogs.reject.reason) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Specificați motivul respingerii propunerii',
          life: 3000
        })
        return
      }
      
      try {
        dialogs.reject.loading = true
        
        // Prepare rejection data for the store action
        const rejectionData = {
          status: 'rejected', // Explicitly set status to rejected from proposed
          reason: dialogs.reject.reason,
          sendEmail: true // Ensure we're sending an email
        }
        
        console.log('Rejecting proposal with data:', rejectionData)
        
        // Use store module to reject the proposal
        const updatedSchedule = await store.dispatch('schedules/rejectProposal', {
          scheduleId: dialogs.reject.proposal.id,
          rejectionData: rejectionData
        })
        
        // Get current user from store with fallback
        const currentUser = store.getters['auth/user'] || {}
        
        // Create reviewer info safely even if currentUser is undefined
        const reviewerName = currentUser.firstName && currentUser.lastName ? 
          `${currentUser.firstName} ${currentUser.lastName}` : 'Administrator'
        
        // Update local data based on API response
        const index = proposals.value.findIndex(p => p.id === dialogs.reject.proposal.id)
        if (index !== -1) {
          proposals.value[index] = {
            ...proposals.value[index],
            status: 'rejected',
            reviewedBy: { 
              name: reviewerName, 
              email: currentUser.email || ''
            },
            rejectionReason: dialogs.reject.reason,
            reviewDate: new Date().toISOString()
          }
        }
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere respinsă',
          detail: 'Propunerea a fost respinsă și notificarea a fost trimisă',
          life: 3000
        })
        
        // Reset dialog data first
        dialogs.reject.proposal = null;
        dialogs.reject.reason = '';
        
        // Close dialog - make sure this really happens
        dialogs.reject.visible = false;
        
        // Refresh proposals list to ensure we have the latest data
        // Use setTimeout to ensure dialog closing completes first
        setTimeout(() => {
          loadProposals();
        }, 100);
      } catch (error) {
        console.error('Error rejecting proposal:', error);
        // Show error notification
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare', 
          detail: error.message || 'A apărut o eroare la respingerea propunerii',
          life: 5000
        })
      } finally {
        dialogs.reject.loading = false
      }
    }
    
    // Get schedules that belong to the CD's subjects
    const loadProposals = async () => {
      try {
        loading.value = true
        
        // Use the store to fetch CD proposals - now using the optimized teacher endpoint
        // that includes group information directly
        const cdSchedules = await store.dispatch('schedules/fetchCDProposals')
        
        // Debug the raw response from API
        console.log('[API Debug] Raw schedule data:', cdSchedules)
        
        // Extract all subject IDs from schedules to batch load them
        const subjectIds = cdSchedules.map(schedule => schedule.subjectId)
        await loadSubjectsByIds(subjectIds)
        
        // Collect room IDs for batch loading
        const roomIds = new Set()
        
        // First get all subjects' data to ensure we have complete information
        const allSubjectsResponse = await SubjectService.getAllSubjects()
        
        // Cache all subjects first
        allSubjectsResponse.forEach(subject => {
          subjectsCache.value[subject.id] = {
            id: subject.id,
            name: subject.name,
            code: subject.shortName || '',
            groupId: subject.groupId || null
          }
        })
        
        // Process each schedule to prepare data dependencies
        for (const schedule of cdSchedules) {
          // Collect room IDs for batch loading
          if (schedule.roomId) {
            roomIds.add(schedule.roomId)
          }
        }
        
        // Batch load any rooms that haven't been cached yet
        for (const roomId of roomIds) {
          if (!roomsCache.value[roomId]) {
            await getRoomById(roomId) // This will cache the room
          }
        }
        
        // Pre-load SG users for all groups using direct API call
        try {
          const sgResponse = await apiClient.get('/users', { params: { role: 'SG' } })
          
          // Initialize the roles cache if needed
          if (!usersCache.value['roles']) {
            usersCache.value['roles'] = {}
          }
          
          // Cache all SG users
          usersCache.value['roles']['SG'] = sgResponse.data
          
          // Also cache individual users
          if (sgResponse.data && Array.isArray(sgResponse.data)) {
            sgResponse.data.forEach(user => {
              usersCache.value[user.id] = {
                id: user.id,
                name: `${user.firstName} ${user.lastName}`,
                email: user.email
              }
            })
          }
        } catch (error) {
          console.error('Error pre-loading SG users:', error)
        }
        
        // Transform the data to match our component's expected format with minimal API calls
        proposals.value = await Promise.all(cdSchedules.map(async schedule => {
          // Get subject details from cache
          const subject = await getSubjectById(schedule.subjectId)
          if (!subject) {
            console.error(`Failed to get subject for proposal ${schedule.id}`)
            return null
          }
          
          // Use group info directly from the API response if available, or fetch if needed
          // Get group information from the API response or from the subject
          console.log(`[DEBUG] Processing group for schedule ${schedule.id}, subject ${schedule.subjectId}:`, {
            hasGroupId: !!schedule.groupId,
            groupId: schedule.groupId,
            hasGroupName: !!schedule.groupName,
            groupName: schedule.groupName,
            subjectGroupId: subject?.groupId
          })
          
          let group
          // Check if group info is directly available in the schedule (from our enhanced endpoint)
          if (schedule.groupId && schedule.groupName) {
            console.log(`[DEBUG] Using group directly from schedule response:`, { id: schedule.groupId, name: schedule.groupName })
            group = { 
              id: schedule.groupId, 
              name: schedule.groupName || `Grupa ${schedule.groupId}` // Ensure name is not empty
            }
            // Also cache this group for future reference
            if (!groupsCache.value[schedule.groupId]) {
              groupsCache.value[schedule.groupId] = group
            }
          } else if (subject && subject.groupId) {
            // Fallback to getting group info from subject if not in API response
            console.log(`[DEBUG] Fallback: Getting group from subject.groupId:`, subject.groupId)
            group = await getGroupById(subject.groupId)
            console.log(`[DEBUG] Result from getGroupById:`, group)
          } else {
            // Last resort fallback
            console.log(`[DEBUG] No group info available, using default fallback`)
            group = { id: null, name: 'Fără grupă' }
          }
          
          // Get room details if available (from cache)
          let room = null
          if (schedule.roomId) {
            room = await getRoomById(schedule.roomId)
          }
          
          // Get proposer information (SG) checking all possible field sources
          let proposedBy = { name: 'Student Group Leader', email: '' }
          
          // Check if schedule already has submittedBy data directly from the backend
          if (schedule.submittedBy && (schedule.submittedBy.firstName || schedule.submittedBy.name)) {
            // Use data directly from the backend response
            proposedBy = {
              name: schedule.submittedBy.name || `${schedule.submittedBy.firstName || ''} ${schedule.submittedBy.lastName || ''}`.trim(),
              email: schedule.submittedBy.email || ''
            }
            
            console.log('[Debug] Found submittedBy directly in schedule:', proposedBy)
          } else if (schedule.proposedBy) {
            // Some API responses might have proposedBy directly
            proposedBy = {
              name: schedule.proposedBy.name || `${schedule.proposedBy.firstName || ''} ${schedule.proposedBy.lastName || ''}`.trim(),
              email: schedule.proposedBy.email || ''
            }
            
            console.log('[Debug] Found proposedBy directly in schedule:', proposedBy)
          } else {
            // Fallback to looking up the SG for this group
            try {
              if (group && group.id && group.id > 0) {
                // Only make the API call if we have a valid group ID
                const response = await apiClient.get('/users', { 
                  params: { role: 'SG', groupId: group.id }
                })
                const sgUsers = response.data || []
                
                if (sgUsers && sgUsers.length > 0) {
                  const sg = sgUsers[0]
                  proposedBy = {
                    name: `${sg.firstName || ''} ${sg.lastName || ''}`.trim(),
                    email: sg.email || ''
                  }
                  
                  console.log('[Debug] Found SG user from API call:', proposedBy)
                  
                  // Cache for future use
                  if (!usersCache.value['roles']) {
                    usersCache.value['roles'] = {}
                  }
                  
                  if (!usersCache.value['roles']['SG']) {
                    usersCache.value['roles']['SG'] = []
                  }
                  
                  // Add only if not already cached
                  sgUsers.forEach(user => {
                    if (!usersCache.value['roles']['SG'].some(u => u.id === user.id)) {
                      usersCache.value['roles']['SG'].push(user)
                    }
                  })
                }
              }
            } catch (error) {
              console.error('Error getting SG user:', error)
              // Keep default in case of error
              proposedBy = { name: 'Student Group Leader', email: '' }
            }
          }
          
          // Ensure proposedBy has a name even if it's empty
          if (!proposedBy.name || proposedBy.name.trim() === '') {
            proposedBy.name = 'Student Group Leader'
          }
          
          // Get reviewer information if applicable
          let reviewedBy = null
          if (schedule.status === 'approved' || schedule.status === 'rejected') {
            const currentUser = store.getters['auth/user']
            reviewedBy = {
              name: currentUser.firstName + ' ' + currentUser.lastName || 'Professor',
              email: currentUser.email || ''
            }
          }
          
          // Transform to our view model - handle various field names from backend
          const proposalData = {
            id: schedule.id,
            subjectId: schedule.subjectId,
            subject: subject,
            group: group,
            proposedDate: schedule.proposedDate || schedule.date || schedule.examDate,
            proposedTimeStart: schedule.proposedTimeStart || schedule.startTime,
            proposedTimeEnd: schedule.proposedTimeEnd || schedule.endTime,
            room: room || { id: null, name: 'Nu este alocată' },
            status: schedule.status,
            comments: schedule.comments,
            proposedBy: proposedBy,
            lastStatusChangeDate: schedule.lastStatusChangeDate,
            rejectionReason: schedule.reason || null,
            roomRequirements: subject.roomRequirements || ''
          }
          
          // Debug the mapped data with date fields
          console.log('[Mapping Debug] Original vs. Mapped:', {
            original: {
              proposedDate: schedule.proposedDate,
              date: schedule.date,
              examDate: schedule.examDate,
              proposedTimeStart: schedule.proposedTimeStart,
              startTime: schedule.startTime,
              proposedTimeEnd: schedule.proposedTimeEnd,
              endTime: schedule.endTime
            },
            mapped: {
              proposedDate: proposalData.proposedDate,
              proposedTimeStart: proposalData.proposedTimeStart,
              proposedTimeEnd: proposalData.proposedTimeEnd
            }
          })
          
          // Debug the transformed data focusing on group info
          console.log(`[DEBUG] Final proposal data for schedule ${schedule.id}:`, {
            hasGroup: !!proposalData.group,
            groupData: proposalData.group,
            groupName: proposalData.group?.name,
            originalGroupId: schedule.groupId,
            originalGroupName: schedule.groupName,
            subjectGroupId: subject?.groupId
          })
          
          return proposalData
        }))
        
        // Filter out any null entries that might have occurred due to failed lookups
        proposals.value = proposals.value.filter(Boolean)
        
        // Extract distinct groups for filtering
        const uniqueGroups = new Set()
        groupOptions.value = proposals.value
          .map(p => ({ 
            name: p.group?.name || 'Fără grupă', 
            value: p.group?.name || 'Fără grupă' 
          }))
          .filter(g => {
            if (uniqueGroups.has(g.value)) {
              return false
            }
            uniqueGroups.add(g.value)
            return true
          })
      } catch (error) {
        console.error('Error loading proposals:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',          detail: 'Nu s-au putut încărca propunerile',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }

    // Load rooms for approval dialog
    const loadRooms = async () => {
      try {
        roomsLoading.value = true

        // Call the service to get all available rooms
        const response = await RoomService.getAllRooms()

        // Transform the data to match our component's expected format
        availableRooms.value = response.map(room => ({
          value: room.id,
          name: room.name,
          shortName: room.shortName,
          buildingName: room.buildingName,
          capacity: room.capacity,
          computers: room.computers
        }))
        
        // Cache each room by ID for later use
        availableRooms.value.forEach(room => {
          roomsCache.value[room.value] = room
        })

        // Also update roomOptions for other UI elements
        // Sort rooms alphabetically by name for better readability in the UI
        roomOptions.value = availableRooms.value
          .map(room => ({
            value: room.value,
            name: room.name
          }))
          .sort((a, b) => a.name.localeCompare(b.name))
      } catch (error) {
        console.error('Error loading rooms:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca sălile',
          life: 5000
        })
      } finally {        roomsLoading.value = false
      }
    }
    
    // Get a room by ID, using cache when possible
    const getRoomById = async (roomId) => {
      // Return from cache if available
      if (roomsCache.value[roomId]) {
        return roomsCache.value[roomId]
      }
      
      try {
        const roomResponse = await RoomService.getById(roomId)
        const room = {
          value: roomResponse.data.id,
          name: roomResponse.data.name,
          shortName: roomResponse.data.shortName,
          buildingName: roomResponse.data.buildingName,
          capacity: roomResponse.data.capacity,
          computers: roomResponse.data.computers
        }
        
        // Cache the result
        roomsCache.value[roomId] = room
        return room
      } catch (error) {
        console.error(`Error fetching room ${roomId}:`, error)
        return null
      }
    }
    
    // Batch load subjects by IDs - this is mostly maintained for compatibility
    // since we now load all subjects at once in loadProposals
    const loadSubjectsByIds = async (subjectIds) => {
      try {
        // Check if we have already loaded all subjects in loadProposals
        if (Object.keys(subjectsCache.value).length > 10) {
          // We probably already loaded all subjects, just check if any are missing
          const idsToFetch = subjectIds.filter(id => !subjectsCache.value[id])
          if (idsToFetch.length === 0) {
            return // All subjects are already cached
          }
          
          // If just a few are missing, fetch them individually
          if (idsToFetch.length <= 3) {
            const promises = idsToFetch.map(id => SubjectService.getById(id))
            const responses = await Promise.all(promises)
            
            responses.forEach(response => {
              const subject = response.data
              subjectsCache.value[subject.id] = {
                id: subject.id,
                name: subject.name,
                code: subject.shortName || '',
                groupId: subject.groupId || null,
                assistantIds: subject.assistantIds || [] // Include assistantIds for pre-selection
              }
            })
            return
          }
        }
        
        // In all other cases, just load all subjects at once
        const allSubjectsResponse = await SubjectService.getAllSubjects()
        allSubjectsResponse.forEach(subject => {
          subjectsCache.value[subject.id] = {
            id: subject.id,
            name: subject.name,
            code: subject.shortName || '',
            groupId: subject.groupId || null
          }
        })
      } catch (error) {
        console.error('Error loading subjects:', error)
      }
    }
    
    // Get group by ID, using cache when possible
    const getGroupById = async (groupId) => {
      // Handle invalid group ID
      if (!groupId) {
        console.log('[DEBUG] Invalid group ID provided to getGroupById')
        return { id: null, name: 'Fără grupă' }
      }
      
      // Return from cache if available
      if (groupsCache.value[groupId]) {
        console.log(`[DEBUG] Returning group from cache for ID ${groupId}:`, groupsCache.value[groupId])
        return groupsCache.value[groupId]
      }
      
      try {
        // Try to find the group from our GroupService
        console.log(`[DEBUG] Fetching group with ID ${groupId} from API`)
        const response = await GroupService.getById(groupId)
        
        const group = {
          id: response.data.id,
          name: response.data.name || `Grupa ${response.data.id}`, // Ensure we always have a name
          shortName: response.data.shortName || ''
        }
        
        // Cache the result
        groupsCache.value[groupId] = group
        console.log(`[DEBUG] Cached group from API:`, group)
        return group
      } catch (error) {
        console.error(`Error fetching group ${groupId}:`, error)
        // Create a fallback group object with at least an ID
        const fallbackGroup = { id: groupId, name: `Grupa ${groupId}` }
        groupsCache.value[groupId] = fallbackGroup // Cache even the fallback
        return fallbackGroup
      }
    }
    
    // Get subject by ID using cache
    const getSubjectById = async (subjectId) => {
      // Handle invalid subject ID
      if (!subjectId) {
        return {
          id: 0,
          name: 'Disciplină nedefinită',
          code: 'N/A',
          groupId: null
        }
      }
      
      // Return from cache if available
      if (subjectsCache.value[subjectId]) {
        return subjectsCache.value[subjectId]
      }
      
      try {
        const response = await SubjectService.getById(subjectId)
        const subject = {
          id: response.data.id,
          name: response.data.name,
          code: response.data.shortName || '',
          groupId: response.data.groupId || null,
          roomRequirements: response.data.roomRequirements || '',
          assistantIds: response.data.assistantIds || []
        }
        
        // Cache the result
        subjectsCache.value[subjectId] = subject
        return subject
      } catch (error) {
        console.error(`Error fetching subject ${subjectId}:`, error)
        return {
          id: subjectId,
          name: `Disciplina ${subjectId}`,
          code: 'N/A',
          groupId: null,
          assistantIds: [] // Add empty assistantIds array for consistency
        }
      }
    }
    
    // Load available assistants for approval dialog (CD users who can assist with exams)
    const loadAssistants = async () => {
      try {
        assistantsLoading.value = true
        
        // Correctly load CD users who can be assistants (as per subject.assistantIds)
        const response = await UserService.getUsersByRole('CD')
        
        // Transform for dropdown
        availableAssistants.value = response.data.map(assistant => ({
          value: assistant.id,
          label: `${assistant.firstName} ${assistant.lastName}`,
          name: `${assistant.firstName} ${assistant.lastName}`,
          email: assistant.email
        }))
        
        // Cache the assistants
        // Cache by role for role-based queries
        if (!usersCache.value['roles']) {
          usersCache.value['roles'] = {}
        }
        usersCache.value['roles']['CD'] = response.data
      } catch (error) {
        console.error('Error loading assistants:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca asistenţii',
          life: 5000
        })
      } finally {
        assistantsLoading.value = false
      }
    }
    
    // Load assistants specific to a subject using the new endpoint
    const loadAssistantsBySubject = async (subjectId) => {
      if (!subjectId) {
        console.warn('No subject ID provided for loading assistants')
        return []
      }
      
      try {
        assistantsLoading.value = true
        console.log(`[DEBUG] Loading assistants for subject ID: ${subjectId}`)
        
        // Use the new endpoint to get only relevant assistants for this subject
        const response = await ScheduleService.getSubjectAssistants(subjectId)
        console.log(`[DEBUG] Received assistants data:`, response.data)
        
        // Transform for dropdown
        const subjectAssistants = response.data.map(assistant => ({
          value: assistant.id,
          label: `${assistant.firstName} ${assistant.lastName}`,
          name: `${assistant.firstName} ${assistant.lastName}`,
          email: assistant.email
        }))
        
        console.log(`[DEBUG] Transformed assistants for dropdown:`, subjectAssistants)
        
        // Update the available assistants list
        availableAssistants.value = subjectAssistants
        assistantOptions.value = subjectAssistants
        
        // Also cache these assistants
        if (!usersCache.value['roles']) {
          usersCache.value['roles'] = {}
        }
        if (!usersCache.value['roles']['CD']) {
          usersCache.value['roles']['CD'] = []
        }
        
        // Add to cache if not already present
        response.data.forEach(assistant => {
          if (!usersCache.value['roles']['CD'].some(a => a.id === assistant.id)) {
            usersCache.value['roles']['CD'].push(assistant)
          }
        })
        
        return subjectAssistants
      } catch (error) {
        console.error(`Error loading assistants for subject ${subjectId}:`, error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca asistenţii pentru această disciplină',
          life: 5000
        })
        return []
      } finally {
        assistantsLoading.value = false
      }
    }
    
    // Get users by role with caching
    const getUsersByRole = async (role, params = {}) => {
      // Check if we have cached data for this role
      if (usersCache.value['roles'] && usersCache.value['roles'][role]) {
        // If params has groupId, filter the cached data
        if (params.groupId) {
          return usersCache.value['roles'][role].filter(user => 
            user.groupId === params.groupId
          )
        }
        return usersCache.value['roles'][role]
      }
      
      try {
        const response = await UserService.getUsersByRole(role, params)
        
        // Initialize roles cache if needed
        if (!usersCache.value['roles']) {
          usersCache.value['roles'] = {}
        }
        
        // Cache users by role and also individually by ID
        usersCache.value['roles'][role] = response.data
        response.data.forEach(user => {
          usersCache.value[user.id] = {
            id: user.id,
            name: `${user.firstName} ${user.lastName}`,
            email: user.email
          }
        })
        
        return response.data
      } catch (error) {
        console.error(`Error fetching users with role ${role}:`, error)
        return []
      }
    }
    
    // Initialize
    onMounted(() => {
      // Load initial data
      loadProposals()
      loadRooms()

      // We're already loading assistants when opening the dialog,
      // so we don't need to call it on mount
    })

    // Return all the necessary reactive data and methods for the template
    return {
      proposals,
      filteredProposals,
      filters,
      loading,
      statusOptions,
      groupOptions,
      roomOptions,
      assistantOptions,
      roomsLoading,
      assistantsLoading,
      availableRooms,
      availableAssistants,
      timeOptions,
      dialogs,
      scheduledExams,
      isApproveFormValid,
      
      // Caches
      subjectsCache,
      roomsCache,
      groupsCache,
      usersCache,
      
      // Cache helper methods
      getSubjectById,
      getRoomById,
      getGroupById,
      getUsersByRole,
      loadSubjectsByIds,
      
      formatDate,
      formatTime,
      formatDatetime,
      getStatusLabel,
      getStatusSeverity,
      
      openApproveDialog,
      openRejectDialog,
      openDetailsDialog,
      closeDialogs,
      
      validateTimeInterval,
      getScheduledExam,
      checkForTimeConflicts,
      
      approveProposal,
      rejectProposal
    }
  }
}
</script>

<style lang="scss" scoped>
.review-proposals {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  .filter-section {
    padding: 1rem;
    
    .p-field {
      margin-bottom: 0;
      
      label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
      }
      
      .w-full {
        width: 100%;
      }
    }
  }
  
  .proposals-table {
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
    
    .action-buttons {
      display: flex;
      justify-content: center;
    }
  }
  
  .proposal-details {
    h3 {
      font-size: 1.25rem;
      color: #2c3e50;
      margin-top: 0;
      margin-bottom: 1rem;
    }
    
    .detail-item {
      margin-bottom: 0.75rem;
      
      .detail-label {
        font-weight: 500;
        margin-right: 0.5rem;
        color: #6c757d;
      }
      
      .detail-value {
        color: #2c3e50;
      }
    }
  }
  
  .required-field {
    color: #f44336;
  }
}
</style>
