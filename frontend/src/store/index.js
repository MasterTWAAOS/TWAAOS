import { createStore } from 'vuex'
import auth from './modules/auth'
import exams from './modules/exams'
import rooms from './modules/rooms'
import groups from './modules/groups'
import users from './modules/users'
import notifications from './modules/notifications'
import schedules from './modules/schedules'
// sync module is imported but currently not used in the store
// import sync from './modules/sync'

export default createStore({
  state: {
    appLoading: false,
    globalError: null
  },
  getters: {
    isAppLoading: state => state.appLoading,
    globalError: state => state.globalError
  },
  mutations: {
    SET_APP_LOADING(state, loading) {
      state.appLoading = loading
    },
    SET_GLOBAL_ERROR(state, error) {
      state.globalError = error
    }
  },
  actions: {
    setAppLoading({ commit }, loading) {
      commit('SET_APP_LOADING', loading)
    },
    setGlobalError({ commit }, error) {
      commit('SET_GLOBAL_ERROR', error)
    }
  },
  modules: {
    auth,
    exams,
    rooms,
    groups, 
    users,
    notifications,
    schedules
  }
})
