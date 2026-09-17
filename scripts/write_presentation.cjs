const pptxgen = require('../.presentation-tools-js/node_modules/pptxgenjs');
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'docs', 'presentation');
const slides = JSON.parse(fs.readFileSync(path.join(out, 'slides.json'), 'utf8'));
const pptx = new pptxgen();
pptx.defineLayout({name:'CUSTOM', width:16, height:9});
pptx.layout='CUSTOM'; pptx.author='Murilo Fretta';
pptx.title='Severe Convective Radar Intelligence';
pptx.subject='Radar data engineering, quality and cell tracking';
pptx.lang='en-US';
pptx.theme={headFontFace:'Arial',bodyFontFace:'Arial',lang:'en-US'};
for(const [index,data] of slides.entries()){
  const s=pptx.addSlide(); s.background={color:'07131F'};
  for(const item of data.items){
    const {x,y,w,h}=item;
    if(item.kind==='rect') s.addShape(pptx.ShapeType.rect,{x,y,w,h,line:{color:item.color,transparency:100},fill:{color:item.color}});
    if(item.kind==='image' && index !== 5) s.addImage({path:item.path,x,y,w,h});
    if(item.kind==='text') s.addText(item.text,{x,y,w,h,fontFace:'Arial',fontSize:item.size,color:item.color,bold:item.bold,margin:0,breakLine:false,paraSpaceAfterPt:5,valign:'top',hyperlink:item.hyperlink?{url:item.hyperlink}:undefined});
  }
  if(index === 5){
    const video=path.join(root,'docs','video','Radar_Replay_2100-2354_UTC.mp4');
    const cover='image/png;base64,'+fs.readFileSync(path.join(root,'docs','video','replay-preview.png')).toString('base64');
    s.addMedia({type:'video',path:video,cover,x:2.88,y:2.05,w:10.24,h:5.76});
    s.addText('PLAY REPLAY  /  21:00–23:54 UTC  /  1.5×  /  ~35 seconds',{x:2.88,y:7.95,w:10.24,h:.3,fontSize:12,color:'52D9EE',margin:0});
  }
  s.addNotes(index===5 ? data.notes+' The MP4 is embedded in this slide. In PowerPoint Slide Show, click the video to play the 1.5× replay (about 35 seconds), from 21:00 to 23:54 UTC. This replaces the static dashboard image.' : data.notes);
}
pptx.writeFile({fileName:path.join(out,'Severe_Convective_Radar_Intelligence.pptx')});
