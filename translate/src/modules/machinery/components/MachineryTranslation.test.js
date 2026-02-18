import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { MachineryTranslationComponent } from './MachineryTranslation';

const ORIGINAL = 'A horse, a horse! My kingdom for a horse!';
const DEFAULT_TRANSLATION = {
  sources: [{ type: 'translation-memory' }],
  original: ORIGINAL,
  translation: 'Un cheval, un cheval ! Mon royaume pour un cheval !',
};

function createMachineryTranslation(translation) {
  const store = createReduxStore();
  const wrapper = mountComponentWithStore(
    MachineryTranslationComponent,
    store,
    { translation },
  );
  createDefaultUser(store);
  return wrapper;
}

describe('<MachineryTranslationComponent>', () => {
  let getSelectionBackup;

  beforeAll(() => {
    getSelectionBackup = window.getSelection;
    window.getSelection = () => {
      return {
        toString: () => {},
      };
    };
  });

  afterAll(() => {
    window.getSelection = getSelectionBackup;
  });

  it('renders a translation correctly', () => {
    const { container } = createMachineryTranslation(DEFAULT_TRANSLATION);

    expect(container.querySelector('.original').textContent).toContain(
      'A horse, a horse!',
    );

    expect(container.querySelector('.suggestion').textContent).toContain(
      'Un cheval, un cheval !',
    );

    // No quality.
    expect(container.querySelector('.quality')).not.toBeInTheDocument();
  });

  it('shows quality when possible', () => {
    const translation = {
      ...DEFAULT_TRANSLATION,
      quality: 100,
    };
    const { container } = createMachineryTranslation(translation);

    expect(container.querySelector('.quality')).toBeInTheDocument();
    expect(container.querySelector('.quality')).toHaveTextContent('100%');
  });
});
