import React from 'react';

import { UnsavedActions, UnsavedChanges } from '~/context/UnsavedChanges';
import { MockLocalizationProvider } from '~/test/utils';

import { UnsavedChangesPopup } from './UnsavedChangesPopup';
import { vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';

const closeButtonText = 'Close unsaved changes popup';
const proceedButtonText = 'PROCEED';
const titleText = 'YOU HAVE UNSAVED CHANGES';
const bodyText = 'Are you sure you want to proceed?';

const mountPopup = (onIgnore, resetUnsavedChanges) =>
  render(
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
    const { container, getByRole, getByText } = mountPopup(() => {});

    expect(container.querySelector('.unsaved-changes')).toBeInTheDocument();
    getByRole('button', { name: closeButtonText });
    getByText(titleText);
    getByText(bodyText);
    getByRole('button', { name: proceedButtonText });
  });

  it('does not render if not shown', () => {
    const { container } = mountPopup(null);

    expect(container).toBeEmptyDOMElement();
  });

  it('closes the unsaved changes popup when the Close button is clicked', () => {
    const resetUnsavedChanges = vi.fn();
    const { getByRole } = mountPopup(() => {}, resetUnsavedChanges);

    fireEvent.click(getByRole('button', { name: closeButtonText }));
    expect(resetUnsavedChanges).toHaveBeenCalledWith(false);
  });

  it('ignores the unsaved changes popup when the Proceed button is clicked', () => {
    const resetUnsavedChanges = vi.fn();
    const { getByRole } = mountPopup(() => {}, resetUnsavedChanges);

    fireEvent.click(getByRole('button', { name: proceedButtonText }));
    expect(resetUnsavedChanges).toHaveBeenCalledWith(true);
  });
});
