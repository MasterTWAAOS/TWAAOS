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
            <p class="p-mb-3"><strong>Exclusiv pentru:</strong> Șefi de grupă (SG), Cadre didactice (CD) și Secretariat (SEC)</p>
            
            <!-- Google Sign In Button -->
            <div class="p-mt-3">
              <!-- Google rendered button -->
              <div id="google-signin-button" class="w-full" style="min-height: 40px;"></div>
            </div>
          </div>
          
          <Divider align="center">
            <span>SAU</span>
          </Divider>
          
          <!-- Admin login form -->
          <div class="admin-login p-mt-3">
            <h3>Administrator</h3>
            <p class="p-mb-3"><strong>Exclusiv pentru conturile de administrator (ADM)</strong></p>
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
                  :feedback="false"
                  :mediumRegex="null"
                  :strongRegex="null"
                  :promptLabel="''"
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
    const isDevelopmentMode = computed(() => process.env.VUE_APP_USE_DEV_AUTH === 'true')
    const showFallbackButton = ref(false)
    
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
    const initiateGoogleSignIn = async () => {
      // We can use the computed property now
      if (isDevelopmentMode.value) {
        console.log('Using development mock authentication');
        // For development, show a dropdown to select test user type
        const testUsers = [
          { 
            name: 'Tudor Albu (Student)', 
            email: 'cooled-herbal0s@icloud.com', 
            role: 'SG', 
            googleId: 'dev-tudor-albu',
            groupId: 914  // This should match the ID of the test group created during sync
          },
          { 
            name: 'Matei Neagu (Professor)', 
            email: 'wins_hangers0v@icloud.com', 
            role: 'CD', 
            googleId: 'dev-matei-neagu',
            groupId: null
          },
          { 
            name: 'Alina Berca (Secretariat)', 
            email: 'lentos.paints.0z@icloud.com', 
            role: 'SEC', 
            googleId: 'dev-alina-berca',
            groupId: null
          }
          // Admin users should use traditional login with email/password
        ];
        
        // Create a simple dialog for user selection
        const userSelect = document.createElement('div');
        userSelect.style.position = 'fixed';
        userSelect.style.top = '0';
        userSelect.style.left = '0';
        userSelect.style.width = '100%';
        userSelect.style.height = '100%';
        userSelect.style.backgroundColor = 'rgba(0,0,0,0.5)';
        userSelect.style.display = 'flex';
        userSelect.style.justifyContent = 'center';
        userSelect.style.alignItems = 'center';
        userSelect.style.zIndex = '9999';
        
        const dialog = document.createElement('div');
        dialog.style.backgroundColor = 'white';
        dialog.style.padding = '20px';
        dialog.style.borderRadius = '8px';
        dialog.style.width = '400px';
        dialog.style.maxWidth = '90%';
        dialog.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        
        const title = document.createElement('h3');
        title.innerText = 'Select Test User';
        title.style.marginTop = '0';
        dialog.appendChild(title);
        
        const description = document.createElement('p');
        description.innerText = 'This is a development-only feature to test different user roles.';
        dialog.appendChild(description);
        
        testUsers.forEach(user => {
          const button = document.createElement('button');
          button.innerText = user.name;
          button.style.display = 'block';
          button.style.width = '100%';
          button.style.padding = '10px';
          button.style.margin = '8px 0';
          button.style.backgroundColor = '#4CAF50';
          button.style.color = 'white';
          button.style.border = 'none';
          button.style.borderRadius = '4px';
          button.style.cursor = 'pointer';
          
          button.addEventListener('click', () => {
            // Create a token in the format expected by the backend: email|role|groupId
            // This format matches what the backend expects in development mode
            const mockToken = `${user.email}|${user.role}|${user.groupId || 'null'}`;
            document.body.removeChild(userSelect);
            
            store.dispatch('auth/loginWithGoogle', mockToken)
              .catch(error => {
                console.error('Google Sign-In failed:', error);
              });
          });
          
          dialog.appendChild(button);
        });
        
        // Add a cancel button
        const cancelButton = document.createElement('button');
        cancelButton.innerText = 'Cancel';
        cancelButton.style.display = 'block';
        cancelButton.style.width = '100%';
        cancelButton.style.padding = '10px';
        cancelButton.style.margin = '8px 0';
        cancelButton.style.backgroundColor = '#f44336';
        cancelButton.style.color = 'white';
        cancelButton.style.border = 'none';
        cancelButton.style.borderRadius = '4px';
        cancelButton.style.cursor = 'pointer';
        
        cancelButton.addEventListener('click', () => {
          document.body.removeChild(userSelect);
        });
        
        dialog.appendChild(cancelButton);
        userSelect.appendChild(dialog);
        document.body.appendChild(userSelect);
      } else {
        // Production mode - Use real Google Sign-In API
        try {
          // Check if Google API is loaded
          if (!window.google || !window.google.accounts) {
            console.error('Google API not loaded. Please make sure the Google API script is included.');
            return;
          }
          
          // Initialize Google Sign-In
          const client_id = process.env.VUE_APP_GOOGLE_CLIENT_ID;
          if (!client_id) {
            console.error('Google Client ID not configured');
            return;
          }
          
          console.log('Initializing Google Sign-In with client ID:', client_id);
          
          // Use Google Identity Services API
          if (!window.googleAuthInitialized) {
            google.accounts.id.initialize({
              client_id: client_id,
              callback: handleCredentialResponse,
              auto_select: false,
              cancel_on_tap_outside: true
            });
            window.googleAuthInitialized = true;
            console.log('Google Auth initialized');
          }
          
          // Render the Google Sign-In button explicitly
          // This will display it where we want and ensure correct behavior
          google.accounts.id.renderButton(
            document.getElementById('google-signin-button'), 
            { 
              theme: 'outline', 
              size: 'large',
              width: document.getElementById('google-signin-button').offsetWidth,
              text: 'signin_with',
              logo_alignment: 'center'
            }
          );
          
          // Also show the One Tap UI for convenience
          google.accounts.id.prompt((notification) => {
            if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
              console.log('One Tap UI skipped or not displayed', notification.getNotDisplayedReason() || notification.getSkippedReason());
              // The One Tap UI wasn't displayed, but the button should still work
            }
          });
        } catch (error) {
          console.error('Error initializing Google Sign-In:', error);
        }
      }
    };
    
    // Handle the response from Google Sign-In
    const handleCredentialResponse = (response) => {
      if (response && response.credential) {
        // Send the ID token to the backend
        store.dispatch('auth/loginWithGoogle', response.credential)
          .catch(error => {
            console.error('Google Sign-In authentication failed:', error);
          });
      }
    }
    
    // Initialize auth and clear errors when component mounts
    onMounted(() => {
      store.dispatch('auth/clearError')
      
      // Always initialize Google Sign-In since we only have one button now
      initializeGoogleAuth()
    })
    
    // Function to initialize Google Auth and render the sign-in button
    const initializeGoogleAuth = () => {
      try {
        // Check if Google API is loaded
        if (!window.google || !window.google.accounts) {
          console.error('Google API not loaded. Please check if script is included in index.html');
          return;
        }
        
        const client_id = process.env.VUE_APP_GOOGLE_CLIENT_ID;
        if (!client_id) {
          console.error('Google Client ID not configured');
          return;
        }
        
        console.log('Initializing Google Sign-In with client ID:', client_id);
        
        // Initialize Google Identity Services API
        if (!window.googleAuthInitialized) {
          google.accounts.id.initialize({
            client_id: client_id,
            callback: handleCredentialResponse,
            auto_select: false,
            cancel_on_tap_outside: true
          });
          window.googleAuthInitialized = true;
          console.log('Google Auth initialized');
        }
        
        // Render the Google Sign-In button
        setTimeout(() => {
          const buttonContainer = document.getElementById('google-signin-button');
          if (buttonContainer) {
            google.accounts.id.renderButton(
              buttonContainer, 
              { 
                theme: 'filled_blue', 
                size: 'large',
                shape: 'rectangular',
                width: buttonContainer.offsetWidth || 240,
                text: 'signin_with',
                logo_alignment: 'center'
              }
            );
            console.log('Google Sign-In button rendered');
          } else {
            console.error('Google Sign-In button container not found');
          }
        }, 100); // Small timeout to ensure DOM is ready
      } catch (error) {
        console.error('Error initializing Google Sign-In:', error);
      }
    }
    
    return {
      username,
      password,
      loginAdmin,
      isDevelopmentMode,
      showFallbackButton,
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
