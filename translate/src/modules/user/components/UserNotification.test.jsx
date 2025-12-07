import { mount } from 'enzyme';
import React from 'react';
import { UserNotification } from './UserNotification';

jest.mock('react-time-ago', () => () => null);

const notificationBase = {
  id: 0,
  level: 'level',
  unread: false,
  description: null,
  verb: 'verb',
  date: 'Jan 31, 2000 10:20',
  date_iso: '2019-01-31T10:20:00+00:00',
  actor: { anchor: 'actor_anchor', url: 'actor_url' },
  target: { anchor: 'target_anchor', url: 'target_url' },
};

describe('<UserNotification>', () => {
  it('shows an "Unreviewed suggestions" notification', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Unreviewed suggestions: <b id="foo">foo</b>' },
    };
    const wrapper = mount(<UserNotification notification={notification} />);

    // https://github.com/enzymejs/enzyme/issues/419
    const desc = wrapper.find('span.description').render();
    expect(desc.find('b#foo')).toHaveLength(1);
  });

  it('shows a "has reviewed suggestions" notification', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Reviewed: <b id="bar">bar</b>' },
      verb: 'has reviewed suggestions',
    };
    const wrapper = mount(<UserNotification notification={notification} />);

    // https://github.com/enzymejs/enzyme/issues/419
    const desc = wrapper.find('span.description').render();
    expect(desc.find('b#bar')).toHaveLength(1);
  });

  it('shows a comment notification', () => {
    const notification = {
      ...notificationBase,
      description: {
        content: 'Comment: <b id="baz">baz</b>',
        is_comment: true,
      },
    };
    const wrapper = mount(<UserNotification notification={notification} />);

    expect(wrapper.find('.message.trim b#baz')).toHaveLength(1);
  });

  it('shows other notification with description', () => {
    const notification = {
      ...notificationBase,
      description: { content: 'Other: <b id="fuzz">fuzz</b>' },
    };
    const wrapper = mount(<UserNotification notification={notification} />);

    // https://github.com/enzymejs/enzyme/issues/419
    const desc = wrapper.find('.message').render();
    expect(desc.find('b#fuzz')).toHaveLength(1);
  });

  it('shows other notification without description', () => {
    const notification = {
      ...notificationBase,
      description: { content: null },
      verb: 'is Other',
    };
    const wrapper = mount(<UserNotification notification={notification} />);

    expect(wrapper.find('.message').text()).toBe('');
    expect(wrapper.find('.verb').text()).toBe('is Other');
  });
});
