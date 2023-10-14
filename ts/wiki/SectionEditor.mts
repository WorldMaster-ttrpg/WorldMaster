import { ChainedCommands, Editor, EditorOptions } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';

export class SectionEditor {
  #id: HTMLInputElement;
  #order: HTMLInputElement;
  #body: HTMLInputElement;
  #editor_div: HTMLDivElement;
  #editor: Editor;
  #disabled: boolean;

  public get disabled(): boolean {
    return this.#disabled;
  }
  public set disabled(disabled: boolean) {
    this.#disabled = disabled;
    this.#id.disabled = disabled;
    this.#order.disabled = disabled;
    this.#body.disabled = disabled;
    this.#editor.setEditable(!disabled);
    if (disabled) {
      this.#editor_div.classList.add('disabled');
    } else {
      this.#editor_div.classList.remove('disabled');
    }
  }

  constructor(section: HTMLLIElement) {
    this.#id = section.querySelector('input.id') as HTMLInputElement;
    this.#order = section.querySelector('input.order') as HTMLInputElement;
    this.#body = section.querySelector('input.body') as HTMLInputElement;
    this.#disabled = this.#body.disabled;

    const menu_div = document.createElement('div');
    menu_div.classList.add('menu');
    this.#body.insertAdjacentElement('afterend', menu_div);

    this.#editor_div = document.createElement('div');
    this.#editor_div.classList.add('editor');
    menu_div.insertAdjacentElement('afterend', this.#editor_div);
    let options: Partial<EditorOptions> = {
      element: this.#editor_div,
      extensions: [
        StarterKit,
      ],
    };
    if (this.#body.value) {
      options.content = JSON.parse(this.#body.value);
    }

    this.#editor = new Editor(options);

    const menu = new DocumentFragment();
    const buttons = [
      {
        label: 'b',
        callback: () => { this.#editor.chain().focus().toggleBold().run(); },
      },
      {
        label: 'i',
        callback: () => { this.#editor.chain().focus().toggleItalic().run(); },
      },
      {
        label: '•',
        callback: () => { this.#editor.chain().focus().toggleBulletList().run(); },
      },
      {
        label: '#',
        callback: () => { this.#editor.chain().focus().toggleOrderedList().run(); },
      },
      {
        label: '<>',
        callback: () => { this.#editor.chain().focus().toggleCode().run(); },
      },
      {
        label: '```',
        callback: () => { this.#editor.chain().focus().toggleCodeBlock().run(); },
      },
      {
        label: '“',
        callback: () => { this.#editor.chain().focus().toggleBlockquote().run(); },
      },
      {
        label: 'H1',
        callback: () => { this.#editor.chain().focus().toggleHeading({ level: 1 }).run(); },
      },
      {
        label: 'H2',
        callback: () => { this.#editor.chain().focus().toggleHeading({ level: 2 }).run(); },
      },
      {
        label: 'H3',
        callback: () => { this.#editor.chain().focus().toggleHeading({ level: 3 }).run(); },
      },
      {
        label: 'H4',
        callback: () => { this.#editor.chain().focus().toggleHeading({ level: 4 }).run(); },
      },
      {
        label: 'H5',
        callback: () => { this.#editor.chain().focus().toggleHeading({ level: 5 }).run(); },
      },
      {
        label: 'H6',
        callback: () => { this.#editor.chain().focus().toggleHeading({ level: 6 }).run(); },
      },
      {
        label: "─",
        callback: () => { this.#editor.chain().focus().toggleStrike().run(); },
      },
    ];
    for (const { label, callback } of buttons) {
      const button = menu.appendChild(document.createElement('button'));
      button.type = 'button';
      button.textContent = label;
      button.addEventListener('click', callback);
    }

    menu_div.appendChild(menu);

    const delete_button = section.querySelector('button.delete') as HTMLButtonElement;

    delete_button.addEventListener('click', () => {
      this.disabled = !this.disabled;
    });
  }

  update() {
    this.#body.value = JSON.stringify(this.#editor.getJSON());
    console.log('body value: ', this.#body.value);
  }
}
