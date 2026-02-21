import React, { useContext } from 'react';

import * as Hooks from '~/hooks';
import * as Translator from '~/hooks/useTranslator';

import * as ExistingTranslation from '../hooks/useExistingTranslationGetter';
import * as SendTranslation from '../hooks/useSendTranslation';
import * as UpdateTranslationStatus from '../hooks/useUpdateTranslationStatus';

import { EditorMainAction } from './EditorMainAction';
import { vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';

beforeAll(() => {
  vi.mock('react', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useContext: vi.fn(),
    };
  });

  vi.mock('@fluent/react', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      Localized: ({ children }) => children,
    };
  });

  vi.spyOn(Hooks, 'useAppSelector').mockImplementation(() => ({}));
  vi.spyOn(Translator, 'useTranslator').mockReturnValue({});
  vi.spyOn(ExistingTranslation, 'useExistingTranslationGetter').mockReturnValue(
    () => ({}),
  );
  vi.spyOn(SendTranslation, 'useSendTranslation').mockReturnValue({});
  vi.spyOn(
    UpdateTranslationStatus,
    'useUpdateTranslationStatus',
  ).mockReturnValue({});
});

beforeEach(() => {
  vi.mocked(useContext).mockReturnValue({ busy: false });
  Hooks.useAppSelector.mockReturnValue(false); // user.settings.forceSuggestions
  Translator.useTranslator.mockReturnValue(true);
  ExistingTranslation.useExistingTranslationGetter.mockReturnValue(
    () => undefined,
  );
  SendTranslation.useSendTranslation.mockReturnValue(() => {});
  UpdateTranslationStatus.useUpdateTranslationStatus.mockReturnValue(() => {});
});

afterAll(() => {
  vi.restoreAllMocks();
});

describe('<EditorMainAction>', () => {
  it('renders the Approve button when an identical translation exists', () => {
    const spy = vi.fn();
    UpdateTranslationStatus.useUpdateTranslationStatus.mockReturnValue(spy);
    ExistingTranslation.useExistingTranslationGetter.mockReturnValue(() => ({
      pk: 1,
    }));

    const { getByRole } = render(<EditorMainAction />);
    fireEvent.click(getByRole('button', { name: /APPROVE/i }));
    expect(spy.mock.calls).toMatchObject([[1, 'approve', false]]);
  });

  it('renders the Suggest button when force suggestion is on', () => {
    const spy = vi.fn();
    SendTranslation.useSendTranslation.mockReturnValue(spy);
    Hooks.useAppSelector.mockReturnValue(true); // user.settings.forceSuggestions

    const { getByRole } = render(<EditorMainAction />);
    fireEvent.click(getByRole('button', { name: /SUGGEST/i }));
    expect(spy.mock.calls).toMatchObject([[]]);
  });

  it('renders the Suggest button when user does not have permission', () => {
    Hooks.useAppSelector.mockReturnValue(true); // user.settings.forceSuggestions

    const { getByRole } = render(<EditorMainAction />);

    getByRole('button', { name: /SUGGEST/i });
  });

  it('shows a spinner and a disabled Suggesting button when running request', () => {
    const spy = vi.fn();
    SendTranslation.useSendTranslation.mockReturnValue(spy);
    Hooks.useAppSelector.mockReturnValue(true); // user.settings.forceSuggestions
    vi.mocked(useContext).mockReturnValue({ busy: true }); // EditorData.busy

    const { getByRole } = render(<EditorMainAction />);
    const button = getByRole('button');

    expect(button.querySelector('.fa-spin')).toBeInTheDocument();

    fireEvent.click(button);
    expect(spy).not.toHaveBeenCalled();
  });

  it('renders the Save button when force suggestion is off and translation is not the same', () => {
    const spy = vi.fn();
    SendTranslation.useSendTranslation.mockReturnValue(spy);

    const { getByRole } = render(<EditorMainAction />);
    fireEvent.click(getByRole('button', { name: /SAVE/i }));
    expect(spy.mock.calls).toMatchObject([[]]);
  });

  it('shows a spinner and a disabled Saving button when running request', () => {
    const spy = vi.fn();
    SendTranslation.useSendTranslation.mockReturnValue(spy);
    vi.mocked(useContext).mockReturnValue({ busy: true }); // EditorData.busy

    const { getByRole } = render(<EditorMainAction />);
    const button = getByRole('button');

    expect(button.querySelector('.fa-spin')).toBeInTheDocument();
    fireEvent.click(button);
    expect(spy).not.toHaveBeenCalled();
  });
});
