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
      :style="{width: '450px'}"
      :modal="true"
    >
      <div class="p-fluid">
        <div class="p-field p-mb-3">
          <label for="approveRoom">Sală</label>
          <Dropdown 
            id="approveRoom" 
            v-model="dialogs.approve.room" 
            :options="roomOptions" 
            optionLabel="name" 
            placeholder="Selectați sala"
            class="w-full"
          />
        </div>
        
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
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
    
    const roomOptions = ref([
      { name: 'C1', value: 'C1' },
      { name: 'C2', value: 'C2' },
      { name: 'C3', value: 'C3' },
      { name: 'C4', value: 'C4' },
      { name: 'A1', value: 'A1' },
      { name: 'A2', value: 'A2' },
      { name: 'SL1', value: 'SL1' },
      { name: 'SL2', value: 'SL2' }
    ])
    
    // Dialog states
    const dialogs = reactive({
      approve: {
        visible: false,
        proposal: null,
        room: null,
        comments: '',
        loading: false
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
    
    // Dialog actions
    const openApproveDialog = (proposal) => {
      dialogs.approve.proposal = proposal
      dialogs.approve.room = null
      dialogs.approve.comments = ''
      dialogs.approve.visible = true
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
      if (!dialogs.approve.room) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Selectați o sală pentru examen',
          life: 3000
        })
        return
      }
      
      try {
        dialogs.approve.loading = true
        
        // In a real implementation, we would call the API
        // await examService.approveProposal({
        //   proposalId: dialogs.approve.proposal.id,
        //   roomId: dialogs.approve.room.value,
        //   comments: dialogs.approve.comments || null
        // })
        
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Update local data
        const index = proposals.value.findIndex(p => p.id === dialogs.approve.proposal.id)
        if (index !== -1) {
          proposals.value[index] = {
            ...proposals.value[index],
            status: 'approved',
            reviewedBy: { name: 'Prof. Current User', email: 'current.user@example.com' },
            reviewDate: new Date().toISOString(),
            comments: dialogs.approve.comments || null,
            room: dialogs.approve.room
          }
        }
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere Aprobată',
          detail: 'Propunerea a fost aprobată cu succes',
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
          detail: 'Specificați motivul respingerii',
          life: 3000
        })
        return
      }
      
      try {
        dialogs.reject.loading = true
        
        // In a real implementation, we would call the API
        // await examService.rejectProposal({
        //   proposalId: dialogs.reject.proposal.id,
        //   reason: dialogs.reject.reason
        // })
        
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Update local data
        const index = proposals.value.findIndex(p => p.id === dialogs.reject.proposal.id)
        if (index !== -1) {
          proposals.value[index] = {
            ...proposals.value[index],
            status: 'rejected',
            reviewedBy: { name: 'Prof. Current User', email: 'current.user@example.com' },
            reviewDate: new Date().toISOString(),
            rejectionReason: dialogs.reject.reason
          }
        }
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Propunere Respinsă',
          detail: 'Propunerea a fost respinsă',
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
    
    // Load proposals
    const loadProposals = async () => {
      try {
        loading.value = true
        
        // In a real implementation, we would call the API
        // const response = await examService.getProposals()
        // proposals.value = response.data
        
        // For demo purposes, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        proposals.value = [
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
            id: 2,
            subject: { name: 'Rețele de Calculatoare', code: 'RC21' },
            group: { name: 'CTI3', program: 'Calculatoare și Tehnologia Informației', year: 3 },
            proposedDate: '2025-06-15',
            proposedTimeStart: '12:00',
            proposedTimeEnd: '14:00',
            status: 'approved',
            submittedBy: { name: 'Ionescu Maria', email: 'maria.ionescu@student.usv.ro' },
            submittedDate: '2025-05-06T10:15:00',
            reviewedBy: { name: 'Prof. Alexandru Gheorghe', email: 'alexandru.gheorghe@usv.ro' },
            reviewDate: '2025-05-07T09:30:00',
            comments: 'Sala C3 rezervată pentru examen.',
            rejectionReason: null
          },
          {
            id: 3,
            subject: { name: 'Inteligență Artificială', code: 'IA42' },
            group: { name: 'CTI4', program: 'Calculatoare și Tehnologia Informației', year: 4 },
            proposedDate: '2025-06-12',
            proposedTimeStart: '14:00',
            proposedTimeEnd: '16:00',
            status: 'rejected',
            submittedBy: { name: 'Georgescu Andrei', email: 'andrei.georgescu@student.usv.ro' },
            submittedDate: '2025-05-05T16:45:00',
            reviewedBy: { name: 'Prof. Mihaela Popescu', email: 'mihaela.popescu@usv.ro' },
            reviewDate: '2025-05-06T11:20:00',
            comments: null,
            rejectionReason: 'Data propusă se suprapune cu un alt examen. Vă rog să propuneți o altă dată.'
          }
        ]
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
    
    // Initialize
    onMounted(() => {
      loadProposals()
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
