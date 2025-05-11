<template>
  <div class="manage-users">
    <h1>Gestionare Utilizatori</h1>
    
    <div class="p-d-flex p-jc-between p-ai-center p-mb-3">
      <div class="p-d-flex p-ai-center">
        <Button 
          label="Adăugare Utilizator" 
          icon="pi pi-plus" 
          @click="openAddUserDialog"
          class="p-mr-2"
        />
        <Button 
          label="Import Utilizatori" 
          icon="pi pi-upload" 
          class="p-button-outlined"
          @click="openImportDialog"
        />
      </div>
      
      <span class="p-input-icon-left">
        <i class="pi pi-search" />
        <InputText v-model="filters.global" placeholder="Căutare..." />
      </span>
    </div>
    
    <DataTable 
      :value="users" 
      :paginator="true" 
      :rows="10"
      :loading="loading"
      v-model:filters="filters"
      filterDisplay="menu"
      :rowHover="true"
      responsiveLayout="scroll"
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="Afișare {first} până la {last} din {totalRecords} utilizatori"
      :rowsPerPageOptions="[10, 25, 50]"
      dataKey="id"
    >
      <Column field="email" header="Email" :sortable="true" style="min-width: 14rem">
        <template #body="slotProps">
          <span>{{ slotProps.data.email }}</span>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText v-model="filterModel.value" @input="filterCallback()" class="p-column-filter" placeholder="Căutare email" />
        </template>
      </Column>
      
      <Column field="name" header="Nume" :sortable="true" style="min-width: 12rem">
        <template #filter="{ filterModel, filterCallback }">
          <InputText v-model="filterModel.value" @input="filterCallback()" class="p-column-filter" placeholder="Căutare nume" />
        </template>
      </Column>
      
      <Column field="role" header="Rol" :sortable="true" style="min-width: 10rem">
        <template #body="slotProps">
          <Tag :value="getRoleName(slotProps.data.role)" :severity="getRoleSeverity(slotProps.data.role)" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <Dropdown 
            v-model="filterModel.value" 
            @change="filterCallback()"
            :options="roleOptions" 
            optionLabel="name"
            optionValue="value"
            placeholder="Toate rolurile"
            class="p-column-filter" 
          />
        </template>
      </Column>
      
      <Column field="faculty" header="Facultate" :sortable="true" style="min-width: 12rem">
        <template #filter="{ filterModel, filterCallback }">
          <Dropdown 
            v-model="filterModel.value" 
            @change="filterCallback()"
            :options="facultyOptions" 
            optionLabel="name"
            optionValue="value"
            placeholder="Toate facultățile"
            class="p-column-filter" 
          />
        </template>
      </Column>
      
      <Column field="status" header="Status" :sortable="true" style="min-width: 8rem">
        <template #body="slotProps">
          <Tag :value="slotProps.data.status ? 'Activ' : 'Inactiv'" :severity="slotProps.data.status ? 'success' : 'danger'" />
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <TriStateCheckbox 
            v-model="filterModel.value" 
            @change="filterCallback()"
          />
        </template>
      </Column>
      
      <Column field="lastLogin" header="Ultima Autentificare" :sortable="true" style="min-width: 10rem">
        <template #body="slotProps">
          <span>{{ formatDate(slotProps.data.lastLogin) }}</span>
        </template>
      </Column>
      
      <Column header="Acțiuni" style="min-width: 10rem">
        <template #body="slotProps">
          <Button 
            icon="pi pi-pencil" 
            class="p-button-rounded p-button-success p-mr-2" 
            @click="editUser(slotProps.data)"
          />
          <Button 
            :icon="slotProps.data.status ? 'pi pi-ban' : 'pi pi-check'" 
            :class="slotProps.data.status ? 'p-button-rounded p-button-secondary p-mr-2' : 'p-button-rounded p-button-success p-mr-2'" 
            @click="toggleUserStatus(slotProps.data)"
          />
          <Button 
            icon="pi pi-trash" 
            class="p-button-rounded p-button-danger" 
            @click="confirmDeleteUser(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
    
    <!-- Add/Edit User Dialog -->
    <Dialog 
      v-model:visible="userDialog.visible" 
      :header="userDialog.isNew ? 'Adăugare Utilizator' : 'Editare Utilizator'" 
      :style="{width: '500px'}" 
      :modal="true"
      :closable="!userDialog.loading"
      :closeOnEscape="!userDialog.loading"
    >
      <div class="p-fluid">
        <div class="p-field">
          <label for="email">Email <span class="required-field">*</span></label>
          <InputText 
            id="email" 
            v-model="userDialog.user.email" 
            :class="{'p-invalid': userDialog.submitted && !userDialog.user.email}"
            :disabled="!userDialog.isNew || userDialog.loading"
          />
          <small class="p-error" v-if="userDialog.submitted && !userDialog.user.email">Emailul este obligatoriu.</small>
        </div>
        
        <div class="p-field">
          <label for="name">Nume <span class="required-field">*</span></label>
          <InputText 
            id="name" 
            v-model="userDialog.user.name" 
            :class="{'p-invalid': userDialog.submitted && !userDialog.user.name}"
            :disabled="userDialog.loading"
          />
          <small class="p-error" v-if="userDialog.submitted && !userDialog.user.name">Numele este obligatoriu.</small>
        </div>
        
        <div class="p-field">
          <label for="role">Rol <span class="required-field">*</span></label>
          <Dropdown 
            id="role" 
            v-model="userDialog.user.role" 
            :options="roleOptions" 
            optionLabel="name"
            optionValue="value"
            placeholder="Selectați rolul"
            :class="{'p-invalid': userDialog.submitted && !userDialog.user.role}"
            :disabled="userDialog.loading"
          />
          <small class="p-error" v-if="userDialog.submitted && !userDialog.user.role">Rolul este obligatoriu.</small>
        </div>
        
        <div class="p-field">
          <label for="faculty">Facultate <span class="required-field">*</span></label>
          <Dropdown 
            id="faculty" 
            v-model="userDialog.user.faculty" 
            :options="facultyOptions" 
            optionLabel="name"
            optionValue="value"
            placeholder="Selectați facultatea"
            :class="{'p-invalid': userDialog.submitted && !userDialog.user.faculty}"
            :disabled="userDialog.loading"
          />
          <small class="p-error" v-if="userDialog.submitted && !userDialog.user.faculty">Facultatea este obligatorie.</small>
        </div>
        
        <div v-if="userDialog.isNew" class="p-field">
          <label for="password">Parola <span class="required-field">*</span></label>
          <Password 
            id="password" 
            v-model="userDialog.user.password" 
            :toggleMask="true"
            :class="{'p-invalid': userDialog.submitted && !userDialog.user.password}"
            :disabled="userDialog.loading"
          />
          <small class="p-error" v-if="userDialog.submitted && !userDialog.user.password">Parola este obligatorie.</small>
        </div>
        
        <div v-if="userDialog.isNew" class="p-field">
          <label for="confirmPassword">Confirmare Parola <span class="required-field">*</span></label>
          <Password 
            id="confirmPassword" 
            v-model="userDialog.user.confirmPassword" 
            :toggleMask="true"
            :class="{'p-invalid': userDialog.submitted && !passwordsMatch}"
            :disabled="userDialog.loading"
          />
          <small class="p-error" v-if="userDialog.submitted && !passwordsMatch">Parolele nu coincid.</small>
        </div>
        
        <div class="p-field-checkbox">
          <Checkbox 
            id="status" 
            v-model="userDialog.user.status" 
            :binary="true"
            :disabled="userDialog.loading"
          />
          <label for="status">Utilizator Activ</label>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="closeUserDialog"
          :disabled="userDialog.loading"
        />
        <Button 
          label="Salvare" 
          icon="pi pi-check" 
          @click="saveUser"
          :loading="userDialog.loading"
        />
      </template>
    </Dialog>
    
    <!-- Import Users Dialog -->
    <Dialog 
      v-model:visible="importDialog.visible" 
      header="Import Utilizatori" 
      :style="{width: '500px'}" 
      :modal="true"
    >
      <div class="p-fluid">
        <div class="p-field">
          <label for="importFile">Fișier CSV sau Excel</label>
          <div class="p-inputgroup">
            <InputText 
              id="importFile" 
              v-model="importDialog.fileName" 
              placeholder="Selectați un fișier" 
              disabled
            />
            <Button 
              icon="pi pi-upload" 
              @click="triggerFileInput"
            />
            <input 
              ref="fileInput" 
              type="file" 
              accept=".csv,.xlsx,.xls" 
              style="display: none"
              @change="onFileSelected"
            />
          </div>
          <small class="helper-text">
            Fișierul trebuie să conțină următoarele coloane: Email, Nume, Rol, Facultate
          </small>
        </div>
        
        <div class="p-field-checkbox">
          <Checkbox 
            id="sendEmails" 
            v-model="importDialog.sendEmails" 
            :binary="true"
          />
          <label for="sendEmails">Trimite emailuri de notificare utilizatorilor importați</label>
        </div>
        
        <div class="p-field-checkbox">
          <Checkbox 
            id="overwriteExisting" 
            v-model="importDialog.overwriteExisting" 
            :binary="true"
          />
          <label for="overwriteExisting">Suprascrie utilizatorii existenți</label>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulare" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="importDialog.visible = false"
          :disabled="importDialog.loading"
        />
        <Button 
          label="Importă" 
          icon="pi pi-check" 
          @click="importUsers"
          :loading="importDialog.loading"
          :disabled="!importDialog.file"
        />
      </template>
    </Dialog>
    
    <!-- Confirm Dialog -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useConfirm } from 'primevue/useconfirm'
import { FilterMatchMode, FilterOperator } from 'primevue/api'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Password from 'primevue/password'
import Checkbox from 'primevue/checkbox'
import TriStateCheckbox from 'primevue/tristatecheckbox'
import Tag from 'primevue/tag'
import ConfirmDialog from 'primevue/confirmdialog'
import UserService from '@/services/user.service'

export default {
  name: 'ManageUsersView',
  components: {
    DataTable,
    Column,
    Button,
    Dialog,
    InputText,
    Dropdown,
    Password,
    Checkbox,
    TriStateCheckbox,
    Tag,
    ConfirmDialog
  },
  setup() {
    const store = useStore()
    const confirm = useConfirm()
    const fileInput = ref(null)
    
    // Loading state
    const loading = ref(false)
    
    // Users list
    const users = ref([])
    
    // Filter state
    const filters = ref({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
      email: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
      name: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
      role: { value: null, matchMode: FilterMatchMode.EQUALS },
      faculty: { value: null, matchMode: FilterMatchMode.EQUALS },
      status: { value: null, matchMode: FilterMatchMode.EQUALS }
    })
    
    // Role options
    const roleOptions = ref([
      { name: 'Administrator', value: 'ADMIN' },
      { name: 'Secretariat', value: 'SECRETARIAT' },
      { name: 'Profesor', value: 'PROFESSOR' },
      { name: 'Student (Șef Grupă)', value: 'STUDENT' }
    ])
    
    // Faculty options
    const facultyOptions = ref([
      { name: 'Facultatea de Inginerie Electrică și Știința Calculatoarelor', value: 'FIESC' },
      { name: 'Facultatea de Inginerie Mecanică', value: 'FIM' },
      { name: 'Facultatea de Științe Economice', value: 'FSE' },
      { name: 'Facultatea de Litere și Științe ale Comunicării', value: 'FLSC' }
    ])
    
    // User dialog state
    const userDialog = reactive({
      visible: false,
      isNew: true,
      submitted: false,
      loading: false,
      user: {
        id: null,
        email: '',
        name: '',
        role: null,
        faculty: null,
        password: '',
        confirmPassword: '',
        status: true,
        lastLogin: null
      }
    })
    
    // Import dialog state
    const importDialog = reactive({
      visible: false,
      loading: false,
      file: null,
      fileName: '',
      sendEmails: true,
      overwriteExisting: false
    })
    
    // Computed for password matching
    const passwordsMatch = computed(() => {
      if (!userDialog.isNew) return true
      return userDialog.user.password === userDialog.user.confirmPassword
    })
    
    // Format date
    const formatDate = (dateString) => {
      if (!dateString) return 'Niciodată'
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ro-RO', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
    
    // Get role name
    const getRoleName = (roleValue) => {
      const role = roleOptions.value.find(r => r.value === roleValue)
      return role ? role.name : roleValue
    }
    
    // Get role severity for tag
    const getRoleSeverity = (role) => {
      switch(role) {
        case 'ADMIN':
          return 'danger'
        case 'SECRETARIAT':
          return 'info'
        case 'PROFESSOR':
          return 'success'
        case 'STUDENT':
          return 'warning'
        default:
          return null
      }
    }
    
    // Open add user dialog
    const openAddUserDialog = () => {
      userDialog.user = {
        id: null,
        email: '',
        name: '',
        role: null,
        faculty: null,
        password: '',
        confirmPassword: '',
        status: true,
        lastLogin: null
      }
      userDialog.isNew = true
      userDialog.submitted = false
      userDialog.visible = true
    }
    
    // Edit user
    const editUser = (user) => {
      userDialog.user = { ...user }
      userDialog.isNew = false
      userDialog.submitted = false
      userDialog.visible = true
    }
    
    // Close user dialog
    const closeUserDialog = () => {
      userDialog.visible = false
      userDialog.submitted = false
    }
    
    // Save user
    const saveUser = async () => {
      userDialog.submitted = true
      
      // Validate form
      if (!userDialog.user.email || !userDialog.user.name || !userDialog.user.role || !userDialog.user.faculty) {
        return
      }
      
      if (userDialog.isNew && (!userDialog.user.password || !passwordsMatch.value)) {
        return
      }
      
      try {
        userDialog.loading = true
        
        if (userDialog.isNew) {
          // In a real implementation, call the API
          // const response = await UserService.createUser(userDialog.user)
          // const newUser = response.data
          
          // For demo purposes, create a new user with ID
          const newUser = {
            ...userDialog.user,
            id: Date.now(),
            lastLogin: null
          }
          
          users.value.unshift(newUser)
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Utilizator Creat',
            detail: `Utilizatorul ${newUser.email} a fost creat cu succes`,
            life: 3000
          })
        } else {
          // In a real implementation, call the API
          // await UserService.updateUser(userDialog.user.id, userDialog.user)
          
          // For demo purposes, update local state
          const index = users.value.findIndex(u => u.id === userDialog.user.id)
          if (index !== -1) {
            users.value[index] = { ...userDialog.user }
          }
          
          store.dispatch('notifications/showNotification', {
            severity: 'success',
            summary: 'Utilizator Actualizat',
            detail: `Utilizatorul ${userDialog.user.email} a fost actualizat cu succes`,
            life: 3000
          })
        }
        
        userDialog.visible = false
        userDialog.submitted = false
      } catch (error) {
        console.error('Error saving user:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'A apărut o eroare la salvarea utilizatorului',
          life: 5000
        })
      } finally {
        userDialog.loading = false
      }
    }
    
    // Toggle user status
    const toggleUserStatus = (user) => {
      const action = user.status ? 'dezactiva' : 'activa'
      
      confirm.require({
        header: `Confirmare ${action} utilizator`,
        message: `Sunteți sigur că doriți să ${action}ți utilizatorul "${user.email}"?`,
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Da',
        rejectLabel: 'Nu',
        accept: async () => {
          try {
            // In a real implementation, call the API
            // await UserService.toggleUserStatus(user.id)
            
            // For demo purposes, update local state
            const index = users.value.findIndex(u => u.id === user.id)
            if (index !== -1) {
              users.value[index].status = !users.value[index].status
            }
            
            store.dispatch('notifications/showNotification', {
              severity: 'success',
              summary: 'Status Actualizat',
              detail: `Utilizatorul a fost ${user.status ? 'dezactivat' : 'activat'} cu succes`,
              life: 3000
            })
          } catch (error) {
            console.error('Error toggling user status:', error)
            
            store.dispatch('notifications/showNotification', {
              severity: 'error',
              summary: 'Eroare',
              detail: 'Nu s-a putut actualiza statusul utilizatorului',
              life: 5000
            })
          }
        }
      })
    }
    
    // Confirm delete user
    const confirmDeleteUser = (user) => {
      confirm.require({
        header: 'Confirmare ștergere',
        message: `Sunteți sigur că doriți să ștergeți utilizatorul "${user.email}"?`,
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Da',
        rejectLabel: 'Nu',
        accept: async () => {
          try {
            // In a real implementation, call the API
            // await UserService.deleteUser(user.id)
            
            // For demo purposes, remove from local state
            users.value = users.value.filter(u => u.id !== user.id)
            
            store.dispatch('notifications/showNotification', {
              severity: 'success',
              summary: 'Utilizator Șters',
              detail: 'Utilizatorul a fost șters cu succes',
              life: 3000
            })
          } catch (error) {
            console.error('Error deleting user:', error)
            
            store.dispatch('notifications/showNotification', {
              severity: 'error',
              summary: 'Eroare',
              detail: 'Nu s-a putut șterge utilizatorul',
              life: 5000
            })
          }
        }
      })
    }
    
    // Open import dialog
    const openImportDialog = () => {
      importDialog.file = null
      importDialog.fileName = ''
      importDialog.visible = true
    }
    
    // Trigger file input
    const triggerFileInput = () => {
      fileInput.value.click()
    }
    
    // Handle file selection
    const onFileSelected = (event) => {
      importDialog.file = event.target.files[0]
      importDialog.fileName = importDialog.file ? importDialog.file.name : ''
    }
    
    // Import users
    const importUsers = async () => {
      if (!importDialog.file) {
        store.dispatch('notifications/showNotification', {
          severity: 'warn',
          summary: 'Fișier Lipsă',
          detail: 'Selectați un fișier pentru import',
          life: 3000
        })
        return
      }
      
      try {
        importDialog.loading = true
        
        // In a real implementation, call the API
        // const formData = new FormData()
        // formData.append('file', importDialog.file)
        // formData.append('sendEmails', importDialog.sendEmails)
        // formData.append('overwriteExisting', importDialog.overwriteExisting)
        // const response = await UserService.importUsers(formData)
        
        // For demo purposes, simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Show success notification
        store.dispatch('notifications/showNotification', {
          severity: 'success',
          summary: 'Import Reușit',
          detail: 'Utilizatorii au fost importați cu succes',
          life: 3000
        })
        
        // Close dialog and refresh users
        importDialog.visible = false
        loadUsers()
      } catch (error) {
        console.error('Error importing users:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut importa utilizatorii',
          life: 5000
        })
      } finally {
        importDialog.loading = false
      }
    }
    
    // Load users
    const loadUsers = async () => {
      try {
        loading.value = true
        
        // In a real implementation, call the API
        // const response = await UserService.getAllUsers()
        // users.value = response.data
        
        // For demo purposes, use mock data
        await new Promise(resolve => setTimeout(resolve, 800))
        
        users.value = [
          {
            id: 1,
            email: 'admin@examens.ro',
            name: 'Administrator Sistem',
            role: 'ADMIN',
            faculty: 'FIESC',
            status: true,
            lastLogin: new Date(2025, 4, 11, 15, 30)
          },
          {
            id: 2,
            email: 'secretariat@fiesc.ro',
            name: 'Secretariat FIESC',
            role: 'SECRETARIAT',
            faculty: 'FIESC',
            status: true,
            lastLogin: new Date(2025, 4, 11, 14, 25)
          },
          {
            id: 3,
            email: 'prof.ionescu@fiesc.ro',
            name: 'Prof. Dr. Maria Ionescu',
            role: 'PROFESSOR',
            faculty: 'FIESC',
            status: true,
            lastLogin: new Date(2025, 4, 10, 9, 15)
          },
          {
            id: 4,
            email: 'prof.popescu@fiesc.ro',
            name: 'Prof. Dr. Ion Popescu',
            role: 'PROFESSOR',
            faculty: 'FIESC',
            status: true,
            lastLogin: new Date(2025, 4, 9, 11, 45)
          },
          {
            id: 5,
            email: 'student.cti3a@stud.usv.ro',
            name: 'Student CTI3A',
            role: 'STUDENT',
            faculty: 'FIESC',
            status: true,
            lastLogin: new Date(2025, 4, 10, 16, 20)
          },
          {
            id: 6,
            email: 'student.is2@stud.usv.ro',
            name: 'Student IS2',
            role: 'STUDENT',
            faculty: 'FIESC',
            status: true,
            lastLogin: new Date(2025, 4, 8, 10, 10)
          },
          {
            id: 7,
            email: 'prof.inactive@fiesc.ro',
            name: 'Profesor Inactiv',
            role: 'PROFESSOR',
            faculty: 'FIESC',
            status: false,
            lastLogin: new Date(2025, 3, 15, 12, 30)
          }
        ]
      } catch (error) {
        console.error('Error loading users:', error)
        
        store.dispatch('notifications/showNotification', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca utilizatorii',
          life: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Initialize
    onMounted(() => {
      loadUsers()
    })
    
    return {
      loading,
      users,
      filters,
      roleOptions,
      facultyOptions,
      userDialog,
      importDialog,
      fileInput,
      passwordsMatch,
      formatDate,
      getRoleName,
      getRoleSeverity,
      openAddUserDialog,
      editUser,
      closeUserDialog,
      saveUser,
      toggleUserStatus,
      confirmDeleteUser,
      openImportDialog,
      triggerFileInput,
      onFileSelected,
      importUsers
    }
  }
}
</script>

<style lang="scss" scoped>
.manage-users {
  h1 {
    color: #2c3e50;
    font-size: 1.75rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
  }
  
  .required-field {
    color: #f44336;
  }
  
  .helper-text {
    display: block;
    color: #6c757d;
    margin-top: 0.25rem;
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
