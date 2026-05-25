const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

export async function getJson(path) {
  const response = await fetch(apiUrl(path));
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.error || 'Request failed.');
  }

  return payload;
}

export async function postForm(path, formData) {
  const response = await fetch(apiUrl(path), {
    method: 'POST',
    body: formData,
  });
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.error || 'Request failed.');
  }

  return payload;
}
