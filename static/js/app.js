const form = document.querySelector('#enquiry-form');
const statusMessage = document.querySelector('#form-status');
const phonePattern = /^[+()\-\s0-9]{7,25}$/;

document.querySelector('.menu-button').addEventListener('click', (event) => {
  const open = event.currentTarget.getAttribute('aria-expanded') === 'true';
  event.currentTarget.setAttribute('aria-expanded', String(!open));
  document.querySelector('#nav-links').classList.toggle('is-open', !open);
});
document.querySelectorAll('.nav-links a').forEach((link) => link.addEventListener('click', () => document.querySelector('#nav-links').classList.remove('is-open')));
document.querySelectorAll('[data-course]').forEach((link) => link.addEventListener('click', () => { document.querySelector('#course').value = link.dataset.course; }));
document.querySelector('#year').textContent = new Date().getFullYear();
const contactCopy = document.querySelector('.contact-copy');
if (contactCopy) {
  const emailLink = document.createElement('a');
  emailLink.className = 'contact-detail';
  emailLink.href = 'mailto:work2wintechnologies@gmail.com';
  emailLink.textContent = 'Email: work2wintechnologies@gmail.com';
  contactCopy.querySelector('.contact-detail')?.before(emailLink);
}

function showError(field, message = '') { const error = field.closest('.field').querySelector('small'); field.setAttribute('aria-invalid', Boolean(message)); error.textContent = message; }
function validate(data) {
  const errors = {};
  if (data.name.trim().length < 2) errors.name = 'Enter your full name.';
  if (!phonePattern.test(data.whatsapp.trim())) errors.whatsapp = 'Enter a valid WhatsApp number.';
  if (!data.course) errors.course = 'Please choose a course.';
  if (data.message.length > 1000) errors.message = 'Message must be 1,000 characters or fewer.';
  return errors;
}
form.addEventListener('submit', async (event) => {
  event.preventDefault(); statusMessage.textContent = '';
  const data = Object.fromEntries(new FormData(form)); const errors = validate(data);
  ['name', 'whatsapp', 'course', 'message'].forEach((key) => showError(form.elements[key], errors[key]));
  if (Object.keys(errors).length) return;
  const button = form.querySelector('button'); button.disabled = true; button.textContent = 'Sending…';
  try { const response = await fetch('/api/enquiry', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); const result = await response.json();
    if (!response.ok) { Object.entries(result.errors || {}).forEach(([key, value]) => form.elements[key] && showError(form.elements[key], value)); throw new Error(result.message); }
    statusMessage.className = 'form-status success'; statusMessage.textContent = result.message; form.reset();
  } catch (error) { statusMessage.className = 'form-status error'; statusMessage.textContent = error.message || 'Unable to send your enquiry right now. Please try again or contact us through WhatsApp.'; }
  finally { button.disabled = false; button.innerHTML = 'Send enquiry <span>→</span>'; }
});
