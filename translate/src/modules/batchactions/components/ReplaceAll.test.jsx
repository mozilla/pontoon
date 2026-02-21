import React from 'react';

import { MockLocalizationProvider } from '~/test/utils';

import { ReplaceAll } from './ReplaceAll';
import { vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

const WrapReplaceAll = (props) => (
  <MockLocalizationProvider>
    <ReplaceAll {...props} />
  </MockLocalizationProvider>
);

describe('<ReplaceAll>', () => {
  it('renders default button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapReplaceAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    getByRole('button', { name: /REPLACE ALL/i });
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(queryByText(/STRINGS REPLACED/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders error button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapReplaceAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'replace',
            error: true,
          },
        }}
      />,
    );

    getByRole('button', { name: /SOMETHING WENT WRONG/i });
    expect(queryByText(/REPLACE ALL/i)).toBeNull();
    expect(queryByText(/STRINGS REPLACED/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders success button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapReplaceAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'replace',
            changedCount: 2,
          },
        }}
      />,
    );
    getByRole('button', { name: /STRINGS REPLACED/i });
    expect(queryByText(/REPLACE ALL/i)).toBeNull();
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(queryByText(/FAILED/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('renders success with invalid button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapReplaceAll
        batchactions={{
          ...DEFAULT_BATCH_ACTIONS,
          response: {
            action: 'replace',
            changedCount: 2,
            invalidCount: 1,
          },
        }}
      />,
    );

    getByRole('button', { name: /^(?=.*STRINGS REPLACED)(?=.*FAILED).*/i });
    expect(queryByText(/REPLACE ALL/i)).toBeNull();
    expect(queryByText(/SOMETHING WENT WRONG/i)).toBeNull();
    expect(container.querySelector('.fas')).toBeNull();
  });

  it('performs replace all action when Replace All button is clicked', () => {
    const mockReplaceAll = vi.fn();

    const { getByRole } = render(
      <WrapReplaceAll
        batchactions={DEFAULT_BATCH_ACTIONS}
        replaceAll={mockReplaceAll}
      />,
    );

    expect(mockReplaceAll).not.toHaveBeenCalled();
    fireEvent.click(getByRole('button', { name: /REPLACE ALL/i }));
    expect(mockReplaceAll).toHaveBeenCalled();
  });
});
