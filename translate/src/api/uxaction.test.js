import { vi } from 'vitest';

vi.mock('./utils/base', () => ({ POST: vi.fn() }));
vi.mock('./utils/csrfToken', () => ({ getCSRFToken: () => 'test-csrf-token' }));
vi.mock('./user', () => ({ fetchUserData: vi.fn() }));

async function setup({
  authenticated: authenticated = true,
  postReject = false,
} = {}) {
  const { fetchUserData } = await import('./user');
  const { POST } = await import('./utils/base');
  const { logUXAction } = await import('./uxaction');

  fetchUserData.mockResolvedValue({ is_authenticated: authenticated });

  if (postReject) {
    POST.mockRejectedValue(new Error('err'));
  } else {
    POST.mockResolvedValue(undefined);
  }

  return { fetchUserData, POST, logUXAction };
}

describe('logUXAction', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
    document.body.innerHTML = '';
  });

  it('does nothing when unauthenticated', async () => {
    const { POST, logUXAction } = await setup({ authenticated: false });

    await logUXAction('Load: X', 'Exp', { a: true });

    expect(POST).not.toHaveBeenCalled();
  });

  it('POSTs when authenticated', async () => {
    const { POST, logUXAction } = await setup({ authenticated: true });

    await logUXAction('Load: X', 'Exp', { a: true });

    expect(POST).toHaveBeenCalledTimes(1);
    expect(POST.mock.calls[0][0]).toBe('/log-ux-action/');
  });

  it('swallows POST errors', async () => {
    const { logUXAction } = await setup({
      authenticated: true,
      postReject: true,
    });

    await expect(logUXAction('Load: X', null, null)).resolves.toBeUndefined();
  });
});
