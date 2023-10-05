function get_order_from_li(li: Element | null): number | null {
  if (li === null) {
    return null;
  }
  const section_order_input: HTMLInputElement | null | undefined = li.querySelector("input[name='wiki-section-order']") as HTMLInputElement | null;
  return Number((section_order_input as HTMLInputElement).value);
}

function add_section(button: HTMLButtonElement) {
  const li = button.parentElement as HTMLLIElement;
  const prev_sibling_order = get_order_from_li(li.previousElementSibling);
  const next_sibling_order = get_order_from_li(li.nextElementSibling);
  let order = 0;
  if (prev_sibling_order !== null && next_sibling_order !== null) {
    order = prev_sibling_order / 2.0 + next_sibling_order / 2.0;
  } else if (prev_sibling_order !== null) {
    order = prev_sibling_order + 1.0;
  } else if (next_sibling_order !== null) {
    order = next_sibling_order - 1.0;
  }
  // Otherwise this is the only section, and should just stay 0 in order.

  const new_button_li = li.cloneNode(true) as HTMLLIElement;
  li.parentElement?.insertBefore(new_button_li, li)
  new_button_li.childNodes[0].addEventListener('click', (event) => add_section(event.target as HTMLButtonElement));

  const new_section_li = document.createElement('li');
  li.parentElement?.insertBefore(new_section_li, li)

  const section_id = new_section_li.appendChild(document.createElement('input'));
  section_id.hidden = true;
  section_id.name = 'wiki-section-id';

  // Leave the value empty to tell the server that it's creating a new section
  section_id.value = '';

  const section_order = new_section_li.appendChild(document.createElement('input'));
  section_order.hidden = true;
  section_order.name = 'wiki-section-order';
  section_order.value = order.toString();

  const section = new_section_li.appendChild(document.createElement('textarea'));
  section.name = 'wiki-section'

  new_section_li.appendChild(document.createTextNode("\n"));

  const delete_button = new_section_li.appendChild(document.createElement('button'));
  delete_button.type = 'button';
  delete_button.textContent = '🗑️';
  delete_button.classList.add('delete-section')
  delete_button.addEventListener('click', (event) => delete_section(event.target as HTMLButtonElement));
}

/** Toggles deletion for the given section.
 */
function delete_section(button: HTMLButtonElement) {
  const li = button.parentElement as HTMLLIElement;
  const section_id = li.querySelector("[name='wiki-section-id']") as HTMLInputElement;
  const section_order = li.querySelector("[name='wiki-section-order']") as HTMLInputElement;
  const section = li.querySelector("[name='wiki-section']") as HTMLInputElement;
  section_id.disabled = !section_id.disabled;
  section_order.disabled = !section_order.disabled;
  section.disabled = !section.disabled;
}

for (const add_section_button of document.querySelectorAll('fieldset.wiki .add-section')) {
  add_section_button.addEventListener('click', (event) => add_section(event.target as HTMLButtonElement));
}

for (const delete_section_button of document.querySelectorAll('fieldset.wiki .delete-section')) {
  delete_section_button.addEventListener('click', (event) => delete_section(event.target as HTMLButtonElement));
}

console.log('could change again 3');

export {}

