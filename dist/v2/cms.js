(()=>{
 const hash=text=>{let n=2166136261;for(const c of text){n^=c.charCodeAt(0);n=Math.imul(n,16777619)}return 't'+(n>>>0).toString(16)};
 const records=(window.welcomeContentRecords||[]).filter(r=>!r.node.parentElement.closest('dialog,footer,.version,.review-controls')&&r.node.parentElement.closest('section,.hero-content,header'));
 const existing=new Set(records.map(r=>r.node));const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;while(node=walker.nextNode()){const parent=node.parentElement;if(!existing.has(node)&&parent.closest('section,.hero-content')&&!parent.closest('script,style,dialog,.review-controls')&&/[a-zA-Zа-яА-Я]/.test(node.textContent)&&node.textContent.trim()){records.push({node,ru:node.textContent,en:node.textContent})}}const schema=[],seen=new Set(),counts={};records.forEach(r=>{const base=hash(r.ru.trim());counts[base]=(counts[base]||0)+1;r.id=base+'_'+counts[base];if(!seen.has(r.id)){seen.add(r.id);schema.push({id:r.id,section:r.node.parentElement.closest('section')?.id||'header',ru:r.ru.trim(),en:r.en.trim()})}});
 let fields={};const apply=()=>{const lang=document.documentElement.lang==='en'?'en':'ru';records.forEach(r=>{const v=fields[r.id]?.[lang];r.node.textContent=typeof v==='string'?v:r[lang]})};
 window.addEventListener('welcome-language-change',apply);
 const preview=new URLSearchParams(location.search).has('cms-preview');
 window.addEventListener('message',e=>{if(e.origin!==location.origin||e.source!==parent||parent===window)return;if(e.data?.type==='welcome-schema-request')parent.postMessage({type:'welcome-schema',schema},location.origin);if(preview&&e.data?.type==='welcome-preview'){fields=e.data.fields||{};apply()}});
 if(preview){parent.postMessage({type:'welcome-schema',schema},location.origin);return}
 const config=window.WELCOME_FIREBASE_CONFIG;if(!config?.projectId)return;
 (async()=>{const [app,db]=await Promise.all([import('https://www.gstatic.com/firebasejs/13.0.0/firebase-app.js'),import('https://www.gstatic.com/firebasejs/13.0.0/firebase-firestore-lite.js')]);const firestore=db.getFirestore(app.initializeApp(config));const snap=await db.getDoc(db.doc(firestore,'siteContent','published'));if(snap.exists()){fields=snap.data().fields||{};apply()}})().catch(()=>console.warn('Не удалось получить обновления контента. Показана сохранённая версия сайта.'));
})();
