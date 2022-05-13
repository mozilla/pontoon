import { mount } from 'enzyme';
import React from 'react';

import { UnsavedChanges } from '~/context/UnsavedChanges';
import { MockLocalizationProvider } from '~/test/utils';

import { UnsavedChangesPopup } from './UnsavedChangesPopup';

const mountPopup = (value) =>
  mount(
    <MockLocalizationProvider>
      <UnsavedChanges.Provider value={value}>
        <UnsavedChangesPopup />
      </UnsavedChanges.Provider>
    </MockLocalizationProvider>,
  );

describe('<UnsavedChangesPopup>', () => {
  it('renders correctly if shown', () => {
    const wrapper = mountPopup({ show: true });

    expect(wrapper.find('.unsaved-changes')).toHaveLength(1);
    expect(wrapper.find('.close')).toHaveLength(1);
    expect(wrapper.find('.title')).toHaveLength(1);
    expect(wrapper.find('.body')).toHaveLength(1);
    expect(wrapper.find('.proceed.anyway')).toHaveLength(1);
  });

  it('does not render if not shown', () => {
    const wrapper = mountPopup({ show: false });

    expect(wrapper.find('.unsaved-changes')).toHaveLength(0);
  });

  it('closes the unsaved changes popup when the Close button is clicked', () => {
    const set = jest.fn();
    const wrapper = mountPopup({ set, show: true });

    wrapper.find('.close').simulate('click');
    expect(set).toHaveBeenCalledWith(null);
  });

  it('ignores the unsaved changes popup when the Proceed button is clicked', () => {
    const set = jest.fn();
    const wrapper = mountPopup({ set, show: true });

    wrapper.find('.proceed.anyway').simulate('click');
    expect(set).toHaveBeenCalledWith({ ignore: true });
  });
});
