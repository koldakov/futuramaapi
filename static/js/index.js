document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('character-modal');

  modal.addEventListener('show.bs.modal', async (event) => {
    const characterId = event.relatedTarget.dataset.characterId;
    const endpoint = `/api/characters/${characterId}`;

    const elements = getModalElements();

    setEndpoint(elements.endpointEl, endpoint);

    const data = await fetchCharacter(endpoint);

    setCharacterImage(elements.imageEl, data);
    setCharacterName(elements.nameEl, data.name);
    setCharacterBadges(elements, data);
    setCharacterJSON(elements.jsonEl, data);
  });
});

function getModalElements() {
  return {
    imageEl: document.getElementById('modal-character-image'),
    nameEl: document.getElementById('modal-character-name'),
    statusEl: document.getElementById('modal-status'),
    genderEl: document.getElementById('modal-gender'),
    speciesEl: document.getElementById('modal-species'),
    endpointEl: document.getElementById('modal-endpoint'),
    jsonEl: document.getElementById('modal-json'),
  };
}

function setEndpoint(el, endpoint) {
  el.textContent = `GET ${endpoint}`;
}

async function fetchCharacter(endpoint) {
  const res = await fetch(endpoint);
  return res.json();
}

function setCharacterImage(el, data) {
  el.src = data.image;
  el.alt = data.name;
}

function setCharacterName(el, name) {
  el.textContent = name;
}

function setCharacterBadges(elements, data) {
  const { statusEl, genderEl, speciesEl } = elements;

  statusEl.textContent = data.status;
  statusEl.className = `badge badge-status badge-status-${data.status.toLowerCase()}`;

  genderEl.textContent = data.gender;
  genderEl.className = `badge badge-gender badge-gender-${data.gender.toLowerCase()}`;

  speciesEl.textContent = data.species;
  speciesEl.className = `badge badge-species badge-species-${data.species.toLowerCase()}`;
}

function setCharacterJSON(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
}
