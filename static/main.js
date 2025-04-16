
// fetch and display all tasks 
async function fetchTasks() {
  const res = await fetch('/api/tasks');
  const tasks = await res.json();
  const list = document.getElementById('task-list');
  list.innerHTML = '';

  // add tasks to dom
  tasks.forEach(task => {
    const li = document.createElement('li');
    li.innerHTML = `
      <input type="checkbox" ${task.done ? 'checked' : ''} onchange="toggleTask(${task.id}, this.checked)">
      ${task.title}
      <button onclick="deleteTask(${task.id})">Delete</button>
    `;
    list.appendChild(li);
  });
}

// toggle done/undone
async function toggleTask(id, done) {
  await fetch('/api/tasks/' + id, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ done })
  });
  fetchTasks();
}

// delete a task with id
async function deleteTask(id) {
  await fetch('/api/tasks/' + id, { method: 'DELETE' });
  fetchTasks();
}

// handle form submission for adding new task
document.getElementById('task-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = document.getElementById('task-title').value;

  // send new task to backend
  await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  document.getElementById('task-title').value = '';
  fetchTasks();
});

fetchTasks();
