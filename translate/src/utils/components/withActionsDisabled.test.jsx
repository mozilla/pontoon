import {describe,it,expect} from "vitest";
import userEvent from "@testing-library/user-event"
import { withActionsDisabled } from './withActionsDisabled';
import {render,screen} from "@testing-library/react";
// A simple fake component that shows props as text for testing
function FakeComp({ isActionDisabled, disableAction, foo, baz }) {
  return (
    <div>
      <span data-testid="disabled">{String(isActionDisabled)}</span>
      <button onClick={disableAction}>disable</button>
      <span data-testid="foo">{foo}</span>
      <span data-testid="baz">{baz}</span>
    </div>
  );
}
const WrappedComp = withActionsDisabled(FakeComp);
describe('withActionsDisabled', () => {
  

  it('passes internal props correctly', () => {
    render(<WrappedComp/>)
     expect(screen.getByTestId("disabled").textContent).toBe("false");
    expect(screen.getByRole("button")).toBeTruthy();
  });

  it('passes other props along', () => {
    render(<WrappedComp foo="bar" baz={42} />);
    expect(screen.getByTestId("foo").textContent).toBe("bar");
    expect(screen.getByTestId("baz").textContent).toBe("42");
  });

  it('turns action off until next render',async () => {
    const user = userEvent.setup();
    const { rerender } = render(<WrappedComp />);

    expect(screen.getByTestId("disabled").textContent).toBe("false");

    await user.click(screen.getByRole("button"));
    expect(screen.getByTestId("disabled").textContent).toBe("true");

    rerender(<WrappedComp foo="var" />);
    expect(screen.getByTestId("disabled").textContent).toBe("false");
  });
});
