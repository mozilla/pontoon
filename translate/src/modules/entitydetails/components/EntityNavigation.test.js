import React from 'react';
import { mount } from 'enzyme';
import sinon from 'sinon';

import { MockLocalizationProvider } from '~/test/utils';

import { EntityNavigation } from './EntityNavigation';

describe('<EntityNavigation>', () => {
  function getEntityNav() {
    const copyMock = sinon.stub();
    const nextMock = sinon.stub();
    const prevMock = sinon.stub();
    const wrapper = mount(
      <MockLocalizationProvider>
        <EntityNavigation
          copyLinkToClipboard={copyMock}
          goToNextEntity={nextMock}
          goToPreviousEntity={prevMock}
        />
      </MockLocalizationProvider>,
    );

    return {
      wrapper,
      copyMock,
      nextMock,
      prevMock,
    };
  }

  it('puts a copy of string link on clipboard', () => {
    const { wrapper, copyMock } = getEntityNav();

    expect(copyMock.calledOnce).toBeFalsy();
    wrapper.find('button.link').simulate('click');
    expect(copyMock.calledOnce).toBeTruthy();
  });

  it('goes to the next entity on click on the Next button', () => {
    const { wrapper, nextMock } = getEntityNav();

    expect(nextMock.calledOnce).toBeFalsy();
    wrapper.find('button.next').simulate('click');
    expect(nextMock.calledOnce).toBeTruthy();
  });

  it('goes to the next entity on Alt + Down', () => {
    // Simulating the key presses on `document`.
    // See https://github.com/airbnb/enzyme/issues/426
    const eventsMap = {};
    document.addEventListener = sinon.spy((event, cb) => {
      eventsMap[event] = cb;
    });

    const { nextMock } = getEntityNav();

    expect(nextMock.calledOnce).toBeFalsy();
    const event = {
      preventDefault: sinon.spy(),
      key: 'ArrowDown',
      altKey: true,
      ctrlKey: false,
      shiftKey: false,
    };
    eventsMap.keydown(event);
    expect(nextMock.calledOnce).toBeTruthy();
  });

  it('goes to the previous entity on click on the Previous button', () => {
    const { wrapper, prevMock } = getEntityNav();

    expect(prevMock.calledOnce).toBeFalsy();
    wrapper.find('button.previous').simulate('click');
    expect(prevMock.calledOnce).toBeTruthy();
  });

  it('goes to the previous entity on Alt + Up', () => {
    // Simulating the key presses on `document`.
    // See https://github.com/airbnb/enzyme/issues/426
    const eventsMap = {};
    document.addEventListener = sinon.spy((event, cb) => {
      eventsMap[event] = cb;
    });

    const { prevMock } = getEntityNav();

    expect(prevMock.calledOnce).toBeFalsy();
    const event = {
      preventDefault: sinon.spy(),
      key: 'ArrowUp',
      altKey: true,
      ctrlKey: false,
      shiftKey: false,
    };
    eventsMap.keydown(event);
    expect(prevMock.calledOnce).toBeTruthy();
  });
});
