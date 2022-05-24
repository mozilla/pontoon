import { mount } from 'enzyme';
import React, { useContext } from 'react';
import Sinon from 'sinon';

import * as EntityView from './EntityView';
import { FailedChecksData, FailedChecksProvider } from './FailedChecksData';

describe('FailedChecksProvider', () => {
  beforeAll(() => Sinon.stub(EntityView, 'useActiveTranslation'));
  afterAll(() => EntityView.useActiveTranslation.restore());

  it('shows failed checks for approved translations with errors or warnings', () => {
    EntityView.useActiveTranslation.returns({ errors: [], warnings: [] });

    let failedChecks;
    const Spy = () => {
      failedChecks = useContext(FailedChecksData);
      return null;
    };
    const wrapper = mount(
      <FailedChecksProvider>
        <Spy />
      </FailedChecksProvider>,
    );

    expect(failedChecks).toMatchObject({
      errors: [],
      warnings: [],
      source: null,
    });

    EntityView.useActiveTranslation.returns({
      errors: ['Error1'],
      warnings: ['Warning1'],
      approved: true,
    });
    wrapper.setProps({});

    expect(failedChecks).toMatchObject({
      errors: ['Error1'],
      warnings: ['Warning1'],
      source: 'stored',
    });
  });

  it('hides failed checks for pretranslated translations without errors or warnings', () => {
    EntityView.useActiveTranslation.returns({
      errors: [],
      warnings: [],
      pretranslated: [],
    });

    let failedChecks;
    const Spy = () => {
      failedChecks = useContext(FailedChecksData);
      return null;
    };
    mount(
      <FailedChecksProvider>
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
