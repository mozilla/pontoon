import { createReduxStore, mountComponentWithStore } from '~/test/store';
import {describe,it,expect} from "vitest"
import { ResourceProgress } from './ResourceProgress';

describe('<ResourceProgress>', () => {
  const STATS = {
    approved: 5,
    pretranslated: 4,
    unreviewed: 5,
    warnings: 3,
    errors: 2,
    missing: 1,
    total: 15,
  };
  const PARAMETERS = {
    entity: 0,
    locale: 'en-GB',
    project: 'tutorial',
    resource: 'all-resources',
    status: 'errors',
    search: null,
  };

  beforeAll(() => {
    HTMLCanvasElement.prototype.getContext = jest.fn();
  });

  it('shows only a selector by default', () => {
    const store = createReduxStore({ stats: STATS });
    const wrapper = mountComponentWithStore(ResourceProgress, store, {
      parameters: PARAMETERS,
    });

    expect(wrapper.find('.selector').exists()).toBeTruthy();
    expect(wrapper.find('ResourceProgressDialog').exists()).toBeFalsy();
  });

  it('shows the info menu after a click', () => {
    const store = createReduxStore({ stats: STATS });
    const wrapper = mountComponentWithStore(ResourceProgress, store, {
      parameters: PARAMETERS,
    });
    wrapper.find('.selector').simulate('click');

    expect(wrapper.find('ResourceProgressDialog').exists()).toBeTruthy();
  });
});
