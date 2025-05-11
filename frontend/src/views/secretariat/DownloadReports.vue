<template>
  <div class="download-reports">
    <h1>Rapoarte Examene</h1>
    
    <Card>
      <template #content>
        <p class="report-info p-mb-4">
          <i class="pi pi-info-circle"></i>
          Generați și descărcați diverse rapoarte despre sesiunea de examene. Rapoartele pot fi exportate în 
          formatele PDF, XLSX sau CSV în funcție de tipul raportului.
        </p>
        
        <div class="p-grid p-m-0">
          <!-- Report Cards -->
          <div class="p-col-12 p-md-6 p-lg-4 p-mb-3">
            <Card class="report-card">
              <template #header>
                <div class="report-icon">
                  <i class="pi pi-calendar"></i>
                </div>
              </template>
              <template #title>
                Programare Examene
              </template>
              <template #content>
                <p>Raport complet cu toate examenele programate în sesiunea curentă, organizate pe zile și săli.</p>
                <div class="p-mt-3">
                  <Dropdown 
                    v-model="selectedFormats.examSchedule" 
                    :options="formatOptions" 
                    optionLabel="label" 
                    placeholder="Format Export"
                    class="p-mb-2 w-full"
                  />
                  <Button 
                    label="Generare Raport" 
                    icon="pi pi-download" 
                    @click="generateReport('examSchedule')"
                    :loading="loading.examSchedule"
                    class="w-full"
                  />
                </div>
              </template>
            </Card>
          </div>
          
          <div class="p-col-12 p-md-6 p-lg-4 p-mb-3">
            <Card class="report-card">
              <template #header>
                <div class="report-icon">
                  <i class="pi pi-users"></i>
                </div>
              </template>
              <template #title>
                Liste Studenți
              </template>
              <template #content>
                <p>Liste cu studenții înscriși la fiecare examen, organizate pe grupe și specializări.</p>
                <div class="p-mt-3">
                  <Dropdown 
                    v-model="selectedFormats.studentLists" 
                    :options="formatOptions" 
                    optionLabel="label" 
                    placeholder="Format Export"
                    class="p-mb-2 w-full"
                  />
                  <Button 
                    label="Generare Raport" 
                    icon="pi pi-download" 
                    @click="generateReport('studentLists')"
                    :loading="loading.studentLists"
                    class="w-full"
                  />
                </div>
              </template>
            </Card>
          </div>
          
          <div class="p-col-12 p-md-6 p-lg-4 p-mb-3">
            <Card class="report-card">
              <template #header>
                <div class="report-icon">
                  <i class="pi pi-building"></i>
                </div>
              </template>
              <template #title>
                Ocupare Săli
              </template>
              <template #content>
                <p>Raport detaliat despre ocuparea sălilor de examen pe zile și intervale orare.</p>
                <div class="p-mt-3">
                  <Dropdown 
                    v-model="selectedFormats.roomOccupancy" 
                    :options="formatOptions" 
                    optionLabel="label" 
                    placeholder="Format Export"
                    class="p-mb-2 w-full"
                  />
                  <Button 
                    label="Generare Raport" 
                    icon="pi pi-download" 
                    @click="generateReport('roomOccupancy')"
                    :loading="loading.roomOccupancy"
                    class="w-full"
                  />
                </div>
              </template>
            </Card>
          </div>
          
          <div class="p-col-12 p-md-6 p-lg-4 p-mb-3">
            <Card class="report-card">
              <template #header>
                <div class="report-icon">
                  <i class="pi pi-user"></i>
                </div>
              </template>
              <template #title>
                Profesori și Discipline
              </template>
              <template #content>
                <p>Lista profesorilor și disciplinele asociate, împreună cu datele programate pentru examene.</p>
                <div class="p-mt-3">
                  <Dropdown 
                    v-model="selectedFormats.professorSubjects" 
                    :options="formatOptions" 
                    optionLabel="label" 
                    placeholder="Format Export"
                    class="p-mb-2 w-full"
                  />
                  <Button 
                    label="Generare Raport" 
                    icon="pi pi-download" 
                    @click="generateReport('professorSubjects')"
                    :loading="loading.professorSubjects"
                    class="w-full"
                  />
                </div>
              </template>
            </Card>
          </div>
          
          <div class="p-col-12 p-md-6 p-lg-4 p-mb-3">
            <Card class="report-card">
              <template #header>
                <div class="report-icon">
                  <i class="pi pi-chart-bar"></i>
                </div>
              </template>
              <template #title>
                Statistici Sesiune
              </template>
              <template #content>
                <p>Statistici și grafice despre sesiunea de examene, inclusiv număr de studenți, promovabilitate și distribuția notelor.</p>
                <div class="p-mt-3">
                  <Dropdown 
                    v-model="selectedFormats.sessionStats" 
                    :options="formatOptions" 
                    optionLabel="label" 
                    placeholder="Format Export"
                    class="p-mb-2 w-full"
                  />
                  <Button 
                    label="Generare Raport" 
                    icon="pi pi-download" 
                    @click="generateReport('sessionStats')"
                    :loading="loading.sessionStats"
                    class="w-full"
                  />
                </div>
              </template>
            </Card>
          </div>
          
          <div class="p-col-12 p-md-6 p-lg-4 p-mb-3">
            <Card class="report-card">
              <template #header>
                <div class="report-icon">
                  <i class="pi pi-exclamation-triangle"></i>
                </div>
              </template>
              <template #title>
                Suprapuneri și Conflicte
              </template>
              <template #content>
                <p>Raport cu potențiale suprapuneri și conflicte de programare pentru examenele din sesiunea curentă.</p>
                <div class="p-mt-3">
                  <Dropdown 
                    v-model="selectedFormats.conflicts" 
                    :options="formatOptions" 
                    optionLabel="label" 
                    placeholder="Format Export"
                    class="p-mb-2 w-full"
                  />
                  <Button 
                    label="Generare Raport" 
                    icon="pi pi-download" 
                    @click="generateReport('conflicts')"
                    :loading="loading.conflicts"
                    class="w-full"
                  />
                </div>
              </template>
            </Card>
          </div>
        </div>
        
        <Divider />
        
        <h2>Raport Personalizat</h2>
        <div class="p-grid">
          <div class="p-col-12 p-md-8">
            <div class="p-fluid">
              <div class="p-field">
                <label for="customReportTitle">Titlu Raport</label>
                <InputText id="customReportTitle" v-model="customReport.title" placeholder="Introduceți titlul raportului" />
              </div>
              
              <div class="p-field p-mb-3">
                <label for="customReportType">Tip Raport</label>
                <Dropdown 
                  id="customReportType" 
                  v-model="customReport.type" 
                  :options="reportTypeOptions" 
                  optionLabel="label" 
                  placeholder="Selectați tipul de raport"
                />
              </div>
              
              <div class="p-formgrid p-grid">
                <div class="p-field p-col-12 p-md-6">
                  <label for="customReportStartDate">De la data</label>
                  <Calendar 
                    id="customReportStartDate" 
                    v-model="customReport.startDate" 
                    dateFormat="dd/mm/yy"
                    :showIcon="true"
                  />
                </div>
                <div class="p-field p-col-12 p-md-6">
                  <label for="customReportEndDate">Până la data</label>
                  <Calendar 
                    id="customReportEndDate" 
                    v-model="customReport.endDate" 
                    dateFormat="dd/mm/yy"
                    :showIcon="true"
                  />
                </div>
              </div>
              
              <div class="p-field p-mb-3">
                <label for="customReportGroups">Grupe (opțional)</label>
                <MultiSelect 
                  id="customReportGroups" 
                  v-model="customReport.groups" 
                  :options="groupOptions" 
                  optionLabel="name" 
                  placeholder="Toate grupele"
                  display="chip"
                />
              </div>
              
              <div class="p-field">
                <label for="customReportFormat">Format Export</label>
                <Dropdown 
                  id="customReportFormat" 
                  v-model="customReport.format" 
                  :options="formatOptions" 
                  optionLabel="label" 
                  placeholder="Selectați formatul"
                />
              </div>
              
              <Button 
                label="Generare Raport Personalizat" 
                icon="pi pi-cog" 
                @click="generateCustomReport"
                :loading="loading.customReport"
                :disabled="!isCustomReportValid"
                class="p-mt-3"
              />
            </div>
          </div>
          
          <div class="p-col-12 p-md-4">
            <Card>
              <template #title>
                Rapoarte Generate Recent
              </template>
              <template #content>
                <div v-if="recentReports.length === 0" class="empty-list">
                  <p>Nu există rapoarte generate recent</p>
                </div>
                <ul v-else class="recent-reports-list">
                  <li v-for="report in recentReports" :key="report.id" class="recent-report-item">
                    <div class="recent-report-info">
                      <span class="recent-report-title">{{ report.title }}</span>
                      <span class="recent-report-date">{{ formatDate(report.date) }}</span>
                    </div>
                    <Button 
                      icon="pi pi-download" 
                      class="p-button-rounded p-button-text" 
                      @click="downloadRecentReport(report)"
                    />
                  </li>
                </ul>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import InputText from 'primevue/inputtext'
import Calendar from 'primevue/calendar'
import Divider from 'primevue/divider'
import ReportService from '@/services/report.service'

export default {
  name: 'DownloadReportsView',
  components: {
    Card,
    Button,
    Dropdown,
    MultiSelect,
    InputText,
    Calendar,
    Divider
  },
  setup() {
    const store = useStore()
    
    // Format options
    const formatOptions = ref([
      { label: 'PDF', value: 'pdf' },
      { label: 'Excel (XLSX)', value: 'xlsx' },
      { label: 'CSV', value: 'csv' }
    ])
    
    // Report type options
    const reportTypeOptions = ref([
      { label: 'Program examene', value: 'exam_schedule' },
      { label: 'Liste studenți', value: 'student_lists' },
      { label: 'Ocupare săli', value: 'room_occupancy' },
      { label: 'Profesori și discipline', value: 'professor_subjects' },
      { label: 'Raport complet', value: 'complete_report' }
    ])
    
    // Group options
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
    
    // Selected formats for each report
    const selectedFormats = reactive({
      examSchedule: null,
      studentLists: null,
      roomOccupancy: null,
      professorSubjects: null,
      sessionStats: null,
      conflicts: null
    })
    
    // Loading states
    const loading = reactive({
      examSchedule: false,
      studentLists: false,
      roomOccupancy: false,
      professorSubjects: false,
      sessionStats: false,
      conflicts: false,
      customReport: false
    })
    
    // Custom report
    const customReport = reactive({
      title: '',
      type: null,
      startDate: null,
      endDate: null,
      groups: [],
      format: null
    })
    
    // Recent reports
    const recentReports = ref([])
    
    // Computed property to check if custom report is valid
    const isCustomReportValid = computed(() => {
      return customReport.title && 
             customReport.type && 
             customReport.format &&
             customReport.startDate &&
             customReport.endDate
    })
    
    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
    
    // Generate report
    const generateReport = async (reportType) => {
      const format = selectedFormats[reportType]
      
      if (!format) {
        store.dispatch('notifications/showNotification', {
          severity: 'warn',
          summary: 'Format Necesar',
          detail: 'Selectați un format de export pentru raport',
          life: 3000
        })
        return
      }
      
      try {
        loading[reportType] = true
        
        // In a real implementation, call the API
        // const response = await ReportService.generateReport(reportType, format)
        // window.open(response.data.url, '_blank')
        
        // For demo purposes, simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Add to recent reports
        const reportNames = {
          examSchedule: 'Programare Examene',
          studentLists: 'Liste Studenți',
          roomOccupancy: 'Ocupare Săli',
          professorSubjects: 'Profesori și Discipline',
          sessionStats: 'Statistici Sesiune',
          conflicts: 'Suprapuneri și Conflicte'
        }
        
        recentReports.value.unshift({
          id: Date.now(),
          title: `${reportNames[reportType]} (${format.toUpperCase()})`,
          type: reportType,
          format: format,
          date: new Date(),
          url: `#` // In a real app, this would be the download URL
        })
        
        // Keep only the 5 most recent reports
        if (recentReports.value.length > 5) {
          recentReports.value = recentReports.value.slice(0, 5)
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Raport Generat',
          detail: `Raportul a fost generat și descărcat cu succes`,
          life: 3000
        })
      } catch (error) {
        console.error(`Error generating ${reportType} report:`, error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: `Nu s-a putut genera raportul`,
          life: 5000
        })
      } finally {
        loading[reportType] = false
      }
    }
    
    // Generate custom report
    const generateCustomReport = async () => {
      if (!isCustomReportValid.value) {
        store.dispatch('notifications/showNotification', {
          severity: 'warn',
          summary: 'Date Incomplete',
          detail: 'Completați toate câmpurile obligatorii',
          life: 3000
        })
        return
      }
      
      try {
        loading.customReport = true
        
        // Create request data
        const requestData = {
          title: customReport.title,
          type: customReport.type.value,
          startDate: customReport.startDate.toISOString().split('T')[0],
          endDate: customReport.endDate.toISOString().split('T')[0],
          groups: customReport.groups.map(g => g.id),
          format: customReport.format.value
        }
        
        // In a real implementation, call the API
        // const response = await ReportService.generateCustomReport(requestData)
        // window.open(response.data.url, '_blank')
        
        // For demo purposes, simulate API call
        await new Promise(resolve => setTimeout(resolve, 2500))
        
        // Add to recent reports
        recentReports.value.unshift({
          id: Date.now(),
          title: `${customReport.title} (${customReport.format.value.toUpperCase()})`,
          type: 'custom',
          format: customReport.format.value,
          date: new Date(),
          url: `#` // In a real app, this would be the download URL
        })
        
        // Keep only the 5 most recent reports
        if (recentReports.value.length > 5) {
          recentReports.value = recentReports.value.slice(0, 5)
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Raport Personalizat Generat',
          detail: `Raportul a fost generat și descărcat cu succes`,
          life: 3000
        })
        
        // Reset custom report form
        customReport.title = ''
        customReport.type = null
        customReport.startDate = null
        customReport.endDate = null
        customReport.groups = []
        customReport.format = null
      } catch (error) {
        console.error('Error generating custom report:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: `Nu s-a putut genera raportul personalizat`,
          life: 5000
        })
      } finally {
        loading.customReport = false
      }
    }
    
    // Download recent report
    const downloadRecentReport = (report) => {
      // In a real implementation, use the URL from the report object
      // window.open(report.url, '_blank')
      
      // For demo purposes, show notification
      store.dispatch('notifications/showNotification', {
        severity: 'info',
        summary: 'Descărcare Raport',
        detail: `Se descarcă raportul: ${report.title}`,
        life: 3000
      })
    }
    
    // Load recent reports
    const loadRecentReports = async () => {
      try {
        // In a real implementation, call the API
        // const response = await ReportService.getRecentReports()
        // recentReports.value = response.data
        
        // For demo purposes, use mock data
        recentReports.value = [
          {
            id: 1,
            title: 'Programare Examene (PDF)',
            type: 'examSchedule',
            format: 'pdf',
            date: new Date(2025, 4, 10, 15, 30),
            url: '#'
          },
          {
            id: 2,
            title: 'Liste Studenți (XLSX)',
            type: 'studentLists',
            format: 'xlsx',
            date: new Date(2025, 4, 10, 14, 45),
            url: '#'
          }
        ]
      } catch (error) {
        console.error('Error loading recent reports:', error)
      }
    }
    
    // Initialize
    onMounted(() => {
      loadRecentReports()
    })
    
    return {
      formatOptions,
      reportTypeOptions,
      groupOptions,
      selectedFormats,
      loading,
      customReport,
      recentReports,
      isCustomReportValid,
      formatDate,
      generateReport,
      generateCustomReport,
      downloadRecentReport
    }
  }
}
</script>

<style lang="scss" scoped>
.download-reports {
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
    margin-bottom: 1rem;
  }
  
  .report-info {
    display: flex;
    align-items: flex-start;
    padding: 1rem;
    background-color: #e3f2fd;
    border-radius: 4px;
    
    i {
      font-size: 1.25rem;
      color: #1E88E5;
      margin-right: 0.75rem;
      margin-top: 0.1rem;
    }
  }
  
  .report-card {
    height: 100%;
    
    :deep(.p-card-header) {
      padding-top: 1.5rem;
      padding-bottom: 0;
    }
    
    .report-icon {
      text-align: center;
      
      i {
        font-size: 2rem;
        color: #1E88E5;
        background-color: #e3f2fd;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
      }
    }
    
    :deep(.p-card-title) {
      text-align: center;
      font-size: 1.25rem;
      margin-bottom: 0.5rem;
    }
    
    :deep(.p-card-content) {
      padding-top: 0;
      
      p {
        text-align: center;
        color: #6c757d;
        min-height: 60px;
      }
    }
  }
  
  .w-full {
    width: 100%;
  }
  
  .recent-reports-list {
    list-style: none;
    padding: 0;
    margin: 0;
    
    .recent-report-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 0;
      border-bottom: 1px solid #e9ecef;
      
      &:last-child {
        border-bottom: none;
      }
      
      .recent-report-info {
        display: flex;
        flex-direction: column;
        
        .recent-report-title {
          font-weight: 500;
          color: #2c3e50;
        }
        
        .recent-report-date {
          font-size: 0.875rem;
          color: #6c757d;
          margin-top: 0.25rem;
        }
      }
    }
  }
  
  .empty-list {
    text-align: center;
    color: #6c757d;
    padding: 1rem;
  }
}
</style>
