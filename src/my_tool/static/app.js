const labsEl = document.getElementById('labs');
const bookingsEl = document.getElementById('bookings');
const selectEl = document.getElementById('lab-select');
const form = document.getElementById('booking-form');
const message = document.getElementById('message');

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || '请求失败');
  return data;
}

function setMessage(text, error = false) {
  message.textContent = text;
  message.className = error ? 'error' : 'ok';
}

async function loadLabs() {
  const {labs} = await api('/api/labs');
  labsEl.replaceChildren();
  selectEl.replaceChildren();
  for (const lab of labs) {
    const item = document.createElement('div');
    item.className = 'lab';
    const title = document.createElement('strong');
    title.textContent = lab.name;
    const detail = document.createElement('small');
    detail.textContent = `${lab.location} · 容纳 ${lab.capacity} 人`;
    item.append(title, detail);
    labsEl.append(item);
    const option = document.createElement('option');
    option.value = lab.id;
    option.textContent = lab.name;
    selectEl.append(option);
  }
}

async function loadBookings() {
  const {bookings} = await api('/api/bookings');
  bookingsEl.replaceChildren();
  if (!bookings.length) {
    const empty = document.createElement('p');
    empty.className = 'empty';
    empty.textContent = '暂无预约，可以先提交一条。';
    bookingsEl.append(empty);
    return;
  }
  for (const booking of bookings) {
    const item = document.createElement('div');
    item.className = 'booking';
    const title = document.createElement('strong');
    title.textContent = booking.lab_name;
    const detail = document.createElement('small');
    detail.textContent = `${booking.start.replace('T', ' ')}—${booking.end.slice(11)} · ${booking.requester} · ${booking.participants} 人 · ${booking.purpose}`;
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = '取消预约';
    button.addEventListener('click', async () => {
      try {
        await api(`/api/bookings/${booking.id}`, {method: 'DELETE'});
        setMessage('预约已取消');
        await loadBookings();
      } catch (error) { setMessage(error.message, true); }
    });
    item.append(title, detail, button);
    bookingsEl.append(item);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(form));
  values.lab_id = Number(values.lab_id);
  values.participants = Number(values.participants);
  try {
    await api('/api/bookings', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(values)
    });
    setMessage('预约成功');
    await loadBookings();
  } catch (error) { setMessage(error.message, true); }
});
document.getElementById('refresh').addEventListener('click', () => loadBookings().catch(e => setMessage(e.message, true)));
Promise.all([loadLabs(), loadBookings()]).catch(error => setMessage(error.message, true));

