import React from "react";

interface AnnouncerProps {
  message: string;
}

export const AccessibleLiveAnnouncer: React.FC<AnnouncerProps> = ({ message }) => {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
      id="screen-reader-announcer"
    >
      {message}
    </div>
  );
};
