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
const defaultText = /REPLACE ALL/i;
const errorText = /SOMETHING WENT WRONG/i;
const successText = /STRINGS REPLACED/i;
const invalidText = /FAILED/i;

describe('<ReplaceAll>', () => {
  it('renders default button correctly', () => {
    const { getByRole, queryByText, container } = render(
      <WrapReplaceAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    getByRole('button', { name: defaultText });
    expect(queryByText(errorText)).toBeNull();
    expect(queryByText(successText)).toBeNull();
    expect(queryByText(invalidText)).toBeNull();
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

    expect(queryByText(defaultText)).toBeNull();
    getByRole('button', { name: errorText });
    expect(queryByText(successText)).toBeNull();
    expect(queryByText(invalidText)).toBeNull();
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
    expect(queryByText(defaultText)).toBeNull();
    expect(queryByText(errorText)).toBeNull();
    getByRole('button', { name: successText });
    expect(queryByText(invalidText)).toBeNull();
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

    expect(queryByText(defaultText)).toBeNull();
    expect(queryByText(errorText)).toBeNull();
    const button = getByRole('button', { name: successText });
    expect(button).toHaveTextContent(invalidText);
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
    fireEvent.click(getByRole('button', { name: defaultText }));
    expect(mockReplaceAll).toHaveBeenCalled();
  });
});
