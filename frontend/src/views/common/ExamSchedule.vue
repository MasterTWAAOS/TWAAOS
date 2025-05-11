<template>
  <div class="exam-schedule">
    <h1>Calendar Examene</h1>
    
    <Card>
      <template #content>
        <p class="schedule-info">
          <i class="pi pi-info-circle"></i>
          Vizualizați programarea examenelor pentru sesiunea {{ currentSessionName }}. 
          Filtrați examenele după grupă sau sală și exportați calendarul în format iCalendar (.ics) pentru a-l importa în 
          Google Calendar, Microsoft Outlook sau Apple Calendar.
        </p>
        
        <ExamCalendar 
          :userRole="userRole" 
          :presetGroup="userGroup" 
          ref="examCalendar"
          @event-edit="openEditDialog"
        />
      </template>
    </Card>
    
    <!-- Edit Exam Dialog (shown only for Admin, Secretariat, and Professor roles) -->
    <Dialog 
      v-model:visible="editDialog.visible" 
      :header="'Editare Examen: ' + (editDialog.exam?.title || '')" 
      :style="{width: '600px'}"
      :modal="true"
      v-if="canEditExams"
    >
      <div class="p-fluid" v-if="editDialog.exam">
        <div class="p-field p-mb-3">
          <label for="examDate">Data Examen <span class="required-field">*</span></label>
          <Calendar 
            id="examDate" 
            v-model="editDialog.date" 
            dateFormat="dd/mm/yy"
            :showIcon="true"
            :minDate="examPeriod.startDate"
            :maxDate="examPeriod.endDate"
            class="w-full"
            :disabled="editDialog.loading"
          />
          <small class="helper-text">
            Perioada de examinare: {{ formatDate(examPeriod.startDate) }} - {{ formatDate(examPeriod.endDate) }}
          </small>
        </div>
        
        <div class="p-formgrid p-grid">
          <div class="p-field p-col-6">
            <label for="startTime">Ora începere <span class="required-field">*</span></label>
            <Dropdown 
              id="startTime" 
              v-model="editDialog.startTime" 
              :options="timeOptions" 
              optionLabel="label"
              optionValue="value"
              placeholder="Selectați ora"
              class="w-full"
              :disabled="editDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-6">
            <label for="endTime">Ora terminare <span class="required-field">*</span></label>
            <Dropdown 
              id="endTime" 
              v-model="editDialog.endTime" 
              :options="timeOptions" 
              optionLabel="label"
              optionValue="value"
              placeholder="Selectați ora"
              class="w-full"
              :disabled="editDialog.loading || !editDialog.startTime"
            />
          </div>
        </div>
        
        <div class="p-field p-mb-3">
          <label for="examRoom">Sală <span class="required-field">*</span></label>
          <Dropdown 
            id="examRoom" 
            v-model="editDialog.room" 
            :options="roomOptions" 
            optionLabel="name"
            optionValue="value"
            placeholder="Selectați sala"
            class="w-full"
            :disabled="editDialog.loading"
          />
        </div>
        
        <div class="p-field">
          <label for="examNotes">Notițe (opțional)</label>
          <Textarea 
            id="examNotes" 
            v-model="editDialog.notes" 
            rows="3" 
            placeholder="Adăugați notițe sau informații suplimentare"
            :disabled="editDialog.loading"
          />
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="editDialog.visible = false"
          :disabled="editDialog.loading"
        />
        <Button 
          label="Salvare" 
          icon="pi pi-check" 
          class="p-button-primary" 
          @click="saveExamChanges"
          :loading="editDialog.loading"
          :disabled="!isEditFormValid"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import ExamCalendar from '@/components/exams/ExamCalendar.vue'
import examService from '@/services/exam.service'

export default {
  name: 'ExamScheduleView',
  components: {
    Card,
    Dialog,
    Calendar,
    Dropdown,
    Textarea,
    Button,
    ExamCalendar
  },
  setup() {
    const store = useStore()
    const examCalendar = ref(null)
    
    // User information from store
    const userRole = computed(() => store.getters['auth/userRole'])
    const userGroup = computed(() => {
      // Only show group filter preset for student role, with their assigned group
      if (userRole.value === 'STUDENT') {
        return store.getters['auth/userGroup']
      }
      return null
    })
    
    // Check if user can edit exams
    const canEditExams = computed(() => {
      return ['ADMIN', 'SECRETARIAT', 'PROFESSOR'].includes(userRole.value)
    })
    
    // Current session info (could come from an API)
    const currentSessionName = ref('Vară 2025')
    
    // Exam period date range (could come from an API)
    const examPeriod = reactive({
      startDate: new Date(2025, 5, 5), // June 5, 2025
      endDate: new Date(2025, 5, 25)   // June 25, 2025
    })
    
    // Time options
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
      { label: '18:00', value: '18:00' }
    ])
    
    // Room options
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
    
    // Edit dialog state
    const editDialog = reactive({
      visible: false,
      exam: null,
      date: null,
      startTime: '',
      endTime: '',
      room: '',
      notes: '',
      loading: false
    })
    
    // Check if edit form is valid
    const isEditFormValid = computed(() => {
      return (
        editDialog.date && 
        editDialog.startTime && 
        editDialog.endTime && 
        editDialog.startTime < editDialog.endTime &&
        editDialog.room
      )
    })
    
    // Format date
    const formatDate = (dateObj) => {
      if (!dateObj) return ''
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric' 
      }).format(dateObj)
    }
    
    // Open edit dialog
    const openEditDialog = (event) => {
      if (!canEditExams.value) return
      
      editDialog.exam = event
      editDialog.date = new Date(event.start)
      
      // Extract time from date object
      const startHours = event.start.getHours().toString().padStart(2, '0')
      const startMinutes = event.start.getMinutes().toString().padStart(2, '0')
      editDialog.startTime = `${startHours}:${startMinutes}`
      
      const endHours = event.end.getHours().toString().padStart(2, '0')
      const endMinutes = event.end.getMinutes().toString().padStart(2, '0')
      editDialog.endTime = `${endHours}:${endMinutes}`
      
      editDialog.room = event.extendedProps.room
      editDialog.notes = event.extendedProps.description || ''
      editDialog.visible = true
    }
    
    // Save exam changes
    const saveExamChanges = async () => {
      if (!isEditFormValid.value) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Completați toate câmpurile obligatorii și asigurați-vă că ora de început este înainte de ora de sfârșit',
          life: 3000
        })
        return
      }
      
      try {
        editDialog.loading = true
        
        // Create date objects for start and end times
        const [startHour, startMinute] = editDialog.startTime.split(':').map(Number)
        const [endHour, endMinute] = editDialog.endTime.split(':').map(Number)
        
        const startDate = new Date(editDialog.date)
        startDate.setHours(startHour, startMinute, 0)
        
        const endDate = new Date(editDialog.date)
        endDate.setHours(endHour, endMinute, 0)
        
        // In a real implementation, call the API to update the exam
        // await examService.updateExam({
        //   examId: editDialog.exam.id,
        //   startDate: startDate.toISOString(),
        //   endDate: endDate.toISOString(),
        //   room: editDialog.room,
        //   description: editDialog.notes
        // })
        
        // For demo purposes, simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Examen Actualizat',
          detail: 'Examenul a fost actualizat cu succes',
          life: 3000
        })
        
        // Refresh calendar
        if (examCalendar.value) {
          await examCalendar.value.loadEvents()
        }
        
        // Close dialog
        editDialog.visible = false
      } catch (error) {
        console.error('Error updating exam:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la actualizarea examenului',
          life: 5000
        })
      } finally {
        editDialog.loading = false
      }
    }
    
    return {
      examCalendar,
      userRole,
      userGroup,
      canEditExams,
      currentSessionName,
      examPeriod,
      timeOptions,
      roomOptions,
      editDialog,
      isEditFormValid,
      formatDate,
      openEditDialog,
      saveExamChanges
    }
  }
}
</script>

<style lang="scss" scoped>
.exam-schedule {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  .schedule-info {
    display: flex;
    align-items: flex-start;
    padding: 0.75rem;
    margin-bottom: 1.5rem;
    background-color: #e3f2fd;
    border-radius: 4px;
    
    i {
      font-size: 1.25rem;
      color: #1E88E5;
      margin-right: 0.75rem;
      margin-top: 0.1rem;
    }
  }
  
  .required-field {
    color: #f44336;
  }
  
  .helper-text {
    display: block;
    color: #6c757d;
    margin-top: 0.25rem;
  }
  
  .w-full {
    width: 100%;
  }
}
</style>
