<template>
  <div class="download-reports">
    <h1>Rapoarte Examene</h1>
    
    <Card>
      <template #content>
        <p class="report-info p-mb-4">
          <i class="pi pi-info-circle"></i>
          Generați și descărcați rapoarte de examene programate. Rapoartele pot fi exportate în 
          formatele PDF și Excel.
        </p>
        
        <div class="p-grid p-m-0">
          <!-- Report Cards -->
          <div class="p-col-12 p-md-6 p-lg-6 p-mb-3">
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
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import ExamService from '@/services/exam.service'

export default {
  name: 'DownloadReportsView',
  components: {
    Card,
    Button,
    Dropdown,
  },
  setup() {
    const store = useStore()
    
    // Format options - limited to PDF and Excel only
    const formatOptions = ref([
      { label: 'PDF', value: 'pdf' },
      { label: 'Excel (XLSX)', value: 'xlsx' }
    ])
    
    // Selected formats for the exam schedule report
    const selectedFormats = reactive({
      examSchedule: null
    })
    
    // Loading states
    const loading = reactive({
      examSchedule: false
    })
    
    // Generate exam schedule report
    const generateReport = async (reportType) => {
      if (!selectedFormats[reportType]) {
        store.dispatch('showToast', { 
          severity: 'warn', 
          summary: 'Format lipsă', 
          detail: 'Vă rugăm selectați un format pentru export' 
        })
        return
      }
      
      loading[reportType] = true
      
      try {
        // Get the format (pdf or xlsx)
        const format = selectedFormats[reportType].value
        
        // Call the exam export API
        const response = await ExamService.exportExams(format)
        
        // Create file download from blob
        const blob = new Blob([response.data], { 
          type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `programare-examene.${format}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        store.dispatch('showToast', { 
          severity: 'success', 
          summary: 'Raport generat', 
          detail: 'Raportul a fost descărcat cu succes' 
        })
      } catch (error) {
        console.error(`Eroare la generarea raportului de examene:`, error)
        store.dispatch('showToast', { 
          severity: 'error', 
          summary: 'Eroare', 
          detail: `Nu s-a putut genera raportul: ${error.message || 'Eroare necunoscută'}` 
        })
      } finally {
        loading[reportType] = false
      }
    }
    
    // Set default format when component mounts
    onMounted(() => {
      // Default to PDF
      selectedFormats.examSchedule = formatOptions.value[0] // PDF
    })
    
    return {
      formatOptions,
      selectedFormats,
      loading,
      generateReport,
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
