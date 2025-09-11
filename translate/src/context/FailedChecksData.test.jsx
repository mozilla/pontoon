import { useContext } from 'react';
import {render} from "@testing-library/react"
import * as EntityView from './EntityView';
import { FailedChecksData, FailedChecksProvider } from './FailedChecksData';
import {describe,it,expect, afterEach, beforeEach } from 'vitest';

describe('FailedChecksProvider', () => {
  let spy;
  beforeEach(() => { 
    spy = vi.spyOn(EntityView, 'useActiveTranslation')});
  afterEach(() => {vi.restoreAllMocks();});

  it('shows failed checks for approved translations with errors or warnings', () => {
    spy.mockReturnValue({ errors: [], warnings: [] });

    let failedChecks;
    const Spy = () => {
      failedChecks = useContext(FailedChecksData);
      return null;
    };
    render(
      <FailedChecksProvider>
        <Spy />
      </FailedChecksProvider>,
    );

    expect(failedChecks).toMatchObject({
      errors: [],
      warnings: [],
      source: null,
    });

    spy.mockReturnValue({
      errors: ['Error1'],
      warnings: ['Warning1'],
      approved: true,
    });
     render(
      <FailedChecksProvider>
        <Spy />
      </FailedChecksProvider>
    );

    expect(failedChecks).toMatchObject({
      errors: ['Error1'],
      warnings: ['Warning1'],
      source: 'stored',
    });
  });

  it('hides failed checks for pretranslated translations without errors or warnings', () => {
    spy.mockReturnValue({
      errors: [],
      warnings: [],
      pretranslated: [],
    });

    let failedChecks;
    const Spy = () => {
      failedChecks = useContext(FailedChecksData);
      return null;
    };
    render(
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
