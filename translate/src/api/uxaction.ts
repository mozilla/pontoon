import { fetchUserData } from './user';
import { POST } from './utils/base';
import { getCSRFToken } from './utils/csrfToken';

let userDataPromise: ReturnType<typeof fetchUserData> | null = null;

async function isAuthenticated(): Promise<boolean> {
  if (!userDataPromise) {
    userDataPromise = fetchUserData();
  }
  try {
    const userData = await userDataPromise;
    return Boolean(userData?.is_authenticated);
  } catch {
    return false;
  }
}

export async function logUXAction(
  action_type: string,
  experiment: string | null,
  data: Record<string, string | number | boolean> | null,
): Promise<void> {
  if (!(await isAuthenticated())) return;
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
