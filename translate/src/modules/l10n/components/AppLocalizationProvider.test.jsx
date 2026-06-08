import React from 'react';
import { act } from 'react-dom/test-utils';

import * as api from '~/api/l10n';

import { AppLocalizationProvider } from './AppLocalizationProvider';
import { vi } from 'vitest';
import { render } from '@testing-library/react';
import { Localized } from '@fluent/react';

describe('<AppLocalizationProvider>', () => {
  beforeAll(() => {
    vi.mock('~/api/l10n', () => ({ fetchL10n: vi.fn() }));
  });
  afterEach(() => api.fetchL10n.mockClear());
  afterAll(() => api.fetchL10n.mockRestore());

  it('fetches a locale when the component mounts', async () => {
    api.fetchL10n.mockResolvedValue('');
    render(
      <AppLocalizationProvider>
        <div />
      </AppLocalizationProvider>,
    );
    await act(() => new Promise((resolve) => setTimeout(resolve)));

    expect(api.fetchL10n).toHaveBeenCalledOnce();
  });

  it('renders messages and children when loaded', async () => {
    const testMessage = 'message';
    api.fetchL10n.mockResolvedValue(`key = ${testMessage}\n`);
    const { getByText, getByTestId } = render(
      <AppLocalizationProvider>
        <Localized id='key'>
          <div data-testid='test' />
        </Localized>
      </AppLocalizationProvider>,
    );
    await act(() => new Promise((resolve) => setTimeout(resolve)));

    getByText(testMessage);
    getByTestId('test');
  });
});
