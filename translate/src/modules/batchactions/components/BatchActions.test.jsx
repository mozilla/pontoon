import React from 'react';

import * as Hooks from '~/hooks';
import * as Actions from '../actions';
import { BATCHACTIONS } from '../reducer';

import { BatchActions } from './BatchActions';
import { vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

describe('<BatchActions>', () => {
  beforeAll(() => {
    vi.mock('~/hooks', () => ({
      useAppDispatch: vi.fn(() => vi.fn()),
      useAppSelector: vi.fn((selector) =>
        selector({ [BATCHACTIONS]: DEFAULT_BATCH_ACTIONS }),
      ),
    }));

    vi.mock('../actions', () => ({
      resetSelection: vi.fn(() => ({ type: 'whatever' })),
      selectAll: vi.fn(() => ({ type: 'whatever' })),
    }));
  });

  afterAll(() => {
    Hooks.useAppDispatch.mockRestore();
    Hooks.useAppSelector.mockRestore();
    Actions.resetSelection.mockRestore();
    Actions.selectAll.mockRestore();
  });

  const WrapBatchAction = () => {
    return (
      <MockLocalizationProvider>
        <BatchActions />
      </MockLocalizationProvider>
    );
  };

  it('renders correctly', () => {
    const {
      container,
      getByRole,
      getByText,
      getByPlaceholderText,
      getAllByRole,
    } = render(<WrapBatchAction />);

    expect(container.querySelector('.batch-actions')).toBeInTheDocument();

    expect(container.querySelector('.topbar')).toBeInTheDocument();
    getByRole('button', { name: /STRINGS SELECTED/i });
    getByRole('button', { name: /SELECT ALL/i });

    expect(container.querySelector('.actions-panel')).toBeInTheDocument();
    getByText(/Warning:/i);

    getByText(/REVIEW TRANSLATIONS/i);
    getByRole('button', { name: /APPROVE ALL/i });
    getByRole('button', { name: /REJECT ALL/i });
    getByRole('heading', { name: /FIND & REPLACE/i });

    expect(getAllByRole('searchbox')).toHaveLength(2);
    getByPlaceholderText(/FIND/i);
    getByPlaceholderText(/REPLACE WITH/i);
    getByRole('button', { name: /REPLACE ALL/i });
  });

  it('closes batch actions panel when the Close button with selected count is clicked', () => {
    const { getByRole } = render(<WrapBatchAction />);
    fireEvent.click(getByRole('button', { name: /STRINGS SELECTED/i }));
    expect(Actions.resetSelection).toHaveBeenCalled();
  });

  it('selects all entities when the Select All button is clicked', () => {
    const { getByRole } = render(<WrapBatchAction />);

    fireEvent.click(getByRole('button', { name: /SELECT ALL/i }));
    expect(Actions.selectAll).toHaveBeenCalled();
  });
});
