import sinon from 'sinon';

import { MentionUsers } from '~/context/MentionUsers';
import { createReduxStore, mountComponentWithStore , renderComponentWithStore} from '~/test/store';
import { AddComment } from './AddComment';

const USER = {
  user: 'RSwanson',
  username: 'Ron_Swanson',
  imageURL: '',
};

describe('<AddComment>', () => {
  it('calls submitComment function',async () => {
 const submitCommentFn = sinon.spy();
    const Wrapper = () => (
      <MentionUsers.Provider
        value={{ initMentions: sinon.spy(), mentionUsers: [] }}
      >
        <AddComment onAddComment={submitCommentFn} user={USER} />
      </MentionUsers.Provider>
    );
    const wrapper = mountComponentWithStore(Wrapper, store);

    const event = {
      preventDefault: sinon.spy(),
    };

    wrapper.find('button').simulate('click', event);
    expect(submitCommentFn.calledOnce).toBeTruthy;
  });

  it.only('fetches mentionable users on render', () => {
    const initMentions = vi.fn();
    const store = createReduxStore();

     renderComponentWithStore(
      ({ ...props }) => (
        <MentionUsers.Provider value={{ initMentions, mentionUsers: [] }}>
          <AddComment {...props} />
        </MentionUsers.Provider>
      ),
      store,
      { user: USER }
    );
    expect(initMentions).toHaveBeenCalledTimes(1);
  });
});
