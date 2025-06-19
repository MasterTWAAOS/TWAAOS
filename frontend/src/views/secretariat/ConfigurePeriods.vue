<template>
  <div class="configure-periods">
    <h1>Configurare Perioade Examene</h1>
    
    <Card>
      <template #content>
        <p class="config-info">
          <i class="pi pi-info-circle"></i>
          Configurați perioada de examene și colocvii. Acestă perioadă va determina intervalul de timp 
          în care pot fi programate examenele și vor fi vizibile pentru toate rolurile din aplicație.
        </p>
        
        <div class="p-grid">
          <div class="p-col-12 p-md-6">
            <h2>Perioade Active</h2>
            <DataTable 
              :value="activePeriods" 
              :paginator="true" 
              :rows="5"
              class="p-datatable-sm" 
              responsiveLayout="scroll"
              :loading="loading.activePeriods"
            >
              <!-- ID field hidden as requested -->
              <Column field="startDate" header="Data Început" :sortable="true">
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.startDate) }}
                </template>
              </Column>
              <Column field="endDate" header="Data Sfârșit" :sortable="true">
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.endDate) }}
                </template>
              </Column>
              <Column field="modified_at" header="Data Modificării" :sortable="true">
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.modified_at) }}
                </template>
              </Column>
              <Column header="Acțiuni" style="width: 15%">
                <template #body="slotProps">
                  <Button 
                    icon="pi pi-pencil" 
                    class="p-button-info p-button-sm p-mr-1" 
                    @click="editPeriod(slotProps.data)"
                  />
                  <Button 
                    icon="pi pi-trash"
                    class="p-button-danger p-button-sm" 
                    @click="togglePeriodStatus(slotProps.data)"
                  />
                </template>
              </Column>
            </DataTable>
          </div>
          
          <div class="p-col-12 p-md-6">
            <Card>
              <template #title>
                {{ editMode ? 'Editare Perioadă' : 'Adăugare Perioadă Nouă' }}
              </template>
              <template #content>
                <div class="p-fluid">                  
                  <div class="p-field p-mb-3">
                    <label for="dateRange">Interval Calendar <span class="required-field">*</span></label>
                    <Calendar 
                      id="dateRange" 
                      v-model="periodForm.dateRange" 
                      selectionMode="range" 
                      dateFormat="dd/mm/yy"
                      :showIcon="true"
                      :class="{'p-invalid': v$.dateRange.$invalid && v$.dateRange.$dirty}"
                      @blur="v$.dateRange.$touch()"
                    />
                    <small class="p-error" v-if="v$.dateRange.$invalid && v$.dateRange.$dirty">
                      {{ v$.dateRange.$errors[0].$message }}
                    </small>
                    <small class="p-info">
                      Selecți o dată de început și una de sfârșit pentru perioada de examene.
                    </small>
                  </div>
                  
                  <div class="form-actions">
                    <Button 
                      label="Anulare" 
                      icon="pi pi-times" 
                      class="p-button-text" 
                      @click="resetForm"
                      :disabled="formSubmitting"
                    />
                    <Button 
                      :label="editMode ? 'Actualizare' : 'Salvare'" 
                      icon="pi pi-check" 
                      @click="savePeriod"
                      :loading="formSubmitting"
                      :disabled="v$.$invalid"
                    />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>
    
    <!-- Confirmation Dialog for Toggle Status -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useConfirm } from 'primevue/useconfirm'
import { useVuelidate } from '@vuelidate/core'
import { required } from '@vuelidate/validators'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Calendar from 'primevue/calendar'
import ConfirmDialog from 'primevue/confirmdialog'
import configService from '@/services/config.service'

export default {
  name: 'ConfigurePeriodsView',
  components: {
    Card,
    DataTable,
    Column,
    Button,
    Calendar,
    ConfirmDialog
  },
  setup() {
    const store = useStore(),
          confirm = useConfirm()
    
    // Loading states
    const loading = reactive({
      activePeriods: false
    })
    
    // Active periods
    const activePeriods = ref([])
    
    // Edit mode
    const editMode = ref(false)
    const editId = ref(null)
    
    // Period types
    const periodTypes = ref([
      { name: 'Sesiune Examinare', value: 'EXAM_SESSION' },
      { name: 'Vacanță', value: 'HOLIDAY' },
      { name: 'Sesiune Restanțe', value: 'RESIT_SESSION' }
    ])
    
    // Form data - simplified to match database structure
    const periodForm = reactive({
      dateRange: null
    })
    
    // Form submitting state
    const formSubmitting = ref(false)
    
    // Form validation rules - simplified to match database fields
    const rules = computed(() => ({
      dateRange: { required }
    }))
    
    // Create vuelidate instance
    const v$ = useVuelidate(rules, periodForm)
    
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
    
    // Load active periods
    const loadActivePeriods = async () => {
      try {
        loading.activePeriods = true
        // Use config service to fetch all configs
        const response = await configService.getAllConfigs()
        
        // Map to frontend format with just the fields we have
        activePeriods.value = response.data.map(config => ({
          id: config.id,
          startDate: new Date(config.startDate),
          endDate: new Date(config.endDate),
          modified_at: new Date(config.modified_at || new Date())
        }))
      } catch (error) {
        console.error('Error loading active periods:', error)
        store.commit('showToast', { severity: 'error', summary: 'Eroare', detail: 'Nu s-au putut încărca perioadele active' })
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca perioadele de examinare',
          life: 5000
        })
      } finally {
        loading.activePeriods = false
      }
    }
    
    // Edit period
    const editPeriod = (period) => {
      editMode.value = true
      editId.value = period.id
      
      // Set form values - only dateRange is needed
      periodForm.dateRange = [new Date(period.startDate), new Date(period.endDate)]
    }
    
    // Delete period (since we don't have a status field in the database)
    const togglePeriodStatus = (period) => {
      const formattedStart = formatDate(period.startDate)
      const formattedEnd = formatDate(period.endDate)
      
      // Use a setTimeout with 0 delay to break the event handling chain and prevent double triggering
      setTimeout(() => {
        confirm.require({
          header: `Confirmare ștergere perioadă`,
          message: `Sunteți sigur că doriți să ștergeți perioada ${formattedStart} - ${formattedEnd}?`,
          icon: 'pi pi-exclamation-triangle',
          acceptLabel: 'Da',
          rejectLabel: 'Nu',
          accept: async () => {
            try {
            // Delete the period
            await configService.deleteConfig(period.id)
            
            // Remove from local state
            activePeriods.value = activePeriods.value.filter(p => p.id !== period.id)
            
            store.dispatch('notifications/showNotification', {
              severity: 'success',
              summary: 'Perioadă Ștearsă',
              detail: `Perioada de examen a fost ștearsă cu succes`,
              life: 3000
            })
          } catch (error) {
            console.error('Error deleting period:', error)
            
            store.dispatch('notifications/showNotification', {
              severity: 'error',
              summary: 'Eroare',
              detail: 'Nu s-a putut șterge perioada de examen',
              life: 5000
            })
          }
        }})
      }, 0)
    }
    
    // Reset form
    const resetForm = () => {
      v$.value.$reset();
      editMode.value = false;
      editId.value = null;
      periodForm.dateRange = null;
    }
    
    // Save period
    const savePeriod = async () => {
      v$.value.$touch()
      
      if (v$.value.$invalid) {
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Validare',
          detail: 'Corectați erorile din formular înainte de a continua',
          life: 3000
        })
        return
      }
      
      try {
        formSubmitting.value = true
        
        // Create request data with proper naming to match backend expectations
        // Format dates without timezone info to be compatible with PostgreSQL
        const startDate = new Date(periodForm.dateRange[0]);
        const endDate = new Date(periodForm.dateRange[1]);
        
        // Format as YYYY-MM-DD HH:MM:SS without timezone info
        const formatDateWithoutTZ = (date) => {
          return date.getFullYear() + '-' + 
                 String(date.getMonth() + 1).padStart(2, '0') + '-' + 
                 String(date.getDate()).padStart(2, '0') + ' ' + 
                 String(date.getHours()).padStart(2, '0') + ':' + 
                 String(date.getMinutes()).padStart(2, '0') + ':' + 
                 String(date.getSeconds()).padStart(2, '0');
        };
        
        // Our service will convert these to snake_case when sending to API
        const data = {
          startDate: formatDateWithoutTZ(startDate),
          endDate: formatDateWithoutTZ(endDate)
        }
        
        console.log('Sending data to backend:', data);
        
        let response;
        if (editMode.value) {
          // Update existing config via API
          response = await configService.updateConfig(editId.value, data)
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Perioadă Examen Actualizată',
            detail: 'Perioada de examen a fost actualizată cu succes',
            life: 3000
          })
        } else {
          // Create new config via API
          response = await configService.createConfig(data)
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Perioadă Examen Creată',
            detail: 'Perioada de examen a fost creată cu succes',
            life: 3000
          })
        }
        
        // Refresh the periods list
        await loadActivePeriods()
        
        // Reset form
        resetForm()
      } catch (error) {
        console.error('Error saving period:', error)
        console.error('Error response:', error.response?.data)
        
        // Create a more detailed error message
        let errorDetail = 'Nu s-a putut salva perioada de examen'
        
        if (error.response?.data?.detail) {
          if (Array.isArray(error.response.data.detail)) {
            // Handle validation errors array
            errorDetail = error.response.data.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join('; ')
          } else {
            // Handle string error
            errorDetail = error.response.data.detail
          }
        }
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare Validare',
          detail: errorDetail,
          life: 5000
        })
      } finally {
        formSubmitting.value = false
      }
    }
    
    // Initialize
    onMounted(() => {
      loadActivePeriods()
    })
    
    return {
      loading,
      activePeriods,
      editMode,
      periodTypes,
      periodForm,
      formSubmitting,
      v$,
      formatDate,
      editPeriod,
      togglePeriodStatus,
      resetForm,
      savePeriod
    }
  }
}
</script>

<style lang="scss" scoped>
.configure-periods {
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
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e9ecef;
  }
  
  .config-info {
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
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1.5rem;
    
    .p-button {
      margin-left: 0.5rem;
    }
  }
  
  .required-field {
    color: #f44336;
  }
  
  :deep(.p-invalid) {
    border-color: #f44336;
  }
  
  .p-error {
    color: #f44336;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
}
</style>
