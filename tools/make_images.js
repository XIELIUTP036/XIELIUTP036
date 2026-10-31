// 產生 apple-touch-icon.png（180×180）與 og.png（1200×630 社群分享預覽圖）。
// 用法：node tools/make_images.js   （需 Playwright；只在圖示或網站描述改變時才需重跑）
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const root=path.join(__dirname,'..');
const svg=fs.readFileSync(path.join(root,'favicon.svg'),'utf8');
const desc=(fs.readFileSync(path.join(root,'index.html'),'utf8').match(/<meta name="description" content="([^"]*)">/)||[])[1]||'';
const font='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@500;900&display=swap"><style>body{margin:0;font-family:"Noto Sans TC","WenQuanYi Zen Hei",sans-serif}</style>';
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:180,height:180}});
  // iOS 會自行裁圓角，這裡用滿版方形避免四角變黑
  await p.setContent(`<body style="margin:0">${svg.replace('rx="5"','rx="0"').replace('<svg ','<svg width="180" height="180" ')}</body>`);
  await p.screenshot({path:path.join(root,'apple-touch-icon.png')});
  const o=await b.newPage({viewport:{width:1200,height:630}});
  await o.setContent(`${font}<body><div style="width:1200px;height:630px;box-sizing:border-box;padding:90px 100px;background:linear-gradient(135deg,#13315c,#1f4f8f);color:#fff;display:flex;flex-direction:column;justify-content:center;gap:36px">
  <div style="display:flex;align-items:center;gap:36px">${svg.replace('<svg ','<svg width="150" height="150" ')}<div style="font-size:120px;font-weight:900;letter-spacing:6px">產險懶人包</div></div>
  <div style="font-size:40px;font-weight:500;line-height:1.5;opacity:.92">${desc}</div></div></body>`,{waitUntil:'networkidle'}).catch(()=>{});
  await o.evaluate(()=>document.fonts.ready);
  await o.screenshot({path:path.join(root,'og.png')});
  await b.close();console.log('已產生 apple-touch-icon.png、og.png');
})();
