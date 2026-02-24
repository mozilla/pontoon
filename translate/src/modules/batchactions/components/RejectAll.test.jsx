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
const defaultText = /REJECT ALL/i;
const errorText = /SOMETHING WENT WRONG/i;
const successText = /STRINGS REJECTED/i;
const invalidText = /FAILED/i;
const dialogBoxText = /ARE YOU SURE/i;

describe('<RejectAll>', () => {
  it('renders default button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapRejectAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    getByRole('button', { name: defaultText });
    expect(queryByText(errorText)).toBeNull();
    expect(queryByText(successText)).toBeNull();
    expect(queryByText(invalidText)).toBeNull();
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
    expect(queryByText(defaultText)).toBeNull();
    getByRole('button', { name: errorText });
    expect(queryByText(successText)).toBeNull();
    expect(queryByText(invalidText)).toBeNull();
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

    expect(queryByText(defaultText)).toBeNull();
    expect(queryByText(errorText)).toBeNull();
    getByRole('button', { name: successText });
    expect(queryByText(invalidText)).toBeNull();
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

    expect(queryByText(defaultText)).toBeNull();
    expect(queryByText(errorText)).toBeNull();
    const button = getByRole('button', { name: successText });
    expect(button).toHaveTextContent(invalidText);
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
    getByText(dialogBoxText);
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
    fireEvent.click(getByRole('button', { name: defaultText }));
    fireEvent.click(getByRole('button', { name: dialogBoxText }));
    expect(mockRejectAll).toHaveBeenCalledOnce();
  });
});
