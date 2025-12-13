import React, { useEffect, useState } from 'react';

const flowcharts = {
  overview: {
    title: "📊 High-Level System Overview",
    diagram: `flowchart LR
    subgraph INPUT["📥 INPUT"]
        A[("🖥️ Desktop App")]
        B[("⚙️ Background Worker")]
    end
    
    subgraph PROCESS["⚡ PROCESSING"]
        C[Image Pipeline]
        D[AI Generation]
        E[CDN Upload]
    end
    
    subgraph OUTPUT["📤 OUTPUT"]
        F[("🌐 Website")]
        G[("📁 Archive")]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G`
  },
  desktop: {
    title: "🖥️ Desktop Application Flow",
    diagram: `flowchart TB
    START([Start]) --> LOAD[Load config.json]
    LOAD --> GUI[Dark Theme GUI]
    GUI --> WAIT{Input?}
    
    WAIT -->|Drop| DROP[Receive Folder]
    WAIT -->|Browse| DIALOG[File Dialog]
    DIALOG --> DROP
    
    DROP --> SCAN[Scan Images]
    SCAN --> DETECT[Auto-Detect Category]
    DETECT --> SKU[Generate SKU]
    
    SKU --> EDIT{Edit?}
    EDIT -->|Crop| CROP[Crop Tool]
    EDIT -->|BG| BGREM[Remove Background]
    EDIT -->|No| OPT
    CROP --> OPT
    BGREM --> OPT
    
    OPT[Optimize WebP]
    OPT --> CDN[Upload ImageKit]
    CDN --> AI[AI Description]
    AI --> REVIEW[Review]
    REVIEW --> PUB{Publish?}
    PUB -->|Yes| SEND[POST API]
    PUB -->|Edit| REVIEW
    SEND --> DONE([Success!])`
  },
  image: {
    title: "📸 Image Processing Pipeline",
    diagram: `flowchart LR
    subgraph IN["Input"]
        RAW[JPG/PNG/TIFF]
    end
    
    subgraph EDIT["Optional"]
        CROP[✂️ Crop]
        BG[🎨 BG Removal]
    end
    
    subgraph OPT["Optimize"]
        SIZE[📐 2400px max]
        WEBP[🔄 WebP 88%]
        EXIF[🧹 Strip EXIF]
    end
    
    subgraph OUT["Output"]
        FINAL[Optimized WebP]
        THUMB[400px Thumb]
    end
    
    RAW --> CROP
    RAW --> BG
    RAW --> SIZE
    CROP --> SIZE
    BG --> SIZE
    SIZE --> WEBP
    WEBP --> EXIF
    EXIF --> FINAL
    EXIF --> THUMB`
  },
  ai: {
    title: "🤖 AI Content Generation",
    diagram: `flowchart TB
    IMG[Images + Context] --> API[Claude API]
    
    API --> TPL{Template}
    TPL -->|MILI| T1[Militaria]
    TPL -->|COLL| T2[Collectibles]
    TPL -->|BOOK| T3[Books]
    TPL -->|ART| T4[Fine Art]
    
    T1 --> GEN[Generate]
    T2 --> GEN
    T3 --> GEN
    T4 --> GEN
    
    GEN --> D1[📝 Description]
    GEN --> D2[🏷️ Title]
    GEN --> D3[🔍 SEO]
    GEN --> D4[💰 Valuation]
    GEN --> D5[🔑 Keywords]`
  },
  publish: {
    title: "🌐 Publishing Flow",
    diagram: `flowchart TB
    subgraph CLIENT["Client"]
        PREP[Prepare Data]
        PREP --> VAL[Validate]
        VAL --> SEND[POST + API Key]
    end
    
    subgraph SERVER["Next.js"]
        RCV[Receive] --> AUTH{Auth?}
        AUTH -->|No| E401[401]
        AUTH -->|Yes| SKU{SKU?}
        SKU -->|Exists| E409[409]
        SKU -->|New| DB[Create]
        DB --> R201[201 OK]
    end
    
    SEND --> RCV
    R201 --> OK[✅ Success]
    E401 --> ERR[❌ Error]
    E409 --> ERR`
  },
  worker: {
    title: "⚙️ Background Worker",
    diagram: `flowchart TB
    START([Start]) --> LOOP[Main Loop]
    LOOP --> SCAN[Scan Folder]
    SCAN --> CHK{New?}
    CHK -->|No| WAIT[Wait 60s]
    WAIT --> SCAN
    CHK -->|Yes| PROC[Process]
    PROC --> IMG[Images]
    IMG --> CDN[Upload]
    CDN --> AI[AI Gen]
    AI --> PUB[Publish]
    PUB --> OK{OK?}
    OK -->|Yes| ARCH[Archive]
    OK -->|No| FAIL[Failed]
    ARCH --> SCAN
    FAIL --> SCAN`
  },
  sku: {
    title: "🔢 SKU Generation",
    diagram: `flowchart LR
    CAT[Category] --> PRE{Prefix}
    PRE -->|Militaria| M[MILI]
    PRE -->|Collectibles| C[COLL]
    PRE -->|Books| B[BOOK]
    PRE -->|Art| A[ART]
    
    M --> YR[2025]
    C --> YR
    B --> YR
    A --> YR
    
    YR --> CNT[Counter]
    CNT --> INC[+1]
    INC --> SKU[MILI-2025-0042]`
  }
};

export default function KollectItFlowchart() {
  const [activeChart, setActiveChart] = useState('overview');
  const [rendered, setRendered] = useState('');

  useEffect(() => {
    const renderDiagram = async () => {
      try {
        const mermaid = await import('https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs');
        mermaid.default.initialize({
          startOnLoad: false,
          theme: 'dark',
          themeVariables: {
            primaryColor: '#e94560',
            primaryTextColor: '#fff',
            primaryBorderColor: '#e94560',
            lineColor: '#a0a0a0',
            secondaryColor: '#16213e',
            background: '#1a1a2e',
            mainBkg: '#16213e',
            nodeBorder: '#e94560'
          }
        });
        
        const { svg } = await mermaid.default.render(
          'mermaid-' + activeChart,
          flowcharts[activeChart].diagram
        );
        setRendered(svg);
      } catch (e) {
        setRendered(`<div style="color: #fc8181; padding: 20px;">Error rendering: ${e.message}</div>`);
      }
    };
    
    renderDiagram();
  }, [activeChart]);

  return (
    <div className="min-h-screen bg-[#1a1a2e] text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#e94560] mb-2">
            🏛️ Kollect-It Product Application
          </h1>
          <p className="text-gray-400">System Architecture & Workflow Flowcharts</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap justify-center gap-2 mb-6">
          {Object.entries(flowcharts).map(([key, { title }]) => (
            <button
              key={key}
              onClick={() => setActiveChart(key)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeChart === key
                  ? 'bg-[#e94560] text-white'
                  : 'bg-[#16213e] text-gray-300 hover:bg-[#1f3460]'
              }`}
            >
              {title.split(' ')[0]}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div className="flex justify-center gap-6 mb-6 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#e94560]"></div>
            <span className="text-sm text-gray-300">Primary Action</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#16213e] border border-[#e94560]"></div>
            <span className="text-sm text-gray-300">Process</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#48bb78]"></div>
            <span className="text-sm text-gray-300">Success</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-[#fc8181]"></div>
            <span className="text-sm text-gray-300">Error</span>
          </div>
        </div>

        {/* Active Chart Title */}
        <h2 className="text-xl font-bold text-[#e94560] mb-4 border-b border-[#e94560] pb-2">
          {flowcharts[activeChart].title}
        </h2>

        {/* Diagram Container */}
        <div className="bg-[#16213e] rounded-xl p-6 overflow-x-auto">
          <div 
            dangerouslySetInnerHTML={{ __html: rendered }}
            className="flex justify-center"
          />
        </div>

        {/* Workflow Summary */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#16213e] rounded-lg p-4 border border-[#2d3748]">
            <h3 className="text-[#e94560] font-bold mb-2">📥 Input</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• Drag & Drop folders</li>
              <li>• Browse from Google Drive</li>
              <li>• Auto-watch folder</li>
            </ul>
          </div>
          <div className="bg-[#16213e] rounded-lg p-4 border border-[#2d3748]">
            <h3 className="text-[#e94560] font-bold mb-2">📸 Processing</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• Crop & rotate</li>
              <li>• AI background removal</li>
              <li>• WebP conversion 88%</li>
            </ul>
          </div>
          <div className="bg-[#16213e] rounded-lg p-4 border border-[#2d3748]">
            <h3 className="text-[#e94560] font-bold mb-2">🤖 AI Generation</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• Description 200-400 words</li>
              <li>• SEO title & meta</li>
              <li>• Price valuation</li>
            </ul>
          </div>
          <div className="bg-[#16213e] rounded-lg p-4 border border-[#2d3748]">
            <h3 className="text-[#e94560] font-bold mb-2">🌐 Output</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• ImageKit CDN upload</li>
              <li>• Publish to website</li>
              <li>• Archive completed</li>
            </ul>
          </div>
        </div>

        {/* SKU Format Reference */}
        <div className="mt-6 bg-[#16213e] rounded-lg p-4 border border-[#2d3748]">
          <h3 className="text-[#e94560] font-bold mb-3">🔢 SKU Format Reference</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="bg-[#1a1a2e] rounded p-3">
              <div className="text-[#e94560] font-mono">MILI-2025-0001</div>
              <div className="text-gray-400">Militaria</div>
            </div>
            <div className="bg-[#1a1a2e] rounded p-3">
              <div className="text-[#e94560] font-mono">COLL-2025-0001</div>
              <div className="text-gray-400">Collectibles</div>
            </div>
            <div className="bg-[#1a1a2e] rounded p-3">
              <div className="text-[#e94560] font-mono">BOOK-2025-0001</div>
              <div className="text-gray-400">Books</div>
            </div>
            <div className="bg-[#1a1a2e] rounded p-3">
              <div className="text-[#e94560] font-mono">ART-2025-0001</div>
              <div className="text-gray-400">Fine Art</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
