import { useEffect, useRef, useState } from "react";

interface Props {
  html: string;
  /** Rendered next to the preview (chat panel), also visible in full screen. */
  aside?: React.ReactNode;
}

type Viewport = "desktop" | "tablet" | "mobile";
type ViewMode = "preview" | "code";

export default function LivePreview({ html, aside }: Props) {
  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [viewMode, setViewMode] = useState<ViewMode>("preview");
  const [copied, setCopied] = useState(false);
  const [frameHeight, setFrameHeight] = useState(900);
  const [fullscreen, setFullscreen] = useState(false);
  const [updated, setUpdated] = useState(false);
  const frameRef = useRef<HTMLIFrameElement>(null);
  const viewerRef = useRef<HTMLDivElement>(null);
  // The iframe is grown to its full content height, so the scrolling element is the
  // viewer container (full screen) or the page itself — never the iframe window.
  const liveScroll = useRef(0);
  const savedScroll = useRef(0);
  const restoring = useRef(false);
  const firstRender = useRef(true);

  const readScroll = () =>
    fullscreen ? viewerRef.current?.scrollTop ?? 0 : window.scrollY;

  const restoreScroll = () => {
    if (!restoring.current) return;
    if (fullscreen) viewerRef.current?.scrollTo(0, savedScroll.current);
    else window.scrollTo(0, savedScroll.current);
  };

  useEffect(() => {
    const onScroll = () => {
      if (!restoring.current) liveScroll.current = readScroll();
    };
    const viewer = viewerRef.current;
    window.addEventListener("scroll", onScroll, { passive: true });
    viewer?.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      viewer?.removeEventListener("scroll", onScroll);
    };
  }, [fullscreen]);

  useEffect(() => {
    setFrameHeight(900);
  }, [html, viewport]);

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    // Freeze the offset before the iframe reload shrinks the page and clamps it.
    savedScroll.current = liveScroll.current;
    restoring.current = true;

    setUpdated(true);
    const badgeTimer = window.setTimeout(() => setUpdated(false), 1500);
    const releaseTimer = window.setTimeout(() => {
      restoring.current = false;
      liveScroll.current = readScroll();
    }, 1500);
    return () => {
      window.clearTimeout(badgeTimer);
      window.clearTimeout(releaseTimer);
    };
  }, [html]);

  useEffect(() => {
    if (!fullscreen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setFullscreen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = "";
    };
  }, [fullscreen]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getViewportWidth = () => {
    switch (viewport) {
      case "mobile":
        return "w-[375px]";
      case "tablet":
        return "w-[768px]";
      default:
        return "w-full";
    }
  };

  const resizePreviewFrame = (frame: HTMLIFrameElement) => {
    const document = frame.contentDocument;
    if (!document) return;

    const height = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight,
      document.body.offsetHeight,
      document.documentElement.offsetHeight
    );
    setFrameHeight(Math.max(height, 600));
    window.requestAnimationFrame(restoreScroll);
  };

  return (
    <div
      className={
        fullscreen
          ? "fixed inset-0 z-50 flex flex-col overflow-hidden bg-[#f7f1eb]"
          : "flex flex-col overflow-hidden rounded-2xl border border-[#e7ddd0] bg-[#f7f1eb] shadow-sm"
      }
    >
      {/* Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e7ddd0] bg-white px-4 py-3">
        {/* View Mode Toggle */}
        <div className="flex items-center rounded-lg bg-gray-100 p-1 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setViewMode("preview")}
            className={`rounded-md px-3 py-1.5 transition ${
              viewMode === "preview"
                ? "bg-white coral-text shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            👁️ Aperçu Visuel
          </button>
          <button
            type="button"
            onClick={() => setViewMode("code")}
            className={`rounded-md px-3 py-1.5 transition ${
              viewMode === "code"
                ? "bg-white coral-text shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            💻 Code HTML
          </button>
        </div>

        {/* Viewport Toggles (only in preview mode) */}
        {viewMode === "preview" && (
          <div className="flex items-center gap-1.5 rounded-lg bg-gray-100 p-1 text-xs font-medium">
            <button
              type="button"
              onClick={() => setViewport("desktop")}
              className={`rounded-md px-2.5 py-1 transition ${
                viewport === "desktop"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              🖥️ Ordi (100%)
            </button>
            <button
              type="button"
              onClick={() => setViewport("tablet")}
              className={`rounded-md px-2.5 py-1 transition ${
                viewport === "tablet"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              📱 Tablette (768px)
            </button>
            <button
              type="button"
              onClick={() => setViewport("mobile")}
              className={`rounded-md px-2.5 py-1 transition ${
                viewport === "mobile"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              📲 Mobile (375px)
            </button>
          </div>
        )}

        {/* Full screen toggle */}
        <button
          type="button"
          onClick={() => setFullscreen((value) => !value)}
          className="coral-soft inline-flex items-center gap-1.5 rounded-full border border-[#f0c5b0] px-3 py-1.5 text-xs font-semibold hover:bg-[#fbe8de]"
        >
          {fullscreen ? "✕ Quitter le plein écran (Échap)" : "⛶ Plein écran"}
        </button>

        {updated && (
          <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">
            ✓ Aperçu mis à jour
          </span>
        )}

        {/* Copy Code button */}
        {viewMode === "code" && (
          <button
            type="button"
            onClick={handleCopyCode}
            className="coral-soft inline-flex items-center gap-1.5 rounded-full border border-[#f0c5b0] px-3 py-1.5 text-xs font-semibold hover:bg-[#fbe8de]"
          >
            {copied ? "✓ Copié !" : "📋 Copier le HTML"}
          </button>
        )}
      </div>

      {/* Main Content Viewer */}
      <div
        ref={viewerRef}
        className={`flex flex-col justify-center gap-4 bg-[#f7f1eb] p-4 lg:flex-row lg:items-start ${
          fullscreen ? "flex-1 overflow-auto" : "min-h-[75vh]"
        }`}
      >
        {viewMode === "preview" ? (
          <div
            className={`transition-all duration-300 ${getViewportWidth()} overflow-hidden rounded-xl border border-[#e7ddd0] bg-white shadow-lg`}
          >
            <iframe
              ref={frameRef}
              srcDoc={html}
              sandbox="allow-same-origin"
              title="Landing Page Preview"
              className="w-full border-0"
              style={{ height: `${frameHeight}px` }}
              onLoad={(event) => {
                const frame = event.currentTarget;
                resizePreviewFrame(frame);
                window.setTimeout(() => resizePreviewFrame(frame), 300);
                window.setTimeout(() => resizePreviewFrame(frame), 1200);
              }}
            />
          </div>
        ) : (
          <div className="w-full max-w-5xl rounded-lg bg-gray-900 p-4 text-gray-100 overflow-auto max-h-[75vh] font-mono text-xs leading-relaxed">
            <pre>{html}</pre>
          </div>
        )}
        {aside && (
          <div className="w-full shrink-0 self-stretch lg:w-[340px]">{aside}</div>
        )}
      </div>
    </div>
  );
}
