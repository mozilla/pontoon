import { mount } from 'enzyme';
import React from 'react';
import { act } from 'react-dom/test-utils';
import Sinon from 'sinon';

import { NotificationMessage, ShowNotification } from '~/context/Notification';
import { NotificationPanel } from './NotificationPanel';

describe('<NotificationPanel>', () => {
  beforeAll(() => Sinon.stub(React, 'useContext'));
  afterAll(() => React.useContext.restore());

  const NOTIF = {
    type: 'info',
    content: 'Hello, World!',
  };

  function mountNotifications(message) {
    const context = new Map([
      [NotificationMessage, message],
      [
        ShowNotification,
        (message) => context.set(NotificationMessage, message),
      ],
    ]);
    React.useContext.callsFake((key) => context.get(key));

    return mount(<NotificationPanel />);
  }

  it('returns an empty element when there is no notification', () => {
    const wrapper = mountNotifications(null);

    expect(wrapper.children()).toHaveLength(1);
    expect(wrapper.find('span').text()).toEqual('');
  });

  it('shows a message when there is a notification', () => {
    const wrapper = mountNotifications(NOTIF);

    expect(wrapper.find('span').text()).toEqual(NOTIF.content);
    expect(wrapper.find('.showing')).toHaveLength(1);
  });

  it('hides a message after a delay', () => {
    jest.useFakeTimers();
    const wrapper = mountNotifications(NOTIF);

    // Run time forward, the message with disappear.
    act(() => jest.runAllTimers());
    wrapper.setProps({});

    expect(wrapper.children()).toHaveLength(1);
    expect(wrapper.find('.showing')).toHaveLength(0);
  });

  it('hides a message on click', () => {
    const wrapper = mountNotifications(NOTIF);

    expect(wrapper.find('.showing')).toHaveLength(1);

    wrapper.simulate('click');
    wrapper.setProps({});

    expect(wrapper.find('.showing')).toHaveLength(0);
  });
});
