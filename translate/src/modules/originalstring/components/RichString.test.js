import ftl from '@fluent/dedent';
import React from 'react';
import { mount } from 'enzyme';
import sinon from 'sinon';

import { editMessageEntry, parseEntry } from '~/utils/message';
import { RichString } from './RichString';

const ORIGINAL = ftl`
  song-title = Hello
      .genre = Pop
      .album = Hello and Good Bye
  `;

describe('<RichString>', () => {
  it('renders value and each attribute correctly', () => {
    const message = editMessageEntry(parseEntry(ORIGINAL));
    const wrapper = mount(<RichString message={message} terms={{}} />);

    expect(wrapper.find('Highlight')).toHaveLength(3);

    expect(wrapper.find('label').at(0).html()).toContain('Value');
    expect(wrapper.find('Highlight').at(0).html()).toContain('Hello');

    expect(wrapper.find('label').at(1).html()).toContain('genre');
    expect(wrapper.find('Highlight').at(1).html()).toContain('Pop');

    expect(wrapper.find('label').at(2).html()).toContain('album');
    expect(wrapper.find('Highlight').at(2).html()).toContain(
      'Hello and Good Bye',
    );
  });

  it('renders select expression correctly', () => {
    const input = ftl`
      user-entry =
          { PLATFORM() ->
              [variant-1] Hello!
             *[variant-2] Good Bye!
          }
      `;

    const message = editMessageEntry(parseEntry(input));
    const wrapper = mount(<RichString message={message} terms={{}} />);

    expect(wrapper.find('Highlight')).toHaveLength(2);

    expect(wrapper.find('label').at(0).html()).toContain('variant-1');
    expect(wrapper.find('Highlight').at(0).html()).toContain('Hello!');

    expect(wrapper.find('label').at(1).html()).toContain('variant-2');
    expect(wrapper.find('Highlight').at(1).html()).toContain('Good Bye!');
  });

  it('renders select expression in attributes properly', () => {
    const input = ftl`
      my-entry =
          .label =
              { PLATFORM() ->
                  [macosx] Preferences
                 *[other] Options
              }
          .accesskey =
              { PLATFORM() ->
                  [macosx] e
                 *[other] s
              }
      `;

    const message = editMessageEntry(parseEntry(input));
    const wrapper = mount(<RichString message={message} terms={{}} />);

    expect(wrapper.find('label')).toHaveLength(4);
    expect(wrapper.find('td > span')).toHaveLength(4);

    expect(wrapper.find('label').at(0).html()).toMatch(/label.*macosx/);
    expect(wrapper.find('td > span').at(0).html()).toContain('Preferences');

    expect(wrapper.find('label').at(1).html()).toMatch(/label.*other/);
    expect(wrapper.find('td > span').at(1).html()).toContain('Options');

    expect(wrapper.find('label').at(2).html()).toMatch(/accesskey.*macosx/);
    expect(wrapper.find('td > span').at(2).html()).toContain('e');

    expect(wrapper.find('label').at(3).html()).toMatch(/accesskey.*other/);
    expect(wrapper.find('td > span').at(3).html()).toContain('s');
  });

  it('calls the onClick function on click on .original', () => {
    const message = editMessageEntry(parseEntry(ORIGINAL));
    const spy = sinon.spy();
    const wrapper = mount(
      <RichString message={message} onClick={spy} terms={{}} />,
    );

    wrapper.find('.original').simulate('click');
    expect(spy.called).toEqual(true);
  });
});
