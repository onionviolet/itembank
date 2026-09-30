import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import http from 'node:http';
import {JSDOM} from 'jsdom';
import {python} from './python_bin.mjs';

const sourceArg = process.argv.indexOf('--browser-source');

if(sourceArg < 0){
  const fixture=JSON.parse(execFileSync(python,['-c',`
import json, runpy, model, runtime
from surfaces import quiz_page
q=model.parse_bank(runpy.run_path('tests/ordering_workflow_roundtrip.py')['authored_text']())[0]
print(json.dumps(dict(script=quiz_page.SERVED_JS,
 page=quiz_page.baseline_for(dict(session_id='synthetic',item=runtime.public_item(q)),{},'/answer',dict(submit='token')))))
`],{cwd:new URL('../..',import.meta.url),encoding:'utf8'}));

  test('native structural drags bubble from each select and retain exact IDs after consecutive drops',()=>{
    const dom=new JSDOM(fixture.page,{runScripts:'outside-only',url:'http://localhost/quiz/ordering'});
    try{
      const w=dom.window;
      const start=fixture.script.indexOf('function installOrderingControls(');
      const end=fixture.script.indexOf('function asOrdering(',start);
      assert.ok(start>=0 && end>start);
      w.eval(fixture.script.slice(start,end));
      const fieldset=w.document.querySelector('[data-ordering-signature]');
      w.installOrderingControls(fieldset);
      const selects=[...fieldset.querySelectorAll('select')];
      const ids=['start','right','left'];
      ids.forEach((id,index)=>{
        const handle=fieldset.querySelector(`[data-ordering-block-id="${id}"]`);
        const transfer={effectAllowed:'none',dropEffect:'none',setData(){}};
        function drag(type,target){
          const event=new w.Event(type,{bubbles:true,cancelable:true});
          Object.defineProperty(event,'dataTransfer',{value:transfer});
          target.dispatchEvent(event);
          return event;
        }
        drag('dragstart',handle);
        assert.equal(transfer.effectAllowed,'copy');
        assert.equal(drag('dragover',selects[index]).defaultPrevented,true);
        assert.equal(transfer.dropEffect,'copy');
        assert.equal(drag('drop',selects[index]).defaultPrevented,true);
        drag('dragend',handle);
        assert.equal(selects[index].value,id);
        assert.equal(w.document.activeElement,selects[index]);
        assert.match(fieldset.querySelector('[role="status"]').textContent,
                     new RegExp(`at position ${index+1}\\.`));
      });
      assert.deepEqual(selects.map(select=>select.value),ids);
    }finally{dom.window.close();}
  });
  test('production guarded dragenter accepts direct target arrival and still refuses external input',()=>{
    const dom=new JSDOM(fixture.page,{runScripts:'outside-only',url:'http://localhost/quiz/ordering'});
    try{
      const w=dom.window, start=fixture.script.indexOf('function installOrderingControls(');
      w.eval(fixture.script.slice(start,fixture.script.indexOf('function asOrdering(',start)));
      const fieldset=w.document.querySelector('[data-ordering-signature]');
      w.installOrderingControls(fieldset);
      const selects=[...fieldset.querySelectorAll('select')];
      const label=selects[1].closest('label');
      assert.equal(label.ondragenter,label.ondragover,'the production hook reuses the guarded handler');
      const enter=()=>{
        const event=new w.Event('dragenter',{bubbles:true,cancelable:true});
        Object.defineProperty(event,'dataTransfer',{value:{dropEffect:'none'}});
        selects[1].dispatchEvent(event);
        return event.defaultPrevented;
      };
      const handle=fieldset.querySelector('[data-ordering-block-id="right"]');
      handle.dispatchEvent(new w.Event('dragstart',{bubbles:true,cancelable:true}));
      label.ondragenter=null;
      assert.equal(enter(),false,'missing dragenter acceptance reproduces the arrival gap');
      label.ondragenter=label.ondragover;
      assert.equal(enter(),true,'proposal reuses the same local/disabled guard');
      selects[1].dispatchEvent(new w.Event('drop',{bubbles:true,cancelable:true}));
      handle.dispatchEvent(new w.Event('dragend',{bubbles:true}));
      assert.equal(selects[1].value,'right');
      assert.equal(enter(),false,'external arrival without a local drag stays refused');
    }finally{dom.window.close();}
  });
}else{
  // Read-only developer fixture: observe actual browser input on the served
  // page. No synthetic drag events are dispatched by this instrumentation.
  const upstream=new URL(process.argv[sourceArg+1]);
  assert.equal(upstream.protocol,'http:');
  assert.ok(['127.0.0.1','localhost'].includes(upstream.hostname));
  let observer=String.raw`<script>
(() => {
  /* optional guarded dragenter proposal */
  const log=document.createElement('pre'); log.id='structural-drag-trace';
  log.style.cssText='white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%';
  log.setAttribute('aria-label','Developer drag event trace');
  document.body.append(log);
  const rows=[];
  for(const type of ['dragstart','dragenter','dragover','dragleave','drop','dragend']){
    document.addEventListener(type,event=>{
      const target=event.target;
      const label=target.closest && target.closest('label');
      const select=label && label.querySelector('select[name^="step_"]');
      const handle=target.closest && target.closest('[data-ordering-block-id]');
        rows.push(JSON.stringify({type,tag:target.tagName,name:target.name||null,
          block:handle && handle.dataset.orderingBlockId,
          position:select && select.name, x:event.clientX,y:event.clientY,
          trusted:event.isTrusted,prevented:event.defaultPrevented,
          effect:event.dataTransfer && event.dataTransfer.dropEffect}));
        while(rows.length>60) rows.shift();
        log.textContent=rows.join('\n');
    });
  }
})();</script>`;
  if(process.argv.includes('--accept-dragenter')){
    observer=observer.replace('/* optional guarded dragenter proposal */',
      `document.querySelectorAll('[data-ordering-signature] select[name^="step_"]').forEach(select=>{
        const label=select.closest('label'); label.ondragenter=label.ondragover;
      });`);
  }
  const server=http.createServer(async(req,res)=>{
    if(req.method!=='GET'){res.writeHead(405);res.end('Developer fixture is read-only.');return;}
    try{
      const url=new URL(req.url,upstream);
      assert.equal(url.origin,upstream.origin);
      const response=await fetch(url);
      const type=response.headers.get('content-type')||'application/octet-stream';
      let body=Buffer.from(await response.arrayBuffer());
      if(type.includes('text/html')) body=Buffer.from(body.toString().replace('</body>',observer+'</body>'));
      res.writeHead(response.status,{'Content-Type':type,'Cache-Control':'no-store'});
      res.end(body);
    }catch(error){res.writeHead(502);res.end(String(error));}
  });
  server.listen(0,'127.0.0.1',()=>{
    process.stdout.write(JSON.stringify({url:`http://127.0.0.1:${server.address().port}/quiz/ordering?mode=exam`,
      upstream:upstream.origin,trace:'structural-drag-trace'})+'\n');
  });
  process.stdin.once('data',()=>{server.close();process.stdin.pause();});
}
