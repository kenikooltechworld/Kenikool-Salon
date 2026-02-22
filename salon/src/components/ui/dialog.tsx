import React from "react";

export interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

export const Dialog = ({ open, onOpenChange, children }: DialogProps) => {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--overlay)]"
      onClick={() => onOpenChange(false)}
    >
      <div
        className="bg-[var(--background)] rounded-[var(--radius-lg)] shadow-[var(--shadow-lg)] max-w-md w-[calc(100%-1rem)] sm:w-full p-3 xs:p-4 sm:p-6 border border-[var(--border)]"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
};

export const DialogContent = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return <div className={className}>{children}</div>;
};

export const DialogHeader = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return <div className={`mb-4 ${className}`}>{children}</div>;
};

export const DialogTitle = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <h2
      className={`text-xl font-semibold text-[var(--foreground)] ${className}`}
    >
      {children}
    </h2>
  );
};

export const DialogDescription = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  return <p className="text-sm text-[var(--muted-foreground)]">{children}</p>;
};

export const DialogFooter = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <div className={`flex justify-end gap-2 mt-6 ${className}`}>{children}</div>
  );
};

export const DialogTrigger = ({
  children,
  onClick,
  className = "",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
}) => {
  return (
    <button onClick={onClick} className={className}>
      {children}
    </button>
  );
};
