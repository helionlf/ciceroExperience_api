document.addEventListener("DOMContentLoaded", () => {
  const countrySelect = document.getElementById("country");
  const stateSelect = document.getElementById("state");
  const citySelect = document.getElementById("city");

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

  fetchWithCache("countries", "/static/data/countries.json")
    .then(countries => {
      countries.forEach(country => {
        const option = document.createElement("option");
        option.value = country.iso2;
        option.textContent = country.name;
        countrySelect.appendChild(option);
      });
    })
    .catch(err => console.error("Erro ao carregar países:", err));

  countrySelect.addEventListener("change", async () => {
    const countryCode = countrySelect.value;

    stateSelect.innerHTML = '<option value="">Selecione um estado</option>';
    citySelect.innerHTML = '<option value="">Selecione uma cidade</option>';

    if (!countryCode) return;

    try {
      let states;
      try {
        states = await fetchWithCache(`states_${countryCode}`, `/static/data/states/${countryCode}.json`);
      } catch (e) {
        console.warn(`[Estados] Arquivo ${countryCode}.json não encontrado para ${countryCode}.`);
      }

      if (!states || states.length === 0) {
        console.warn(`Nenhuma estado encontrado para este país.`);
        citySelect.innerHTML = '<option value="">Nenhum estado encontrado</option>';
        return;
      }

      states.forEach(state => {
        const option = document.createElement("option");
        option.value = state.iso2;
        option.textContent = state.name;
        stateSelect.appendChild(option);
      });
    } catch (err) {
      console.error("Erro ao carregar estados:", err);
    }
  });

  stateSelect.addEventListener("change", async () => {
    const stateCode = stateSelect.value;
    const countryCode = countrySelect.value;
    const BRAZIL_ISO = 'BR';

    citySelect.innerHTML = '<option value="">Selecione uma cidade</option>';
    if (!stateCode || !countryCode) return;

    let citiesList = null;

    if (countryCode === BRAZIL_ISO) {
      try {
        let rawData = await fetchWithCache(`cities_${stateCode}`, `/static/data/cities/${stateCode}.json`);

        const stateData = Array.isArray(rawData) ? rawData[0] : rawData;

        citiesList = stateData ? stateData.cities : null;

      } catch (e) {
        console.warn(`[Cidades] Arquivo ${stateCode}.json não encontrado para ${countryCode}.`);
      }
    }

    if (!citiesList || citiesList.length === 0) {
      console.warn(`Nenhuma cidade encontrada para este estado.`);
      citySelect.innerHTML = '<option value="">Nenhuma cidade encontrada</option>';
      return;
    }

    citiesList.forEach(city => {
      const option = document.createElement("option");
      option.textContent = city.name;
      citySelect.appendChild(option);
    });
  });
});
