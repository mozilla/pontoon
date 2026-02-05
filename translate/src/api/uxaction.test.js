import { vi } from 'vitest';

vi.mock('./utils/base', () => ({
  POST: vi.fn(),
}));

vi.mock('./utils/csrfToken', () => ({
  getCSRFToken: () => 'test-csrf-token',
}));

import { POST } from './utils/base';
import { logUXAction } from './uxaction';

function setRoot(isAuthenticated) {
  document.body.innerHTML = `<div id="root" data-is-authenticated="${isAuthenticated}"></div>`;
}

describe('logUXAction', () => {
  beforeEach(() => {
    POST.mockResolvedValue(undefined);
  });

  afterEach(() => {
    vi.clearAllMocks();
    document.body.innerHTML = '';
  });

  it('does nothing when unauthenticated', async () => {
    setRoot('false');
    await logUXAction('Load: X', 'Exp', { a: true });
    expect(POST).not.toHaveBeenCalled();
  });

  it('POSTs when authenticated', async () => {
    setRoot('true');
    await logUXAction('Load: X', 'Exp', { a: true });
    expect(POST).toHaveBeenCalledTimes(1);
    expect(POST.mock.calls[0][0]).toBe('/log-ux-action/');
  });

  it('swallows POST errors', async () => {
    setRoot('true');
    POST.mockRejectedValue(new Error('boom'));
    await expect(logUXAction('Load: X', null, null)).resolves.toBeUndefined();
  });
});
