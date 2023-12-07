import { useEffect, useState } from 'react';

const BREAKPOINTS = {
  narrow: 600,
  medium: 800,
};

/**
 * Return window width range: narrow, medium or wide.
 *
 * Useful in Responsive Web Design.
 */
export function useWindowWidth(): 'narrow' | 'medium' | 'wide' {
  function get_range(): 'narrow' | 'medium' | 'wide' {
    if (window.innerWidth <= BREAKPOINTS.narrow) {
      return 'narrow';
    }
    if (window.innerWidth <= BREAKPOINTS.medium) {
      return 'medium';
    }
    return 'wide';
  }

  const [windowWidth, setWindowWidth] = useState(get_range());

  useEffect(() => {
    const handleWindowResize = () => setWindowWidth(get_range());
    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, []);

  return windowWidth;
}
