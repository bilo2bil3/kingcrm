function click2Call(event) {
  // sending the request
  const btn = event.target;
  const CALL_ENDPOINT = '/leads/click2call';
  const CSRF_TOKEN = document.cookie
  .split(';')
  .find(row => row.startsWith('csrftoken='))
  .split('=')[1];
  const HEADERS = { 'content-type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, }
  const PAYLOAD = { lead: btn.dataset.lead }  
  fetch(CALL_ENDPOINT, { method: 'POST', body: JSON.stringify(PAYLOAD), headers: HEADERS })
    .then(res => {
      if (res.ok) {
        console.log('successfuly called client!');
        alert(`Calling ${btn.dataset.firstname} ${btn.dataset.firstname}`);
        // hide call btn
        btn.style.display = 'none';
        // show hangup btn
        btn.nextElementSibling.style.display = 'inline';
      }
      return res.text();
    })
    .then(data => console.log(data))
    .catch(err => console.log(err));
}

function hangupCall(event) {
  // sending the request
  const btn = event.target;
  const HANGUP_ENDPOINT = '/leads/click2call-hangup';
  const PAYLOAD = {}
  const CSRF_TOKEN = document.cookie
    .split(';')
    .find(row => row.startsWith('csrftoken='))
    .split('=')[1];
  const HEADERS = { 'content-type': 'application/json', 'X-CSRFToken': CSRF_TOKEN, }
  fetch(HANGUP_ENDPOINT, { method: 'POST', body: JSON.stringify(PAYLOAD), headers: HEADERS })
    .then(res => {
      if (res.ok) {
        console.log('successfuly disconnected from call');
        // hide hangup btn
        btn.style.display = 'none';
        // show call btn
        btn.previousElementSibling.style.display = 'inline';
      }
      return res.text();
    })
    .then(data => console.log(data))
    .catch(err => console.log(err));
}

document.addEventListener('DOMContentLoaded', () => {
  const click2CallBtns = document.querySelectorAll('.click2call-call');
  const hangupCallBtns = document.querySelectorAll('.click2call-hangup');

  
  click2CallBtns.forEach(btn => {
    btn.addEventListener('click', click2Call);
  })

  hangupCallBtns.forEach(btn => {
    btn.addEventListener('click', hangupCall);
    // initially hide hangup button
    btn.style.display = 'none';
  })
})
