import { useState, useEffect, useRef } from "react";

type Alignment = "left" | "center" | "right";

interface PositionOptions {
  align?: Alignment;
  offset?: number;
  viewportPadding?: number;
}

interface PositionResult {
  alignment: Alignment;
  shouldFlip: boolean;
  style: React.CSSProperties;
}

export function useDropdownPosition(
  triggerRef: React.RefObject<HTMLElement | null>,
  contentRef: React.RefObject<HTMLElement | null>,
  options: PositionOptions = {},
): PositionResult {
  const { align = "left", offset = 8, viewportPadding = 8 } = options;
  const [position, setPosition] = useState<PositionResult>({
    alignment: align,
    shouldFlip: false,
    style: {},
  });

  useEffect(() => {
    function update() {
      if (!triggerRef.current || !contentRef.current) return;

      const triggerRect = triggerRef.current.getBoundingClientRect();
      const contentRect = contentRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;

      const spaceRight = viewportWidth - triggerRect.right - viewportPadding;
      const spaceLeft = triggerRect.left - viewportPadding;
      const contentWidth = contentRect.width || 200;

      let alignment: Alignment = align;
      let shouldFlip = false;

      if (align === "left" && spaceRight < contentWidth && spaceLeft > spaceRight) {
        alignment = "right";
        shouldFlip = true;
      } else if (align === "right" && spaceLeft < contentWidth && spaceRight > spaceLeft) {
        alignment = "left";
        shouldFlip = true;
      } else if (align === "center") {
        const spaceBelow =
          window.innerHeight - triggerRect.bottom - viewportPadding;
        if (spaceBelow < (contentRect.height || 200) && triggerRect.top > spaceBelow) {
          shouldFlip = true;
        }
      }

      const top = triggerRect.bottom + offset;
      const left =
        alignment === "left"
          ? triggerRect.left
          : alignment === "right"
            ? triggerRect.right - contentWidth
            : triggerRect.left + triggerRect.width / 2 - contentWidth / 2;

      setPosition({
        alignment,
        shouldFlip,
        style: {
          position: "fixed",
          top: Math.min(top, window.innerHeight - (contentRect.height || 200) - viewportPadding),
          left: Math.max(viewportPadding, Math.min(left, viewportWidth - contentWidth - viewportPadding)),
          zIndex: 9999,
        },
      });
    }

    update();
    window.addEventListener("resize", update);
    window.addEventListener("scroll", update, true);
    return () => {
      window.removeEventListener("resize", update);
      window.removeEventListener("scroll", update, true);
    };
  }, [triggerRef, contentRef, align, offset, viewportPadding]);

  return position;
}
