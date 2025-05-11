<template>
  <div class="setup-exams">
    <h1>Configurare Examene</h1>
    
    <Card>
      <template #content>
        <p class="p-mb-4">
          <i class="pi pi-info-circle p-mr-2"></i>
          Configurați detaliile pentru examenele la disciplinele pe care le predați. Setările vor fi vizibile pentru studenți și secretariat.
        </p>
        
        <div v-if="loading" class="p-d-flex p-jc-center">
          <ProgressSpinner />
        </div>
        
        <div v-else-if="!courses.length" class="empty-state">
          <i class="pi pi-exclamation-circle"></i>
          <h3>Nu aveți discipline alocate</h3>
          <p>Nu sunt înregistrate discipline pentru dumneavoastră în semestrul curent. Contactați secretariatul pentru detalii.</p>
        </div>
        
        <div v-else>
          <DataTable 
            :value="courses" 
            v-model:expandedRows="expandedRows"
            dataKey="id"
            class="p-mb-4"
          >
            <Column expander style="width: 3rem" />
            <Column field="name" header="Disciplină" :sortable="true"></Column>
            <Column field="code" header="Cod" style="width: 8rem"></Column>
            <Column field="semester" header="Semestru" style="width: 8rem"></Column>
            <Column field="examDate" header="Data Examen" style="width: 12rem">
              <template #body="slotProps">
                <span v-if="slotProps.data.examDate">{{ formatDate(slotProps.data.examDate) }}</span>
                <span v-else class="status-badge warning">Neprogramat</span>
              </template>
            </Column>
            <Column field="examStatus" header="Status" style="width: 8rem">
              <template #body="slotProps">
                <Tag 
                  :value="slotProps.data.examStatus" 
                  :severity="getStatusSeverity(slotProps.data.examStatus)"
                />
              </template>
            </Column>
            
            <template #expansion="slotProps">
              <div class="p-p-3">
                <h3>Configurare Examen: {{ slotProps.data.name }}</h3>
                
                <div class="p-fluid p-formgrid p-grid">
                  <div class="p-field p-col-12 p-md-6">
                    <label for="examType">Tip Examen</label>
                    <Dropdown 
                      id="examType" 
                      v-model="slotProps.data.examConfig.examType" 
                      :options="examTypes" 
                      optionLabel="name"
                      optionValue="value"
                      placeholder="Selectați tipul de examen"
                      @change="saveExamConfig(slotProps.data)"
                    />
                  </div>
                  
                  <div class="p-field p-col-12 p-md-6">
                    <label for="duration">Durată (minute)</label>
                    <InputNumber 
                      id="duration" 
                      v-model="slotProps.data.examConfig.duration" 
                      :min="30" 
                      :max="240" 
                      :step="15"
                      suffix=" min"
                      @blur="saveExamConfig(slotProps.data)"
                    />
                  </div>
                  
                  <div class="p-field p-col-12">
                    <label for="materialsAllowed">Materiale Permise</label>
                    <MultiSelect 
                      id="materialsAllowed" 
                      v-model="slotProps.data.examConfig.materialsAllowed" 
                      :options="materialOptions" 
                      optionLabel="name"
                      optionValue="value"
                      placeholder="Selectați materialele permise"
                      display="chip"
                      @change="saveExamConfig(slotProps.data)"
                    />
                  </div>
                  
                  <div class="p-field p-col-12">
                    <label for="requirements">Cerințe Examen</label>
                    <Textarea 
                      id="requirements" 
                      v-model="slotProps.data.examConfig.requirements" 
                      rows="4" 
                      placeholder="Descrieți cerințele examenului"
                      @blur="saveExamConfig(slotProps.data)"
                    />
                  </div>
                  
                  <div class="p-field p-col-12">
                    <label>Structură Notă</label>
                    <div class="p-formgrid p-grid">
                      <div class="p-field p-col-12 p-md-4">
                        <label for="writtenWeight">Scris (%)</label>
                        <InputNumber 
                          id="writtenWeight" 
                          v-model="slotProps.data.examConfig.grading.writtenWeight" 
                          :min="0" 
                          :max="100" 
                          suffix=" %"
                          @blur="validateGradingWeights(slotProps.data)"
                        />
                      </div>
                      <div class="p-field p-col-12 p-md-4">
                        <label for="practicalWeight">Practic (%)</label>
                        <InputNumber 
                          id="practicalWeight" 
                          v-model="slotProps.data.examConfig.grading.practicalWeight" 
                          :min="0" 
                          :max="100" 
                          suffix=" %"
                          @blur="validateGradingWeights(slotProps.data)"
                        />
                      </div>
                      <div class="p-field p-col-12 p-md-4">
                        <label for="activityWeight">Activitate (%)</label>
                        <InputNumber 
                          id="activityWeight" 
                          v-model="slotProps.data.examConfig.grading.activityWeight" 
                          :min="0" 
                          :max="100" 
                          suffix=" %"
                          @blur="validateGradingWeights(slotProps.data)"
                        />
                      </div>
                    </div>
                    <small v-if="slotProps.data.examConfig.gradingError" class="p-error">{{ slotProps.data.examConfig.gradingError }}</small>
                  </div>
                  
                  <div class="p-field p-col-12">
                    <label for="passingScore">Nota minimă de promovare</label>
                    <Dropdown 
                      id="passingScore" 
                      v-model="slotProps.data.examConfig.passingScore" 
                      :options="passingScoreOptions" 
                      optionLabel="label"
                      optionValue="value"
                      @change="saveExamConfig(slotProps.data)"
                    />
                  </div>
                  
                  <div class="p-field-checkbox p-col-12">
                    <Checkbox 
                      id="notifyStudents" 
                      v-model="slotProps.data.examConfig.notifyStudents" 
                      :binary="true"
                      @change="saveExamConfig(slotProps.data)"
                    />
                    <label for="notifyStudents">Notifică studenții despre modificările configurației examenului</label>
                  </div>
                </div>
                
                <div class="p-d-flex p-jc-end p-mt-3">
                  <Button 
                    label="Salvare" 
                    icon="pi pi-check" 
                    @click="saveExamConfig(slotProps.data, true)"
                    :loading="slotProps.data.examConfig.saving"
                  />
                </div>
              </div>
            </template>
          </DataTable>
          
          <Divider />
          
          <h3>Examene Programate</h3>
          <DataTable 
            :value="scheduledExams" 
            class="p-mt-3"
            :rowHover="true"
            responsiveLayout="scroll"
            :paginator="true"
            :rows="5"
            paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
            :rowsPerPageOptions="[5, 10, 25]"
            emptyMessage="Nu aveți examene programate în sesiunea curentă"
          >
            <Column field="course.name" header="Disciplină" :sortable="true"></Column>
            <Column field="date" header="Data" :sortable="true">
              <template #body="slotProps">
                {{ formatDate(slotProps.data.date) }}
              </template>
            </Column>
            <Column field="timeRange" header="Ora" style="width: 10rem">
              <template #body="slotProps">
                {{ slotProps.data.startTime }} - {{ slotProps.data.endTime }}
              </template>
            </Column>
            <Column field="room" header="Sala" style="width: 8rem"></Column>
            <Column field="groups" header="Grupe">
              <template #body="slotProps">
                <div class="group-chips">
                  <Chip 
                    v-for="group in slotProps.data.groups" 
                    :key="group"
                    :label="group"
                    class="p-mr-1 p-mb-1"
                  />
                </div>
              </template>
            </Column>
            <Column header="Acțiuni" style="width: 8rem">
              <template #body="slotProps">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-rounded p-button-text p-button-info p-mr-2" 
                  @click="viewExamDetails(slotProps.data)"
                />
                <Button 
                  icon="pi pi-calendar-plus" 
                  class="p-button-rounded p-button-text p-button-success" 
                  @click="generateAttendanceSheet(slotProps.data)"
                />
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
    
    <!-- Exam Details Dialog -->
    <Dialog 
      v-model:visible="examDetailsDialog.visible" 
      :header="examDetailsDialog.title" 
      :style="{width: '500px'}" 
      :modal="true"
    >
      <div class="p-grid exam-details" v-if="examDetailsDialog.exam">
        <div class="p-col-4 detail-label">Disciplină:</div>
        <div class="p-col-8 detail-value">{{ examDetailsDialog.exam.course.name }}</div>
        
        <div class="p-col-4 detail-label">Data:</div>
        <div class="p-col-8 detail-value">{{ formatDate(examDetailsDialog.exam.date) }}</div>
        
        <div class="p-col-4 detail-label">Interval orar:</div>
        <div class="p-col-8 detail-value">{{ examDetailsDialog.exam.startTime }} - {{ examDetailsDialog.exam.endTime }}</div>
        
        <div class="p-col-4 detail-label">Sala:</div>
        <div class="p-col-8 detail-value">{{ examDetailsDialog.exam.room }}</div>
        
        <div class="p-col-4 detail-label">Grupe:</div>
        <div class="p-col-8 detail-value">
          <Chip 
            v-for="group in examDetailsDialog.exam.groups" 
            :key="group"
            :label="group"
            class="p-mr-1 p-mb-1"
          />
        </div>
        
        <div class="p-col-4 detail-label">Tip examen:</div>
        <div class="p-col-8 detail-value">{{ getExamTypeName(examDetailsDialog.exam.examType) }}</div>
        
        <div class="p-col-4 detail-label">Durată:</div>
        <div class="p-col-8 detail-value">{{ examDetailsDialog.exam.duration }} minute</div>
        
        <div class="p-col-12 p-mt-3" v-if="examDetailsDialog.exam.requirements">
          <div class="detail-label">Cerințe:</div>
          <div class="detail-value description">{{ examDetailsDialog.exam.requirements }}</div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Închide" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="examDetailsDialog.visible = false"
        />
        <Button 
          label="Editează Configurație" 
          icon="pi pi-cog" 
          @click="openConfigForCourse(examDetailsDialog.exam.course.id)"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'
import Dialog from 'primevue/dialog'
import Divider from 'primevue/divider'
import Tag from 'primevue/tag'
import Chip from 'primevue/chip'
import ProgressSpinner from 'primevue/progressspinner'
import ExamService from '@/services/exam.service'

export default {
  name: 'SetupExamsView',
  components: {
    Card,
    DataTable,
    Column,
    Button,
    Dropdown,
    MultiSelect,
    InputNumber,
    Textarea,
    Checkbox,
    Dialog,
    Divider,
    Tag,
    Chip,
    ProgressSpinner
  },
  setup() {
    const store = useStore()
    const loading = ref(true)
    const expandedRows = ref([])
    const courses = ref([])
    const scheduledExams = ref([])
    
    // Options for dropdowns
    const examTypes = ref([
      { name: 'Examen Scris', value: 'WRITTEN' },
      { name: 'Proiect', value: 'PROJECT' },
      { name: 'Examen Practic', value: 'PRACTICAL' },
      { name: 'Scris și Practic', value: 'WRITTEN_PRACTICAL' },
      { name: 'Colocviu', value: 'COLLOQUIUM' }
    ])
    
    const materialOptions = ref([
      { name: 'Niciun material', value: 'NONE' },
      { name: 'Documentație tipărită', value: 'PRINTED_DOCS' },
      { name: 'Carte/Manual', value: 'BOOK' },
      { name: 'Calculator', value: 'CALCULATOR' },
      { name: 'Dicționar', value: 'DICTIONARY' },
      { name: 'Tabele/Formule', value: 'FORMULAS' },
      { name: 'Notițe proprii', value: 'NOTES' }
    ])
    
    const passingScoreOptions = ref([
      { label: '5', value: 5 },
      { label: '5.5', value: 5.5 },
      { label: '6', value: 6 }
    ])
    
    // Exam details dialog
    const examDetailsDialog = reactive({
      visible: false,
      title: '',
      exam: null
    })
    
    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric',
        weekday: 'long'
      }).format(date)
    }
    
    // Get status severity
    const getStatusSeverity = (status) => {
      switch(status) {
        case 'CONFIGURED':
          return 'success'
        case 'PENDING':
          return 'warning'
        case 'NOT_CONFIGURED':
          return 'danger'
        default:
          return 'info'
      }
    }
    
    // Get exam type name
    const getExamTypeName = (typeValue) => {
      const type = examTypes.value.find(t => t.value === typeValue)
      return type ? type.name : typeValue
    }
    
    // Load courses
    const loadCourses = async () => {
      try {
        loading.value = true
        
        // In a real implementation, call the API
        // const response = await ExamService.getProfessorCourses()
        // courses.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 800))
        
        courses.value = [
          {
            id: 1,
            name: 'Programare Web',
            code: 'PW',
            semester: 2,
            examDate: new Date('2025-06-10'),
            examStatus: 'CONFIGURED',
            examConfig: {
              saving: false,
              examType: 'WRITTEN_PRACTICAL',
              duration: 180,
              materialsAllowed: ['PRINTED_DOCS', 'NOTES'],
              requirements: 'Studenții trebuie să rezolve un set de probleme teoretice și să implementeze o aplicație web simplă.',
              grading: {
                writtenWeight: 40,
                practicalWeight: 50,
                activityWeight: 10
              },
              gradingError: '',
              passingScore: 5,
              notifyStudents: true
            }
          },
          {
            id: 2,
            name: 'Baze de Date',
            code: 'BD',
            semester: 2,
            examDate: new Date('2025-06-15'),
            examStatus: 'PENDING',
            examConfig: {
              saving: false,
              examType: 'WRITTEN',
              duration: 120,
              materialsAllowed: ['FORMULAS'],
              requirements: 'Examen scris cu probleme de modelare, optimizare și normalizare baze de date.',
              grading: {
                writtenWeight: 70,
                practicalWeight: 20,
                activityWeight: 10
              },
              gradingError: '',
              passingScore: 5,
              notifyStudents: true
            }
          },
          {
            id: 3,
            name: 'Inteligență Artificială',
            code: 'IA',
            semester: 2,
            examDate: null,
            examStatus: 'NOT_CONFIGURED',
            examConfig: {
              saving: false,
              examType: 'PROJECT',
              duration: 0,
              materialsAllowed: [],
              requirements: '',
              grading: {
                writtenWeight: 0,
                practicalWeight: 80,
                activityWeight: 20
              },
              gradingError: '',
              passingScore: 5,
              notifyStudents: false
            }
          }
        ]
      } catch (error) {
        console.error('Error loading courses:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca disciplinele',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Load scheduled exams
    const loadScheduledExams = async () => {
      try {
        // In a real implementation, call the API
        // const response = await ExamService.getProfessorExams()
        // scheduledExams.value = response.data
        
        // For demo purposes, use mock data
        scheduledExams.value = [
          {
            id: 101,
            course: {
              id: 1,
              name: 'Programare Web',
              code: 'PW'
            },
            date: new Date('2025-06-10'),
            startTime: '10:00',
            endTime: '13:00',
            room: 'C2',
            groups: ['CTI2A', 'CTI2B'],
            examType: 'WRITTEN_PRACTICAL',
            duration: 180,
            requirements: 'Studenții trebuie să rezolve un set de probleme teoretice și să implementeze o aplicație web simplă.'
          },
          {
            id: 102,
            course: {
              id: 2,
              name: 'Baze de Date',
              code: 'BD'
            },
            date: new Date('2025-06-15'),
            startTime: '09:00',
            endTime: '11:00',
            room: 'C1',
            groups: ['CTI2A', 'CTI2B', 'IS2'],
            examType: 'WRITTEN',
            duration: 120,
            requirements: 'Examen scris cu probleme de modelare, optimizare și normalizare baze de date.'
          }
        ]
      } catch (error) {
        console.error('Error loading scheduled exams:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca examenele programate',
          life: 5000
        })
      }
    }
    
    // Validate grading weights
    const validateGradingWeights = (course) => {
      const { writtenWeight, practicalWeight, activityWeight } = course.examConfig.grading
      const total = writtenWeight + practicalWeight + activityWeight
      
      if (total !== 100) {
        course.examConfig.gradingError = `Totalul ponderilor trebuie să fie 100%. Actual: ${total}%`
        return false
      } else {
        course.examConfig.gradingError = ''
        saveExamConfig(course)
        return true
      }
    }
    
    // Save exam configuration
    const saveExamConfig = async (course, showNotification = false) => {
      if (course.examConfig.gradingError) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Validare',
          detail: 'Ponderea notelor trebuie să însumeze 100%',
          life: 3000
        })
        return
      }
      
      try {
        course.examConfig.saving = true
        
        // Create request data
        const configData = {
          courseId: course.id,
          examType: course.examConfig.examType,
          duration: course.examConfig.duration,
          materialsAllowed: course.examConfig.materialsAllowed,
          requirements: course.examConfig.requirements,
          grading: course.examConfig.grading,
          passingScore: course.examConfig.passingScore,
          notifyStudents: course.examConfig.notifyStudents
        }
        
        // In a real implementation, call the API
        // await ExamService.saveExamConfig(course.id, configData)
        
        // For demo purposes, simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Update status if previously not configured
        if (course.examStatus === 'NOT_CONFIGURED') {
          course.examStatus = 'CONFIGURED'
        }
        
        if (showNotification) {
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Configurație Salvată',
            detail: `Configurația examenului la ${course.name} a fost salvată cu succes`,
            life: 3000
          })
        }
      } catch (error) {
        console.error('Error saving exam config:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut salva configurația examenului',
          life: 5000
        })
      } finally {
        course.examConfig.saving = false
      }
    }
    
    // View exam details
    const viewExamDetails = (exam) => {
      examDetailsDialog.exam = exam
      examDetailsDialog.title = `Detalii Examen: ${exam.course.name}`
      examDetailsDialog.visible = true
    }
    
    // Open configuration for a specific course
    const openConfigForCourse = (courseId) => {
      // Close dialog
      examDetailsDialog.visible = false
      
      // Find course and expand it
      const course = courses.value.find(c => c.id === courseId)
      if (course) {
        expandedRows.value = [course]
      }
    }
    
    // Generate attendance sheet
    const generateAttendanceSheet = async (exam) => {
      try {
        // In a real implementation, call the API
        // const response = await ExamService.generateAttendanceSheet(exam.id)
        // window.open(response.data.url, '_blank')
        
        // For demo purposes, show notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Document Generat',
          detail: 'Fișa de prezență a fost generată și descărcată',
          life: 3000
        })
      } catch (error) {
        console.error('Error generating attendance sheet:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut genera fișa de prezență',
          life: 5000
        })
      }
    }
    
    // Initialize
    onMounted(() => {
      loadCourses()
      loadScheduledExams()
    })
    
    return {
      loading,
      courses,
      expandedRows,
      scheduledExams,
      examTypes,
      materialOptions,
      passingScoreOptions,
      examDetailsDialog,
      formatDate,
      getStatusSeverity,
      getExamTypeName,
      validateGradingWeights,
      saveExamConfig,
      viewExamDetails,
      openConfigForCourse,
      generateAttendanceSheet
    }
  }
}
</script>

<style lang="scss" scoped>
.setup-exams {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  h3 {
    color: #2c3e50;
    font-size: 1.25rem;
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  .empty-state {
    text-align: center;
    padding: 2rem;
    
    i {
      font-size: 3rem;
      color: #e0e0e0;
      margin-bottom: 1rem;
    }
    
    h3 {
      margin-bottom: 0.5rem;
    }
    
    p {
      color: #6c757d;
    }
  }
  
  .status-badge {
    background-color: #ffc107;
    color: #fff;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    font-size: 0.875rem;
    
    &.warning {
      background-color: #ffc107;
    }
  }
  
  .group-chips {
    display: flex;
    flex-wrap: wrap;
  }
  
  .exam-details {
    .detail-label {
      font-weight: 600;
      color: #495057;
    }
    
    .detail-value {
      color: #212529;
      
      &.description {
        white-space: pre-line;
        margin-top: 0.5rem;
        padding: 0.75rem;
        background-color: #f8f9fa;
        border-radius: 4px;
      }
    }
  }
  
  .p-error {
    color: #f44336;
    font-size: 0.875rem;
  }
}
</style>
