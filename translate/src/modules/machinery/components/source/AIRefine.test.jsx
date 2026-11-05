import React from 'react';
import { act, fireEvent, render, within } from '@testing-library/react';
import { vi } from 'vitest';

import { MockLocalizationProvider } from '~/test/utils';

import { AIRefine } from './AIRefine';

const mount = (props) =>
  render(
    <MockLocalizationProvider>
      <AIRefine
        selectedOption=''
        onSelect={() => {}}
        onRestore={() => {}}
        {...props}
      />
    </MockLocalizationProvider>,
  );

describe('<AIRefine>', () => {
  it('opens a menu of refinement options', () => {
    const { container, getByRole, queryByRole } = mount();

    expect(queryByRole('list')).not.toBeInTheDocument();

    fireEvent.click(container.querySelector('.selector'));
    expect(within(getByRole('list')).getAllByRole('listitem')).toHaveLength(3);
  });

  it('offers to restore the original once an option is applied', () => {
    const { container, getByRole } = mount({ selectedOption: 'formal' });

    fireEvent.click(container.querySelector('.selector'));
    // The three options, the separator, and SHOW ORIGINAL.
    expect(within(getByRole('list')).getAllByRole('listitem')).toHaveLength(5);
    expect(container.querySelector('.selected-option')).toHaveTextContent(
      'formal',
    );
  });

  it('reports the chosen characteristic and closes', async () => {
    const onSelect = vi.fn();
    const { container, queryByRole, getByText } = mount({ onSelect });

    fireEvent.click(container.querySelector('.selector'));
    // The handler awaits the refinement before closing, so the close lands a
    // microtask later than the click.
    await act(async () => {
      fireEvent.click(getByText('MAKE INFORMAL'));
    });

    expect(onSelect).toHaveBeenCalledWith('informal');
    expect(queryByRole('list')).not.toBeInTheDocument();
  });

  it('restores rather than refines when showing the original', async () => {
    const onSelect = vi.fn();
    const onRestore = vi.fn();
    const { container, getByText } = mount({
      selectedOption: 'formal',
      onSelect,
      onRestore,
    });

    fireEvent.click(container.querySelector('.selector'));
    await act(async () => {
      fireEvent.click(getByText('SHOW ORIGINAL'));
    });

    expect(onRestore).toHaveBeenCalled();
    expect(onSelect).not.toHaveBeenCalled();
  });
});
