document.addEventListener('DOMContentLoaded', () => {
    const reminder_date = document.getElementById('div_id_date')
    reminder_date.style.display = 'none'
    const reminder_title = document.getElementById('div_id_title')
    reminder_title.style.display = 'none'
    const reminder_time = document.getElementById('div_id_time')
    const is_reminder = document.getElementById('is_reminder')
    reminder_time.style.display = 'none'
    const add_reminder_button = document.getElementById('show-reminder-fields');
    const hide_reminder_button = document.getElementById('hide-reminder-fields');
    hide_reminder_button.style.display = 'none'

    add_reminder_button.addEventListener('click', () => {
        reminder_date.style.display = ''
        reminder_time.style.display = ''
        reminder_title.style.display = ''
        add_reminder_button.style.display = 'none'
        hide_reminder_button.style.display = ''
        is_reminder.value = true
    })

    hide_reminder_button.addEventListener('click', () => {
        reminder_date.style.display = 'none'
        reminder_time.style.display = 'none'
        reminder_title.style.display = 'none'
        add_reminder_button.style.display = ''
        hide_reminder_button.style.display = 'none'
        is_reminder.value = false
    })
})