import React from 'react';
import { shallow } from 'enzyme';
import { Linkify } from '.';

describe('Linkify', () => {
  it('renders links as expected on plain text', () => {
    const wrapper = shallow(
      <Linkify>See pontoon.mozilla.org for more.</Linkify>,
    );
    const links = wrapper.find('a');
    expect(links.length).toBe(1);
    const link = links.at(0);
    expect(link.text()).toBe('pontoon.mozilla.org');
    expect(link.prop('href')).toBe('http://pontoon.mozilla.org');
    expect(link.prop('target')).toBeUndefined();
  });
  it('sets rel and target', () => {
    const wrapper = shallow(
      <Linkify
        properties={{
          target: '_blank',
          rel: 'noopener noreferrer',
        }}
      >
        more pontoon.mozilla.org content
      </Linkify>,
    );
    const links = wrapper.find('a');
    expect(links.length).toBe(1);
    const link = links.at(0);
    expect(link.text()).toBe('pontoon.mozilla.org');
    expect(link.prop('href')).toBe('http://pontoon.mozilla.org');
    expect(link.prop('target')).toBe('_blank');
    expect(link.prop('rel')).toContain('noopener');
    expect(link.prop('rel')).toContain('noreferrer');
  });
  it('leaves existing links alone', () => {
    const wrapper = shallow(
      <Linkify>
        more <a href='https://example.com'>pontoon.mozilla.org</a> content
      </Linkify>,
    );
    const links = wrapper.find('a');
    expect(links.length).toBe(1);
    const link = links.at(0);
    expect(link.text()).toBe('pontoon.mozilla.org');
    expect(link.prop('href')).toBe('https://example.com');
  });
});
