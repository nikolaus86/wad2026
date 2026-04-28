function appendMessage(role, content) {
  const messages = document.getElementById('messages');
  const welcome = messages.querySelector('.welcome');
  if (welcome) welcome.remove();
  const article = document.createElement('article');
  article.className = `message ${role}`;
  article.innerHTML = '<div class="role"></div><p></p>';
  article.querySelector('.role').textContent = role;
  article.querySelector('p').textContent = content;
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

const askForm = document.getElementById('ask-form');
if (askForm) {
  askForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const chatId = document.querySelector('.chat-panel').dataset.chatId;
    const textarea = document.getElementById('prompt');
    const content = textarea.value.trim();
    if (!content) return;
    textarea.value = '';
    appendMessage('user', content);
    appendMessage('assistant', 'Thinking...');
    const response = await fetch(`/api/chats/${chatId}/messages`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({content})
    });
    const pending = [...document.querySelectorAll('.message.assistant')].at(-1);
    if (!response.ok) {
      pending.querySelector('p').textContent = 'Request failed. Please login again or check the server logs.';
      return;
    }
    const data = await response.json();
    pending.querySelector('p').textContent = data.assistant_message.content;
  });
}
