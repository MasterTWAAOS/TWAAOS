import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// PrimeVue imports
import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/saga-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

// Custom components and UI elements
import Button from 'primevue/button'
import Card from 'primevue/card'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmationService from 'primevue/confirmationservice'

// Import global styles
import './assets/styles/main.scss'

const app = createApp(App)

// Register PrimeVue components
app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)
app.use(router)
app.use(store)

// Register global components
app.component('Button', Button)
app.component('Card', Card)
app.component('Dialog', Dialog)
app.component('InputText', InputText)
app.component('Dropdown', Dropdown)
app.component('Calendar', Calendar)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)

app.mount('#app')
