<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-header">
        <picture>
          <!-- Use SVG as primary format (better for scaling) -->
          <source srcset="@/assets/images/logo.svg" type="image/svg+xml">
          <!-- Fallback to PNG if SVG not supported -->
          <img src="@/assets/images/logo.png" alt="FIESC Logo" class="auth-logo" onerror="this.onerror=null; this.src='/logo.png';" />
        </picture>
        <h1>FIESC - Planificarea Examenelor</h1>
      </div>
      
      <div class="auth-content">
        <router-view />
      </div>
      
      <div class="auth-footer">
        <p>&copy; {{ currentYear }} Universitatea Ștefan cel Mare din Suceava. Toate drepturile rezervate.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'AuthLayout',
  setup() {
    const currentYear = ref(new Date().getFullYear())
    
    return {
      currentYear
    }
  }
}
</script>

<style lang="scss" scoped>
.auth-layout {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 1rem;
}

.auth-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  padding: 2rem;
  text-align: center;
}

.auth-header {
  margin-bottom: 2rem;
  
  .auth-logo {
    height: 60px;
    margin-bottom: 1rem;
    object-fit: contain;
    max-width: 100%;
  }
  
  picture {
    display: inline-block;
    line-height: 0;
  }
  
  h1 {
    font-size: 1.5rem;
    color: #2c3e50;
    font-weight: 500;
  }
}

.auth-content {
  margin-bottom: 2rem;
}

.auth-footer {
  color: #6c757d;
  font-size: 0.875rem;
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
}
</style>
