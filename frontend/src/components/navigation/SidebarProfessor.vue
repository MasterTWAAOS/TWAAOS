<template>
  <div class="sidebar-professor">
    <h2>Cadru Didactic</h2>
    <div class="menu">
      <ul>
        <li>
          <router-link :to="{ name: 'ProfessorDashboard' }" class="menu-item">
            <i class="pi pi-home"></i>
            <span>Dashboard</span>
          </router-link>
        </li>
        <li>
          <router-link :to="{ name: 'ReviewProposals' }" class="menu-item">
            <i class="pi pi-check-square"></i>
            <span>Validare Propuneri</span>
          </router-link>
        </li>
        <li>
          <router-link :to="{ name: 'SetupExams' }" class="menu-item">
            <i class="pi pi-cog"></i>
            <span>Configurare Examene</span>
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SidebarProfessor'
}
</script>

<style lang="scss" scoped>
.sidebar-professor {
  h2 {
    font-size: 1.25rem;
    color: #2c3e50;
    margin-top: 0;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e9ecef;
  }
  
  .menu {
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        margin-bottom: 0.5rem;
        
        .menu-item {
          display: flex;
          align-items: center;
          padding: 0.75rem;
          border-radius: 4px;
          text-decoration: none;
          color: #495057;
          transition: all 0.2s ease;
          
          i {
            margin-right: 0.75rem;
            font-size: 1.1rem;
          }
          
          &:hover, &.router-link-active {
            background-color: #e3f2fd;
            color: #1E88E5;
          }
        }
      }
    }
  }
}
</style>
