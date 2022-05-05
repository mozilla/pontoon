import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { ProjectInfo } from './ProjectInfo';

describe('<ProjectInfo>', () => {
  const PROJECT = { fetching: false, name: 'hello', info: 'Hello, World!' };

  it('shows only a button by default', () => {
    const store = createReduxStore({ project: PROJECT });
    const wrapper = mountComponentWithStore(ProjectInfo, store);

    expect(wrapper.find('.button').exists()).toBeTruthy();
    expect(wrapper.find('aside').exists()).toBeFalsy();
  });

  it('shows the info panel after a click', () => {
    const store = createReduxStore({ project: PROJECT });
    const wrapper = mountComponentWithStore(ProjectInfo, store);
    wrapper.find('.button').simulate('click');

    expect(wrapper.find('aside.panel').exists()).toBeTruthy();
  });

  it('returns null when data is being fetched', () => {
    const store = createReduxStore({ project: { ...PROJECT, fetching: true } });
    const wrapper = mountComponentWithStore(ProjectInfo, store);

    expect(wrapper.find('ProjectInfo').isEmptyRender()).toBe(true);
  });

  it('returns null when info is null', () => {
    const store = createReduxStore({ project: { ...PROJECT, info: '' } });
    const wrapper = mountComponentWithStore(ProjectInfo, store);

    expect(wrapper.find('ProjectInfo').isEmptyRender()).toBe(true);
  });

  it('displays project info with HTML unchanged (', () => {
    const html = '<a href="#">test</a>';
    const store = createReduxStore({ project: { ...PROJECT, info: html } });
    const wrapper = mountComponentWithStore(ProjectInfo, store);
    wrapper.find('.button').simulate('click');

    expect(wrapper.find('aside.panel').html()).toContain(html);
  });
});
