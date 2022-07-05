import { mount } from 'enzyme';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';
import sinon from 'sinon';

import * as Hooks from '~/hooks';

import {
  EntityView,
  EntityViewProvider,
  useActiveTranslation,
} from './EntityView';
import { Locale } from './Locale';
import { Location } from './Location';

const ENTITIES = [
  { pk: 1, original: 'hello' },
  { pk: 2, original: 'world', original_plural: 'plural' },
  { pk: 3 },
];

describe('<EntityViewProvider', () => {
  beforeAll(() => sinon.stub(Hooks, 'useAppSelector').returns(ENTITIES));
  afterAll(() => Hooks.useAppSelector.restore());

  it('returns the current entity', () => {
    let view;
    const Spy = () => {
      view = useContext(EntityView);
      return null;
    };

    const wrapper = mount(
      <Location.Provider value={{ entity: 1 }}>
        <Locale.Provider value={{ cldrPlurals: [1, 5] }}>
          <EntityViewProvider>
            <Spy />
          </EntityViewProvider>
        </Locale.Provider>
      </Location.Provider>,
    );

    expect(view).toMatchObject({
      entity: ENTITIES[0],
      hasPluralForms: false,
      pluralForm: 0,
    });

    wrapper.setProps({ value: { entity: 2 } });

    expect(view).toMatchObject({
      entity: ENTITIES[1],
      hasPluralForms: true,
      pluralForm: 0,
    });

    act(() => view.setPluralForm(1));

    expect(view).toMatchObject({
      entity: ENTITIES[1],
      hasPluralForms: true,
      pluralForm: 1,
    });
  });
});

describe('useActiveTranslation', () => {
  beforeAll(() => {
    sinon.stub(React, 'useContext');
    sinon.stub(React, 'useMemo').callsFake((cb) => cb());
  });

  afterAll(() => {
    React.useContext.restore();
    React.useMemo.restore();
  });

  it('returns the correct string', () => {
    React.useContext.returns({
      entity: { translation: [{ string: 'world' }] },
      pluralForm: 0,
    });
    const res = useActiveTranslation();
    expect(res).toEqual({ string: 'world' });
  });

  it('does not return rejected translations', () => {
    React.useContext.returns({
      entity: { translation: [{ string: 'world', rejected: true }] },
      pluralForm: 0,
    });
    const res = useActiveTranslation();
    expect(res).toBeNull();
  });
});
