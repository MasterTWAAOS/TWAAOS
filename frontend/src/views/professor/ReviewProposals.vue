<template>
  <div class="review-proposals">
    <h1>Validare Propuneri Examene</h1>
    
    <div class="filter-section p-card p-mb-3">
      <div class="p-grid">
        <div class="p-col-12 p-md-3">
          <div class="p-field">
            <label for="statusFilter">Status</label>
            <Dropdown 
              id="statusFilter" 
              v-model="filters.status" 
              :options="statusOptions" 
              optionLabel="name" 
              placeholder="Toate statusurile"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="p-col-12 p-md-3">
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
              placeholder="Caută după denumire sau cod"
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
            <Chip :label="slotProps.data.group.name" />
          </template>
        </Column>
        <Column field="proposedDate" header="Dată Propusă" :sortable="true" style="width: 15%">
          <template #body="slotProps">
            <div class="proposed-date">
              <div class="date">{{ formatDate(slotProps.data.proposedDate) }}</div>
              <div class="time">{{ formatTime(slotProps.data.proposedTimeStart) }} - {{ formatTime(slotProps.data.proposedTimeEnd) }}</div>
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
                v-if="slotProps.data.status === 'pending'"
                @click="openApproveDialog(slotProps.data)"
              />
              <Button 
                icon="pi pi-times" 
                class="p-button-danger p-button-sm p-mr-1" 
                v-tooltip.top="'Respinge propunerea'"
                v-if="slotProps.data.status === 'pending'"
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
                display="chip"
                class="w-full"
                :filter="true"
              />
              <small v-if="dialogs.approve.validationErrors.assistants" class="p-error">{{ dialogs.approve.validationErrors.assistants }}</small>
            </div>
          </div>

          <!-- Comentarii -->
          <div class="p-col-12">
            <div class="p-field p-mb-3">
              <label for="approveComment">Comentarii (opțional)</label>
              <Textarea 
                id="approveComment" 
                v-model="dialogs.approve.comments" 
                rows="3" 
                placeholder="Adăugați comentarii pentru propunere"
              />
            </div>
          </div>

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
              <span class="detail-value">{{ dialogs.details.proposal.submittedBy.name }}</span>
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
import { ref, computed, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Chip from 'primevue/chip'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'

export default {
  name: 'ReviewProposalsView',
  components: {
    DataTable,
    Column,
    Dropdown,
    InputText,
    Chip,
    Tag,
    Dialog,
    Textarea,
    Button
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const proposals = ref([])
    const scheduledExams = ref([])
    
    // Load available rooms for approval dialog
    const loadRooms = async () => {
      try {
        roomsLoading.value = true
        
        // Call the API to get all available rooms
        const response = await axios.get(ROOMS_ENDPOINT)
        
        // Transform the data to match our component's expected format
        availableRooms.value = response.data.map(room => ({
          value: room.id,
          name: room.name,
          shortName: room.shortName,
          buildingName: room.buildingName,
          capacity: room.capacity,
          computers: room.computers
        }))
      } catch (error) {
        console.error(error)
      } finally {
        roomsLoading.value = false
      }
    }
    
    // Load available assistants for approval dialog (CD users who can assist with exams)
    const loadAssistants = async () => {
      try {
        assistantsLoading.value = true
        
        // Get CD users who can serve as assistants
        const response = await axios.get(`${USERS_ENDPOINT}?role=CD`)
        
        // Transform the data to match our component's expected format
        availableAssistants.value = response.data.map(assistant => ({
          value: assistant.id,
          name: `${assistant.firstName} ${assistant.lastName}`,
          department: assistant.department
        }))
      } catch (error) {
        console.error(error)
      } finally {
        assistantsLoading.value = false
      }
    }
    
    // Filters
    const filters = reactive({
      status: null,
      group: null,
      search: ''
    })
    
    // Filter options
    const statusOptions = ref([
      { name: 'În așteptare', value: 'pending' },
      { name: 'Aprobate', value: 'approved' },
      { name: 'Respinse', value: 'rejected' }
    ])
    
    const groupOptions = ref([
      { name: 'CTI1', value: 'CTI1' },
      { name: 'CTI2', value: 'CTI2' },
      { name: 'CTI3', value: 'CTI3' },
      { name: 'CTI4', value: 'CTI4' },
      { name: 'AITC1', value: 'AITC1' },
      { name: 'AITC2', value: 'AITC2' },
      { name: 'AITC3', value: 'AITC3' }
    ])
    
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
    
    // Assistant options
    const assistantOptions = ref([
      { id: 1, name: 'Asist. Maria Ionescu', department: 'Calculatoare' },
      { id: 2, name: 'Asist. Ion Popescu', department: 'Calculatoare' },
      { id: 3, name: 'Asist. Elena Vasilescu', department: 'Automatică' },
      { id: 4, name: 'Asist. Andrei Georgescu', department: 'Calculatoare' },
      { id: 5, name: 'Asist. Cristina Dumitrescu', department: 'Automatică' }
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
        
        // Filter by search term
        if (filters.search) {
          const searchTerm = filters.search.toLowerCase()
          const subjectName = proposal.subject.name.toLowerCase()
          const subjectCode = proposal.subject.code.toLowerCase()
          
          if (!subjectName.includes(searchTerm) && !subjectCode.includes(searchTerm)) {
            return false
          }
        }
        
        return true
      })
    })
    
    // Check if approve form is valid
    const isApproveFormValid = computed(() => {
      const { rooms, startTime, endTime, assistants, validationErrors } = dialogs.approve
      return (
        rooms && rooms.length > 0 &&
        startTime && endTime &&
        assistants && assistants.length > 0 &&
        !validationErrors.rooms &&
        !validationErrors.timeInterval &&
        !validationErrors.assistants
      )
    })
    
    // Format functions
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric' 
      }).format(date)
    }
    
    const formatTime = (timeString) => {
      return timeString
    }
    
    const formatDatetime = (dateString) => {
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
    
    // Status helpers
    const getStatusLabel = (status) => {
      switch (status) {
        case 'pending': return 'În așteptare'
        case 'approved': return 'Aprobat'
        case 'rejected': return 'Respins'
        default: return status
      }
    }
    
    const getStatusSeverity = (status) => {
      switch (status) {
        case 'pending': return 'warning'
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
      }
      
      // After validation passes, check for conflicts
      checkForTimeConflicts()
    }
    
    const checkForRoomConflicts = () => {
      const { rooms, startTime, endTime, proposal } = dialogs.approve
      // Reset room conflicts
      const conflicts = []
      
      // Check if rooms are selected and times are set
      if (!rooms || rooms.length === 0 || !startTime || !endTime) return
      
      // In a real implementation, we would check against the database of scheduled exams
      // Here we're using the mock data for demonstration
      scheduledExams.value.forEach(exam => {
        // Skip if it's the same proposal
        if (proposal && exam.id === proposal.id) return
        
        // Check if date is the same
        if (exam.date !== proposal.proposedDate) return
        
        // Check for time overlap
        const examStart = exam.startTime
        const examEnd = exam.endTime
        
        if ((startTime < examEnd && endTime > examStart)) {
          // Check if any selected room is already in use
          const conflictingRooms = rooms.filter(r => 
            exam.rooms.some(er => er.value === r.value)
          )
          
          if (conflictingRooms.length > 0) {
            const roomNames = conflictingRooms.map(r => r.name).join(', ')
            conflicts.push(`Sala(sălile) ${roomNames} este/sunt deja rezervată(e) între ${examStart} - ${examEnd}`)
          }
        }
      })
      
      return conflicts
    }
    
    const checkForAssistantConflicts = () => {
      const { assistants, startTime, endTime, proposal } = dialogs.approve
      const conflicts = []
      
      // Check if assistants are selected and times are set
      if (!assistants || assistants.length === 0 || !startTime || !endTime) return conflicts
      
      // In a real implementation, we would check against the database of scheduled exams
      scheduledExams.value.forEach(exam => {
        // Skip if it's the same proposal
        if (proposal && exam.id === proposal.id) return
        
        // Check if date is the same
        if (exam.date !== proposal.proposedDate) return
        
        // Check for time overlap
        const examStart = exam.startTime
        const examEnd = exam.endTime
        
        if ((startTime < examEnd && endTime > examStart)) {
          // Check if any selected assistant is already assigned
          const conflictingAssistants = assistants.filter(a => 
            exam.assistants.some(ea => ea.id === a.id)
          )
          
          if (conflictingAssistants.length > 0) {
            const assistantNames = conflictingAssistants.map(a => a.name).join(', ')
            conflicts.push(`Asistentul/Asistenții ${assistantNames} este/sunt deja alocat(ți) între ${examStart} - ${examEnd}`)
          }
        }
      })
      
      return conflicts
    }
    
    const checkForTimeConflicts = () => {
      // Combine all conflict checks
      dialogs.approve.conflicts = [
        ...checkForRoomConflicts() || [],
        ...checkForAssistantConflicts() || []
      ]
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
          // Find rooms that match the requirements
          const matchingRooms = availableRooms.value.filter(room => 
            // For example, if requirement includes 'computers', filter rooms with computers
            (proposal.roomRequirements.toLowerCase().includes('calculatoare') && room.computers) ||
            // If capacity is mentioned, filter by capacity
            (proposal.roomRequirements.match(/\d+/) && room.capacity >= parseInt(proposal.roomRequirements.match(/\d+/)[0]))
          )
          
          if (matchingRooms.length > 0) {
            dialogs.approve.rooms = [matchingRooms[0]] // Pre-select the first matching room
          }
        }
        
        // Load available assistants if not already loaded
        if (availableAssistants.value.length === 0) {
          await loadAssistants()
        }
        
        // Check if subject has previous assigned assistants and pre-select them
        if (proposal.subject && proposal.subject.id) {
          try {
            const subjectResponse = await axios.get(`${API_BASE_URL}/subjects/${proposal.subject.id}`)
            const subjectData = subjectResponse.data
            
            if (subjectData.assistantIds && subjectData.assistantIds.length > 0) {
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
      const { rooms, assistants, startTime, endTime } = dialogs.approve
      
      // Reset validation errors
      dialogs.approve.validationErrors = {
        rooms: null,
        timeInterval: null,
        assistants: null
      }
      
      // Validate required fields
      let hasErrors = false
      
      if (!rooms || rooms.length === 0) {
        dialogs.approve.validationErrors.rooms = 'Selectați cel puțin o sală pentru examen'
        hasErrors = true
      }
      
      if (!assistants || assistants.length === 0) {
        dialogs.approve.validationErrors.assistants = 'Selectați cel puțin un asistent pentru examen'
        hasErrors = true
      }
      
      if (!startTime || !endTime) {
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
      checkForTimeConflicts()
      if (dialogs.approve.conflicts.length > 0) {
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
        
        // Prepare data for API call
        const approvalData = {
          scheduleId: dialogs.approve.proposal.id,
          status: 'approved',
          roomIds: dialogs.approve.rooms.map(r => r.value),
          assistantIds: dialogs.approve.assistants.map(a => a.id),
          startTime: dialogs.approve.startTime,
          endTime: dialogs.approve.endTime,
          comments: dialogs.approve.comments || null
        }
        
        // Prepare the data according to the ScheduleUpdate DTO structure
        const updateData = {
          status: 'approved',
          roomId: dialogs.approve.rooms[0]?.value, // Primary room
          startTime: dialogs.approve.startTime,
          endTime: dialogs.approve.endTime,
          additionalRoomIds: dialogs.approve.rooms.length > 1 
            ? dialogs.approve.rooms.slice(1).map(r => r.value) 
            : [],
          assistantIds: dialogs.approve.assistants.map(a => a.value),
          comments: dialogs.approve.comments || null,
          sendEmail: false // No email for approval
        }
        
        console.log('Approving proposal with data:', updateData)
        
        // Call the backend API to update schedule
        const response = await axios.put(`${SCHEDULES_ENDPOINT}/${dialogs.approve.proposal.id}`, updateData)
        const updatedSchedule = response.data
        
        // Get current user info for the reviewer details
        const currentUserResponse = await axios.get(`${API_BASE_URL}/auth/me`)
        const currentUser = currentUserResponse.data
        
        // Update local data
        const index = proposals.value.findIndex(p => p.id === dialogs.approve.proposal.id)
        if (index !== -1) {
          // Get the room info for display
          const roomResponse = await axios.get(`${ROOMS_ENDPOINT}/${updatedSchedule.roomId}`)
          const primaryRoom = {
            value: roomResponse.data.id,
            name: roomResponse.data.name
          }
          
          // Get assistant info for all assistant IDs
          const assistantsList = []
          if (updateData.assistantIds && updateData.assistantIds.length > 0) {
            // In a production app, we would use Promise.all with multiple requests
            // or have a batch endpoint to get all users at once
            for (const assistantId of updateData.assistantIds) {
              try {
                const assistantResponse = await axios.get(`${USERS_ENDPOINT}/${assistantId}`)
                assistantsList.push({
                  id: assistantResponse.data.id,
                  name: `${assistantResponse.data.firstName} ${assistantResponse.data.lastName}`,
                  department: assistantResponse.data.department
                })
              } catch (err) {
                console.error(`Error fetching assistant with ID ${assistantId}:`, err)
              }
            }
          }
          
          // Update the local proposal with the new data
          proposals.value[index] = {
            ...proposals.value[index],
            status: 'approved',
            reviewedBy: { 
              name: `${currentUser.firstName} ${currentUser.lastName}`, 
              email: currentUser.email 
            },
            reviewDate: new Date().toISOString(),
            comments: updatedSchedule.comments || dialogs.approve.comments || null,
            room: primaryRoom,
            startTime: updatedSchedule.startTime || dialogs.approve.startTime,
            endTime: updatedSchedule.endTime || dialogs.approve.endTime,
            assistants: assistantsList
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
            assistants: assistantsList
          })
        }
        
        // Refresh the proposals list to make sure we have the latest data
        loadProposals()
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere Aprobată',
          detail: 'Propunerea a fost aprobată și examenul a fost programat cu succes',
          life: 3000
        })
        
        // Close dialog
        dialogs.approve.visible = false
      } catch (error) {
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
        
        // Prepare the data according to the ScheduleUpdate DTO structure
        const updateData = {
          status: 'rejected',
          reason: dialogs.reject.reason,
          sendEmail: true // This will trigger automatic email to SG
        }
        
        console.log('Rejecting proposal with data:', updateData)
        
        // Call the backend API to update schedule
        const response = await axios.put(`${SCHEDULES_ENDPOINT}/${dialogs.reject.proposal.id}`, updateData)
        const updatedSchedule = response.data
        
        // Get current user info for the reviewer details
        const currentUserResponse = await axios.get(`${API_BASE_URL}/auth/me`)
        const currentUser = currentUserResponse.data
        
        // Update local data based on API response
        const index = proposals.value.findIndex(p => p.id === dialogs.reject.proposal.id)
        if (index !== -1) {
          proposals.value[index] = {
            ...proposals.value[index],
            status: 'rejected',
            reviewedBy: { 
              name: `${currentUser.firstName} ${currentUser.lastName}`, 
              email: currentUser.email 
            },
            reviewDate: new Date().toISOString(),
            rejectionReason: updateData.reason
          }
        }
        
        // Refresh the proposals list to ensure we have the latest data
        loadProposals()
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere Respinsă',
          detail: 'Propunerea a fost respinsă cu succes. Un email a fost trimis către șeful de grupă.',
          life: 3000
        })
        
        // Close dialog
        dialogs.reject.visible = false
      } catch (error) {
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
    
    // API endpoints
    const API_BASE_URL = '/api'
    const SCHEDULES_ENDPOINT = `${API_BASE_URL}/schedules`
    const ROOMS_ENDPOINT = `${API_BASE_URL}/rooms`
    const USERS_ENDPOINT = `${API_BASE_URL}/users`
    // Note: assistants are CD users who can assist with exams
    
    // Get schedules that belong to the CD's subjects
    const loadProposals = async () => {
      try {
        loading.value = true
        
        // Get current user info to identify CD's subjects
        const currentUserResponse = await axios.get(`${API_BASE_URL}/auth/me`)
        const currentUserId = currentUserResponse.data.id
        
        // Get all schedules with status 'proposed'
        const schedulesResponse = await axios.get(`${SCHEDULES_ENDPOINT}?status=proposed`)
        let allSchedules = schedulesResponse.data
        
        // For CD users, we need to filter to only show schedules for subjects where they are the teacher
        // Get subjects where the current user is the teacher
        const subjectsResponse = await axios.get(`${API_BASE_URL}/subjects?teacherId=${currentUserId}`)
        const cdSubjects = subjectsResponse.data
        const cdSubjectIds = cdSubjects.map(subject => subject.id)
        
        // Filter schedules to only include those for the CD's subjects
        const cdSchedules = allSchedules.filter(schedule => 
          cdSubjectIds.includes(schedule.subjectId)
        )
        
        // Transform the data to match our component's expected format
        proposals.value = await Promise.all(cdSchedules.map(async schedule => {
          // Get subject details
          const subjectResponse = await axios.get(`${API_BASE_URL}/subjects/${schedule.subjectId}`)
          const subject = subjectResponse.data
          
          // Get group details
          const groupResponse = await axios.get(`${API_BASE_URL}/groups/${subject.groupId}`)
          const group = groupResponse.data
          
          // Get room details if available
          let room = null
          if (schedule.roomId) {
            const roomResponse = await axios.get(`${ROOMS_ENDPOINT}/${schedule.roomId}`)
            room = {
              value: roomResponse.data.id,
              name: roomResponse.data.name
            }
          }
          
          // Get proposer information (SG)
          let proposedBy = { name: 'Student Group Leader', email: '' }
          const sgUsersResponse = await axios.get(`${USERS_ENDPOINT}?role=SG&groupId=${group.id}`)
          if (sgUsersResponse.data.length > 0) {
            const sg = sgUsersResponse.data[0]
            proposedBy = { 
              name: sg.name || 'Student Group Leader', 
              email: sg.email || '' 
            }
          }
          
          // Get reviewer information if applicable
          let reviewedBy = null
          if (schedule.status === 'approved' || schedule.status === 'rejected') {
            reviewedBy = {
              name: currentUserResponse.data.name || 'Professor',
              email: currentUserResponse.data.email || ''
            }
          }
          
          return {
            id: schedule.id,
            subject: { 
              id: subject.id, 
              name: subject.name, 
              code: subject.shortName || ''
            },
            group: { 
              id: group.id, 
              name: group.name 
            },
            proposedDate: schedule.date,
            status: schedule.status,
            proposedBy: proposedBy,
            proposalDate: new Date().toISOString(), // Assuming this isn't stored in the DB
            reviewedBy: reviewedBy,
            reviewDate: reviewedBy ? new Date().toISOString() : null,
            room: room,
            startTime: schedule.startTime,
            endTime: schedule.endTime,
            rejectionReason: schedule.reason || null
          }
        }))
        
        // Extract distinct groups for filtering
        const uniqueGroups = new Set()
        groups.value = proposals.value
          .map(p => ({ name: p.group.name, value: p.group.name }))
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
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca propunerile',
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
        
        // Call the API to get all available rooms
        const response = await axios.get(ROOMS_ENDPOINT)
        
        // Transform the data to match our component's expected format
        availableRooms.value = response.data.map(room => ({
          value: room.id,
          name: room.name,
          shortName: room.shortName,
          buildingName: room.buildingName,
          capacity: room.capacity,
          computers: room.computers
        }))
        
        // Also update roomOptions for other UI elements
        roomOptions.value = availableRooms.value.map(room => ({
          value: room.value,
          name: room.name
        }))
      } catch (error) {
        console.error('Error loading rooms:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca sălile',
          life: 5000
        })
      } finally {
        roomsLoading.value = false
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
    
    return {
      loading,
      proposals,
      filteredProposals,
      filters,
      statusOptions,
      groupOptions,
      roomOptions,
      dialogs,
      formatDate,
      formatTime,
      formatDatetime,
      getStatusLabel,
      getStatusSeverity,
      openApproveDialog,
      openRejectDialog,
      openDetailsDialog,
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
