<template>
  <div class="manage-exams">
    <h1>Gestionare Examene</h1>
    
    <Card>
      <template #content>
        <TabView>
          <TabPanel header="Creare Examen">
            <div class="create-exam-form">
              <h2>Adăugare Examen Nou</h2>
              
              <div class="p-fluid p-formgrid p-grid">
                <div class="p-field p-col-12 p-md-6">
                  <label for="subject">Disciplina <span class="required-field">*</span></label>
                  <Dropdown 
                    id="subject" 
                    v-model="examForm.subject" 
                    :options="subjectOptions" 
                    optionLabel="name"
                    placeholder="Selectați disciplina"
                    :class="{'p-invalid': submitted && !examForm.subject}"
                  />
                  <small class="p-error" v-if="submitted && !examForm.subject">Disciplina este obligatorie</small>
                </div>
                
                <div class="p-field p-col-12 p-md-6">
                  <label for="groups">Grupe <span class="required-field">*</span></label>
                  <MultiSelect 
                    id="groups" 
                    v-model="examForm.groups" 
                    :options="groupOptions" 
                    optionLabel="name"
                    placeholder="Selectați grupele"
                    display="chip"
                    :class="{'p-invalid': submitted && !examForm.groups.length}"
                  />
                  <small class="p-error" v-if="submitted && !examForm.groups.length">Cel puțin o grupă este obligatorie</small>
                </div>
                
                <div class="p-field p-col-12 p-md-4">
                  <label for="date">Data <span class="required-field">*</span></label>
                  <Calendar 
                    id="date" 
                    v-model="examForm.date" 
                    dateFormat="dd/mm/yy"
                    :showIcon="true"
                    placeholder="Selectați data"
                    :class="{'p-invalid': submitted && !examForm.date}"
                  />
                  <small class="p-error" v-if="submitted && !examForm.date">Data este obligatorie</small>
                </div>
                
                <div class="p-field p-col-12 p-md-4">
                  <label for="startTime">Ora de începere <span class="required-field">*</span></label>
                  <Dropdown 
                    id="startTime" 
                    v-model="examForm.startTime" 
                    :options="timeOptions" 
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Selectați ora"
                    :class="{'p-invalid': submitted && !examForm.startTime}"
                  />
                  <small class="p-error" v-if="submitted && !examForm.startTime">Ora de începere este obligatorie</small>
                </div>
                
                <div class="p-field p-col-12 p-md-4">
                  <label for="duration">Durata (ore) <span class="required-field">*</span></label>
                  <Dropdown 
                    id="duration" 
                    v-model="examForm.duration" 
                    :options="durationOptions" 
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Selectați durata"
                    :class="{'p-invalid': submitted && !examForm.duration}"
                  />
                  <small class="p-error" v-if="submitted && !examForm.duration">Durata este obligatorie</small>
                </div>
                
                <div class="p-field p-col-12 p-md-6">
                  <label for="room">Sala <span class="required-field">*</span></label>
                  <Dropdown 
                    id="room" 
                    v-model="examForm.room" 
                    :options="roomOptions" 
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Selectați sala"
                    :class="{'p-invalid': submitted && !examForm.room}"
                  />
                  <small class="p-error" v-if="submitted && !examForm.room">Sala este obligatorie</small>
                </div>
                
                <div class="p-field p-col-12 p-md-6">
                  <label for="professor">Cadru Didactic <span class="required-field">*</span></label>
                  <Dropdown 
                    id="professor" 
                    v-model="examForm.professor" 
                    :options="professorOptions" 
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Selectați cadrul didactic"
                    :class="{'p-invalid': submitted && !examForm.professor}"
                  />
                  <small class="p-error" v-if="submitted && !examForm.professor">Cadrul didactic este obligatoriu</small>
                </div>
                
                <div class="p-field p-col-12">
                  <label for="notes">Observații</label>
                  <Textarea 
                    id="notes" 
                    v-model="examForm.notes" 
                    rows="3" 
                    placeholder="Adăugați detalii sau observații despre examen"
                  />
                </div>
                
                <div class="p-col-12">
                  <div class="p-d-flex p-jc-end">
                    <Button 
                      label="Resetare" 
                      icon="pi pi-undo" 
                      class="p-button-text p-mr-2" 
                      @click="resetForm"
                      :disabled="loading"
                    />
                    <Button 
                      label="Salvare" 
                      icon="pi pi-save" 
                      @click="saveExam"
                      :loading="loading"
                    />
                  </div>
                </div>
              </div>
            </div>
          </TabPanel>
          
          <TabPanel header="Lista Examene">
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
              
              <Column field="time" header="Ora" :sortable="true">
                <template #body="slotProps">
                  {{ slotProps.data.startTime }} - {{ calculateEndTime(slotProps.data.startTime, slotProps.data.duration) }}
                </template>
              </Column>
              
              <Column field="room" header="Sala" :sortable="true">
                <template #body="slotProps">
                  {{ slotProps.data.room.name }}
                </template>
              </Column>
              
              <Column field="groups" header="Grupe">
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
              
              <Column field="status" header="Status" :sortable="true" style="width: 12%">
                <template #body="slotProps">
                  <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)" />
                </template>
              </Column>
              
              <Column header="Acțiuni" style="width: 10%">
                <template #body="slotProps">
                  <Button 
                    icon="pi pi-pencil" 
                    class="p-button-rounded p-button-success p-mr-1" 
                    @click="editExam(slotProps.data)"
                  />
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-rounded p-button-danger" 
                    @click="confirmDeleteExam(slotProps.data)"
                  />
                </template>
              </Column>
            </DataTable>
          </TabPanel>
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
            <label for="edit-room">Sala <span class="required-field">*</span></label>
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
          
          <div class="p-field p-col-12">
            <label for="edit-notes">Observații</label>
            <Textarea 
              id="edit-notes" 
              v-model="editDialog.exam.notes" 
              rows="3"
              :disabled="editDialog.loading"
            />
          </div>
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
    
    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useConfirm } from 'primevue/useconfirm'
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
    Textarea,
    Dialog,
    Tag,
    Chip,
    ConfirmDialog
  },
  setup() {
    const store = useStore()
    const confirm = useConfirm()
    
    // Loading state
    const loading = ref(false)
    
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
    
    // Exams list
    const exams = ref([])
    
    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return ''
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
    
    // Get severity class for status tag
    const getStatusSeverity = (status) => {
      switch(status) {
        case 'SCHEDULED':
          return 'success'
        case 'PENDING':
          return 'warning'
        case 'CANCELED':
          return 'danger'
        default:
          return 'info'
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
    
    // Edit exam
    const editExam = (exam) => {
      editDialog.exam = { ...exam }
      editDialog.visible = true
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
        
        // In a real implementation, call the API
        // await examService.updateExam(editDialog.exam.id, editDialog.exam)
        
        // For demo purposes, update local list
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
    
    // Load exams
    const loadExams = async () => {
      try {
        loading.value = true
        
        // In a real implementation, call the API
        // const response = await examService.getExams()
        // exams.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        exams.value = [
          {
            id: 1,
            subject: subjectOptions.value[0],
            groups: [groupOptions.value[0], groupOptions.value[1]],
            date: new Date(2025, 5, 10),
            startTime: '10:00',
            duration: 2,
            room: roomOptions.value[0],
            professor: professorOptions.value[0],
            notes: 'Examen scris + aplicație practică',
            status: 'SCHEDULED'
          },
          {
            id: 2,
            subject: subjectOptions.value[1],
            groups: [groupOptions.value[2], groupOptions.value[3]],
            date: new Date(2025, 5, 12),
            startTime: '09:00',
            duration: 3,
            room: roomOptions.value[1],
            professor: professorOptions.value[1],
            notes: 'Examen scris',
            status: 'SCHEDULED'
          },
          {
            id: 3,
            subject: subjectOptions.value[2],
            groups: [groupOptions.value[4], groupOptions.value[5]],
            date: new Date(2025, 5, 15),
            startTime: '14:00',
            duration: 2,
            room: roomOptions.value[2],
            professor: professorOptions.value[2],
            notes: '',
            status: 'PENDING'
          }
        ]
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
    
    // Initialize
    onMounted(() => {
      loadExams()
    })
    
    return {
      loading,
      submitted,
      examForm,
      subjectOptions,
      groupOptions,
      timeOptions,
      durationOptions,
      roomOptions,
      professorOptions,
      exams,
      editDialog,
      formatDate,
      calculateEndTime,
      getStatusSeverity,
      resetForm,
      saveExam,
      editExam,
      cancelEdit,
      updateExam,
      confirmDeleteExam
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
}
</style>
