/**
 * Scroll `element` into view, respecting the user's reduced-motion preference.
 */
export function scrollIntoView(element: Element | null | undefined): void {
  const mediaQuery = window.matchMedia?.('(prefers-reduced-motion: reduce)');
  element?.scrollIntoView?.({
    behavior: mediaQuery?.matches ? 'auto' : 'smooth',
    block: 'nearest',
  });
}
