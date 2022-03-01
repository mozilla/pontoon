import sinon from 'sinon';
import * as Hooks from '~/hooks';
import * as Location from '~/hooks/useLocation';
import { useReadonlyEditor } from './useReadonlyEditor';

beforeAll(() => {
  sinon.stub(Hooks, 'useAppSelector');
  sinon.stub(Location, 'useLocation').returns({ entity: 42 });
});
afterAll(() => {
  Hooks.useAppSelector.restore();
  Location.useLocation.restore();
});

const fakeSelector = (readonly, isAuthenticated) => (cb) =>
  cb({
    entities: {
      entities: [{ pk: 42, original: 'hello', readonly }],
    },
    user: { isAuthenticated },
  });

describe('useReadonlyEditor', () => {
  it('returns true if user not authenticated', () => {
    Hooks.useAppSelector.callsFake(fakeSelector(false, false));
    expect(useReadonlyEditor()).toBeTruthy();
  });

  it('returns true if entity read-only', () => {
    Hooks.useAppSelector.callsFake(fakeSelector(true, true));
    expect(useReadonlyEditor()).toBeTruthy();
  });

  it('returns false if entity not read-only and user authenticated', () => {
    Hooks.useAppSelector.callsFake(fakeSelector(false, true));
    expect(useReadonlyEditor()).toBeFalsy();
  });
});
