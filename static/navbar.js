const setup = () => {
  const getTheme = () => {
    if (window.localStorage.getItem('dark')) {
      return JSON.parse(window.localStorage.getItem('dark'))
    }
    return !!window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  const setTheme = (value) => {
    window.localStorage.setItem('dark', value)
  }

  return {
    loading: true,
    isDark: getTheme(),
    navigate(uri){
      window.location.href = window.location.origin + uri
    },
    showNotification: false,
    toggleTheme() {
      this.isDark = !this.isDark
      setTheme(this.isDark)
    },
    showNotifications(){
      const notification = document.getElementById('notification-dropdown')
      if (!this.showNotification){
        notification.classList.remove('hidden')
      }else{
        notification.classList.add('hidden')
      }
      this.showNotification = !this.showNotification
    }
  }
}
