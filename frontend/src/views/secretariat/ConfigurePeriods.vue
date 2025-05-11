<template>
  <div class="configure-periods">
    <h1>Configurare Perioade Examene</h1>
    
    <Card>
      <template #content>
        <p class="config-info">
          <i class="pi pi-info-circle"></i>
          Configurați perioadele de examene pentru fiecare sesiune. Aceste perioade vor determina intervalul de timp 
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
              <Column field="name" header="Denumire" :sortable="true"></Column>
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
              <Column field="status" header="Status" :sortable="true" style="width: 15%">
                <template #body="slotProps">
                  <Tag 
                    :value="slotProps.data.active ? 'Activ' : 'Inactiv'" 
                    :severity="slotProps.data.active ? 'success' : 'secondary'"
                  />
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
                    :icon="slotProps.data.active ? 'pi pi-power-off' : 'pi pi-check'" 
                    :class="slotProps.data.active ? 'p-button-danger p-button-sm' : 'p-button-success p-button-sm'" 
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
                    <label for="periodName">Denumire Perioadă <span class="required-field">*</span></label>
                    <InputText 
                      id="periodName" 
                      v-model="periodForm.name" 
                      placeholder="ex: Sesiune Vara 2025"
                      :class="{'p-invalid': v$.name.$invalid && v$.name.$dirty}"
                      @blur="v$.name.$touch()"
                    />
                    <small class="p-error" v-if="v$.name.$invalid && v$.name.$dirty">
                      {{ v$.name.$errors[0].$message }}
                    </small>
                  </div>
                  
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
                  </div>
                  
                  <div class="p-field p-mb-3">
                    <label for="periodType">Tip Perioadă <span class="required-field">*</span></label>
                    <Dropdown 
                      id="periodType" 
                      v-model="periodForm.type" 
                      :options="periodTypes" 
                      optionLabel="name"
                      optionValue="value"
                      placeholder="Selectați tipul de perioadă"
                      :class="{'p-invalid': v$.type.$invalid && v$.type.$dirty}"
                      @blur="v$.type.$touch()"
                    />
                    <small class="p-error" v-if="v$.type.$invalid && v$.type.$dirty">
                      {{ v$.type.$errors[0].$message }}
                    </small>
                  </div>
                  
                  <div class="p-field">
                    <label for="periodDescription">Descriere (opțional)</label>
                    <Textarea 
                      id="periodDescription" 
                      v-model="periodForm.description" 
                      rows="3" 
                      placeholder="Adăugați o descriere pentru această perioadă" 
                    />
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
import { required, minLength } from '@vuelidate/validators'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import ConfirmDialog from 'primevue/confirmdialog'

export default {
  name: 'ConfigurePeriodsView',
  components: {
    Card,
    DataTable,
    Column,
    Button,
    InputText,
    Calendar,
    Dropdown,
    Textarea,
    Tag,
    ConfirmDialog
  },
  setup() {
    const store = useStore()
    const confirm = useConfirm()
    
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
    
    // Form state
    const periodForm = reactive({
      name: '',
      dateRange: null,
      type: null,
      description: ''
    })
    
    // Form submitting state
    const formSubmitting = ref(false)
    
    // Form validation rules
    const rules = computed(() => ({
      name: { required, minLength: minLength(3) },
      dateRange: { required },
      type: { required }
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
        
        // In a real implementation, call the API
        // const response = await periodService.getActivePeriods()
        // activePeriods.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 500))
        
        activePeriods.value = [
          {
            id: 1,
            name: 'Sesiune Iarnă 2025',
            startDate: '2025-01-05',
            endDate: '2025-01-25',
            type: 'EXAM_SESSION',
            description: 'Sesiune ordinară de iarnă pentru toate programele de studiu',
            active: false
          },
          {
            id: 2,
            name: 'Sesiune Vară 2025',
            startDate: '2025-06-05',
            endDate: '2025-06-25',
            type: 'EXAM_SESSION',
            description: 'Sesiune ordinară de vară pentru toate programele de studiu',
            active: true
          },
          {
            id: 3,
            name: 'Sesiune Restanțe Toamnă 2025',
            startDate: '2025-09-01',
            endDate: '2025-09-15',
            type: 'RESIT_SESSION',
            description: 'Sesiune de restanțe pentru toate programele de studiu',
            active: false
          }
        ]
      } catch (error) {
        console.error('Error loading active periods:', error)
        
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
      
      // Set form values
      periodForm.name = period.name
      periodForm.dateRange = [new Date(period.startDate), new Date(period.endDate)]
      periodForm.type = period.type
      periodForm.description = period.description
    }
    
    // Toggle period status
    const togglePeriodStatus = (period) => {
      const action = period.active ? 'dezactiva' : 'activa'
      
      confirm.require({
        header: `Confirmare ${action} perioadă`,
        message: `Sunteți sigur că doriți să ${action}ți perioada "${period.name}"?`,
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Da',
        rejectLabel: 'Nu',
        accept: async () => {
          try {
            // In a real implementation, call the API
            // await periodService.togglePeriodStatus(period.id)
            
            // For demo purposes, update local state
            const index = activePeriods.value.findIndex(p => p.id === period.id)
            if (index !== -1) {
              activePeriods.value[index].active = !activePeriods.value[index].active
            }
            
            store.dispatch('notifications/showNotification', {
              severity: 'success',
              summary: 'Status Actualizat',
              detail: `Perioada a fost ${period.active ? 'dezactivată' : 'activată'} cu succes`,
              life: 3000
            })
          } catch (error) {
            console.error('Error toggling period status:', error)
            
            store.dispatch('notifications/showNotification', {
              severity: 'error',
              summary: 'Eroare',
              detail: 'Nu s-a putut actualiza statusul perioadei',
              life: 5000
            })
          }
        }
      })
    }
    
    // Reset form
    const resetForm = () => {
      v$.value.$reset()
      editMode.value = false
      editId.value = null
      periodForm.name = ''
      periodForm.dateRange = null
      periodForm.type = null
      periodForm.description = ''
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
        
        // Create request data
        const data = {
          name: periodForm.name,
          startDate: periodForm.dateRange[0].toISOString().split('T')[0],
          endDate: periodForm.dateRange[1].toISOString().split('T')[0],
          type: periodForm.type,
          description: periodForm.description
        }
        
        if (editMode.value) {
          // In a real implementation, call the API
          // await periodService.updatePeriod(editId.value, data)
          
          // For demo purposes, update local state
          const index = activePeriods.value.findIndex(p => p.id === editId.value)
          if (index !== -1) {
            activePeriods.value[index] = {
              ...activePeriods.value[index],
              ...data
            }
          }
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Perioadă Actualizată',
            detail: 'Perioada a fost actualizată cu succes',
            life: 3000
          })
        } else {
          // In a real implementation, call the API
          // const response = await periodService.createPeriod(data)
          
          // For demo purposes, add to local state with a mock ID
          activePeriods.value.push({
            id: Date.now(),
            ...data,
            active: false
          })
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Perioadă Creată',
            detail: 'Perioada a fost creată cu succes',
            life: 3000
          })
        }
        
        // Reset form
        resetForm()
      } catch (error) {
        console.error('Error saving period:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-a putut salva perioada',
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
