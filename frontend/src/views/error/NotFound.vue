<template>
  <div class="not-found">
    <div class="error-container">
      <div class="error-code">404</div>
      <h1>Pagină Negăsită</h1>
      <p>Ne pare rău, dar pagina pe care o căutați nu există sau a fost mutată.</p>
      <div class="error-actions">
        <Button 
          label="Înapoi la Dashboard" 
          icon="pi pi-home"
          class="p-button-primary" 
          @click="goToDashboard"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import Button from 'primevue/button'

export default {
  name: 'NotFoundView',
  components: {
    Button
  },
  setup() {
    const router = useRouter()
    const store = useStore()
    const isAuthenticated = store.getters['auth/isAuthenticated']
    
    const goToDashboard = () => {
      if (isAuthenticated) {
        router.push('/')
      } else {
        router.push('/login')
      }
    }
    
    return {
      goToDashboard
    }
  }
}
</script>

<style lang="scss" scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f8f9fa;
  
  .error-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 500px;
    padding: 2rem;
    text-align: center;
    
    .error-code {
      font-size: 6rem;
      font-weight: 700;
      color: #f44336;
      line-height: 1;
      margin-bottom: 1rem;
    }
    
    h1 {
      font-size: 2rem;
      color: #2c3e50;
      margin-bottom: 1rem;
    }
    
    p {
      color: #6c757d;
      margin-bottom: 2rem;
    }
    
    .error-actions {
      margin-top: 1rem;
    }
  }
}
</style>
