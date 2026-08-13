import { useEffect, useMemo, useRef, useState } from "react";

interface Props {
  html: string;
}

type Viewport = "desktop" | "tablet" | "mobile";
type ViewMode = "preview" | "code";

export default function LivePreview({ html }: Props) {
  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [viewMode, setViewMode] = useState<ViewMode>("preview");
  const [copied, setCopied] = useState(false);
  const [frameHeight, setFrameHeight] = useState(900);
  const [availableWidth, setAvailableWidth] = useState(0);
  const previewHostRef = useRef<HTMLDivElement | null>(null);

  // Apply preview safeguards before the iframe paints.  Adding them after load
  // briefly displayed header logos at their natural (very large) dimensions.
  const previewHtml = useMemo(() => {
    const previewStyles = `
      <style id="landing-page-preview-guards">
        img { max-width: 100%; }
        .site-header {
          position: static !important;
          top: auto !important;
          right: auto !important;
          bottom: auto !important;
          left: auto !important;
        }
        header .logo img,
        .site-header .logo img,
        header img[alt*="logo" i] {
          display: block !important;
          width: auto !important;
          height: 36px !important;
          max-width: min(220px, 100%) !important;
          max-height: 36px !important;
          object-fit: contain !important;
        }
      </style>`;

    return html.includes("</head>")
      ? html.replace("</head>", `${previewStyles}</head>`)
      : `${previewStyles}${html}`;
  }, [html]);

  useEffect(() => {
    setFrameHeight(900);
  }, [html, viewport]);

  useEffect(() => {
    const host = previewHostRef.current;
    if (!host) return;

    // The host has 16 px padding on each side; only its content box is usable.
    const updateWidth = () => setAvailableWidth(Math.max(host.clientWidth - 32, 1));
    updateWidth();
    const observer = new ResizeObserver(updateWidth);
    observer.observe(host);
    return () => observer.disconnect();
  }, []);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getViewportWidth = () => {
    switch (viewport) {
      case "mobile":
        return 375;
      case "tablet":
        return 768;
      default:
        return availableWidth || 1;
    }
  };

  const frameWidth = getViewportWidth();
  const previewScale = viewport === "desktop" ? 1 : Math.min(1, (availableWidth || frameWidth) / frameWidth);

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
  };

  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-[#e7ddd0] bg-[#f7f1eb] shadow-sm">
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
      <div ref={previewHostRef} className="flex min-h-[75vh] justify-center bg-[#f7f1eb] p-4">
        {viewMode === "preview" ? (
          <div
            className="overflow-hidden rounded-xl border border-[#e7ddd0] bg-white shadow-lg transition-all duration-300"
            style={{
              width: `${frameWidth * previewScale}px`,
              height: `${frameHeight * previewScale}px`,
            }}
          >
            <iframe
              srcDoc={previewHtml}
              sandbox="allow-same-origin"
              title="Landing Page Preview"
              className="block border-0"
              style={{
                width: `${frameWidth}px`,
                height: `${frameHeight}px`,
                transform: `scale(${previewScale})`,
                transformOrigin: "top left",
              }}
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
      </div>
    </div>
  );
}
