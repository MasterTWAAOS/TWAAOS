<template>
  <div class="notification-container">
    <Toast position="top-right" />
  </div>
</template>

<script>
import { onMounted, onBeforeUnmount } from 'vue'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

export default {
  name: 'NotificationContainer',
  components: {
    Toast
  },
  setup() {
    const toast = useToast()
    
    onMounted(() => {
      // Make the toast service globally available for use by the Vuex notifications module
      window.$toast = toast
    })
    
    onBeforeUnmount(() => {
      // Clean up
      delete window.$toast
    })
    
    return {}
  }
}
</script>

<style scoped>
.notification-container {
  /* Empty style block needed for scoped styles */
}
</style>
