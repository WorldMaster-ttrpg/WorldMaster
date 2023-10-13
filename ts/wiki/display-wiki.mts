import StarterKit from '@tiptap/starter-kit';
import { generateHTML } from '@tiptap/core';

for (const section of document.querySelectorAll('article.wiki section')) {
  if (section instanceof HTMLElement) {
    const body = section.dataset.body;
    if (body !== undefined) {
      const json = JSON.parse(body);
      const html = generateHTML(json, [StarterKit]);
      section.innerHTML = html;
    }
  }
}

export { }
