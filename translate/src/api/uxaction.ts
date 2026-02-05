import { POST } from './utils/base';
import { getCSRFToken } from './utils/csrfToken';

function isAuthenticated(): boolean {
  const root = document.getElementById('root');
  return root?.dataset.isAuthenticated === 'true';
}

export async function logUXAction(
  action_type: string,
  experiment: string | null,
  data: Record<string, string | number | boolean> | null,
): Promise<void> {
  if (!isAuthenticated()) return;
  const csrfToken = getCSRFToken();

  const payload = new URLSearchParams({
    csrfmiddlewaretoken: csrfToken,
    action_type,
  });
  if (experiment) {
    payload.append('experiment', experiment);
  }
  if (data) {
    payload.append('data', JSON.stringify(data));
  }

  const headers = new Headers({ 'X-CSRFToken': csrfToken });

  try {
    await POST('/log-ux-action/', payload, { headers });
  } catch {
    /* Ignore errors during UX action logging */
  }
}
