import { createReduxStore } from '~/test/store';
import {describe,it,expect, vi } from 'vitest';
import {render,screen} from "@testing-library/react"
import { UserControls } from './UserControls';
import {Provider} from "react-redux"
import { SignInOutForm } from './SignInOutForm';

vi.mock('./UserAutoUpdater', () => ({ UserAutoUpdater: () => null }));
vi.mock('./SignInOutForm',()=>({
  SignInOutForm: ({children,url})=> <a href={url}>{children}</a>,
}))
vi.mock('@fluent/react',()=>({
  Localized: ({children})=> <>{children}</>
}))

describe('<UserControls>', () => {
  it('shows a Sign in link when user is logged out', () => {
    const store = createReduxStore({
      user: { isAuthenticated: false, notifications: {} , signInURL: '/login'},
    });
     render(
     <Provider store={store}>
      <UserControls/>
     </Provider>
     );
     const link = screen.getByRole('link', {name: /sign in/i})
     expect(link).toBeInTheDocument()
     expect(link).toHaveAttribute('href','/login');
  });

  it('hides a Sign in link when user is logged in', () => {
    const store = createReduxStore({
      user: { isAuthenticated: true, notifications: {}, signInURL: '/login' },
    });
    render(
    <Provider store={store}>
         <UserControls/>
      </Provider>
      );
      expect(screen.queryByRole('link', {name: /sign in/i})).toBeNull();
  });
});
