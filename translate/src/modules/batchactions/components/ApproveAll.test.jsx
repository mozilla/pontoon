import React from 'react';

import { MockLocalizationProvider } from '~/test/utils';

import { ApproveAll } from './ApproveAll';
import { vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

const WrapApproveAll = (props) => (
  <MockLocalizationProvider>
    <ApproveAll {...props} />
  </MockLocalizationProvider>
);

describe('<ApproveAll>', () => {
  it('renders default button correctly', () => {
    const { container, getByRole, queryByText } = render(
      <WrapApproveAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    getByRole('button', { name: /APPROVE ALL/i });
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(queryByText(/STRINGS APPROVED/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders error button correctly', () => {
    const { container, getByRole, queryByText } = render(
      <WrapApproveAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'approve',
            error: true,
          },
        }}
      />,
    );
    getByRole('button', { name: /SOMETHING WENT WRONG/i });
    expect(queryByText(/APPROVE ALL/i)).toBeNull();
    expect(queryByText(/STRINGS APPROVED/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders success button correctly', () => {
    const { container, getByRole, queryByText } = render(
      <WrapApproveAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'approve',
            changedCount: 2,
          },
        }}
      />,
    );
    getByRole('button', { name: /STRINGS APPROVED/i });
    expect(queryByText(/APPROVE ALL/i)).toBeNull();
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders success with invalid button correctly', () => {
    const { container, getByRole, queryByText } = render(
      <WrapApproveAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'approve',
            changedCount: 2,
            invalidCount: 1,
          },
        }}
      />,
    );

    getByRole('button', { name: /^(?=.*STRINGS APPROVED)(?=.*FAILED).*/i });
    expect(queryByText(/APPROVE ALL/i)).toBeNull();
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('performs approve all action when Approve All button is clicked', () => {
    const mockApproveAll = vi.fn();

    const { getByRole } = render(
      <WrapApproveAll
        batchactions={DEFAULT_BATCH_ACTIONS}
        approveAll={mockApproveAll}
      />,
    );

    expect(mockApproveAll).not.toHaveBeenCalled();
    fireEvent.click(getByRole('button'));
    expect(mockApproveAll).toHaveBeenCalled();
  });
});
