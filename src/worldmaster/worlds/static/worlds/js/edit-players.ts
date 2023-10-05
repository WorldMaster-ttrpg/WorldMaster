function add_player(button: HTMLButtonElement) {
  const li = button.parentElement as HTMLLIElement;
  const list = li.parentElement as HTMLOListElement | HTMLUListElement;

  const new_player_li = document.createElement('li');
  list.insertBefore(new_player_li, li)

  const player = new_player_li.appendChild(document.createElement('input'));
  player.name = 'player'

  new_player_li.appendChild(document.createTextNode("\n"));

  const delete_button = new_player_li.appendChild(document.createElement('button'));
  delete_button.type = 'button';
  delete_button.textContent = '🗑️';
  delete_button.classList.add('delete-player')
  delete_button.addEventListener('click', (event) => delete_player(event.target as HTMLButtonElement));
}

/** Delete the given player.
 */
function delete_player(button: HTMLButtonElement) {
  const li = button.parentElement as HTMLLIElement;
  const list = li.parentElement as HTMLOListElement | HTMLUListElement;
  list.removeChild(li);
}

for (const add_player_button of document.querySelectorAll('fieldset.players .add-player')) {
  add_player_button.addEventListener('click', (event) => add_player(event.target as HTMLButtonElement));
}

for (const delete_player_button of document.querySelectorAll('fieldset.players .delete-player')) {
  delete_player_button.addEventListener('click', (event) => delete_player(event.target as HTMLButtonElement));
}

export {}
