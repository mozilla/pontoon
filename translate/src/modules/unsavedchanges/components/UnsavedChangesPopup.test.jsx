import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UnsavedActions, UnsavedChanges } from '~/context/UnsavedChanges';
import { MockLocalizationProvider } from '~/test/utils';

import { UnsavedChangesPopup } from './UnsavedChangesPopup';

const renderPopup = (onIgnore, resetUnsavedChanges) =>
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
  const { container } = renderPopup(() => {});

    expect(container.querySelector(".unsaved-changes")).toBeInTheDocument();
    expect(container.querySelector(".close")).toBeInTheDocument();
    expect(container.querySelector(".title")).toBeInTheDocument();
    expect(container.querySelector(".body")).toBeInTheDocument();
    expect(container.querySelector(".proceed.anyway")).toBeInTheDocument();
  });

  it('does not render if not shown', () => {
    const { container } = renderPopup(null);

    expect(container.querySelector(".unsaved-changes")).not.toBeInTheDocument();
  });

  it('closes the unsaved changes popup when the Close button is clicked', async() => {
    const resetUnsavedChanges = vi.fn();
    const { container } = renderPopup(() => {}, resetUnsavedChanges);
    const user = userEvent.setup();
    await user.click(container.querySelector(".close"));
    expect(resetUnsavedChanges).toHaveBeenCalledWith(false);
  });

  it('ignores the unsaved changes popup when the Proceed button is clicked',async () => {
    const user = userEvent.setup();
    const resetUnsavedChanges = vi.fn();
    const { container } = renderPopup(() => {}, resetUnsavedChanges);

    await user.click(container.querySelector(".proceed.anyway"));
    expect(resetUnsavedChanges).toHaveBeenCalledWith(true);
  });
});
