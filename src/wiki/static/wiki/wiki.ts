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

  const new_button_li = li.cloneNode(true) as HTMLLIElement;
  li.parentElement?.insertBefore(new_button_li, li)
  new_button_li.childNodes[0].addEventListener('click', (event) => add_section(event.target as HTMLButtonElement));

  const new_section_li = document.createElement('li');
  li.parentElement?.insertBefore(new_section_li, li)

  const section_id = new_section_li.appendChild(document.createElement('input'));
  section_id.hidden = true;
  section_id.name = 'wiki-section-id';
  section_id.value = '-1';

  const section_order = new_section_li.appendChild(document.createElement('input'));
  section_order.hidden = true;
  section_order.name = 'wiki-section-order';
  section_order.value = order.toString();

  const section = new_section_li.appendChild(document.createElement('textarea'));
  section.name = 'wiki-section'
}

for (const add_section_button of document.getElementsByClassName('add-section')) {
  add_section_button.addEventListener('click', (event) => add_section(event.target as HTMLButtonElement));
}
