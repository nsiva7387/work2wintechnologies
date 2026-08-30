const form = document.querySelector('#enquiry-form');
const statusMessage = document.querySelector('#form-status');
const phonePattern = /^[+()\-\s0-9]{7,25}$/;

const registrationForm = document.querySelector('#course-registration-form');
if (registrationForm) {
  const registrationStatus = registrationForm.querySelector('.form-status');
  const registrationError = (field, message = '') => {
    field.setAttribute('aria-invalid', Boolean(message));
    field.closest('.field').querySelector('small').textContent = message;
  };
  registrationForm.addEventListener('submit', async (event) => {
    event.preventDefault(); registrationStatus.textContent = '';
    const data = Object.fromEntries(new FormData(registrationForm));
    const errors = {};
    if (data.name.trim().length < 2) errors.name = 'Enter your full name.';
    if (!phonePattern.test(data.phone.trim())) errors.phone = 'Enter a valid phone number.';
    if (data.email && !/^\S+@\S+\.\S+$/.test(data.email)) errors.email = 'Enter a valid email address.';
    ['name', 'phone', 'email', 'message'].forEach((key) => registrationError(registrationForm.elements[key], errors[key]));
    if (Object.keys(errors).length) return;
    const button = registrationForm.querySelector('button'); button.disabled = true; button.textContent = 'Registering...';
    try {
      const response = await fetch('/api/course-registration', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
      const result = await response.json();
      if (!response.ok) { Object.entries(result.errors || {}).forEach(([key, value]) => registrationForm.elements[key] && registrationError(registrationForm.elements[key], value)); throw new Error(result.message); }
      registrationStatus.className = 'form-status success'; registrationStatus.textContent = result.message; registrationForm.reset();
    } catch (error) { registrationStatus.className = 'form-status error'; registrationStatus.textContent = error.message || 'Unable to register right now. Please try again.'; }
    finally { button.disabled = false; button.textContent = 'Register now'; }
  });
}

document.querySelector('.menu-button').addEventListener('click', (event) => {
  const open = event.currentTarget.getAttribute('aria-expanded') === 'true';
  event.currentTarget.setAttribute('aria-expanded', String(!open));
  document.querySelector('#nav-links').classList.toggle('is-open', !open);
});
document.querySelectorAll('.nav-links a').forEach((link) => link.addEventListener('click', () => {
  document.querySelector('#nav-links').classList.remove('is-open');
  document.querySelector('.menu-button').setAttribute('aria-expanded', 'false');
}));
document.querySelectorAll('[data-course]').forEach((link) => {
  link.setAttribute('href', '#registration');
  link.addEventListener('click', () => {
    const courseSelect = document.querySelector('#registration-course');
    if (courseSelect) courseSelect.value = link.dataset.course;
  });
});
document.querySelector('#year').textContent = new Date().getFullYear();
document.querySelector('.feedback-float-close')?.addEventListener('click', () => {
  document.querySelector('.latest-feedback-float')?.remove();
});
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

const publicRegistrationForm = document.querySelector('#registration-form');
if (publicRegistrationForm) {
  publicRegistrationForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const status = publicRegistrationForm.querySelector('.form-status');
    const data = Object.fromEntries(new FormData(publicRegistrationForm));
    const errors = {};
    if (data.name.trim().length < 2) errors.name = 'Enter your full name.';
    if (!phonePattern.test(data.phone.trim())) errors.phone = 'Enter a valid mobile number.';
    if (data.whatsapp && !phonePattern.test(data.whatsapp.trim())) errors.whatsapp = 'Enter a valid WhatsApp number.';
    if (data.email && !/^\S+@\S+\.\S+$/.test(data.email)) errors.email = 'Enter a valid email address.';
    if (!data.course) errors.course = 'Please select a course.';
    ['name', 'phone', 'whatsapp', 'email', 'course', 'message'].forEach((key) => {
      const field = publicRegistrationForm.elements[key];
      const message = errors[key] || '';
      field.setAttribute('aria-invalid', Boolean(message));
      field.closest('.field').querySelector('small').textContent = message;
    });
    if (Object.keys(errors).length) return;
    const button = publicRegistrationForm.querySelector('button');
    button.disabled = true;
    status.className = 'form-status';
    status.textContent = 'Submitting your registration…';
    try {
      const response = await fetch('/api/course-registration/', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Unable to submit your registration.');
      status.className = 'form-status success';
      status.textContent = result.message;
      publicRegistrationForm.reset();
    } catch (error) {
      status.className = 'form-status error';
      status.textContent = error.message || 'Unable to submit your registration. Please try again.';
    } finally {
      button.disabled = false;
    }
  });
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
