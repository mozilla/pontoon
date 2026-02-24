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
const defaultText = /APPROVE ALL/i;
const errorText = /SOMETHING WENT WRONG/i;
const successText = /STRINGS APPROVED/i;
const invalidText = /FAILED/i;

describe('<ApproveAll>', () => {
  it('renders default button correctly', () => {
    const { container, getByRole, queryByText } = render(
      <WrapApproveAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    getByRole('button', { name: defaultText });
    expect(queryByText(errorText)).toBeNull();
    expect(queryByText(successText)).toBeNull();
    expect(queryByText(invalidText)).toBeNull();
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
    expect(queryByText(defaultText)).toBeNull();
    getByRole('button', { name: errorText });
    expect(queryByText(successText)).toBeNull();
    expect(queryByText(invalidText)).toBeNull();
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
    expect(queryByText(defaultText)).toBeNull();
    expect(queryByText(errorText)).toBeNull();
    getByRole('button', { name: successText });
    expect(queryByText(invalidText)).toBeNull();
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

    expect(queryByText(defaultText)).toBeNull();
    expect(queryByText(errorText)).toBeNull();
    const button = getByRole('button', { name: successText });
    expect(button).toHaveTextContent(invalidText);
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
