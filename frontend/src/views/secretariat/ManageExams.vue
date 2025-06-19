<template>
  <div class="manage-exams">
    <h1>Gestionare Examene</h1>
    
    <Card class="exams-card">
      <template #content>
        <TabView>
          <TabPanel header="Lista Examene">
            <div class="p-d-flex p-jc-between p-ai-center p-mb-3">
              <h2>Lista examene programate</h2>
              <Button 
                label="Export Excel" 
                icon="pi pi-file-excel" 
                class="p-button-primary" 
                @click="generateExamExcel"
                :loading="generatingExcel"
                :disabled="generatingExcel"
              />
            </div>
            <DataTable 
              :value="exams" 
              :paginator="true" 
              :rows="10"
              :loading="loading"
              paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
              currentPageReportTemplate="Afișare {first} până la {last} din {totalRecords} examene"
              responsiveLayout="scroll"
              filterDisplay="menu"
              :rowHover="true"
              removableSort
              class="expanded-table"
              style="width: 100%; overflow-x: auto; min-width: 1000px;"
            >
              <template #empty>Nu există examene programate.</template>
              <template #loading>Se încarcă examenele, vă rugăm așteptați...</template>
              
              <Column field="subject" header="Disciplină" :sortable="true" filterField="subject">
                <template #body="slotProps">
                  <span>{{ slotProps.data.subject.name }}</span>
                </template>
                <template #filter="{ filterModel, filterCallback }">
                  <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Căutare..." class="p-column-filter" />
                </template>
              </Column>
              
              <Column field="date" header="Data" :sortable="true">
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.date) }}
                </template>
              </Column>
              
              <Column field="startTime" header="Ora" :sortable="true">
                <template #body="slotProps">
                  {{ slotProps.data.startTime }} ({{ slotProps.data.duration }} ore)
                </template>
              </Column>
              
              <Column field="roomNames" header="Săli" :sortable="true">
                <template #body="slotProps">
                  <div v-if="Array.isArray(slotProps.data.roomNames) && slotProps.data.roomNames.length > 0">
                    {{ slotProps.data.roomNames.join(', ') }}
                  </div>
                  <div v-else-if="slotProps.data.room && slotProps.data.room.name">
                    {{ slotProps.data.room.name }}
                  </div>
                  <div v-else>-</div>
                </template>
              </Column>
              
              <Column field="professor.name" header="Profesor" :sortable="true">
                <template #body="slotProps">
                  {{ slotProps.data.professor.name }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                  <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Căutare..." class="p-column-filter" />
                </template>
              </Column>
              
              <!-- Assistants column removed as requested -->
              
              <!-- Program studiu column removed as requested -->
              
              <Column field="studyYear" header="An" :sortable="true">
                <template #body="slotProps">
                  {{ slotProps.data.studyYear }}
                </template>
              </Column>
              
              <Column field="groupNames" header="Grupe" :sortable="true">
                <template #body="slotProps">
                  <div class="groups-chips">
                    <Chip 
                      v-for="group in slotProps.data.groups" 
                      :key="group.id" 
                      :label="group.name" 
                      class="p-mr-1 p-mb-1"
                    />
                  </div>
                </template>
              </Column>
              
              <Column field="status" header="Status" :sortable="true">
                <template #body="slotProps">
                  <Tag :severity="getStatusSeverity(slotProps.data?.status)">
                    {{ getStatusLabel(slotProps.data?.status) }}
                  </Tag>
                </template>
              </Column>
              
              <Column header="Acțiuni" style="min-width:12rem">
                <template #body="slotProps">
                  <div class="action-buttons">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-rounded p-button-success p-button-sm" 
                      @click="editExam(slotProps.data)"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-rounded p-button-danger p-button-sm" 
                      @click="confirmDelete(slotProps.data)"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </TabPanel>
          
          <TabPanel header="Lista Sali">
            <div class="room-list">
              <div class="p-d-flex p-jc-between p-ai-center p-mb-3">
                <h2>Lista săli disponibile</h2>
                <Button 
                  label="Export Excel" 
                  icon="pi pi-file-excel" 
                  class="p-button-primary" 
                  @click="generateRoomExcel"
                  :loading="generatingRoomExcel"
                  :disabled="generatingRoomExcel"
                />
              </div>
              
              <DataTable 
                :value="rooms" 
                :paginator="true" 
                :rows="10"
                :loading="loadingRooms"
                paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                currentPageReportTemplate="Afișare {first} până la {last} din {totalRecords} săli"
                responsiveLayout="scroll"
                filterDisplay="menu"
                :rowHover="true"
                removableSort
              >
                <template #empty>Nu există săli înregistrate.</template>
                <template #loading>Se încarcă sălile, vă rugăm așteptați...</template>
                
                <Column field="name" header="Nume" :sortable="true">
                  <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Căutare..." class="p-column-filter" />
                  </template>
                </Column>
                
                <Column field="shortName" header="Nume scurt" :sortable="true">
                </Column>
                
                <Column field="buildingName" header="Clădire" :sortable="true">
                  <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" @input="filterCallback()" placeholder="Căutare..." class="p-column-filter" />
                  </template>
                </Column>
                
                <Column field="capacity" header="Capacitate" :sortable="true">
                  <template #body="slotProps">
                    {{ slotProps.data.capacity }} locuri
                  </template>
                </Column>
                
                <Column field="computers" header="Calculatoare" :sortable="true">
                  <template #body="slotProps">
                    {{ slotProps.data.computers }} buc
                  </template>
                </Column>
                
                <Column header="Acțiuni" style="min-width:12rem">
                  <template #body="slotProps">
                    <div class="action-buttons">
                      <Button 
                        icon="pi pi-search" 
                        class="p-button-rounded p-button-info p-button-sm" 
                        @click="viewRoom(slotProps.data)"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </TabPanel>
          
          <!-- Creare Examen tab removed as requested -->
        </TabView>
      </template>
    </Card>
    
    <!-- Edit Exam Dialog -->
    <Dialog 
      v-model:visible="editDialog.visible" 
      :header="'Editare Examen'" 
      :style="{width: '650px'}"
      :modal="true"
      :closable="!editDialog.loading"
      :closeOnEscape="!editDialog.loading"
    >
      <div v-if="editDialog.exam" class="p-fluid">
        <div class="p-formgrid p-grid">
          <div class="p-field p-col-12 p-md-6">
            <label for="edit-subject">Disciplina</label>
            <InputText id="edit-subject" v-model="editDialog.exam.subject.name" disabled />
          </div>
          
          <div class="p-field p-col-12 p-md-6">
            <label for="edit-groups">Grupe <span class="required-field">*</span></label>
            <MultiSelect 
              id="edit-groups" 
              v-model="editDialog.exam.groups" 
              :options="groupOptions" 
              optionLabel="name"
              display="chip"
              :disabled="editDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-12 p-md-4">
            <label for="edit-date">Data <span class="required-field">*</span></label>
            <Calendar 
              id="edit-date" 
              v-model="editDialog.exam.date" 
              dateFormat="dd/mm/yy"
              :showIcon="true"
              :disabled="editDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-12 p-md-4">
            <label for="edit-startTime">Ora de începere <span class="required-field">*</span></label>
            <Dropdown 
              id="edit-startTime" 
              v-model="editDialog.exam.startTime" 
              :options="timeOptions" 
              optionLabel="label"
              optionValue="value"
              :disabled="editDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-12 p-md-4">
            <label for="edit-duration">Durata (ore) <span class="required-field">*</span></label>
            <Dropdown 
              id="edit-duration" 
              v-model="editDialog.exam.duration" 
              :options="durationOptions" 
              optionLabel="label"
              optionValue="value"
              :disabled="editDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-12 p-md-6">
            <label for="edit-room">Sălile <span class="required-field">*</span></label>
            <Dropdown 
              id="edit-room" 
              v-model="editDialog.exam.room" 
              :options="roomOptions" 
              optionLabel="name"
              optionValue="id"
              :disabled="editDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-12 p-md-6">
            <label for="edit-professor">Cadru Didactic <span class="required-field">*</span></label>
            <Dropdown 
              id="edit-professor" 
              v-model="editDialog.exam.professor" 
              :options="professorOptions" 
              optionLabel="name"
              optionValue="id"
              :disabled="editDialog.loading"
            />
          </div>
          
          <div class="p-field p-col-12 p-md-6">
            <label for="edit-status">Status</label>
            <Dropdown 
              id="edit-status" 
              v-model="editDialog.exam.status" 
              :options="statusOptions" 
              optionLabel="label"
              optionValue="value"
              :disabled="editDialog.loading"
            />
          </div>
          
          <!-- Mesaj de la Cadrul Didactic section removed as requested -->
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="cancelEdit"
          :disabled="editDialog.loading"
        />
        <Button 
          label="Salvare" 
          icon="pi pi-check" 
          @click="updateExam"
          :loading="editDialog.loading"
        />
      </template>
    </Dialog>
    
    <!-- Room Details Dialog -->
    <Dialog 
      v-model:visible="viewRoomDialog.visible" 
      :style="{width: '450px'}" 
      header="Detalii Sală" 
      :modal="true"
      :closable="true"
    >
      <div class="p-grid p-fluid" v-if="viewRoomDialog.room">
        <div class="p-field p-col-12">
          <label>Nume</label>
          <div>{{ viewRoomDialog.room.name }}</div>
        </div>
        <div class="p-field p-col-12">
          <label>Nume scurt</label>
          <div>{{ viewRoomDialog.room.shortName }}</div>
        </div>
        <div class="p-field p-col-12">
          <label>Clădire</label>
          <div>{{ viewRoomDialog.room.buildingName }}</div>
        </div>
        <div class="p-field p-col-12">
          <label>Capacitate</label>
          <div>{{ viewRoomDialog.room.capacity }} locuri</div>
        </div>
        <div class="p-field p-col-12">
          <label>Calculatoare</label>
          <div>{{ viewRoomDialog.room.computers }} buc</div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Închide" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="viewRoomDialog.visible = false"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import { useConfirm } from 'primevue/useconfirm'
import examService from '@/services/exam.service'
import roomService from '@/services/room.service'
import teacherService from '@/services/teacher.service'
import subjectService from '@/services/subject.service'
import groupService from '@/services/group.service'
import Card from 'primevue/card'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Calendar from 'primevue/calendar'
import Textarea from 'primevue/textarea'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import Chip from 'primevue/chip'
import ConfirmDialog from 'primevue/confirmdialog'

export default {
  name: 'ManageExamsView',
  components: {
    Card,
    TabView,
    TabPanel,
    DataTable,
    Column,
    Button,
    InputText,
    Dropdown,
    MultiSelect,
    Calendar,
    Dialog,
    Tag,
    Chip,
    ConfirmDialog
  },
  setup() {
    const store = useStore()
    const confirm = useConfirm()
    
    // Loading states
    const loading = ref(false)
    const generatingExcel = ref(false)
    const loadingRooms = ref(false)
    const generatingRoomExcel = ref(false)
    
    // Data lists
    const exams = ref([])
    const rooms = ref([])
    
    // Room dialog
    const selectedRoom = ref(null)
    const viewRoomDialog = reactive({
      visible: false,
      room: null
    })
    
    // Submitted flag for validation
    const submitted = ref(false)
    
    // Exam form data
    const examForm = reactive({
      subject: null,
      groups: [],
      date: null,
      startTime: null,
      duration: null,
      room: null,
      professor: null,
      notes: ''
    })
    
    // Edit dialog state
    const editDialog = reactive({
      visible: false,
      loading: false,
      exam: null
    })
    
    // Mock data for dropdowns
    const subjectOptions = ref([
      { id: 1, name: 'Programare Web', code: 'PW' },
      { id: 2, name: 'Algoritmi și Structuri de Date', code: 'ASD' },
      { id: 3, name: 'Programare Orientată pe Obiecte', code: 'POO' },
      { id: 4, name: 'Inteligență Artificială', code: 'IA' },
      { id: 5, name: 'Baze de Date', code: 'BD' }
    ])
    
    const groupOptions = ref([
      { id: 1, name: 'CTI1A' },
      { id: 2, name: 'CTI1B' },
      { id: 3, name: 'CTI2A' },
      { id: 4, name: 'CTI2B' },
      { id: 5, name: 'CTI3A' },
      { id: 6, name: 'CTI3B' },
      { id: 7, name: 'IS1' },
      { id: 8, name: 'IS2' },
      { id: 9, name: 'IS3' }
    ])
    
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
      { label: '17:00', value: '17:00' }
    ])
    
    const durationOptions = ref([
      { label: '1 oră', value: 1 },
      { label: '2 ore', value: 2 },
      { label: '3 ore', value: 3 },
      { label: '4 ore', value: 4 }
    ])
    
    const statusOptions = ref([
      { label: 'Programat', value: 'approved' },
      { label: 'Propus', value: 'proposed' },
      { label: 'În așteptare', value: 'pending' },
      { label: 'Anulat/Respins', value: 'rejected' }
    ])
    
    const roomOptions = ref([
      { id: 1, name: 'C1', capacity: 120 },
      { id: 2, name: 'C2', capacity: 150 },
      { id: 3, name: 'C3', capacity: 80 },
      { id: 4, name: 'C4', capacity: 100 },
      { id: 5, name: 'A1', capacity: 30 },
      { id: 6, name: 'A2', capacity: 25 },
      { id: 7, name: 'SL1', capacity: 20 },
      { id: 8, name: 'SL2', capacity: 20 }
    ])
    
    const professorOptions = ref([
      { id: 1, name: 'Prof. Dr. Ionescu Maria' },
      { id: 2, name: 'Prof. Dr. Popescu Ion' },
      { id: 3, name: 'Prof. Dr. Vasilescu Ana' },
      { id: 4, name: 'Conf. Dr. Georgescu Radu' },
      { id: 5, name: 'Conf. Dr. Dumitrescu Elena' }
    ])
    
    // Format a date as DD MMMM YYYY in Romanian
    const formatDate = (dateString) => {
      if (!dateString) return ''
      // If dateString is exactly 'Nesetat', return it directly
      if (dateString === 'Nesetat') return 'Nesetat'
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric' 
      }).format(date)
    }
    
    // Calculate end time based on start time and duration
    const calculateEndTime = (startTime, duration) => {
      if (!startTime || !duration) return ''
      
      const [hours, minutes] = startTime.split(':').map(Number)
      const endHours = hours + duration
      
      return `${endHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
    }
    
    // Get status severity class based on status
    const getStatusSeverity = (status) => {
      const normalizedStatus = status?.toLowerCase() || '';
      
      switch(normalizedStatus) {
        case 'approved':
          return 'success'
        case 'proposed':
          return 'warning'
        case 'pending':
          return 'info'
        case 'rejected':
          return 'danger'
        default:
          return 'secondary'
      }
    }
    
    // Get status label in Romanian (for display purposes)
    const getStatusLabel = (status) => {
      const normalizedStatus = status?.toLowerCase() || '';
      
      switch(normalizedStatus) {
        case 'approved':
          return 'Programat'
        case 'proposed':
          return 'Propus'
        case 'pending':
          return 'În așteptare'
        case 'rejected':
          return 'Respins/Anulat'
        default:
          return status || 'Necunoscut'
      }
    }
    
    // Reset form
    const resetForm = () => {
      submitted.value = false
      examForm.subject = null
      examForm.groups = []
      examForm.date = null
      examForm.startTime = null
      examForm.duration = null
      examForm.room = null
      examForm.professor = null
      examForm.notes = ''
    }
    
    // Save exam
    const saveExam = async () => {
      submitted.value = true
      
      // Validate form
      if (!examForm.subject || !examForm.groups.length || !examForm.date || 
          !examForm.startTime || !examForm.duration || !examForm.room || !examForm.professor) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Completați toate câmpurile obligatorii',
          life: 3000
        })
        return
      }
      
      try {
        loading.value = true
        
        // Create exam object
        const exam = {
          subject: examForm.subject,
          groups: examForm.groups,
          date: examForm.date,
          startTime: examForm.startTime,
          duration: examForm.duration,
          room: roomOptions.value.find(r => r.id === examForm.room),
          professor: professorOptions.value.find(p => p.id === examForm.professor),
          notes: examForm.notes,
          status: 'SCHEDULED'
        }
        
        // In a real implementation, call the API
        // await examService.createExam(exam)
        
        // For demo purposes, add to local list
        exam.id = Date.now()
        exams.value.unshift(exam)
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Examen Creat',
          detail: 'Examenul a fost programat cu succes',
          life: 3000
        })
        
        // Reset form
        resetForm()
      } catch (error) {
        console.error('Error creating exam:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la programarea examenului',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Load rooms data
    const loadRooms = async () => {
      try {
        loadingRooms.value = true
        
        // Call the API to get real room data from the backend
        const response = await roomService.getAllRooms()
        
        // Set the rooms data
        rooms.value = response
        
        // Update roomOptions from the real data
        roomOptions.value = response.map(room => ({
          id: room.id,
          name: room.name,
          capacity: room.capacity || 0
        }))
        
        console.log('Loaded rooms:', roomOptions.value);
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Săli încărcate',
          detail: `${rooms.value.length} săli au fost încărcate cu succes`,
          life: 3000
        })
      } catch (error) {
        console.error('Error loading rooms:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la încărcarea sălilor',
          life: 5000
        })
      } finally {
        loadingRooms.value = false
      }
    }

    // Generate Excel file with room information
    const generateRoomExcel = async () => {
      try {
        generatingRoomExcel.value = true
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Generare Excel',
          detail: 'Se generează lista de săli cu informații complete...',
          life: 3000
        })

        // Call the API to generate the Excel file
        const response = await roomService.generateRoomExcel()
        
        // Create a blob from the response
        const blob = new Blob([response.data], { 
          type: response.headers['content-type'] || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        
        // Create download link
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Get filename from content-disposition or use default
        const contentDisposition = response.headers ? response.headers['content-disposition'] : null
        let filename = 'lista_sali.xlsx'
        
        if (contentDisposition) {
          // Extract filename from the Content-Disposition header
          // eslint-disable-next-line no-useless-escape
          const filenameRegex = /filename[^;=\\n]*=((['\"]).*?\\2|[^;\\n]*)/
          const matches = filenameRegex.exec(contentDisposition)
          if (matches && matches[1]) {
            // eslint-disable-next-line no-useless-escape
            filename = matches[1].replace(/['\"]/g, '')
          }
        }
        
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        
        // Clean up
        window.URL.revokeObjectURL(url)
        document.body.removeChild(link)
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Excel Generat',
          detail: 'Lista de săli a fost generată și descărcată cu succes',
          life: 3000
        })
      } catch (error) {
        console.error('Error generating room Excel:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la generarea Excel-ului',
          life: 5000
        })
      } finally {
        generatingRoomExcel.value = false
      }
    }

    // View room details
    const viewRoom = (room) => {
      viewRoomDialog.room = {...room}
      viewRoomDialog.visible = true
    }

    // Generate Excel file with exam information for all groups
    const generateExamExcel = async () => {
      try {
        generatingExcel.value = true
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Generare Excel',
          detail: 'Se generează lista de examene cu informații despre cadre didactice...',
          life: 3000
        })

        // Call the API to generate the Excel file
        const response = await examService.generateExamExcel()
        
        // Create a blob from the response
        const blob = new Blob([response.data], { 
          type: response.headers['content-type'] || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        
        // Create download link
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // Get filename from content-disposition or use default
        const contentDisposition = response.headers ? response.headers['content-disposition'] : null
        let filename = 'lista_examene.xlsx'
        
        if (contentDisposition) {
          const filenameRegex = /filename[^;=\n]*=((['"]).??\2|[^;\n]*)/
          const matches = filenameRegex.exec(contentDisposition)
          if (matches && matches[1]) {
            filename = matches[1].replace(/['"]*/g, '')
          }
        }
        
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Excel Generat',
          detail: 'Lista de examene a fost generată cu succes.',
          life: 3000
        })
        
        // Refresh the exams list to show any updated information
        loadExams()
      } catch (error) {
        console.error('Error generating Excel:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Generare',
          detail: error.message || 'A apărut o eroare la generarea listei de examene.',
          life: 5000
        })
      } finally {
        generatingExcel.value = false
      }
    }

    // Edit exam
    const editExam = (exam) => {
      console.log('Original exam data:', exam);
      
      // Convert date string to Date object if needed
      let examDate;
      if (exam.date) {
        examDate = typeof exam.date === 'string' ? new Date(exam.date) : exam.date;
      }
      
      // Process startTime to ensure correct format
      let startTime;
      if (exam.startTime) {
        // First check if it's a full object with value property
        if (typeof exam.startTime === 'object' && exam.startTime !== null && exam.startTime.value) {
          startTime = exam.startTime;
        } 
        // If it's already a dropdown option object
        else if (typeof exam.startTime === 'object' && exam.startTime !== null && ('label' in exam.startTime)) {
          startTime = exam.startTime;
        }
        // Then check if it's a string and find matching option
        else if (typeof exam.startTime === 'string') {
          console.log('Finding time option for:', exam.startTime);
          console.log('Available time options:', timeOptions.value);
          // First try exact match on value
          let timeOption = timeOptions.value.find(t => t.value === exam.startTime);
          // Then try exact match on label
          if (!timeOption) {
            timeOption = timeOptions.value.find(t => t.label === exam.startTime);
          }
          // Then try partial match
          if (!timeOption) {
            timeOption = timeOptions.value.find(t => t.value.includes(exam.startTime) || exam.startTime.includes(t.value));
          }
          startTime = timeOption || timeOptions.value[0];
        } 
        // Fallback
        else {
          startTime = timeOptions.value[0];
        }
      } else {
        startTime = timeOptions.value[0];
      }
      console.log('Selected startTime:', startTime);
      
      // Make proper room object
      let roomObject;
      console.log('Finding room match. Room data:', exam.room);
      console.log('Available roomOptions:', roomOptions.value);
      
      // First try to use roomNames if available
      if (exam.roomNames && Array.isArray(exam.roomNames) && exam.roomNames.length > 0) {
        // Get the first room name and try to find a matching room
        const primaryRoomName = exam.roomNames[0];
        roomObject = roomOptions.value.find(r => r.name === primaryRoomName);
      }
      
      // If not found by roomNames, try the room object
      if (!roomObject && typeof exam.room === 'object' && exam.room !== null) {
        // Try to find by id first
        if (exam.room.id) {
          roomObject = roomOptions.value.find(r => r.id === exam.room.id);
        }
        // Then try by name
        if (!roomObject && exam.room.name) {
          roomObject = roomOptions.value.find(r => r.name === exam.room.name);
        }
        // If not found, use the original object
        if (!roomObject) {
          roomObject = exam.room;
        }
      } 
      // Try by room ID if available
      if (!roomObject && exam.roomId) {
        roomObject = roomOptions.value.find(r => r.id === exam.roomId);
      }
      // Try by room name if no ID
      if (!roomObject && exam.roomName) {
        roomObject = roomOptions.value.find(r => r.name === exam.roomName);
      }
      
      // If still no match found, use the first available room
      if (!roomObject && roomOptions.value && roomOptions.value.length > 0) {
        roomObject = roomOptions.value[0];
      }
      
      console.log('Selected roomObject:', roomObject);
      
      // Make proper professor object
      let professorObject;
      console.log('Finding professor match. Professor data:', exam.professor);
      console.log('Available professorOptions:', professorOptions.value);
      
      if (typeof exam.professor === 'object' && exam.professor !== null) {
        // Try to find by id first
        if (exam.professor.id) {
          professorObject = professorOptions.value.find(p => p.id === exam.professor.id);
        }
        // Then try by name
        if (!professorObject && exam.professor.name) {
          professorObject = professorOptions.value.find(p => p.name === exam.professor.name);
        }
        // If not found, use the original object
        if (!professorObject) {
          professorObject = exam.professor;
        }
      }
      // Try by teacher ID if available 
      if (!professorObject && exam.teacherId) {
        professorObject = professorOptions.value.find(p => p.id === exam.teacherId);
      }
      // Try by teacher name if no ID
      if (!professorObject && exam.teacherName) {
        professorObject = professorOptions.value.find(p => p.name === exam.teacherName);
      }
      
      // If still no match found, use the first available professor
      if (!professorObject && professorOptions.value && professorOptions.value.length > 0) {
        professorObject = professorOptions.value[0];
      }
      
      console.log('Selected professorObject:', professorObject);
      
      // Make proper groups array
      let groupsArray = [];
      if (Array.isArray(exam.groups) && exam.groups.length > 0) {
        // Map existing groups to ensure they're in the right format and filter out any invalid entries
        groupsArray = exam.groups
          .filter(group => group && (group.id || group.name))
          .map(group => {
            // Try to find a matching group in options
            const matchingGroup = groupOptions.value.find(g => g.id === group.id || g.name === group.name);
            return matchingGroup || group;
          });
      } else if (exam.groupId) {
        const group = groupOptions.value.find(g => g.id === exam.groupId) || 
          { id: exam.groupId, name: exam.groupName || 'Nedefinită' };
        groupsArray = [group];
      }
      
      // Make proper subject object
      let subjectObject;
      if (typeof exam.subject === 'object' && exam.subject !== null && exam.subject.id) {
        subjectObject = subjectOptions.value.find(s => s.id === exam.subject.id) || exam.subject;
      } else if (exam.subjectId) {
        subjectObject = subjectOptions.value.find(s => s.id === exam.subjectId) || 
          { id: exam.subjectId, name: exam.subjectName || 'Nedefinit' };
      } else {
        subjectObject = null;
      }
      
      // Set duration - convert to number if needed
      let duration;
      if (typeof exam.duration === 'number') {
        duration = exam.duration;
      } else if (typeof exam.duration === 'string') {
        duration = parseInt(exam.duration, 10);
      } else {
        duration = durationOptions.value[0].value;
      }
      
      // Ensure status is in the standardized English format
      let statusValue;
      if (exam.status) {
        // If status is already a dropdown option object
        if (typeof exam.status === 'object' && exam.status !== null && exam.status.value) {
          statusValue = exam.status.value;
        } else {
          // Try to normalize string status
          const normalizedStatus = typeof exam.status === 'string' ? exam.status.toLowerCase() : 'pending';
          
          if (normalizedStatus.includes('approved') || normalizedStatus.includes('scheduled') || normalizedStatus.includes('programat')) {
            statusValue = 'approved';
          } else if (normalizedStatus.includes('pending') || normalizedStatus.includes('asteptare')) {
            statusValue = 'pending';
          } else if (normalizedStatus.includes('rejected') || normalizedStatus.includes('canceled') || normalizedStatus.includes('anulat') || normalizedStatus.includes('respins')) {
            statusValue = 'rejected';
          } else if (normalizedStatus.includes('proposed') || normalizedStatus.includes('propus')) {
            statusValue = 'proposed';
          } else {
            // Default to pending if status is unknown
            statusValue = 'pending';
          }
        }
      } else {
        statusValue = 'pending';
      }
      
      // Find the matching status option
      const statusOption = statusOptions.value.find(s => s.value === statusValue);
      console.log('Selected status:', statusValue, 'Matched option:', statusOption);
      
      // Create complete exam object for edit dialog
      editDialog.exam = { 
        ...exam,
        date: examDate,
        startTime: startTime,
        duration: duration,
        room: roomObject,
        professor: professorObject,
        groups: groupsArray,
        subject: subjectObject,
        status: statusValue,
        notes: exam.notes || ''
      };
      
      console.log('Edit dialog populated with:', editDialog.exam);
      
      console.log('Processed exam data for edit:', editDialog.exam);
      editDialog.visible = true;
    }
    
    // Cancel edit
    const cancelEdit = () => {
      editDialog.visible = false
      editDialog.exam = null
    }
    
    // Update exam
    const updateExam = async () => {
      // Validate form
      if (!editDialog.exam.groups.length || !editDialog.exam.date || 
          !editDialog.exam.startTime || !editDialog.exam.duration || 
          !editDialog.exam.room || !editDialog.exam.professor) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Completați toate câmpurile obligatorii',
          life: 3000
        })
        return
      }
      
      try {
        editDialog.loading = true

        // Calculate end time if not present
        const endTime = editDialog.exam.endTime || calculateEndTime(editDialog.exam.startTime, editDialog.exam.duration);

        // Prepare data for API
        const updateData = {
          date: editDialog.exam.date,
          startTime: editDialog.exam.startTime,
          endTime: endTime,
          roomId: editDialog.exam.room.id,
          teacherId: editDialog.exam.professor.id,
          groups: editDialog.exam.groups.map(g => g.id),
          status: editDialog.exam.status || 'proposed',
          notes: editDialog.exam.notes
        }
        
        console.log('Sending update data to API:', updateData);
        
        // Call the backend API
        const response = await examService.updateExam(editDialog.exam.id, updateData)
        
        // Update local list with the updated exam
        const index = exams.value.findIndex(e => e.id === editDialog.exam.id)
        if (index !== -1) {
          exams.value[index] = { ...editDialog.exam }
        }
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Examen Actualizat',
          detail: 'Examenul a fost actualizat cu succes',
          life: 3000
        })
        
        // Close dialog
        editDialog.visible = false
        editDialog.exam = null
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
    
    // Confirm delete exam
    const confirmDeleteExam = (exam) => {
      confirm.require({
        header: 'Confirmare ștergere',
        message: `Sunteți sigur că doriți să ștergeți examenul la ${exam.subject.name}?`,
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Da',
        rejectLabel: 'Nu',
        accept: () => deleteExam(exam)
      })
    }
    
    // Delete exam
    const deleteExam = async (exam) => {
      try {
        loading.value = true
        
        // In a real implementation, call the API
        // await examService.deleteExam(exam.id)
        
        // For demo purposes, remove from local list
        exams.value = exams.value.filter(e => e.id !== exam.id)
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Examen Șters',
          detail: 'Examenul a fost șters cu succes',
          life: 3000
        })
      } catch (error) {
        console.error('Error deleting exam:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la ștergerea examenului',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Load exams from the backend API
    const loadExams = async () => {
      try {
        loading.value = true
        
        // Call the API to get real exam data from the backend
        const response = await examService.getAllExams()
        
        // Process the data to match our component's expected structure
        exams.value = response.map(exam => {
          // Find matching subject object or create one
          let subject = subjectOptions.value.find(s => s.id === exam.subjectId) || {
            id: exam.subjectId,
            name: exam.subjectName,
            shortName: exam.subjectShortName || exam.subjectName.substring(0, 3)
          }
          
          // Find matching room object or create one
          let room = exam.roomId == null ? {
            id: null,
            name: 'Nesetat',
            capacity: 0,
            building: ''
          } : roomOptions.value.find(r => r.id === exam.roomId) || {
            id: exam.roomId,
            name: exam.roomName || `Room ${exam.roomId}`,
            capacity: exam.roomCapacity || 0,
            building: exam.building || 'Main Building'
          }
          
          // Create professor object from the data
          let professor = professorOptions.value.find(p => p.id === exam.teacherId) || {
            id: exam.teacherId,
            name: exam.teacherName,
            email: exam.teacherEmail || '',
            phone: exam.teacherPhone || 'N/A'
          }
          
          // For groups, we'll need to find the corresponding group in groupOptions
          // In a real scenario, we'd have a separate API call to get all groups for this exam
          // For now, we'll use the groupId and groupName from the exam data
          let group = groupOptions.value.find(g => g.id === exam.groupId) || {
            id: exam.groupId,
            name: exam.groupName,
            studyProgram: exam.specializationShortName || '',
            studyYear: exam.studyYear || 1
          }
          
          // Parse date string to Date object if needed, or set to "Nesetat" if null
          let examDate = exam.date == null ? "Nesetat" : (typeof exam.date === 'string' ? new Date(exam.date) : exam.date)
          
          // Format start time with proper null checking
          let startTime = exam.startTime == null ? 
                "Nesetat" : 
                (typeof exam.startTime === 'string' ? 
                  exam.startTime : 
                  `${exam.startTime?.hour?.toString().padStart(2, '0') || '00'}:${exam.startTime?.minute?.toString().padStart(2, '0') || '00'}`)
          
          // Process room names from API if available
          const roomNames = [];
          if (exam.roomNames && Array.isArray(exam.roomNames) && exam.roomNames.length > 0) {
            roomNames.push(...exam.roomNames);
          } else if (room && room.name && room.name !== 'Nesetat') {
            roomNames.push(room.name);
          }

          // Prepare a formatted exam object with all needed properties
          const formattedExam = {
            id: exam.id,
            subject: subject,
            // For simplicity, we're currently showing only the primary group
            // In a full implementation, you'd fetch all groups for this exam
            groups: [group],
            date: examDate,
            startTime: startTime,
            duration: exam.duration,
            room: room,
            roomNames: roomNames,
            professor: professor,
            notes: exam.notes || '',
            status: exam.status || 'Nepregătit',
            // Additional fields from Excel export
            studyProgram: exam.specializationShortName,
            studyYear: exam.studyYear,
            // Assistant-related properties
            assistantsLoaded: false,
            loadingAssistants: false,
            assistantNames: [],
            assistantIds: exam.assistantIds || []
          };
          
          // Create groupNames field for proper sorting
          formattedExam.groupNames = '';
          if (formattedExam.groups && Array.isArray(formattedExam.groups)) {
            const groupNames = formattedExam.groups.map(g => g.name).filter(name => !!name);
            if (groupNames.length > 0) {
              formattedExam.groupNames = groupNames.join(', ');
            }
          } else if (exam.groupName) {
            formattedExam.groupNames = exam.groupName;
          }
          
          return formattedExam
        })
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Examene încărcate',
          detail: `${exams.value.length} examene au fost încărcate cu succes`,
          life: 3000
        })
      } catch (error) {
        console.error('Error loading exams:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca examenele',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Load professors data
    const loadProfessors = async () => {
      try {
        // Call the API to get real professor data from the backend (Users with role 'CD')
        const response = await teacherService.getAllTeachers()
        
        // Update professorOptions from the real data
        professorOptions.value = response.map(professor => ({
          id: professor.id,
          // Teachers are users with firstName and lastName
          name: `${professor.firstName || ''} ${professor.lastName || ''}`.trim()
        })).filter(p => p.name) // Filter out any with empty names
        
        console.log('Loaded professors:', professorOptions.value);
      } catch (error) {
        console.error('Error loading professors:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca cadre didactice',
          life: 5000
        })
      }
    }
    
    // Load subjects data
    const loadSubjects = async () => {
      try {
        // Call the API to get real subject data from the backend
        const response = await subjectService.getAllSubjects()
        
        // Update subjectOptions from the real data
        subjectOptions.value = response.map(subject => ({
          id: subject.id,
          name: subject.name,
          code: subject.code || ''
        }))
        
        console.log('Loaded subjects:', subjectOptions.value);
      } catch (error) {
        console.error('Error loading subjects:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca disciplinele',
          life: 5000
        })
      }
    }
    
    // Load assistants for a specific exam
    const loadExamAssistants = async (exam) => {
      if (!exam || exam.assistantsLoaded || exam.loadingAssistants) return;
      
      exam.loadingAssistants = true;
      try {
        // Call the API to get assistants for this exam
        const response = await examService.getExamAssistants(exam.id);
        
        // Parse assistant names
        if (response && Array.isArray(response.data)) {
          exam.assistantNames = response.data.map(assistant => 
            assistant.name || `${assistant.firstName || ''} ${assistant.lastName || ''}`.trim()
          ).filter(name => name);
        } else if (exam.assistantIds && Array.isArray(exam.assistantIds)) {
          // Fallback if the API call doesn't work as expected
          exam.assistantNames = exam.assistantIds.map(id => {
            const assistant = professorOptions.value.find(p => p.id === id);
            return assistant ? assistant.name : `Assistant ${id}`;
          });
        } else {
          exam.assistantNames = [];
        }
        
        exam.assistantsLoaded = true;
      } catch (error) {
        console.error(`Error loading assistants for exam ${exam.id}:`, error);
        exam.assistantNames = [];
      } finally {
        exam.loadingAssistants = false;
      }
    };
    
    // Load groups data
    const loadGroups = async () => {
      try {
        // Call the API to get real group data from the backend
        const response = await groupService.getAllGroups()
        
        // Update groupOptions from the real data
        groupOptions.value = response.map(group => ({
          id: group.id,
          name: group.name,
          studyProgram: group.studyProgram || group.specializationShortName,
          studyYear: group.studyYear || 1
        }))
        
        console.log('Loaded groups:', groupOptions.value);
      } catch (error) {
        console.error('Error loading groups:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca grupele',
          life: 5000
        })
      }
    }
    
    // Initialize
    onMounted(() => {
      loadExams()
      loadRooms()
      loadProfessors()
      loadSubjects()
      loadGroups()
    })
    
    return {
      loading,
      generatingExcel,
      submitted,
      examForm,
      subjectOptions,
      groupOptions,
      timeOptions,
      durationOptions,
      statusOptions,
      roomOptions,
      professorOptions,
      exams,
      editDialog,
      generateExamExcel,
      formatDate,
      calculateEndTime,
      getStatusSeverity,
      getStatusLabel,
      resetForm,
      saveExam,
      editExam,
      cancelEdit,
      updateExam,
      confirmDeleteExam,
      loadExamAssistants,
      rooms,
      loadingRooms,
      generatingRoomExcel,
      loadRooms,
      generateRoomExcel,
      viewRoom,
      viewRoomDialog
    }
  }
}
</script>

<style lang="scss" scoped>
.manage-exams {
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
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e9ecef;
  }
  
  .create-exam-form {
    padding: 1rem 0;
  }
  
  .required-field {
    color: #f44336;
  }
  
  .groups-chips {
    display: flex;
    flex-wrap: wrap;
  }
  
  :deep(.p-tabview-panels) {
    padding: 1.5rem 0 0 0;
  }
  
  :deep(.expanded-table) {
    min-width: 100%;
    overflow-x: auto;
  }
  
  .action-buttons {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
  }
}

.actions-column {
  min-width: 12rem;
  text-align: center;
}

.action-icons {
  display: flex;
  justify-content: space-around;
}

.expanded-table {
  margin: 0 -1rem; /* Negative margin to expand beyond the card padding */
  width: calc(100% + 2rem) !important;
}

.exams-card {
  width: 98%;
  max-width: 1600px;
  margin: 0 auto;
}
</style>