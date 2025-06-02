import React, { useEffect, useRef } from "react";

export default function Modal({ children, onClose }) {
  const ref = useRef();

  // Inject modal animation CSS once
  useEffect(() => {
    if (!document.getElementById("modal-anim-css")) {
      const style = document.createElement("style");
      style.id = "modal-anim-css";
      style.innerHTML = `
        .modal-fade-in { animation: modalFadeIn 0.22s cubic-bezier(.4,1.4,.6,1) both; }
        .modal-fade-out { animation: modalFadeOut 0.16s cubic-bezier(.4,1.4,.6,1) both; }
        @keyframes modalFadeIn { from { opacity:0; transform: translateY(30px) scale(.97); } to { opacity:1; transform: none; } }
        @keyframes modalFadeOut { from { opacity:1; } to { opacity:0; transform: translateY(30px) scale(.97); } }
        .modal-content:focus { outline: 2px solid #2684ff !important; box-shadow: 0 0 0 2px #b2d6ff; }
      `;
      document.head.appendChild(style);
    }
  }, []);

  // Focus trap and close with Enter/Escape
  useEffect(() => {
    const el = ref.current;
    if (el) el.focus();
    function handleKey(e) {
      if (e.key === "Escape" || (e.key === "Enter" && e.target === el)) onClose();
      if (e.key === "Tab") {
        const focusable = el.querySelectorAll("button, [href], input, select, textarea, [tabindex]:not([tabindex=\"-1\"])");
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  // Fade in/out state
  const [fadeOut, setFadeOut] = React.useState(false);
  const handleClose = () => {
    setFadeOut(true);
    setTimeout(onClose, 160);
  };

  return (
    <div
      className={fadeOut ? "modal-fade-out" : "modal-fade-in"}
      style={{
        position: "fixed", left: 0, top: 0, width: "100vw", height: "100vh",
        background: "rgba(0,0,0,0.35)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center",
        padding: 0, margin: 0,
      }}
      role="presentation"
      onClick={handleClose}
    >
      <div
        ref={ref}
        tabIndex={0}
        className="modal-content"
        role="dialog"
        aria-modal="true"
        aria-describedby="modal-content"
        style={{
          background: "#fff", borderRadius: 12, boxShadow: "0 4px 32px #0003", padding: 30, minWidth: 320, maxWidth: 480, width: "92vw", position: "relative",
          outline: "none",
          margin: 0,
          fontSize: 16,
          color: "#1a1a1a",
          transition: "box-shadow .16s",
          ...(window.innerWidth < 600 ? { minWidth: "unset", maxWidth: "unset", width: "100vw", borderRadius: 0, alignSelf: "flex-end" } : {})
        }}
        onClick={e => e.stopPropagation()}
        id="modal-content"
        aria-live="polite"
      >
        <button
          onClick={handleClose}
          style={{ position: "absolute", top: 14, right: 18, fontSize: 24, background: "none", border: "none", cursor: "pointer", color: "#666", padding: 2, borderRadius: 4 }}
          aria-label="Close dialog"
          tabIndex={0}
          onKeyDown={e => { if (e.key === "Enter") handleClose(); }}
        >×</button>
        {children}
      </div>
    </div>
  );
}

