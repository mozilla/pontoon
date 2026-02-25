import React from 'react';

import * as hookModule from '~/hooks/useTranslator';
import { Entity } from './Entity';
import { it, vitest } from 'vitest';
import { fireEvent, render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

beforeAll(() => {
  vitest.mock('~/hooks/useTranslator', () => ({
    useTranslator: vi.fn(() => false),
  }));
});
afterAll(() => hookModule.useTranslator.mockRestore());

describe('<Entity>', () => {
  const ENTITY_A = {
    original: 'string a',
    translation: {
      string: 'chaine a',
      approved: true,
      errors: [],
      warnings: [],
    },
  };

  const ENTITY_B = {
    original: 'string b',
    translation: {
      string: 'chaine b',
      pretranslated: true,
      errors: [],
      warnings: [],
    },
  };

  const ENTITY_C = {
    original: 'string c',
    translation: {
      string: 'chaine c',
      errors: [],
      warnings: [],
    },
  };

  const ENTITY_D = {
    original: 'string d',
    translation: {
      string: 'chaine d',
      approved: true,
      errors: ['error'],
      warnings: [],
    },
  };

  const ENTITY_E = {
    original: 'string e',
    translation: {
      string: 'chaine e',
      pretranslated: true,
      errors: [],
      warnings: ['warning'],
    },
  };
  const WrapEntity = (props) => {
    return (
      <MockLocalizationProvider>
        <Entity {...props} />
      </MockLocalizationProvider>
    );
  };

  it('renders the source string and the first translation', () => {
    const { getByText } = render(
      <WrapEntity entity={ENTITY_A} parameters={{}} />,
    );

    getByText(ENTITY_A.original);
    getByText(ENTITY_A.translation.string);
  });

  it.each([
    { entity: ENTITY_A, classname: 'approved' },
    { entity: ENTITY_B, classname: 'pretranslated' },
    { entity: ENTITY_C, classname: 'missing' },
    { entity: ENTITY_D, classname: 'errors' },
    { entity: ENTITY_E, classname: 'warnings' },
  ])('renders $classname state correctly', ({ entity, classname }) => {
    const { container } = render(
      <WrapEntity entity={entity} parameters={{}} />,
    );

    expect(container.querySelector(`.${classname}`)).toBeInTheDocument();
  });

  it('calls the selectEntity function on click on li', () => {
    const selectEntityFn = vi.fn();
    const { getByRole } = render(
      <WrapEntity
        entity={ENTITY_A}
        selectEntity={selectEntityFn}
        parameters={{}}
      />,
    );
    fireEvent.click(getByRole('button'));
    expect(selectEntityFn).toHaveBeenCalledOnce();
  });

  it('calls the toggleForBatchEditing function on click on .status', () => {
    hookModule.useTranslator.mockReturnValue(true);
    const toggleForBatchEditingFn = vi.fn();
    const { getByRole } = render(
      <WrapEntity
        entity={ENTITY_A}
        isReadOnlyEditor={false}
        toggleForBatchEditing={toggleForBatchEditingFn}
        parameters={{}}
      />,
    );
    fireEvent.click(getByRole('checkbox'));
    expect(toggleForBatchEditingFn).toHaveBeenCalledOnce();
  });

  it('does not call the toggleForBatchEditing function if user not translator', () => {
    const toggleForBatchEditingFn = vi.fn();
    const selectEntityFn = vi.fn();
    const { getByRole } = render(
      <WrapEntity
        entity={ENTITY_A}
        isReadOnlyEditor={false}
        toggleForBatchEditing={toggleForBatchEditingFn}
        selectEntity={selectEntityFn}
        parameters={{}}
      />,
    );
    fireEvent.click(getByRole('checkbox'));
    expect(toggleForBatchEditingFn).not.toHaveBeenCalled();
  });

  it('does not call the toggleForBatchEditing function if read-only editor', () => {
    const toggleForBatchEditingFn = vi.fn();
    const selectEntityFn = vi.fn();
    const { getByRole } = render(
      <WrapEntity
        entity={ENTITY_A}
        isReadOnlyEditor={true}
        toggleForBatchEditing={toggleForBatchEditingFn}
        selectEntity={selectEntityFn}
        parameters={{}}
      />,
    );
    fireEvent.click(getByRole('checkbox'));
    expect(toggleForBatchEditingFn).not.toHaveBeenCalled();
  });
});
