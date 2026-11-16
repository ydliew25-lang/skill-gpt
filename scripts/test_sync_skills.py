"""Offline regression tests. Fictional catalog entries never reach published files."""
import copy, tempfile, unittest
from pathlib import Path
import sync_skills as s
class SyncTests(unittest.TestCase):
 def setUp(self):
  self.item={'id':'test-skill','path':'skills/test-skill/SKILL.md','name':'测试 <script> [x]','summary':'概述 | &','inputs':'输入','outputs':'输出','profile_summary':'简介','website_summary':'简介 <b>','published':True}
  self.data={'schema_version':1,'skills':[self.item]}
 def test_schema(self):self.assertEqual(len(s.validate(self.data)),1)
 def test_bad_inputs(self):
  for change in [lambda d:d['skills'][0].update(path='../secret'),lambda d:d['skills'].append(d['skills'][0]),lambda d:d.update(skills=[]),lambda d:d['skills'][0].update(published='yes'),lambda d:d['skills'][0].update(name='bad\nline')]:
   d=copy.deepcopy(self.data);change(d)
   with self.assertRaises(ValueError):s.validate(d)
 def test_regions_escaping_and_repeat(self):
  for mode,names in [('catalog',['CATALOG']),('profile',['PROFILE']),('website',['HERO_COUNT','MARK','ROWS'])]:
   text='keep-photo-data\n'+''.join(f'<!-- SKILLS:{n}:START -->old<!-- SKILLS:{n}:END -->' for n in names)+'\nkeep-footer'
   result=s.render(text,[self.item],mode)
   self.assertEqual(s.render(result,[self.item],mode),result)
   self.assertTrue(result.startswith('keep-photo-data\n'));self.assertTrue(result.endswith('\nkeep-footer'))
   self.assertNotIn('<script>',result)
 def test_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'README.md';p.write_text('no markers')
   with self.assertRaises(ValueError):s.update(p,[self.item],'profile')
   self.assertEqual(p.read_text(),'no markers')
 def test_added_item(self):
  text='<!-- SKILLS:HERO_COUNT:START -->01<!-- SKILLS:HERO_COUNT:END --><!-- SKILLS:MARK:START --><!-- SKILLS:MARK:END --><!-- SKILLS:ROWS:START --><!-- SKILLS:ROWS:END -->'
  other=dict(self.item,id='second',path='skills/second/SKILL.md')
  result=s.render(text,[self.item,other],'website')
  self.assertEqual(result.count('class="skill-row"'),2);self.assertIn('>02<',result)
if __name__=='__main__':unittest.main()
