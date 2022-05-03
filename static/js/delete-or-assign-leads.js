// toggle status of checkboxes for selecting leads
// between checked or not checked
// based on the status of select-all btn
function toggleAllCheckboxes(selectAllBtn) {
  document.querySelectorAll('.select-lead').forEach(e => {
    e.checked = selectAllBtn.checked;
  })
}

// send a request to server to delete selected leads
// TODO: problem is: now where to redirect after success?
function deleteSelectedLeads(selectAllBtn) {
  // console.log('deleting selected leads')
  const leadsToDelete = [];
  document.querySelectorAll('input.select-lead:checked').forEach(e => {
    // console.log('deleteing:', e.value)
    leadsToDelete.push(e.value);
    // e.parentElement.parentElement.remove();
  })
  selectAllBtn.checked= false;
  if (!leadsToDelete.length) {
    // console.log('nothing to delete')
    return;
  }
  // console.log('leads to delete:', leadsToDelete);

  // sending the request
  const answer = confirm('Are you sure you want to delete the selected leads?')
  if (!answer) {
    console.log('cancelled');
    return;
  }
  const DELETE_ENDPOINT = '/leads/delete-selected-leads'
  const CSRF_TOKEN = document.cookie
    .split(';')
    .find(row => row.startsWith('csrftoken='))
    .split('=')[1];
  const HEADERS = { 'content-type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, }
  const PAYLOAD = { leads: leadsToDelete, url: window.location.href }
  fetch(DELETE_ENDPOINT, { redirect: 'follow', method: 'POST', headers: HEADERS, body: JSON.stringify(PAYLOAD) })
    .then(res => {
      if (res.ok) {
        // console.log('successfuly deleted leads!')
        // console.log('res url:', res.url);
        window.location.href = res.url;
      }
    })
    .catch(err => console.log(err));
}

function showAssignLeadsForm() {
  // toggle between two views
  // assign selected btn
  // dropdown of leads and two buttons: assign, cancel
  // if click cancel: redirect to first view
  document.getElementById('assign-leads-view-1').style.display = 'none';
  document.getElementById('assign-leads-view-2').style.display = 'block';
}

function assignSelectedLeads(selectAllBtn) {
  // get leads
  const leadsToAssign = [];
  document.querySelectorAll('input.select-lead:checked').forEach(e => {
    leadsToAssign.push(e.value);
  })
  selectAllBtn.checked= false;
  if (!leadsToAssign.length) {
    return;
  }
  // get agents
  const agents = $('#agent-to-assign').select2('data').map(e=> e.id);

  // sending the request
  const answer = confirm('Are you sure you want to assign the selected leads?')
  if (!answer) {
    console.log('cancelled');
    return;
  }
  const ASSIGN_ENDPOINT = '/leads/assign-selected-leads'
  const CSRF_TOKEN = document.cookie
    .split(';')
    .find(row => row.startsWith('csrftoken='))
    .split('=')[1];
  const HEADERS = { 'content-type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, }
  const PAYLOAD = { leads: leadsToAssign, agents: agents, url: window.location.href }
  fetch(ASSIGN_ENDPOINT, { redirect: 'follow', method: 'POST', headers: HEADERS, body: JSON.stringify(PAYLOAD) })
    .then(res => {
      if (res.ok) {
        window.location.href = res.url;
      }
    })
    .catch(err => console.log(err));
}

function assignSelectedLeadsRandomly(selectAllBtn) {
  // get leads
  const leadsToAssign = [];
  document.querySelectorAll('input.select-lead:checked').forEach(e => {
    leadsToAssign.push(e.value);
  })
  selectAllBtn.checked= false;
  if (!leadsToAssign.length) {
    return;
  }

  // sending the request
  const answer = confirm('Are you sure you want to assign the selected leads?')
  if (!answer) {
    console.log('cancelled');
    return;
  }
  const ASSIGN_ENDPOINT = '/leads/assign-selected-leads-randomly';
  const CSRF_TOKEN = document.cookie
    .split(';')
    .find(row => row.startsWith('csrftoken='))
    .split('=')[1];
  const HEADERS = { 'content-type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, }
  const PAYLOAD = { leads: leadsToAssign, url: window.location.href }
  fetch(ASSIGN_ENDPOINT, { redirect: 'follow', method: 'POST', headers: HEADERS, body: JSON.stringify(PAYLOAD) })
    .then(res => {
      if (res.ok) {
        window.location.href = res.url;
      }
    })
    .catch(err => console.log(err));
}

function hideAssignLeadsForm() {
  document.getElementById('assign-leads-view-2').style.display = 'none';
  document.getElementById('assign-leads-view-1').style.display = 'block';
}

document.addEventListener('DOMContentLoaded', () => {
  const selectAllBtn = document.getElementById('select-all');
  const deleteSelectedBtn = document.getElementById('delete-leads');
  const showAssignBtn = document.getElementById('show-assign-leads');
  const hideAssignBtn = document.getElementById('hide-assign-leads');
  const assignSelectedBtn = document.getElementById('assign-leads');
  const assignSelectedRandomlyBtn = document.getElementById('assign-leads-random');
  
  selectAllBtn.addEventListener('change', () => toggleAllCheckboxes(selectAllBtn));
  deleteSelectedBtn.addEventListener('click', () => deleteSelectedLeads(selectAllBtn));
  showAssignBtn.addEventListener('click', showAssignLeadsForm);
  hideAssignBtn.addEventListener('click', hideAssignLeadsForm);
  assignSelectedBtn.addEventListener('click', () => assignSelectedLeads(selectAllBtn));
  assignSelectedRandomlyBtn.addEventListener('click', () => assignSelectedLeadsRandomly(selectAllBtn));

  // initially hide assign leads view #2
  // the one with two buttons: assign, cancel
  document.getElementById('assign-leads-view-2').style.display = 'none';
})
