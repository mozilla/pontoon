import { mount } from 'enzyme';
import { useContext } from 'react';

import * as EntityView from './EntityView';
import { FailedChecksData, FailedChecksProvider } from './FailedChecksData';
import { vi } from 'vitest';

describe('FailedChecksProvider', () => {
  beforeAll(() => {
    vi.mock('./EntityView', () => ({ useActiveTranslation: vi.fn() }));
  });

  afterAll(() => {
    EntityView.useActiveTranslation.mockRestore();
  });

  it('shows failed checks for approved translations with errors or warnings', () => {
    EntityView.useActiveTranslation.mockReturnValue({
      errors: [],
      warnings: [],
    });

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

    EntityView.useActiveTranslation.mockReturnValue({
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
    EntityView.useActiveTranslation.mockReturnValue({
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
