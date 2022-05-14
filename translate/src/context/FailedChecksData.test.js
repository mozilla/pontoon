import { mount } from 'enzyme';
import React, { useContext } from 'react';

import { FailedChecksData, FailedChecksProvider } from './FailedChecksData';

describe('FailedChecksProvider', () => {
  it('shows failed checks for approved translations with errors or warnings', () => {
    let failedChecks;
    const Spy = () => {
      failedChecks = useContext(FailedChecksData);
      return null;
    };
    const translation = { errors: [], warnings: [] };
    const wrapper = mount(
      <FailedChecksProvider translation={translation}>
        <Spy />
      </FailedChecksProvider>,
    );

    expect(failedChecks).toMatchObject({
      errors: [],
      warnings: [],
      source: null,
    });

    wrapper.setProps({
      translation: {
        errors: ['Error1'],
        warnings: ['Warning1'],
        approved: true,
      },
    });

    expect(failedChecks).toMatchObject({
      errors: ['Error1'],
      warnings: ['Warning1'],
      source: 'stored',
    });
  });

  it('hides failed checks for pretranslated translations without errors or warnings', () => {
    let failedChecks;
    const Spy = () => {
      failedChecks = useContext(FailedChecksData);
      return null;
    };
    const translation = { errors: [], warnings: [], pretranslated: [] };
    mount(
      <FailedChecksProvider translation={translation}>
        <Spy />
      </FailedChecksProvider>,
    );

    expect(failedChecks).toMatchObject({
      errors: [],
      warnings: [],
      source: null,
    });
  });
});
