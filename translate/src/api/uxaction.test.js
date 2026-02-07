import { vi } from 'vitest';

vi.mock('./utils/base', () => ({ POST: vi.fn() }));
vi.mock('./utils/csrfToken', () => ({ getCSRFToken: () => 'test-csrf-token' }));

async function setup({ postReject = false } = {}) {
  const { POST } = await import('./utils/base');
  const { logUXAction } = await import('./uxaction');

  if (postReject) {
    POST.mockRejectedValue(new Error('err'));
  } else {
    POST.mockResolvedValue(undefined);
  }

  return { POST, logUXAction };
}

describe('logUXAction', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('POSTs when called', async () => {
    const { POST, logUXAction } = await setup();

    await logUXAction('Load: X', 'Exp', { a: true });

    expect(POST).toHaveBeenCalledTimes(1);
    expect(POST.mock.calls[0][0]).toBe('/log-ux-action/');
  });

  it('swallows POST errors', async () => {
    const { logUXAction } = await setup({ postReject: true });

    await expect(logUXAction('Load: X', null, null)).resolves.toBeUndefined();
  });

  it('includes CSRF token and payload fields', async () => {
    const { POST, logUXAction } = await setup();

    await logUXAction('Test Action', 'Test Experiment', { foo: 'bar', num: 1 });

    expect(POST).toHaveBeenCalledTimes(1);

    const payload = POST.mock.calls[0][1];
    expect(payload).toBeInstanceOf(URLSearchParams);

    expect(payload.get('csrfmiddlewaretoken')).toBe('test-csrf-token');
    expect(payload.get('action_type')).toBe('Test Action');
    expect(payload.get('experiment')).toBe('Test Experiment');

    expect(JSON.parse(payload.get('data'))).toEqual({ foo: 'bar', num: 1 });
  });
});
