import { WikiEditor } from './WikiEditor.mjs';

for (const wiki of document.querySelectorAll('fieldset.wiki')) {
  new WikiEditor(wiki as HTMLFieldSetElement);
}

export { }
