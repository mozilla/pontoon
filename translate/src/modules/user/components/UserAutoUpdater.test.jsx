import React from 'react';
import sinon from 'sinon';
import { mount } from 'enzyme';

import { UserAutoUpdater } from './UserAutoUpdater';

describe('<UserAutoUpdater>', () => {
  it('fetches user data on mount', () => {
    const getUserData = sinon.spy();
    mount(<UserAutoUpdater getUserData={getUserData} />);

    expect(getUserData.callCount).toEqual(1);
  });

  it('fetches user data every 2 minutes', () => {
    jest.useFakeTimers();

    const getUserData = sinon.spy();
    mount(<UserAutoUpdater getUserData={getUserData} />);

    jest.advanceTimersByTime(2 * 60 * 1000);
    expect(getUserData.callCount).toEqual(2);

    jest.advanceTimersByTime(2 * 60 * 1000);
    expect(getUserData.callCount).toEqual(3);

    // If less than 2 minutes have passed, it doesn't trigger.
    jest.advanceTimersByTime(60 * 1000);
    expect(getUserData.callCount).toEqual(3);
  });
});
