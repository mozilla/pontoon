import { mount } from 'enzyme';
import React from 'react';

import { UnsavedActions, UnsavedChanges } from '~/context/UnsavedChanges';
import { MockLocalizationProvider } from '~/test/utils';

import { UnsavedChangesPopup } from './UnsavedChangesPopup';

const mountPopup = (onIgnore, resetUnsavedChanges) =>
  mount(
    <MockLocalizationProvider>
      <UnsavedChanges.Provider value={{ onIgnore }}>
        <UnsavedActions.Provider value={{ resetUnsavedChanges }}>
          <UnsavedChangesPopup />
        </UnsavedActions.Provider>
      </UnsavedChanges.Provider>
    </MockLocalizationProvider>,
  );

describe('<UnsavedChangesPopup>', () => {
  it('renders correctly if shown', () => {
    const wrapper = mountPopup(() => {});

    expect(wrapper.find('.unsaved-changes')).toHaveLength(1);
    expect(wrapper.find('.close')).toHaveLength(1);
    expect(wrapper.find('.title')).toHaveLength(1);
    expect(wrapper.find('.body')).toHaveLength(1);
    expect(wrapper.find('.proceed.anyway')).toHaveLength(1);
  });

  it('does not render if not shown', () => {
    const wrapper = mountPopup(null);

    expect(wrapper.find('.unsaved-changes')).toHaveLength(0);
  });

  it('closes the unsaved changes popup when the Close button is clicked', () => {
    const resetUnsavedChanges = jest.fn();
    const wrapper = mountPopup(() => {}, resetUnsavedChanges);

    wrapper.find('.close').simulate('click');
    expect(resetUnsavedChanges).toHaveBeenCalledWith(false);
  });

  it('ignores the unsaved changes popup when the Proceed button is clicked', () => {
    const resetUnsavedChanges = jest.fn();
    const wrapper = mountPopup(() => {}, resetUnsavedChanges);

    wrapper.find('.proceed.anyway').simulate('click');
    expect(resetUnsavedChanges).toHaveBeenCalledWith(true);
  });
});
