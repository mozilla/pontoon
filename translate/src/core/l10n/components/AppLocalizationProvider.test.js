import { mount } from 'enzyme';
import React from 'react';
import { act } from 'react-dom/test-utils';
import sinon from 'sinon';

import * as api from '~/api/l10n';

import { AppLocalizationProvider } from './AppLocalizationProvider';

describe('<AppLocalizationProvider>', () => {
  beforeAll(() => sinon.stub(api, 'fetchL10n'));
  afterEach(() => api.fetchL10n.resetHistory());
  afterAll(() => api.fetchL10n.restore());

  it('fetches a locale when the component mounts', async () => {
    api.fetchL10n.resolves('');
    mount(
      <AppLocalizationProvider>
        <div />
      </AppLocalizationProvider>,
    );
    await act(() => new Promise((resolve) => setTimeout(resolve)));

    expect(api.fetchL10n.callCount).toEqual(1);
  });

  it('renders messages and children when loaded', async () => {
    api.fetchL10n.resolves('key = message\n');
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
