import { mount } from 'enzyme';
import React from 'react';
import { act } from 'react-dom/test-utils';
import sinon from 'sinon';

import api from '~/core/api';

import { AppLocalizationProvider } from './AppLocalizationProvider';

describe('<AppLocalizationProvider>', () => {
  beforeAll(() => sinon.stub(api.l10n, 'get'));
  afterEach(() => api.l10n.get.resetHistory());
  afterAll(() => api.l10n.get.restore());

  it('fetches a locale when the component mounts', async () => {
    api.l10n.get.resolves('');
    mount(
      <AppLocalizationProvider>
        <div />
      </AppLocalizationProvider>,
    );
    await act(() => new Promise((resolve) => setTimeout(resolve)));

    expect(api.l10n.get.callCount).toEqual(1);
  });

  it('renders messages and children when loaded', async () => {
    api.l10n.get.resolves('key = message\n');
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
