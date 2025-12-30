import { mount } from 'enzyme';
import  { useContext } from 'react';

import {
  EntityView,
  EntityViewProvider,
} from './EntityView';
import { Locale } from './Locale';
import { Location } from './Location';

const ENTITIES = [
  { pk: 1, original: 'hello' },
  { pk: 2, original: 'world' },
  { pk: 3 },
];

describe('<EntityViewProvider', () => {
  vi.mock('~/hooks', () => ({ useAppSelector: vi.fn(() => ENTITIES) }));

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

    expect(view).toMatchObject({ entity: ENTITIES[0] });

    wrapper.setProps({ value: { entity: 2 } });

    expect(view).toMatchObject({ entity: ENTITIES[1] });
  });
});
