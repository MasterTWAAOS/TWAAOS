<template>
  <div class="upload-data">
    <h1>Încărcare Date</h1>
    
    <div class="p-grid">
      <!-- Excel templates -->
      <div class="p-col-12 p-md-6">
        <Card>
          <template #title>
            <h2><i class="pi pi-download"></i> Descărcare Template-uri</h2>
          </template>
          <template #content>
            <p>Descărcați formatul Excel pentru a încărca liste cu șefi de grupe.</p>
            <div class="template-buttons">
              <Button 
                class="p-button-primary p-mb-2" 
                icon="pi pi-file-excel" 
                label="Template Șefi de Grupă" 
                @click="downloadTemplate('group-leaders')"
              />
            </div>
          </template>
        </Card>
      </div>
      
      <!-- Upload files -->
      <div class="p-col-12 p-md-6">
        <Card>
          <template #title>
            <h2><i class="pi pi-upload"></i> Încărcare Fișiere</h2>
          </template>
          <template #content>
            <p>Selectați și încărcați fișierul Excel cu datele despre Șefii de Grupă.</p>
            
            <div class="file-upload p-mb-3">
              <h3>Șefi de Grupă</h3>
              <FileUpload
                mode="basic"
                :customUpload="true"
                @uploader="uploadGroupLeaders"
                accept=".xlsx,.xls"
                :auto="true"
                chooseLabel="Selectare fișier"
              />
              <small v-if="uploads?.groupLeaders?.status" :class="getStatusClass(uploads?.groupLeaders?.status)">
                {{ uploads?.groupLeaders?.message || '' }}
              </small>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Sync with USV API -->
    <Card class="p-mt-3">
      <template #title>
        <h2><i class="pi pi-sync"></i> Sincronizare cu API-ul USV</h2>
      </template>
      <template #content>
        <p>
          Această acțiune va sincroniza toate datele din API-urile USV: grupe, săli și cadre didactice.
        </p>
        
        <div class="sync-status p-mb-3" v-if="syncStatus?.all">
          <i :class="[getSyncIconClass(syncStatus?.all?.success), 'sync-icon']"></i>
          <span>{{ syncStatus?.all?.message || '' }}</span>
        </div>
        
        <div>
          <Button 
            icon="pi pi-sync" 
            label="Sincronizare date ORAR USV" 
            @click="syncData"
            :loading="syncing.all"
            class="p-button-success p-button-lg"
          />
        </div>
      </template>
    </Card>
    
    <!-- Current data summary -->
    <Card class="p-mt-3">
      <template #title>
        <h2><i class="pi pi-database"></i> Date Actuale</h2>
      </template>
      <template #content>
        <div class="p-grid">
          <div class="p-col-12 p-md-4">
            <div class="data-summary">
              <div class="data-title">Grupe</div>
              <div class="data-count">{{ currentData?.groups || 0 }}</div>
            </div>
          </div>
          <div class="p-col-12 p-md-4">
            <div class="data-summary">
              <div class="data-title">Săli</div>
              <div class="data-count">{{ currentData?.rooms || 0 }}</div>
            </div>
          </div>
          <div class="p-col-12 p-md-4">
            <div class="data-summary">
              <div class="data-title">Cadre Didactice</div>
              <div class="data-count">{{ currentData?.professors || 0 }}</div>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import excelTemplateService from '@/services/excel-template.service'
import { useStore } from 'vuex'
import FileUpload from 'primevue/fileupload'
import { saveAs } from 'file-saver'
import adminService from '@/services/admin.service'

export default defineComponent({
  name: 'UploadDataView',
  components: {
    FileUpload
  },
  setup() {
    // Get store for notifications
    const store = useStore()
    
    // Initialize all objects with default values
    
    // Upload status tracking
    const uploads = ref({
      subjects: { status: null, message: '' },
      groupLeaders: { status: null, message: '' },
      rooms: { status: null, message: '' }
    })
    
    // Sync status tracking
    const syncStatus = ref({
      groups: null,
      rooms: null,
      professors: null,
      all: null
    })
    
    // Loading state for sync operations
    const syncing = ref({
      groups: false,
      rooms: false,
      professors: false,
      all: false
    })
    
    // Current data summary
    const currentData = ref({
      groups: 0,
      rooms: 0,
      professors: 0
    })
    
    // Function to load current data counts from backend
    const loadCurrentDataCounts = async () => {
      try {
        // Fetch all counts in parallel
        const [groupsResponse, roomsResponse, professorsResponse] = await Promise.all([
          adminService.getGroupCount(),
          adminService.getRoomCount(),
          adminService.getProfessorCount()
        ])
        
        // Update the data with fetched values
        currentData.value.groups = groupsResponse.data.count || 0
        currentData.value.rooms = roomsResponse.data.count || 0
        currentData.value.professors = professorsResponse.data.count || 0
      } catch (error) {
        console.error('Error fetching data counts:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca datele actuale.',
          life: 3000
        })
      }
    }
    
    // Loading state for other operations
    const loading = ref({
      refreshData: false,
      downloadTemplate: false
    })
    
    // Function to download Excel templates
    /**
     * Downloads a template for the selected type
     * @param {string} templateType - Type of template to download
     */
    const downloadTemplate = async (templateType) => {
      try {
        if (loading.value) loading.value.refreshData = true
        
        // Map frontend template type to backend enum
        const templateTypeMap = {
          'subjects': 'cd',     // Course/Discipline
          'group-leaders': 'sg', // Student Group Leaders
          'rooms': 'sali'       // Rooms
        }
        
        const backendType = templateTypeMap[templateType]
        if (!backendType) {
          throw new Error(`Tipul de template '${templateType}' nu este valid.`)
        }
        
        // For group leaders we'll look for a specific name
        let searchName = null
        if (templateType === 'group-leaders') {
          searchName = 'template_SG' // Specific name for group leader template
        }
        
        // Get templates of the specified type using the service
        const response = await excelTemplateService.getTemplatesByType(backendType, searchName)
        
        const templates = response.data
        if (!templates || templates.length === 0) {
          throw new Error(`Nu există template pentru ${templateType}`)
        }
        
        // Use the first template found
        const template = templates[0]
        
        // Now download the actual template file using the service
        const downloadResponse = await excelTemplateService.downloadTemplate(template.id)
        
        // Extract blob from axios response and create download link
        const blob = new Blob([downloadResponse.data], { 
          type: downloadResponse.headers ? downloadResponse.headers['content-type'] : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        const url = window.URL.createObjectURL(blob)
        
        const link = document.createElement('a')
        link.href = url
        
        // Get filename from content-disposition or use a default
        const contentDisposition = downloadResponse.headers ? downloadResponse.headers['content-disposition'] : null
        let filename = null;
        if (contentDisposition) {
          const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
          const matches = filenameRegex.exec(contentDisposition);
          if (matches && matches[1]) {
            filename = matches[1].replace(/['"]/g, '');
          }
        }
        
        if (!filename) {
          // Fallback filename
          const templateNames = {
            'subjects': 'template_discipline.xlsx',
            'group-leaders': 'template_sefi_grupa.xlsx',
            'rooms': 'template_sali.xlsx'
          }
          filename = templateNames[templateType] || `template_${templateType}.xlsx`
        }
        
        link.download = filename;
        
        // Trigger download
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Clean up URL object
        window.URL.revokeObjectURL(url)
        
        // Show success notification
        const templateLabels = {
          'subjects': 'Discipline',
          'group-leaders': 'Șefi de Grupă',
          'rooms': 'Săli'
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Descărcare Reușită',
          detail: `Template-ul pentru ${templateLabels[templateType]} a fost descărcat cu succes.`,
          life: 3000
        })
      } catch (error) {
        console.error('Error downloading template:', error)
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Descărcare',
          detail: error.message || 'A apărut o eroare la descărcarea template-ului.',
          life: 5000
        })
      }
    }
    
    // File upload handlers
    const uploadSubjects = async (event) => {
      try {
        const file = event.files[0]
        uploads.value.subjects = { status: 'loading', message: 'Se încarcă fișierul...' }
        
        // In a real implementation, you would upload the file
        // For example:
        // const formData = new FormData()
        // formData.append('file', file)
        // await uploadService.uploadSubjects(formData)
        
        // Mock timeout to simulate upload
        setTimeout(() => {
          uploads.value.subjects = { status: 'success', message: 'Încărcare reușită! 47 discipline au fost importate.' }
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Încărcare Reușită',
            detail: 'Lista de discipline a fost încărcată cu succes.',
            life: 3000
          })
        }, 1500)
      } catch (error) {
        uploads.value.subjects = { status: 'error', message: error.message || 'A apărut o eroare la încărcarea fișierului.' }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Încărcare',
          detail: error.message || 'A apărut o eroare la încărcarea listei de discipline.',
          life: 5000
        })
      }
    }
    
    const uploadGroupLeaders = async (event) => {
      try {
        const file = event.files[0]
        uploads.value.groupLeaders = { status: 'loading', message: 'Se încarcă fișierul...' }
        
        // Create a form data object to send the file
        const formData = new FormData()
        formData.append('file', file)
        
        // Send the file to the backend API
        const response = await fetch('/sync/groups/upload-leaders', {
          method: 'POST',
          body: formData,
          headers: {
            // Don't set Content-Type header for multipart/form-data
            'Accept': 'application/json'
          }
        })
        
        const data = await response.json()
        
        if (!response.ok) {
          throw new Error(data.detail || 'A apărut o eroare la încărcarea fișierului.')
        }
        
        // Update the status based on the response
        if (data.success) {
          uploads.value.groupLeaders = { 
            status: 'success', 
            message: `Încărcare reușită! ${data.created_count} șefi de grupă au fost importați.` 
          }
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Încărcare Reușită',
            detail: data.message || 'Lista șefilor de grupă a fost încărcată cu succes.',
            life: 3000
          })
        } else {
          // Handle failed upload but with a valid response
          const errorDetail = data.errors && data.errors.length > 0 
            ? data.errors.join('\n')
            : data.message || 'Au apărut erori la procesarea fișierului.'
            
          uploads.value.groupLeaders = { 
            status: 'error', 
            message: `Încărcare parțială: ${data.created_count} reușite, ${data.failed_count} eșuate.` 
          }
          
          store.dispatch('notifications/showNotification', {
            severity: 'warn',
            summary: 'Încărcare Parțială',
            detail: errorDetail,
            life: 5000
          })
        }
      } catch (error) {
        uploads.value.groupLeaders = { status: 'error', message: error.message || 'A apărut o eroare la încărcarea fișierului.' }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Încărcare',
          detail: error.message || 'A apărut o eroare la încărcarea listei de șefi de grupă.',
          life: 5000
        })
      }
    }
    
    const uploadRooms = async (event) => {
      try {
        const file = event.files[0]
        uploads.value.rooms = { status: 'loading', message: 'Se încarcă fișierul...' }
        
        // Mock timeout to simulate upload
        setTimeout(() => {
          uploads.value.rooms = { status: 'success', message: 'Încărcare reușită! 38 săli au fost importate.' }
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Încărcare Reușită',
            detail: 'Lista sălilor a fost încărcată cu succes.',
            life: 3000
          })
        }, 1500)
      } catch (error) {
        uploads.value.rooms = { status: 'error', message: error.message || 'A apărut o eroare la încărcarea fișierului.' }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Încărcare',
          detail: error.message || 'A apărut o eroare la încărcarea listei de săli.',
          life: 5000
        })
      }
    }
    
    // Synchronize data using adminService.syncData() - this uses the FastAPI endpoint
    const syncData = async () => {
      try {
        syncing.value.all = true
        syncStatus.value.all = null
        
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Sincronizare în curs',
          detail: 'Se sincronizează toate datele din API-urile USV...',
          life: 3000
        })
        
        // Call the sync API via admin service
        await adminService.syncData()
        
        // Update sync status
        syncStatus.value.all = { 
          success: true, 
          message: 'Toate datele au fost sincronizate cu succes!' 
        }
        
        // Refresh counters
        await loadCurrentDataCounts()
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare Completă',
          detail: 'Toate datele au fost sincronizate cu succes din API-urile USV.',
          life: 3000
        })
      } catch (error) {
        console.error('Error syncing data:', error);
        
        syncStatus.value.all = { 
          success: false, 
          message: error.message || 'A apărut o eroare la sincronizarea datelor.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Sincronizare',
          detail: error.message || 'A apărut o eroare la sincronizarea datelor din API-urile USV.',
          life: 5000
        })
      } finally {
        syncing.value.all = false
      }
    }
    
    // Load data counts when component is mounted
    onMounted(async () => {
      await loadCurrentDataCounts()
    })
    
    // Helper functions
    const getStatusClass = (status) => {
      if (status === 'success') return 'text-success'
      if (status === 'error') return 'text-danger'
      if (status === 'loading') return 'text-info'
      return ''
    }
    
    const getSyncIconClass = (success) => {
      return success ? 'pi pi-check-circle text-success' : 'pi pi-times-circle text-danger'
    }
    
    return {
      uploads,
      syncStatus,
      syncing,
      currentData,
      loading,
      downloadTemplate,
      uploadSubjects,
      uploadGroupLeaders,
      uploadRooms,
      syncData,
      getStatusClass,
      getSyncIconClass
    }
  }
})
</script>

<style lang="scss" scoped>
.upload-data {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  h2 {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
    margin: 0;
    
    i {
      margin-right: 0.75rem;
      color: #1E88E5;
    }
  }
  
  h3 {
    font-size: 1.1rem;
    margin-top: 0;
    margin-bottom: 0.75rem;
    color: #2c3e50;
  }
  
  p {
    color: #6c757d;
    margin-bottom: 1.5rem;
  }
  
  .template-buttons {
    display: flex;
    flex-direction: column;
    
    .p-button {
      margin-right: 0;
    }
  }
  
  .file-upload {
    margin-bottom: 1rem;
    
    h3 {
      margin-bottom: 0.5rem;
    }
  }
  
  .sync-card {
    height: 100%;
    
    .sync-status {
      margin-top: 1rem;
      display: flex;
      align-items: center;
      
      i {
        margin-right: 0.5rem;
        font-size: 1.1rem;
      }
    }
  }
  
  .data-summary {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    
    .data-title {
      font-size: 1.1rem;
      color: #6c757d;
      margin-bottom: 0.5rem;
    }
    
    .data-count {
      font-size: 2.5rem;
      font-weight: 600;
      color: #1E88E5;
    }
  }
  
  .text-success {
    color: #4caf50;
  }
  
  .text-danger {
    color: #f44336;
  }
  
  .text-info {
    color: #2196f3;
  }
}
</style>
