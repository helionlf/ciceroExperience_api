document.addEventListener("DOMContentLoaded", () => {
  const countrySelect = document.getElementById("country");
  const stateSelect = document.getElementById("state");
  const citySelect = document.getElementById("city");

  const BRAZIL_ISO = "BR";

  async function fetchWithCache(key, url) {
    const cached = localStorage.getItem(key);
    if (cached) {
      return JSON.parse(cached);
    }

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Erro ${response.status}: Falha ao carregar ${url}`);
    }

    const data = await response.json();
    localStorage.setItem(key, JSON.stringify(data));
    return data;
  }

  function resetSelect(selectEl, placeholder) {
    selectEl.innerHTML = "";
    const option = document.createElement("option");
    option.value = "";
    option.textContent = placeholder;
    selectEl.appendChild(option);
  }

  function fillSelect(selectEl, items, mapper) {
    items.forEach(item => {
      const mapped = mapper(item);
      const option = document.createElement("option");
      option.value = mapped.value;
      option.textContent = mapped.label;
      selectEl.appendChild(option);
    });
  }

  fetchWithCache("countries", "/static/data/countries.json")
    .then(countries => {
      resetSelect(countrySelect, "Selecione um pais");
      fillSelect(countrySelect, countries, country => ({
        value: country.iso2,
        label: country.name
      }));
    })
    .catch(err => console.error("Erro ao carregar paises:", err));

  countrySelect.addEventListener("change", async () => {
    const countryCode = countrySelect.value;

    resetSelect(stateSelect, "Selecione um estado");
    resetSelect(citySelect, "Selecione uma cidade");

    if (!countryCode) return;

    try {
      let states;
      try {
        states = await fetchWithCache(`states_${countryCode}`, `/static/data/states/${countryCode}.json`);
      } catch (e) {
        console.warn(`[Estados] Arquivo ${countryCode}.json nao encontrado para ${countryCode}.`);
      }

      if (!states || states.length === 0) {
        console.warn("Nenhum estado encontrado para este pais.");
        citySelect.innerHTML = '<option value="">Nenhum estado encontrado</option>';
        return;
      }

      fillSelect(stateSelect, states, state => ({
        value: state.iso2,
        label: state.name
      }));
    } catch (err) {
      console.error("Erro ao carregar estados:", err);
    }
  });

  stateSelect.addEventListener("change", async () => {
    const stateCode = stateSelect.value;
    const countryCode = countrySelect.value;

    resetSelect(citySelect, "Selecione uma cidade");
    if (!stateCode || !countryCode) return;

    let citiesList = null;

    if (countryCode === BRAZIL_ISO) {
      try {
        const rawData = await fetchWithCache(`cities_${stateCode}`, `/static/data/cities/${stateCode}.json`);
        const stateData = Array.isArray(rawData) ? rawData[0] : rawData;
        citiesList = stateData ? stateData.cities : null;
      } catch (e) {
        console.warn(`[Cidades] Arquivo ${stateCode}.json nao encontrado para ${countryCode}.`);
      }
    }

    if (!citiesList || citiesList.length === 0) {
      console.warn("Nenhuma cidade encontrada para este estado.");
      citySelect.innerHTML = '<option value="">Nenhuma cidade encontrada</option>';
      return;
    }

    fillSelect(citySelect, citiesList, city => ({
      value: city.name,
      label: city.name
    }));
  });
});
