import React, { useEffect, useRef } from 'react';

import './ProgressChart.css';

import type { Stats } from '~/modules/stats';

type Props = {
  stats: Stats;
  size: number;
};

/**
 * Render current resource progress data on canvas.
 */
export function ProgressChart({
  size,
  stats,
}: Props): React.ReactElement<'canvas'> {
  const canvas = useRef<HTMLCanvasElement>(null);
  const dpr = window.devicePixelRatio || 1;
  const style = getComputedStyle(document.body);

  useEffect(() => {
    if (canvas.current) {
      const { height, width } = canvas.current;
      // Set up canvas to be HiDPI display ready
      canvas.current.style.width = width + 'px';
      canvas.current.style.height = height + 'px';
      canvas.current.width = width * dpr;
      canvas.current.height = height * dpr;
    }
  }, [dpr]);

  useEffect(() => {
    const { approved, pretranslated, warnings, errors, missing, total } = stats;

    if (!canvas.current || !total) {
      return;
    }
    const { height, width } = canvas.current;
    const context = canvas.current.getContext('2d');
    if (!context) {
      return;
    }

    const data = [
      { type: approved, color: style.getPropertyValue('--status-translated') },
      {
        type: pretranslated,
        color: style.getPropertyValue('--status-pretranslated'),
      },
      { type: warnings, color: style.getPropertyValue('--status-warning') },
      { type: errors, color: style.getPropertyValue('--status-error') },
      { type: missing, color: style.getPropertyValue('--status-missing') },
    ];

    // Clear old canvas content to avoid aliasing
    context.clearRect(0, 0, width, height);
    context.lineWidth = 3 * dpr;

    // Range: -0.25 .. 0.75
    let end = -0.25;

    const radius = (width - context.lineWidth) / 2;
    for (const { color, type } of data) {
      const start = end;
      end += type / total;

      context.beginPath();
      context.arc(
        width / 2,
        height / 2,
        radius,
        start * 2 * Math.PI,
        end * 2 * Math.PI,
      );
      context.strokeStyle = color;
      context.stroke();
    }
  }, [stats]);

  return <canvas ref={canvas} height={size} width={size} />;
}
