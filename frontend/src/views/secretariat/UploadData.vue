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
            <p>Descărcați formatul Excel pentru a încărca liste de discipline, șefi de grupe sau săli disponibile.</p>
            <div class="template-buttons">
              <Button 
                class="p-button-primary p-mb-2" 
                icon="pi pi-file-excel" 
                label="Template Discipline" 
                @click="downloadTemplate('subjects')"
              />
              <Button 
                class="p-button-primary p-mb-2" 
                icon="pi pi-file-excel" 
                label="Template Șefi de Grupă" 
                @click="downloadTemplate('group-leaders')"
              />
              <Button 
                class="p-button-primary" 
                icon="pi pi-file-excel" 
                label="Template Săli" 
                @click="downloadTemplate('rooms')"
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
            <p>Selectați și încărcați fișierele Excel cu datele necesare.</p>
            
            <div class="file-upload p-mb-3">
              <h3>Discipline și Cadre Didactice</h3>
              <FileUpload
                mode="basic"
                :customUpload="true"
                @uploader="uploadSubjects"
                accept=".xlsx,.xls"
                :auto="true"
                chooseLabel="Selectare fișier"
              />
              <small v-if="uploads.subjects.status" :class="getStatusClass(uploads.subjects.status)">
                {{ uploads.subjects.message }}
              </small>
            </div>
            
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
              <small v-if="uploads.groupLeaders.status" :class="getStatusClass(uploads.groupLeaders.status)">
                {{ uploads.groupLeaders.message }}
              </small>
            </div>
            
            <div class="file-upload">
              <h3>Săli Disponibile</h3>
              <FileUpload
                mode="basic"
                :customUpload="true"
                @uploader="uploadRooms"
                accept=".xlsx,.xls"
                :auto="true"
                chooseLabel="Selectare fișier"
              />
              <small v-if="uploads.rooms.status" :class="getStatusClass(uploads.rooms.status)">
                {{ uploads.rooms.message }}
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
          Puteți sincroniza direct datele de la API-urile USV pentru a obține cele mai recente informații despre facultăți, 
          programe de studii, grupe, săli și cadre didactice.
        </p>
        <div class="p-grid">
          <div class="p-col-12 p-md-4">
            <Card class="sync-card">
              <template #title>
                <span>Sincronizare Grupe</span>
              </template>
              <template #content>
                <p>Sincronizează toate grupele aferente facultății FIESC din API-ul USV.</p>
                <Button 
                  icon="pi pi-users" 
                  label="Sincronizare Grupe" 
                  @click="syncGroups"
                  :loading="syncing.groups"
                  class="p-button-info"
                />
                <div v-if="syncStatus.groups" class="sync-status">
                  <i :class="getSyncIconClass(syncStatus.groups.success)"></i>
                  <span>{{ syncStatus.groups.message }}</span>
                </div>
              </template>
            </Card>
          </div>
          
          <div class="p-col-12 p-md-4">
            <Card class="sync-card">
              <template #title>
                <span>Sincronizare Săli</span>
              </template>
              <template #content>
                <p>Sincronizează toate sălile disponibile din API-ul USV.</p>
                <Button 
                  icon="pi pi-building" 
                  label="Sincronizare Săli" 
                  @click="syncRooms"
                  :loading="syncing.rooms"
                  class="p-button-info"
                />
                <div v-if="syncStatus.rooms" class="sync-status">
                  <i :class="getSyncIconClass(syncStatus.rooms.success)"></i>
                  <span>{{ syncStatus.rooms.message }}</span>
                </div>
              </template>
            </Card>
          </div>
          
          <div class="p-col-12 p-md-4">
            <Card class="sync-card">
              <template #title>
                <span>Sincronizare Cadre Didactice</span>
              </template>
              <template #content>
                <p>Sincronizează toate cadrele didactice din API-ul USV.</p>
                <Button 
                  icon="pi pi-user" 
                  label="Sincronizare Cadre" 
                  @click="syncProfessors"
                  :loading="syncing.professors"
                  class="p-button-info"
                />
                <div v-if="syncStatus.professors" class="sync-status">
                  <i :class="getSyncIconClass(syncStatus.professors.success)"></i>
                  <span>{{ syncStatus.professors.message }}</span>
                </div>
              </template>
            </Card>
          </div>
        </div>
        
        <div class="p-mt-3">
          <Button 
            icon="pi pi-sync" 
            label="Sincronizare Completă" 
            @click="syncAll"
            :loading="syncing.all"
            class="p-button-success p-button-lg"
          />
          <small class="p-d-block p-mt-2">
            Această acțiune va sincroniza toate datele: grupe, săli și cadre didactice.
          </small>
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
              <div class="data-count">{{ currentData.groups }}</div>
            </div>
          </div>
          <div class="p-col-12 p-md-4">
            <div class="data-summary">
              <div class="data-title">Săli</div>
              <div class="data-count">{{ currentData.rooms }}</div>
            </div>
          </div>
          <div class="p-col-12 p-md-4">
            <div class="data-summary">
              <div class="data-title">Cadre Didactice</div>
              <div class="data-count">{{ currentData.professors }}</div>
            </div>
          </div>
        </div>
        
        <Button 
          icon="pi pi-refresh" 
          label="Actualizare" 
          @click="refreshData"
          :loading="loading.refreshData"
          class="p-button-outlined p-mt-3"
        />
      </template>
    </Card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import FileUpload from 'primevue/fileupload'
import { saveAs } from 'file-saver'
import syncService from '@/services/sync.service'

export default {
  name: 'UploadDataView',
  components: {
    FileUpload
  },
  setup() {
    const store = useStore()
    
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
      groups: 21,
      rooms: 38,
      professors: 47
    })
    
    // Loading state for other operations
    const loading = ref({
      refreshData: false
    })
    
    // Function to download Excel templates
    const downloadTemplate = (templateType) => {
      try {
        // This would connect to your API to download the template
        
        if (templateType === 'group-leaders') {
          // Create a simple Excel template for group leaders
          // We'll use a library like exceljs or xlsx in a real implementation
          // For now, we'll create a simple CSV content and convert it to a Blob
          
          const headers = ['lastName', 'firstName', 'email', 'groupName']
          const exampleRow = ['Popescu', 'Ion', 'ion.popescu@student.usv.ro', '3103B']
          
          // Create CSV content
          const csvContent = [
            headers.join(','),
            exampleRow.join(',')
          ].join('\n')
          
          // Create a Blob from the CSV content
          const blob = new Blob([csvContent], { type: 'text/csv' })
          
          // Create a download link and trigger the download
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = 'sefi_de_grupa_template.csv'
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          
          // In a real implementation, you would request the template from the server
          // For example:
          // const response = await fetch(`/api/excel-templates/download/group-leaders`)
          // const blob = await response.blob()
          // const url = URL.createObjectURL(blob)
          // ... download as above
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Descărcare Reușită',
            detail: `Template-ul pentru Șefi de Grupă a fost descărcat cu succes.`,
            life: 3000
          })
        } else {
          // For other template types, we'll keep the original behavior
          // In a real implementation, you would request the template from the server
          // For example:
          // const response = await fetch(`/api/templates/${templateType}`)
          // const blob = await response.blob()
          
          // For the example, we'll simulate a delay and then create a dummy message
          setTimeout(() => {
            // This would download the actual file in a real implementation
            store.dispatch('notifications/showNotification', {
              severity: 'success',
              summary: 'Descărcare Reușită',
              detail: `Template-ul a fost descărcat cu succes.`,
              life: 3000
            })
          }, 1000)
        }
      } catch (error) {
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
    
    // Synchronization functions - these would connect to the Flask sync API
    const syncGroups = async () => {
      try {
        syncing.value.groups = true
        syncStatus.value.groups = null
        
        // Call the sync API - this would connect to our Flask service
        // const response = await syncService.syncGroups()
        
        // Mock timeout to simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Update status
        syncStatus.value.groups = { 
          success: true, 
          message: 'Sincronizare reușită! 21 grupe au fost actualizate.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare Reușită',
          detail: 'Grupele au fost sincronizate cu succes.',
          life: 3000
        })
      } catch (error) {
        syncStatus.value.groups = { 
          success: false, 
          message: error.message || 'A apărut o eroare la sincronizarea grupelor.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Sincronizare',
          detail: error.message || 'A apărut o eroare la sincronizarea grupelor.',
          life: 5000
        })
      } finally {
        syncing.value.groups = false
      }
    }
    
    const syncRooms = async () => {
      try {
        syncing.value.rooms = true
        syncStatus.value.rooms = null
        
        // Mock timeout to simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Update status
        syncStatus.value.rooms = { 
          success: true, 
          message: 'Sincronizare reușită! 38 săli au fost actualizate.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare Reușită',
          detail: 'Sălile au fost sincronizate cu succes.',
          life: 3000
        })
      } catch (error) {
        syncStatus.value.rooms = { 
          success: false, 
          message: error.message || 'A apărut o eroare la sincronizarea sălilor.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Sincronizare',
          detail: error.message || 'A apărut o eroare la sincronizarea sălilor.',
          life: 5000
        })
      } finally {
        syncing.value.rooms = false
      }
    }
    
    const syncProfessors = async () => {
      try {
        syncing.value.professors = true
        syncStatus.value.professors = null
        
        // Mock timeout to simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Update status
        syncStatus.value.professors = { 
          success: true, 
          message: 'Sincronizare reușită! 47 cadre didactice au fost actualizate.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare Reușită',
          detail: 'Cadrele didactice au fost sincronizate cu succes.',
          life: 3000
        })
      } catch (error) {
        syncStatus.value.professors = { 
          success: false, 
          message: error.message || 'A apărut o eroare la sincronizarea cadrelor didactice.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Sincronizare',
          detail: error.message || 'A apărut o eroare la sincronizarea cadrelor didactice.',
          life: 5000
        })
      } finally {
        syncing.value.professors = false
      }
    }
    
    // Synchronize all data at once - this connects to our Flask synchronization system
    const syncAll = async () => {
      try {
        syncing.value.all = true
        syncStatus.value.all = null
        
        store.dispatch('notifications/showNotification', {
          severity: 'info',
          summary: 'Sincronizare în curs',
          detail: 'Se sincronizează toate datele din API-urile USV...',
          life: 3000
        })
        
        // Call the sync API to fetch all data - this would access our Flask sync service that handles USV API calls
        await syncService.syncAll()
        
        // Update all sync statuses
        syncStatus.value.groups = { 
          success: true, 
          message: 'Sincronizare reușită! 21 grupe actualizate.' 
        }
        
        syncStatus.value.rooms = { 
          success: true, 
          message: 'Sincronizare reușită! 38 săli actualizate.' 
        }
        
        syncStatus.value.professors = { 
          success: true, 
          message: 'Sincronizare reușită! 47 cadre didactice actualizate.' 
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Sincronizare Completă',
          detail: 'Toate datele au fost sincronizate cu succes.',
          life: 5000
        })
        
        // Refresh data summary
        refreshData()
      } catch (error) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Sincronizare',
          detail: error.message || 'A apărut o eroare la sincronizarea datelor.',
          life: 5000
        })
      } finally {
        syncing.value.all = false
      }
    }
    
    // Refresh current data summary
    const refreshData = async () => {
      try {
        loading.value.refreshData = true
        
        // In a real implementation, this would fetch the current data counts
        // For example:
        // const response = await dataService.getCounts()
        // currentData.value = response.data
        
        // Mock timeout to simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Random variation for demonstration
        currentData.value = {
          groups: 21,
          rooms: 38,
          professors: 47
        }
      } catch (error) {
        console.error('Error refreshing data:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Actualizare',
          detail: 'Nu s-au putut actualiza contoarele de date.',
          life: 3000
        })
      } finally {
        loading.value.refreshData = false
      }
    }
    
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
    
    // Initialize
    onMounted(() => {
      refreshData()
    })
    
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
      syncGroups,
      syncRooms,
      syncProfessors,
      syncAll,
      refreshData,
      getStatusClass,
      getSyncIconClass
    }
  }
}
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
