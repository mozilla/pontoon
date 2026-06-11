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
    key: ['A'],
    original: 'string a',
    value: ['string a'],
    translation: {
      status: 'approved',
      string: 'chaine a',
      value: ['chaine a'],
    },
  };

  const ENTITY_B = {
    key: ['B'],
    original: 'string b',
    value: ['string b'],
    translation: {
      status: 'pretranslated',
      string: 'chaine b',
      value: ['chaine b'],
    },
  };

  const ENTITY_C = {
    key: ['C'],
    original: 'string c',
    value: ['string c'],
    translation: {
      status: 'unreviewed',
      string: 'chaine c',
      value: ['chaine c'],
    },
  };

  const ENTITY_D = {
    key: ['D'],
    original: 'string d',
    value: ['string d'],
    translation: {
      status: 'approved',
      string: 'chaine d',
      value: ['chaine d'],
      errors: ['error'],
    },
  };

  const ENTITY_E = {
    key: ['E'],
    original: 'string e',
    value: ['string e'],
    translation: {
      status: 'pretranslated',
      string: 'chaine e',
      value: ['chaine e'],
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
