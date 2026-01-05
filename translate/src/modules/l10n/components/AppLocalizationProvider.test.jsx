import { mount } from 'enzyme';
import React from 'react';
import { act } from 'react-dom/test-utils';

import * as api from '~/api/l10n';

import { AppLocalizationProvider } from './AppLocalizationProvider';
import { vi } from 'vitest';

describe('<AppLocalizationProvider>', () => {
  beforeAll(() => {
    vi.mock('~/api/l10n', () => ({ fetchL10n: vi.fn() }));
  });
  afterEach(() => api.fetchL10n.mockClear());
  afterAll(() => api.fetchL10n.mockRestore());

  it('fetches a locale when the component mounts', async () => {
    api.fetchL10n.mockResolvedValue('');
    mount(
      <AppLocalizationProvider>
        <div />
      </AppLocalizationProvider>,
    );
    await act(() => new Promise((resolve) => setTimeout(resolve)));

    expect(api.fetchL10n).toHaveBeenCalledTimes(1);
  });

  it('renders messages and children when loaded', async () => {
    api.fetchL10n.mockResolvedValue('key = message\n');
    const wrapper = mount(
      <AppLocalizationProvider>
        <div id='test' />
      </AppLocalizationProvider>,
    );
    await act(() => new Promise((resolve) => setTimeout(resolve)));
    wrapper.update();

    const localization = wrapper.find('LocalizationProvider').prop('l10n');
    expect(localization.getString('key')).toEqual('message');
    expect(wrapper.find('#test')).toHaveLength(1);
  });
});
