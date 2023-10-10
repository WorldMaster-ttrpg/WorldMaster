import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';

export class SectionEditor {
  #id: HTMLInputElement;
  #order: HTMLInputElement;
  #body: HTMLInputElement;
  #editor_div: HTMLDivElement;
  #editor: Editor;
  #disabled: boolean;
  #delete_button: HTMLButtonElement;

  public get disabled(): boolean {
    return this.#disabled;
  }
  public set disabled(value: boolean) {
    this.#disabled = value;
    this.#id.disabled = value;
    this.#order.disabled = value;
    this.#body.disabled = value;
    this.#editor.setEditable(!value);
  }

  constructor(section: HTMLLIElement) {
    this.#id = section.querySelector('input.id') as HTMLInputElement;
    this.#order = section.querySelector('input.order') as HTMLInputElement;
    this.#body = section.querySelector('input.body') as HTMLInputElement;
    this.#disabled = this.#body.disabled;
    this.#editor_div = document.createElement('div');
    this.#editor_div.classList.add('editor');
    this.#body.insertAdjacentElement('afterend', this.#editor_div);
    this.#editor = new Editor({
      element: this.#editor_div,
      extensions: [
        StarterKit,
      ],
      content: JSON.parse(this.#body.value),
    });

    this.#delete_button = section.querySelector('button.delete') as HTMLButtonElement;

    this.#delete_button.addEventListener('click', () => {
      this.disabled = !this.disabled;
    });
  }

  update() {
    this.#body.value = JSON.stringify(this.#editor.getJSON());
  }
}
