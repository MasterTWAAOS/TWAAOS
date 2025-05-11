<template>
  <div class="exam-calendar">
    <div class="calendar-options p-mb-3">
      <div class="p-grid">
        <div class="p-col-12 p-md-4">
          <div class="p-field">
            <label for="calendarView">Vizualizare</label>
            <Dropdown
              id="calendarView"
              v-model="calendarView"
              :options="viewOptions"
              optionLabel="name"
              optionValue="value"
              placeholder="Selectați vizualizarea"
              class="w-full"
            />
          </div>
        </div>
        <div class="p-col-12 p-md-4">
          <div class="p-field">
            <label for="groupFilter">Grupă (opțional)</label>
            <Dropdown
              id="groupFilter"
              v-model="groupFilter"
              :options="groupOptions"
              optionLabel="name"
              placeholder="Toate grupele"
              class="w-full"
            />
          </div>
        </div>
        <div class="p-col-12 p-md-4">
          <div class="p-field">
            <label for="roomFilter">Sală (opțional)</label>
            <Dropdown
              id="roomFilter"
              v-model="roomFilter"
              :options="roomOptions"
              optionLabel="name"
              placeholder="Toate sălile"
              class="w-full"
            />
          </div>
        </div>
      </div>
      <div class="p-d-flex p-jc-end p-mt-2">
        <Button
          icon="pi pi-download"
          label="Export Calendar"
          class="p-button-outlined p-button-sm"
          @click="exportCalendar"
        />
      </div>
    </div>
    
    <div class="calendar-container">
      <div v-if="loading" class="loading-container">
        <ProgressSpinner />
      </div>
      <FullCalendar 
        v-else
        ref="fullCalendar"
        :options="calendarOptions" 
      />
    </div>
    
    <!-- Event Details Dialog -->
    <Dialog 
      v-model:visible="eventDetails.visible" 
      :header="eventDetails.title" 
      :style="{width: '500px'}"
      :modal="true"
    >
      <div class="event-details" v-if="eventDetails.event">
        <div class="p-grid">
          <div class="p-col-4 detail-label">Disciplină:</div>
          <div class="p-col-8 detail-value">{{ eventDetails.event.title }}</div>
          
          <div class="p-col-4 detail-label">Data:</div>
          <div class="p-col-8 detail-value">{{ formatDate(eventDetails.event.start) }}</div>
          
          <div class="p-col-4 detail-label">Ora:</div>
          <div class="p-col-8 detail-value">{{ formatTime(eventDetails.event.start) }} - {{ formatTime(eventDetails.event.end) }}</div>
          
          <div class="p-col-4 detail-label">Grupă:</div>
          <div class="p-col-8 detail-value">
            <Chip 
              v-for="group in eventDetails.event.extendedProps.groups" 
              :key="group" 
              :label="group" 
              class="p-mr-1"
            />
          </div>
          
          <div class="p-col-4 detail-label">Sală:</div>
          <div class="p-col-8 detail-value">{{ eventDetails.event.extendedProps.room }}</div>
          
          <div class="p-col-4 detail-label">Cadru didactic:</div>
          <div class="p-col-8 detail-value">{{ eventDetails.event.extendedProps.professor }}</div>
          
          <div class="p-col-12 p-mt-3" v-if="eventDetails.event.extendedProps.description">
            <div class="detail-label">Detalii:</div>
            <div class="detail-value description">{{ eventDetails.event.extendedProps.description }}</div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Închide" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="eventDetails.visible = false"
        />
        <Button 
          v-if="userCanEdit"
          label="Editează" 
          icon="pi pi-pencil" 
          class="p-button-outlined" 
          @click="editEvent"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Chip from 'primevue/chip'
import ProgressSpinner from 'primevue/progressspinner'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import roLocale from '@fullcalendar/core/locales/ro'
import examService from '@/services/exam.service'

export default {
  name: 'ExamCalendar',
  components: {
    Dropdown,
    Button,
    Dialog,
    Chip,
    ProgressSpinner,
    FullCalendar
  },
  props: {
    userRole: {
      type: String,
      default: 'STUDENT'
    },
    presetGroup: {
      type: String,
      default: null
    },
    presetView: {
      type: String,
      default: 'dayGridMonth'
    },
    height: {
      type: String,
      default: '650px'
    }
  },
  emits: ['event-edit'],
  setup(props, { emit }) {
    const store = useStore()
    const fullCalendar = ref(null)
    
    // Calendar state
    const calendarView = ref(props.presetView)
    const groupFilter = ref(props.presetGroup ? { name: props.presetGroup, value: props.presetGroup } : null)
    const roomFilter = ref(null)
    const loading = ref(false)
    const events = ref([])
    
    // Event details dialog
    const eventDetails = reactive({
      visible: false,
      event: null,
      title: ''
    })
    
    // Calendar options
    const viewOptions = ref([
      { name: 'Lună', value: 'dayGridMonth' },
      { name: 'Săptămână', value: 'timeGridWeek' },
      { name: 'Zi', value: 'timeGridDay' }
    ])
    
    // Filter options
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
    
    // Calendar options with reactive data
    const calendarOptions = computed(() => ({
      plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
      initialView: calendarView.value,
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      events: filteredEvents.value,
      eventClick: handleEventClick,
      height: props.height,
      locale: roLocale,
      firstDay: 1, // Monday
      allDaySlot: false,
      slotMinTime: '08:00:00',
      slotMaxTime: '20:00:00',
      slotDuration: '00:30:00',
      eventTimeFormat: {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      },
      businessHours: {
        daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
        startTime: '08:00',
        endTime: '20:00'
      }
    }))
    
    // Filtered events based on selections
    const filteredEvents = computed(() => {
      return events.value.filter(event => {
        // Filter by group
        if (groupFilter.value && !event.extendedProps.groups.includes(groupFilter.value.value)) {
          return false
        }
        
        // Filter by room
        if (roomFilter.value && event.extendedProps.room !== roomFilter.value.value) {
          return false
        }
        
        return true
      })
    })
    
    // Check if user can edit events
    const userCanEdit = computed(() => {
      return ['ADMIN', 'SECRETARIAT', 'PROFESSOR'].includes(props.userRole)
    })
    
    // Format functions
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric'
      }).format(date)
    }
    
    const formatTime = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return new Intl.DateTimeFormat('ro-RO', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
      }).format(date)
    }
    
    // Event handlers
    const handleEventClick = (info) => {
      eventDetails.event = info.event
      eventDetails.title = info.event.title
      eventDetails.visible = true
    }
    
    const editEvent = () => {
      eventDetails.visible = false
      emit('event-edit', eventDetails.event)
    }
    
    // Export calendar
    const exportCalendar = () => {
      try {
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Export Calendar',
          detail: 'Se generează fișierul de export...',
          life: 3000
        })
        
        // In a real implementation, this would call an API to generate and download a .ics file
        // For now, we'll just show a success notification
        setTimeout(() => {
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Export Completat',
            detail: 'Calendarul a fost exportat cu succes.',
            life: 3000
          })
        }, 1500)
      } catch (error) {
        console.error('Error exporting calendar:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Export',
          detail: 'A apărut o eroare la exportul calendarului.',
          life: 5000
        })
      }
    }
    
    // Load events
    const loadEvents = async () => {
      try {
        loading.value = true
        
        // In a real implementation, we would call the API
        // const response = await examService.getExamsForCalendar()
        // events.value = response.data
        
        // For demo purposes, we'll use mock data
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Mock exam period from June 5th to June 25th, 2025
        const examPeriodStart = new Date(2025, 5, 5) // June 5, 2025
        
        events.value = [
          {
            id: 1,
            title: 'Programare Orientată pe Obiecte',
            start: new Date(2025, 5, 10, 9, 0), // June 10, 2025, 9:00 AM
            end: new Date(2025, 5, 10, 11, 0),  // June 10, 2025, 11:00 AM
            backgroundColor: '#4CAF50',
            borderColor: '#4CAF50',
            extendedProps: {
              groups: ['CTI2'],
              room: 'C2',
              professor: 'Prof. Dr. Popescu Ion',
              status: 'approved',
              description: 'Examen final la disciplina Programare Orientată pe Obiecte'
            }
          },
          {
            id: 2,
            title: 'Rețele de Calculatoare',
            start: new Date(2025, 5, 15, 12, 0), // June 15, 2025, 12:00 PM
            end: new Date(2025, 5, 15, 14, 0),  // June 15, 2025, 2:00 PM
            backgroundColor: '#4CAF50',
            borderColor: '#4CAF50',
            extendedProps: {
              groups: ['CTI3'],
              room: 'C3',
              professor: 'Prof. Dr. Georgescu Alexandru',
              status: 'approved',
              description: 'Examen final la disciplina Rețele de Calculatoare'
            }
          },
          {
            id: 3,
            title: 'Inteligență Artificială',
            start: new Date(2025, 5, 12, 14, 0), // June 12, 2025, 2:00 PM
            end: new Date(2025, 5, 12, 16, 0),  // June 12, 2025, 4:00 PM
            backgroundColor: '#F44336',
            borderColor: '#F44336',
            extendedProps: {
              groups: ['CTI4'],
              room: 'A2',
              professor: 'Prof. Dr. Mihaela Popescu',
              status: 'rejected',
              description: 'Examen final la disciplina Inteligență Artificială'
            }
          },
          {
            id: 4,
            title: 'Baze de Date',
            start: new Date(2025, 5, 18, 10, 0), // June 18, 2025, 10:00 AM
            end: new Date(2025, 5, 18, 12, 0),  // June 18, 2025, 12:00 PM
            backgroundColor: '#FFC107',
            borderColor: '#FFC107',
            extendedProps: {
              groups: ['AITC2'],
              room: 'SL1',
              professor: 'Prof. Dr. Dumitrescu Elena',
              status: 'pending',
              description: 'Examen final la disciplina Baze de Date'
            }
          },
          {
            id: 5,
            title: 'Metode Numerice',
            start: new Date(2025, 5, 20, 9, 0), // June 20, 2025, 9:00 AM
            end: new Date(2025, 5, 20, 11, 0),  // June 20, 2025, 11:00 AM
            backgroundColor: '#4CAF50',
            borderColor: '#4CAF50',
            extendedProps: {
              groups: ['CTI2', 'AITC2'],
              room: 'C1',
              professor: 'Prof. Dr. Stanescu Maria',
              status: 'approved',
              description: 'Examen final la disciplina Metode Numerice'
            }
          }
        ]
      } catch (error) {
        console.error('Error loading events:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Încărcare',
          detail: 'Nu s-au putut încărca evenimentele pentru calendar.',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Watch for filter changes to update calendar
    watch([calendarView, groupFilter, roomFilter], () => {
      if (fullCalendar.value) {
        const calendarApi = fullCalendar.value.getApi()
        calendarApi.changeView(calendarView.value)
      }
    })
    
    // Initialize
    onMounted(() => {
      loadEvents()
    })
    
    return {
      calendarView,
      groupFilter,
      roomFilter,
      loading,
      events,
      eventDetails,
      viewOptions,
      groupOptions,
      roomOptions,
      calendarOptions,
      filteredEvents,
      userCanEdit,
      fullCalendar,
      formatDate,
      formatTime,
      handleEventClick,
      editEvent,
      exportCalendar
    }
  }
}
</script>

<style lang="scss" scoped>
.exam-calendar {
  .calendar-options {
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
  
  .calendar-container {
    background-color: #fff;
    border-radius: 4px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
    
    .loading-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 400px;
    }
  }
  
  :deep(.fc) {
    .fc-toolbar-title {
      text-transform: capitalize;
    }
    
    .fc-event {
      cursor: pointer;
    }
  }
  
  .event-details {
    .detail-label {
      font-weight: 500;
      color: #6c757d;
    }
    
    .detail-value {
      color: #2c3e50;
      
      &.description {
        margin-top: 0.5rem;
        white-space: pre-line;
      }
    }
  }
}
</style>
