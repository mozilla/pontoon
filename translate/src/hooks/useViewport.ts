import { useEffect, useState } from 'react';

/**
 * Return current window width. Useful in Responsive Web Design.
 */
export function useViewport(): { width: number } {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleWindowResize = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, []);

  return { width };
}
