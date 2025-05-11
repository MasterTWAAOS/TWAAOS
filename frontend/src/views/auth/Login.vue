<template>
  <div class="login-view">
    <Card>
      <template #title>
        <h2>Autentificare</h2>
      </template>
      <template #content>
        <div class="login-options p-fluid">
          <!-- Google Sign In Button for SG, CD and SEC roles -->
          <div class="google-login p-mb-3">
            <h3>Utilizatori FIESC</h3>
            <p class="p-mb-3">Șefi de grupă, Cadre didactice și Secretariat</p>
            
            <div id="googleSignInButton" class="p-mt-3">
              <Button 
                class="google-btn p-button-raised" 
                @click="initiateGoogleSignIn"
              >
                <i class="pi pi-google p-mr-2"></i>
                Sign in with Google
              </Button>
            </div>
          </div>
          
          <Divider align="center">
            <span>SAU</span>
          </Divider>
          
          <!-- Admin login form -->
          <div class="admin-login p-mt-3">
            <h3>Administrator</h3>
            <form @submit.prevent="loginAdmin">
              <div class="p-field p-mb-3">
                <label for="username">Utilizator</label>
                <InputText 
                  id="username" 
                  type="text" 
                  v-model="username" 
                  class="p-inputtext-lg"
                  required
                />
              </div>
              
              <div class="p-field p-mb-4">
                <label for="password">Parolă</label>
                <Password 
                  id="password" 
                  v-model="password" 
                  toggleMask 
                  class="p-inputtext-lg" 
                  inputClass="w-full"
                  required
                />
              </div>
              
              <Button 
                type="submit" 
                label="Autentificare" 
                class="p-button-primary p-button-raised p-button-lg w-full"
                :loading="isLoading"
              />
            </form>
          </div>
        </div>
      </template>
    </Card>
    
    <div v-if="errorMessage" class="error-message p-mt-3">
      <Message severity="error">{{ errorMessage }}</Message>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import Password from 'primevue/password'
import Message from 'primevue/message'
import Divider from 'primevue/divider'

export default {
  name: 'LoginView',
  components: {
    Password,
    Message,
    Divider
  },
  setup() {
    const store = useStore()
    const username = ref('')
    const password = ref('')
    const isLoading = computed(() => store.getters['auth/isLoading'])
    const errorMessage = computed(() => store.getters['auth/authError'])
    
    // Method to handle admin login
    const loginAdmin = async () => {
      try {
        await store.dispatch('auth/loginWithCredentials', {
          username: username.value,
          password: password.value
        })
      } catch (error) {
        // Error is handled in store
        console.error('Login failed:', error)
      }
    }
    
    // Method to initiate Google Sign-In
    const initiateGoogleSignIn = () => {
      // In a real implementation, this would integrate with the Google Sign-In API
      // For now, we'll just mock the process for demonstration purposes
      
      // In production, you would use something like:
      // gapi.auth2.getAuthInstance().signIn().then(googleUser => {
      //   const idToken = googleUser.getAuthResponse().id_token
      //   store.dispatch('auth/loginWithGoogle', idToken)
      // })
      
      // Mock implementation for demonstration
      store.dispatch('auth/loginWithGoogle', 'mock_google_token')
        .catch(error => {
          console.error('Google Sign-In failed:', error)
        })
    }
    
    // Clear any previous errors when the component mounts
    onMounted(() => {
      store.dispatch('auth/clearError')
    })
    
    return {
      username,
      password,
      loginAdmin,
      initiateGoogleSignIn,
      isLoading,
      errorMessage
    }
  }
}
</script>

<style lang="scss" scoped>
.login-view {
  .p-card {
    margin-bottom: 1.5rem;
    
    :deep(.p-card-title) {
      h2 {
        color: #2c3e50;
        margin: 0;
        font-weight: 500;
        text-align: center;
      }
    }
  }
  
  .login-options {
    h3 {
      font-size: 1.25rem;
      color: #2c3e50;
      margin-top: 0;
      margin-bottom: 0.5rem;
    }
    
    p {
      color: #6c757d;
      margin-top: 0;
    }
    
    .google-login {
      text-align: center;
      
      .google-btn {
        width: 100%;
        background-color: #ffffff;
        color: #555555;
        border: 1px solid #dddddd;
        
        &:hover {
          background-color: #f8f9fa;
        }
        
        i {
          color: #4285F4;
        }
      }
    }
    
    .admin-login {
      form {
        .w-full {
          width: 100%;
        }
        
        label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
      }
    }
  }
}
</style>
