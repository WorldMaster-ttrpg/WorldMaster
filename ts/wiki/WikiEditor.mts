import { SectionEditor } from './SectionEditor.mjs';

/** A dynamic wiki editor attached to the wiki fieldset.
*/
export class WikiEditor {
  private editors: Set<SectionEditor> = new Set();

  static #findForm(element: Element): HTMLFormElement | null {
    if (element instanceof HTMLFormElement) {
      return element;
    }

    const parent = element.parentElement;
    if (parent !== null) {
      return this.#findForm(parent);
    } else {
      return null;
    }
  }

  constructor(wiki: HTMLFieldSetElement) {
    const form = WikiEditor.#findForm(wiki);
    if (form === null) {
      throw new Error('The wiki editor needs to be in a form');
    }

    for (const section of wiki.querySelectorAll('.section')) {
      this.editors.add(new SectionEditor(section as HTMLLIElement));
    }

    for (const add_section_button of wiki.querySelectorAll('.add-section button')) {
      add_section_button.addEventListener(
        'click',
        (event) => {
          this.#add_section(event.target as HTMLButtonElement);
        },
      );
    }

    form.addEventListener('submit', () => {
      for (const editor of this.editors) {
        if (!editor.disabled) {
          editor.update();
        }
      }
    });
  }

  static #get_order_from_section(li: Element | null): number | null {
    if (li === null) {
      return null;
    }
    const order_input = li.querySelector(".order") as HTMLInputElement;
    return Number(order_input.value);
  }

  #add_section(button: HTMLButtonElement) {
    const add_section_li = button.parentElement as HTMLLIElement;
    const prev_section_order = WikiEditor.#get_order_from_section(add_section_li.previousElementSibling);
    const next_section_order = WikiEditor.#get_order_from_section(add_section_li.nextElementSibling);
    let order = 0;
    if (prev_section_order !== null && next_section_order !== null) {
      order = prev_section_order / 2 + next_section_order / 2;
    } else if (prev_section_order !== null) {
      order = prev_section_order + 1;
    } else if (next_section_order !== null) {
      order = next_section_order - 1;
    }
    // Otherwise this is the only section, and should stay 0 in order.

    const fragment = new DocumentFragment();

    const new_button_li = fragment.appendChild(add_section_li.cloneNode(true) as HTMLLIElement);
    new_button_li.querySelector('button')
      ?.addEventListener(
        'click',
        (event) => {
          this.#add_section(event.target as HTMLButtonElement);
        },
      );

    const section_li = fragment.appendChild(document.createElement('li'));
    section_li.classList.add('section');

    const section_id = section_li.appendChild(document.createElement('input'));
    section_id.hidden = true;
    section_id.name = 'wiki-section-id';
    section_id.classList.add('id');

    // Leave the value empty to tell the server that it's creating a new section
    section_id.value = '';

    const section_order = section_li.appendChild(document.createElement('input'));
    section_order.hidden = true;
    section_order.name = 'wiki-section-order';
    section_order.classList.add('order');
    section_order.value = order.toString();

    const section_body = section_li.appendChild(document.createElement('input'));
    section_body.hidden = true;
    section_body.name = 'wiki-section-body';
    section_body.classList.add('body');

    const delete_button = section_li.appendChild(document.createElement('button'));
    delete_button.type = 'button';
    delete_button.textContent = '🗑️';
    delete_button.classList.add('section');

    add_section_li.parentElement?.insertBefore(section_li, fragment);

    this.editors.add(new SectionEditor(section_li));
  }
}
