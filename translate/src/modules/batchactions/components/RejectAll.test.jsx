import React from 'react';

import { MockLocalizationProvider } from '~/test/utils';

import { RejectAll } from './RejectAll';
import { vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

const WrapRejectAll = (props) => (
  <MockLocalizationProvider>
    <RejectAll {...props} />
  </MockLocalizationProvider>
);

describe('<RejectAll>', () => {
  it('renders default button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapRejectAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    getByRole('button', { name: /REJECT ALL/i });
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(queryByText(/STRINGS REJECTED/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders error button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapRejectAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'reject',
            error: true,
          },
        }}
      />,
    );
    getByRole('button', { name: /SOMETHING WENT WRONG/i });
    expect(queryByText(/REJECT ALL/i)).toBeNull();
    expect(queryByText(/STRINGS REJECTED/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders success button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapRejectAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'reject',
            changedCount: 2,
          },
        }}
      />,
    );

    getByRole('button', { name: /STRINGS REJECTED/i });
    expect(queryByText(/REJECT ALL/i)).toBeNull();
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders success with invalid button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapRejectAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'reject',
            changedCount: 2,
            invalidCount: 1,
          },
        }}
      />,
    );

    getByRole('button', { name: /^(?=.*STRINGS REJECTED)(?=.*FAILED).*/i });
    expect(queryByText(/REJECT ALL/i)).toBeNull();
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('raise confirmation warning when Reject All button is clicked', () => {
    const mockRejectAll = vi.fn();

    const { getByRole, getByText } = render(
      <WrapRejectAll
        batchactions={DEFAULT_BATCH_ACTIONS}
        rejectAll={mockRejectAll}
      />,
    );
    fireEvent.click(getByRole('button'));
    expect(mockRejectAll).not.toHaveBeenCalled();
    getByText(/ARE YOU SURE/i);
  });

  it('performs reject all action when Reject All button is confirmed', () => {
    const mockRejectAll = vi.fn();

    const { getByRole } = render(
      <WrapRejectAll
        batchactions={DEFAULT_BATCH_ACTIONS}
        rejectAll={mockRejectAll}
      />,
    );

    expect(mockRejectAll).not.toHaveBeenCalled();
    fireEvent.click(getByRole('button', { name: /REJECT ALL/i }));
    fireEvent.click(getByRole('button', { name: /ARE YOU SURE/i }));
    expect(mockRejectAll).toHaveBeenCalledOnce();
  });
});
