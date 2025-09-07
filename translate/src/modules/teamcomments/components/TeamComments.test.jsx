import { createReduxStore } from '../../../test/store';
import {describe,it,expect} from "vitest"
import { TeamComments } from './TeamComments';
import {Provider} from "react-redux"
import {render,screen} from "@testing-library/react"
vi.mock('react-time-ago', () =>({
  default:()=> null,
}));

describe('<TeamComments>', () => {
  const DEFAULT_USER = 'AndyDwyer';

  it('shows correct message when no comments', () => {
    const store = createReduxStore();
    render(
      <Provider store={store}>
        <TeamComments 
         teamComments={{entity: 267,comments:[]}}
         user={DEFAULT_USER}/>
      </Provider>
    )

    expect(screen.getByText('/No comments available./i')).toBeInTheDocument();
  });

  it('renders correctly when there are comments', () => {
    const store = createReduxStore();
    render(<Provider store={store}
    >
      <TeamComments
            teamComments={{
        entity: 267,
        comments: [
          { id: 1, content: '11', userBanner: '' },
          { id: 2, content: '22', userBanner: '' },
          { id: 3, content: '33', userBanner: '' },
        ],
      }}
      user={DEFAULT_USER}
      />
    </Provider>)
    expect(wrapper.children()).toHaveLength(1);
    expect(wrapper.find('li')).toHaveLength(3);
  });
});
