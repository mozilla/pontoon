import { useEffect, useRef } from 'react';

type Props = {
  getUserData: () => void;
};

/**
 * Regularly fetch user data to keep it up-to-date with the server.
 */
export function UserAutoUpdater({ getUserData }: Props): null {
  const timer = useRef<number | null>(null);
  useEffect(() => {
    getUserData();
    timer.current = window.setInterval(getUserData, 2 * 60 * 1000);
    return () => {
      if (typeof timer.current === 'number') {
        window.clearInterval(timer.current);
        timer.current = null;
      }
    };
  }, []);

  return null;
}
