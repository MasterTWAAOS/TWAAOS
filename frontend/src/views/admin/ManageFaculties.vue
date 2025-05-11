<template>
  <div class="manage-faculties">
    <h1>Gestionare Facultăți</h1>
    
    <div class="p-d-flex p-jc-between p-ai-center p-mb-3">
      <Button 
        label="Adăugare Facultate" 
        icon="pi pi-plus" 
        @click="openAddFacultyDialog"
      />
      
      <span class="p-input-icon-left">
        <i class="pi pi-search" />
        <InputText v-model="filters.global" placeholder="Căutare..." />
      </span>
    </div>
    
    <DataTable 
      :value="faculties" 
      :paginator="true" 
      :rows="10"
      :loading="loading"
      v-model:filters="filters"
      filterDisplay="menu"
      :rowHover="true"
      responsiveLayout="scroll"
      dataKey="id"
    >
      <Column field="name" header="Denumire" :sortable="true">
        <template #filter="{ filterModel, filterCallback }">
          <InputText v-model="filterModel.value" @input="filterCallback()" class="p-column-filter" placeholder="Căutare..." />
        </template>
      </Column>
      
      <Column field="code" header="Cod" :sortable="true">
        <template #filter="{ filterModel, filterCallback }">
          <InputText v-model="filterModel.value" @input="filterCallback()" class="p-column-filter" placeholder="Căutare..." />
        </template>
      </Column>
      
      <Column field="departments" header="Departamente" style="min-width: 8rem">
        <template #body="slotProps">
          <Badge :value="slotProps.data.departments.length" severity="info" />
        </template>
      </Column>
      
      <Column field="groups" header="Grupe" style="min-width: 8rem">
        <template #body="slotProps">
          <Badge :value="slotProps.data.groups.length" severity="info" />
        </template>
      </Column>
      
      <Column field="status" header="Status" :sortable="true" style="min-width: 8rem">
        <template #body="slotProps">
          <Tag :value="slotProps.data.status ? 'Activă' : 'Inactivă'" :severity="slotProps.data.status ? 'success' : 'danger'" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <TriStateCheckbox 
            v-model="filterModel.value" 
            @change="filterCallback()"
          />
        </template>
      </Column>
      
      <Column header="Acțiuni" style="min-width: 10rem">
        <template #body="slotProps">
          <Button 
            icon="pi pi-pencil" 
            class="p-button-rounded p-button-success p-mr-2" 
            @click="editFaculty(slotProps.data)"
          />
          <Button 
            :icon="slotProps.data.status ? 'pi pi-ban' : 'pi pi-check'" 
            :class="slotProps.data.status ? 'p-button-rounded p-button-secondary p-mr-2' : 'p-button-rounded p-button-success p-mr-2'" 
            @click="toggleFacultyStatus(slotProps.data)"
          />
          <Button 
            icon="pi pi-trash" 
            class="p-button-rounded p-button-danger" 
            @click="confirmDeleteFaculty(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
    
    <!-- Faculty Dialog -->
    <Dialog 
      v-model:visible="facultyDialog.visible" 
      :header="facultyDialog.isNew ? 'Adăugare Facultate' : 'Editare Facultate'" 
      :style="{width: '500px'}" 
      :modal="true"
    >
      <div class="p-fluid">
        <div class="p-field">
          <label for="name">Denumire <span class="required-field">*</span></label>
          <InputText 
            id="name" 
            v-model="facultyDialog.faculty.name" 
            :class="{'p-invalid': facultyDialog.submitted && !facultyDialog.faculty.name}"
          />
          <small class="p-error" v-if="facultyDialog.submitted && !facultyDialog.faculty.name">Denumirea este obligatorie.</small>
        </div>
        
        <div class="p-field">
          <label for="code">Cod <span class="required-field">*</span></label>
          <InputText 
            id="code" 
            v-model="facultyDialog.faculty.code" 
            :class="{'p-invalid': facultyDialog.submitted && !facultyDialog.faculty.code}"
          />
          <small class="p-error" v-if="facultyDialog.submitted && !facultyDialog.faculty.code">Codul este obligatoriu.</small>
        </div>
        
        <div class="p-field">
          <label for="description">Descriere</label>
          <Textarea 
            id="description" 
            v-model="facultyDialog.faculty.description" 
            rows="3" 
          />
        </div>
        
        <div class="p-field-checkbox">
          <Checkbox 
            id="status" 
            v-model="facultyDialog.faculty.status" 
            :binary="true"
          />
          <label for="status">Facultate Activă</label>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="facultyDialog.visible = false"
        />
        <Button 
          label="Salvare" 
          icon="pi pi-check" 
          @click="saveFaculty"
        />
      </template>
    </Dialog>
    
    <!-- Confirm Dialog -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useConfirm } from 'primevue/useconfirm'
import { FilterMatchMode, FilterOperator } from 'primevue/api'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'
import TriStateCheckbox from 'primevue/tristatecheckbox'
import Tag from 'primevue/tag'
import Badge from 'primevue/badge'
import ConfirmDialog from 'primevue/confirmdialog'
import AdminService from '@/services/admin.service'

export default {
  name: 'ManageFacultiesView',
  components: {
    DataTable,
    Column,
    Button,
    Dialog,
    InputText,
    Textarea,
    Checkbox,
    TriStateCheckbox,
    Tag,
    Badge,
    ConfirmDialog
  },
  setup() {
    const store = useStore()
    const confirm = useConfirm()
    
    // Loading state
    const loading = ref(false)
    
    // Faculties list
    const faculties = ref([])
    
    // Filter state
    const filters = ref({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
      name: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
      code: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
      status: { value: null, matchMode: FilterMatchMode.EQUALS }
    })
    
    // Faculty dialog state
    const facultyDialog = reactive({
      visible: false,
      isNew: true,
      submitted: false,
      faculty: {
        id: null,
        name: '',
        code: '',
        description: '',
        status: true,
        departments: [],
        groups: []
      }
    })
    
    // Open add faculty dialog
    const openAddFacultyDialog = () => {
      facultyDialog.faculty = {
        id: null,
        name: '',
        code: '',
        description: '',
        status: true,
        departments: [],
        groups: []
      }
      facultyDialog.isNew = true
      facultyDialog.submitted = false
      facultyDialog.visible = true
    }
    
    // Edit faculty
    const editFaculty = (faculty) => {
      facultyDialog.faculty = { ...faculty }
      facultyDialog.isNew = false
      facultyDialog.submitted = false
      facultyDialog.visible = true
    }
    
    // Save faculty
    const saveFaculty = async () => {
      facultyDialog.submitted = true
      
      // Validate form
      if (!facultyDialog.faculty.name || !facultyDialog.faculty.code) {
        return
      }
      
      try {
        if (facultyDialog.isNew) {
          // In a real implementation, call the API
          // const response = await AdminService.createFaculty(facultyDialog.faculty)
          // const newFaculty = response.data
          
          // For demo purposes, create a new faculty with ID
          const newFaculty = {
            ...facultyDialog.faculty,
            id: Date.now()
          }
          
          faculties.value.unshift(newFaculty)
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Facultate Creată',
            detail: `Facultatea ${newFaculty.name} a fost creată cu succes`,
            life: 3000
          })
        } else {
          // In a real implementation, call the API
          // await AdminService.updateFaculty(facultyDialog.faculty.id, facultyDialog.faculty)
          
          // For demo purposes, update local state
          const index = faculties.value.findIndex(f => f.id === facultyDialog.faculty.id)
          if (index !== -1) {
            faculties.value[index] = { ...facultyDialog.faculty }
          }
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Facultate Actualizată',
            detail: `Facultatea ${facultyDialog.faculty.name} a fost actualizată cu succes`,
            life: 3000
          })
        }
        
        facultyDialog.visible = false
        facultyDialog.submitted = false
      } catch (error) {
        console.error('Error saving faculty:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la salvarea facultății',
          life: 5000
        })
      }
    }
    
    // Toggle faculty status
    const toggleFacultyStatus = (faculty) => {
      const action = faculty.status ? 'dezactiva' : 'activa'
      
      confirm.require({
        header: `Confirmare ${action} facultate`,
        message: `Sunteți sigur că doriți să ${action}ți facultatea "${faculty.name}"?`,
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Da',
        rejectLabel: 'Nu',
        accept: async () => {
          try {
            // In a real implementation, call the API
            // await AdminService.toggleFacultyStatus(faculty.id)
            
            // For demo purposes, update local state
            const index = faculties.value.findIndex(f => f.id === faculty.id)
            if (index !== -1) {
              faculties.value[index].status = !faculties.value[index].status
            }
            
            store.dispatch('notifications/showNotification', {
              severity: 'success',
              summary: 'Status Actualizat',
              detail: `Facultatea a fost ${faculty.status ? 'dezactivată' : 'activată'} cu succes`,
              life: 3000
            })
          } catch (error) {
            console.error('Error toggling faculty status:', error)
            
            store.dispatch('notifications/showNotification', {
              severity: 'error',
              summary: 'Eroare',
              detail: 'Nu s-a putut actualiza statusul facultății',
              life: 5000
            })
          }
        }
      })
    }
    
    // Confirm delete faculty
    const confirmDeleteFaculty = (faculty) => {
      confirm.require({
        header: 'Confirmare ștergere',
        message: `Sunteți sigur că doriți să ștergeți facultatea "${faculty.name}"?`,
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Da',
        rejectLabel: 'Nu',
        accept: async () => {
          try {
            // In a real implementation, call the API
            // await AdminService.deleteFaculty(faculty.id)
            
            // For demo purposes, remove from local state
            faculties.value = faculties.value.filter(f => f.id !== faculty.id)
            
            store.dispatch('notifications/showNotification', {
              severity: 'success',
              summary: 'Facultate Ștearsă',
              detail: 'Facultatea a fost ștearsă cu succes',
              life: 3000
            })
          } catch (error) {
            console.error('Error deleting faculty:', error)
            
            store.dispatch('notifications/showNotification', {
              severity: 'error',
              summary: 'Eroare',
              detail: 'Nu s-a putut șterge facultatea',
              life: 5000
            })
          }
        }
      })
    }
    
    // Load faculties
    const loadFaculties = async () => {
      try {
        loading.value = true
        
        // In a real implementation, call the API
        // const response = await AdminService.getAllFaculties()
        // faculties.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 800))
        
        faculties.value = [
          {
            id: 1,
            name: 'Facultatea de Inginerie Electrică și Știința Calculatoarelor',
            code: 'FIESC',
            description: 'Facultatea de Inginerie Electrică și Știința Calculatoarelor din cadrul Universității Ștefan cel Mare',
            status: true,
            departments: [
              { id: 1, name: 'Calculatoare și Automatizări' },
              { id: 2, name: 'Electronică și Telecomunicații' },
              { id: 3, name: 'Electrotehnică' }
            ],
            groups: [
              { id: 1, name: 'CTI1A' },
              { id: 2, name: 'CTI1B' },
              { id: 3, name: 'CTI2A' },
              { id: 4, name: 'CTI2B' },
              { id: 5, name: 'CTI3A' },
              { id: 6, name: 'CTI3B' },
              { id: 7, name: 'CTI4A' },
              { id: 8, name: 'CTI4B' }
            ]
          },
          {
            id: 2,
            name: 'Facultatea de Inginerie Mecanică',
            code: 'FIM',
            description: 'Facultatea de Inginerie Mecanică din cadrul Universității Ștefan cel Mare',
            status: true,
            departments: [
              { id: 4, name: 'Mecanică Aplicată' },
              { id: 5, name: 'Autovehicule și Motoare' }
            ],
            groups: [
              { id: 9, name: 'IM1' },
              { id: 10, name: 'IM2' },
              { id: 11, name: 'IM3' },
              { id: 12, name: 'IM4' }
            ]
          },
          {
            id: 3,
            name: 'Facultatea de Științe Economice',
            code: 'FSE',
            description: 'Facultatea de Științe Economice din cadrul Universității Ștefan cel Mare',
            status: false,
            departments: [
              { id: 6, name: 'Contabilitate și Finanțe' },
              { id: 7, name: 'Management și Administrarea Afacerilor' }
            ],
            groups: [
              { id: 13, name: 'CIG1' },
              { id: 14, name: 'CIG2' },
              { id: 15, name: 'CIG3' }
            ]
          }
        ]
      } catch (error) {
        console.error('Error loading faculties:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca facultățile',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Initialize
    onMounted(() => {
      loadFaculties()
    })
    
    return {
      loading,
      faculties,
      filters,
      facultyDialog,
      openAddFacultyDialog,
      editFaculty,
      saveFaculty,
      toggleFacultyStatus,
      confirmDeleteFaculty
    }
  }
}
</script>

<style lang="scss" scoped>
.manage-faculties {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  .required-field {
    color: #f44336;
  }
  
  :deep(.p-datatable-sm) {
    .p-datatable-thead > tr > th {
      padding: 0.75rem 1rem;
    }
    
    .p-datatable-tbody > tr > td {
      padding: 0.75rem 1rem;
    }
  }
  
  :deep(.p-button-sm) {
    font-size: 0.875rem;
  }
}
</style>
