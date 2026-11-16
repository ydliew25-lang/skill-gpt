#!/usr/bin/env python3
"""Validate data, then atomically update only explicit Skills regions. No dependencies."""
import argparse, html, json, os, re, tempfile
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = 'ydliew25-lang/skill-gpt'
MAX_BYTES = 200_000
FIELDS = {'id','name','path','summary','inputs','outputs','profile_summary','website_summary','published'}

def fetch(url):
    request = Request(url, headers={'User-Agent':'skill-catalog-sync/1.0','Accept':'application/vnd.github+json'})
    with urlopen(request, timeout=30) as r:
        data = r.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise ValueError('Response too large')
    return data

def validate(data):
    if not isinstance(data,dict) or set(data)!={'schema_version','skills'} or data['schema_version']!=1:
        raise ValueError('Unsupported catalog schema')
    rows=data['skills']
    if not isinstance(rows,list) or not 1<=len(rows)<=100: raise ValueError('Invalid catalog size')
    ids=set(); paths=set()
    for item in rows:
        if not isinstance(item,dict) or set(item)!=FIELDS: raise ValueError('Invalid item fields')
        if type(item['published']) is not bool: raise ValueError('published must be boolean')
        for k in FIELDS-{'published'}:
            v=item[k]
            if not isinstance(v,str) or not v.strip() or len(v)>600 or any(ord(c)<32 for c in v):
                raise ValueError('Invalid text field: '+k)
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',item['id']): raise ValueError('Unsafe id')
        # Existing storyboard location remains supported; new skills live under skills/.
        if item['path'] not in ('skills/'+item['id']+'/SKILL.md','create-product-storyboards/SKILL.md'):
            raise ValueError('Unsafe skill path')
        if item['path']=='create-product-storyboards/SKILL.md' and item['id']!='create-product-storyboards':
            raise ValueError('Path and id mismatch')
        if item['id'] in ids or item['path'] in paths: raise ValueError('Duplicate item')
        ids.add(item['id']); paths.add(item['path'])
    public=[r for r in rows if r['published']]
    if not public: raise ValueError('Empty public catalog; preserve last good page')
    return public

def load_catalog(path=None, source_root=None):
    if path:
        data=json.loads(Path(path).read_text(encoding='utf-8')); rows=validate(data)
        if source_root:
            root=Path(source_root).resolve()
            for r in rows:
                target=root/r['path']
                if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
                    raise ValueError('Missing/unsafe skill file: '+r['path'])
                if not target.read_bytes().strip(): raise ValueError('Empty skill file: '+r['path'])
        return rows
    # Pin catalog and linked files to one immutable commit, not a changing branch.
    head=json.loads(fetch(f'https://api.github.com/repos/{SOURCE}/git/ref/heads/main'))['object']['sha']
    if not re.fullmatch(r'[0-9a-f]{40}',head): raise ValueError('Invalid source revision')
    base=f'https://raw.githubusercontent.com/{SOURCE}/{head}/'
    rows=validate(json.loads(fetch(base+'skills-catalog.json')))
    for r in rows:
        if not fetch(base+r['path']).strip(): raise ValueError('Empty linked skill')
    return rows

def md(text):
    # Escape Markdown punctuation as HTML character references, including table pipes.
    return ''.join('&#'+str(ord(c))+';' if c in r'\`*_{}[]<>()#+-.!|&' else c for c in text)

def link(row, local=False):
    path=row['path']
    return path if local else 'https://github.com/'+SOURCE+'/blob/main/'+path

def replace_region(text,name,value):
    start=f'<!-- SKILLS:{name}:START -->'; end=f'<!-- SKILLS:{name}:END -->'
    if text.count(start)!=1 or text.count(end)!=1: raise ValueError('Missing/duplicate region '+name)
    a=text.index(start)+len(start); b=text.index(end)
    if b<a: raise ValueError('Reversed region '+name)
    return text[:a]+value+text[b:]

def render(text,rows,mode):
    n=len(rows)
    if mode=='catalog':
        block=f'\n本仓库收录 {n} 项公开展示 Skill，并保留行业案例更新器的 1 个历史版本。每项 Skill 都有明确的输入、执行步骤、输出要求和质量边界，供具备相应工具的 AI 助手读取执行。\n\n## Skill 目录\n\n| Skill | 解决的问题 | 主要输入 | 主要输出 |\n|---|---|---|---|\n'
        block+=''.join(f"| [{md(r['name'])}]({link(r,True)}) | {md(r['summary'])} | {md(r['inputs'])} | {md(r['outputs'])} |\n" for r in rows)+'\n'
        return replace_region(text,'CATALOG',block)
    if mode=='profile':
        block=f'\n将产品工作中的方法整理成 {n} 项可复用 Skill，明确输入材料、执行步骤、输出格式与质量要求。\n\n**能力关键词：** AI 协作 · 结构化研究 · 工作流设计 · 质量检查\n\n| Skill | 解决的问题 |\n|---|---|\n'
        block+=''.join(f"| [{md(r['name'])}]({link(r)}) | {md(r['profile_summary'])} |\n" for r in rows)
        block+='\n[进入完整 Skill 仓库](https://github.com/'+SOURCE+')\n\n'
        return replace_region(text,'PROFILE',block)
    if mode=='website':
        text=replace_region(text,'HERO_COUNT',f'{n:02}')
        text=replace_region(text,'MARK',f'<div class="workflow-mark" aria-label="{n} 项可复用工作流"><span class="workflow-big">{n:02}</span><span class="workflow-small">REUSABLE SKILLS</span></div>')
        block='\n'+''.join(f'          <a class="skill-row" href="{html.escape(link(r),quote=True)}" target="_blank" rel="noopener noreferrer"><span class="skill-index">{i:02}</span><span class="skill-name">{html.escape(r["name"])}</span><span class="skill-desc">{html.escape(r["website_summary"])}</span><svg class="arrow" aria-hidden="true"><use href="#arrow-up-right"/></svg></a>\n' for i,r in enumerate(rows,1))
        return replace_region(text,'ROWS',block)
    raise ValueError('Invalid mode')

def update(path, rows, mode):
    path=Path(path); old=path.read_bytes(); text=old.decode('utf-8'); new=render(text,rows,mode).encode('utf-8')
    if old==new: return False
    # Verify only marked regions differ, and all inline images are unchanged.
    def strip(t): return re.sub(r'(?<=<!-- SKILLS:)(.*?)(:START -->).*?(<!-- SKILLS:\1:END -->)',r'\1\2\3',t,flags=re.S)
    if strip(text)!=strip(new.decode('utf-8')): raise ValueError('Change escaped generated regions')
    if re.findall(r'data:image/[^"\s]+',text)!=re.findall(r'data:image/[^"\s]+',new.decode('utf-8')): raise ValueError('Image change rejected')
    fd,tmp=tempfile.mkstemp(prefix='.skills-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f: f.write(new)
        os.chmod(tmp,path.stat().st_mode & 0o777)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['catalog','profile','website'],required=True);p.add_argument('--target',required=True);p.add_argument('--catalog');p.add_argument('--source-root');args=p.parse_args()
    rows=load_catalog(args.catalog,args.source_root)
    changed=update(args.target,rows,args.mode)
    print('Updated' if changed else 'Already current')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('changed='+str(changed).lower()+'\n')
if __name__=='__main__':main()
