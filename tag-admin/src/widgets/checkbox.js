import React, { useEffect, useRef } from 'react';

/** A checkbox which you can set `indeterminate` on */
export function Checkbox({ indeterminate, ...props }) {
  const ref = useRef();

  useEffect(() => {
    if (ref.current) {
      ref.current.indeterminate = !!indeterminate;
    }
  }, [indeterminate]);

  return <input {...props} type='checkbox' ref={ref} />;
}
