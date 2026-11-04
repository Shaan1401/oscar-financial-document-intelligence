import React from 'react';

interface OscarLogoProps {
  size?: number;
  className?: string;
  showWordmark?: boolean;
}

export const OscarLogo: React.FC<OscarLogoProps> = ({
  size = 36,
  className = '',
  showWordmark = false,
}) => {
  return (
    <div className={`inline-flex items-center space-x-2.5 ${className}`}>
      {/* Signature OSCAR Financial Intelligence Mark */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0"
        aria-label="OSCAR Logo"
      >
        <defs>
          <linearGradient id="oscarNavyGrad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#101B2D" />
            <stop offset="100%" stopColor="#080F1C" />
          </linearGradient>
          <linearGradient id="oscarGoldGrad" x1="6" y1="4" x2="26" y2="28" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#F5EEDC" />
            <stop offset="50%" stopColor="#D6B36A" />
            <stop offset="100%" stopColor="#C49F52" />
          </linearGradient>
          <linearGradient id="oscarAccentGrad" x1="9" y1="23" x2="23" y2="15" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#20B889" />
            <stop offset="60%" stopColor="#D6B36A" />
            <stop offset="100%" stopColor="#F5EEDC" />
          </linearGradient>
        </defs>

        {/* Elevated Navy Surface with subtle Gold metallic frame */}
        <rect
          x="1"
          y="1"
          width="30"
          height="30"
          rx="7"
          fill="url(#oscarNavyGrad)"
          stroke="#D6B36A"
          strokeWidth="1.2"
          strokeOpacity="0.5"
        />

        {/* 1. Document / Bank Statement Silhouette with Folded Corner */}
        <path
          d="M8.5 6.5C8.5 5.67157 9.17157 5 10 5H18.5L23.5 10V24C23.5 24.8284 22.8284 25.5 22 25.5H10C9.17157 25.5 8.5 24.8284 8.5 24V6.5Z"
          fill="#17243A"
          fillOpacity="0.45"
          stroke="url(#oscarGoldGrad)"
          strokeWidth="1.3"
          strokeLinejoin="round"
        />

        {/* Folded Corner Ear Flap */}
        <path
          d="M18.5 5V10H23.5"
          stroke="url(#oscarGoldGrad)"
          strokeWidth="1.2"
          strokeLinejoin="round"
          fill="#D6B36A"
          fillOpacity="0.2"
        />

        {/* 2. Statement Ledger Transaction Lines */}
        <line
          x1="11.5"
          y1="12"
          x2="16.5"
          y2="12"
          stroke="#DFC793"
          strokeWidth="1.4"
          strokeLinecap="round"
        />
        <line
          x1="11.5"
          y1="15"
          x2="15"
          y2="15"
          stroke="#DFC793"
          strokeWidth="1.4"
          strokeLinecap="round"
          strokeOpacity="0.75"
        />

        {/* 3. Upward Financial Analytics & Reconciliation Trajectory */}
        <path
          d="M11.5 21.5L14.5 18.5L17.5 20.5L21.5 15"
          stroke="url(#oscarAccentGrad)"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Terminal Reconciliation Proof Node Dot */}
        <circle
          cx="21.5"
          cy="15"
          r="1.4"
          fill="#F5EEDC"
          stroke="#D6B36A"
          strokeWidth="0.8"
        />
      </svg>

      {showWordmark && (
        <span className="font-extrabold text-lg text-slate-900 dark:text-[#F4F1E9] tracking-tight">
          OSCAR
        </span>
      )}
    </div>
  );
};
